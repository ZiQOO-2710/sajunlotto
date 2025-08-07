"""
YouTube 학습 시스템 서비스
YouTube 영상에서 사주 관련 지식을 학습하고 예측에 활용
"""

import os
import re
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import sqlite3
from sqlalchemy.orm import Session

# YouTube 관련
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# 음성 처리 (선택적)
try:
    import whisper
    import torch
    from moviepy.editor import VideoFileClip
    from pydub import AudioSegment
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"음성 처리 라이브러리 누락 (자막 기반 학습은 가능): {e}")
    AUDIO_PROCESSING_AVAILABLE = False

# AI/NLP (선택적 - 없어도 작동)
SENTENCE_TRANSFORMERS_AVAILABLE = False
try:
    # SentenceTransformer는 선택적 - 없어도 기본 기능은 작동
    pass  # 일단 비활성화
except ImportError:
    pass


class YouTubeService:
    """YouTube 학습 서비스"""

    def __init__(self, db: Session, knowledge_db_path: str = "saju_knowledge_complete.db"):
        self.db = db
        self.knowledge_db_path = knowledge_db_path
        
        # 사주 전문 용어 정의
        self.saju_terms = {
            # 천간 (10개)
            '천간': ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'],
            
            # 지지 (12개) 
            '지지': ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'],
            
            # 오행 (5개)
            '오행': ['목', '화', '토', '금', '수', '나무', '불', '흙', '쇠', '물'],
            
            # 십신 (10개)
            '십신': ['비견', '겁재', '식신', '상관', '편재', '정재', '편관', '정관', '편인', '정인'],
            
            # 육친
            '육친': ['부모', '형제', '부부', '자녀', '친구', '직장'],
            
            # 운세 관련
            '운세': ['대운', '세운', '월운', '일운', '시운', '길운', '흉운', '화', '복'],
            
            # 궁합 관련
            '궁합': ['상생', '상극', '조화', '충돌', '합', '형', '해', '파'],
            
            # 성격 특성
            '성격': ['성격', '기질', '성향', '특성', '장점', '단점', '재능', '능력'],
            
            # 직업/진로
            '직업': ['직업', '진로', '적성', '사업', '취업', '창업', '발전', '성공'],
            
            # 건강
            '건강': ['건강', '체질', '질병', '장수', '수명', '병', '약', '치료'],
            
            # 재물
            '재물': ['돈', '재물', '재운', '부', '투자', '사업', '수입', '지출', '저축'],
            
            # 애정/결혼
            '애정': ['사랑', '연애', '결혼', '이혼', '배우자', '만남', '이별', '화합']
        }
        
        # 문장 유형 키워드
        self.sentence_types = {
            'interpretation': ['해석', '의미', '뜻', '표현', '나타낸', '보여준', '말해준'],
            'prediction': ['예측', '운세', '미래', '앞으로', '될것', '가능성', '경향', '흐름'],
            'personality': ['성격', '기질', '성향', '특성', '타입', '스타일', '면모', '모습'],
            'relationship': ['관계', '궁합', '만남', '상대', '파트너', '연인', '배우자', '가족']
        }

        # 지식 데이터베이스 초기화
        self._init_knowledge_db()
        
        # SentenceTransformer 모델 (가능한 경우)
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens')
            except:
                self.sentence_model = None
        else:
            self.sentence_model = None

    def _init_knowledge_db(self):
        """지식 데이터베이스 초기화"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # 지식 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saju_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                video_title TEXT,
                content TEXT,
                saju_terms TEXT,  -- JSON string
                sentence_type TEXT,
                confidence REAL,
                timestamp INTEGER,
                source TEXT DEFAULT 'youtube',
                embedding BLOB,  -- 벡터 임베딩 (선택적)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 영상 정보 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_info (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                duration INTEGER,
                view_count INTEGER,
                upload_date TEXT,
                channel_name TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    async def extract_transcript(self, video_id: str, language: str = 'ko') -> Optional[str]:
        """YouTube 자막 추출"""
        try:
            # YouTubeTranscriptApi 인스턴스 생성
            api = YouTubeTranscriptApi()
            
            # 여러 언어로 자막 시도
            languages_to_try = ['ko', 'en']
            
            for lang in languages_to_try:
                try:
                    # 인스턴스 메소드로 자막 추출
                    transcript = api.fetch(video_id, languages=[lang])
                    
                    # FetchedTranscript 객체에서 텍스트 추출
                    transcript_text = ' '.join([snippet.text for snippet in transcript.snippets])
                    print(f"자막 추출 성공 (언어: {lang}, 길이: {len(transcript_text)})")
                    return transcript_text
                    
                except Exception as lang_error:
                    print(f"언어 {lang} 자막 추출 실패: {lang_error}")
                    continue
            
            # 기본 언어로 자동 자막 시도
            try:
                transcript = api.fetch(video_id)
                transcript_text = ' '.join([snippet.text for snippet in transcript.snippets])
                print(f"기본 자막 추출 성공 (길이: {len(transcript_text)})")
                return transcript_text
            except Exception as auto_error:
                print(f"기본 자막 추출 실패: {auto_error}")
            
            return None
            
        except Exception as e:
            print(f"자막 추출 실패 (video_id: {video_id}): {e}")
            return None

    async def analyze_saju_content(self, text: str) -> Dict[str, Any]:
        """텍스트에서 사주 관련 내용 분석"""
        
        # 사주 용어 추출
        found_terms = {}
        for category, terms in self.saju_terms.items():
            found_in_category = []
            for term in terms:
                if term in text:
                    found_in_category.append(term)
            if found_in_category:
                found_terms[category] = found_in_category

        # 문장 유형 분류
        sentence_type = 'general'
        max_score = 0
        
        for s_type, keywords in self.sentence_types.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > max_score:
                max_score = score
                sentence_type = s_type

        # 신뢰도 계산 (사주 용어 밀도 기반)
        total_terms = sum(len(terms) for terms in found_terms.values())
        text_length = len(text)
        confidence = min(total_terms / max(text_length / 100, 1), 1.0)  # 정규화

        return {
            'saju_terms': found_terms,
            'sentence_type': sentence_type,
            'confidence': confidence,
            'term_count': total_terms,
            'text_length': text_length
        }

    async def learn_from_video(self, video_id: str) -> Dict[str, Any]:
        """단일 영상에서 학습"""
        
        # 자막 추출
        transcript = await self.extract_transcript(video_id)
        if not transcript:
            return {"success": False, "error": "자막 추출 실패"}

        # 영상 정보 수집
        video_info = await self._get_video_info(video_id)
        
        # 텍스트 분할 및 분석
        sentences = self._split_text_into_sentences(transcript)
        learned_count = 0
        
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        try:
            for sentence in sentences:
                if len(sentence.strip()) < 20:  # 너무 짧은 문장 스킵
                    continue
                    
                analysis = await self.analyze_saju_content(sentence)
                
                # 사주 관련 내용만 저장 (신뢰도 0.1 이상)
                if analysis['confidence'] > 0.1:
                    cursor.execute("""
                        INSERT INTO saju_knowledge 
                        (video_id, video_title, content, saju_terms, sentence_type, confidence, timestamp, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        video_id,
                        video_info.get('title', ''),
                        sentence,
                        json.dumps(analysis['saju_terms'], ensure_ascii=False),
                        analysis['sentence_type'],
                        analysis['confidence'],
                        int(datetime.now().timestamp()),
                        'youtube_transcript'
                    ))
                    learned_count += 1
            
            # 영상 정보 저장
            cursor.execute("""
                INSERT OR REPLACE INTO video_info 
                (video_id, title, duration, view_count, upload_date, channel_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                video_id,
                video_info.get('title', ''),
                video_info.get('duration', 0),
                video_info.get('view_count', 0),
                video_info.get('upload_date', ''),
                video_info.get('channel_name', '')
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

        return {
            "success": True,
            "video_id": video_id,
            "learned_sentences": learned_count,
            "total_sentences": len(sentences),
            "video_info": video_info
        }

    async def batch_learn_from_videos(self, video_ids: List[str]) -> Dict[str, Any]:
        """여러 영상에서 일괄 학습"""
        
        results = []
        total_learned = 0
        
        for video_id in video_ids:
            result = await self.learn_from_video(video_id)
            results.append(result)
            
            if result.get("success"):
                total_learned += result.get("learned_sentences", 0)

        return {
            "success": True,
            "processed_videos": len(video_ids),
            "total_learned_sentences": total_learned,
            "results": results
        }

    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """지식 검색"""
        
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # 단순 텍스트 검색 (개선 가능)
        cursor.execute("""
            SELECT video_id, video_title, content, saju_terms, sentence_type, confidence, created_at
            FROM saju_knowledge 
            WHERE content LIKE ? OR saju_terms LIKE ?
            ORDER BY confidence DESC, created_at DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "video_id": row[0],
                "video_title": row[1],
                "content": row[2],
                "saju_terms": json.loads(row[3]) if row[3] else {},
                "sentence_type": row[4],
                "confidence": row[5],
                "created_at": row[6]
            })
        
        conn.close()
        return results

    async def get_knowledge_summary(self) -> Dict[str, Any]:
        """학습된 지식 요약"""
        
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # 기본 통계
        cursor.execute("SELECT COUNT(*) FROM saju_knowledge")
        total_knowledge = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT video_id) FROM saju_knowledge")
        total_videos = cursor.fetchone()[0]
        
        # 문장 유형별 통계
        cursor.execute("""
            SELECT sentence_type, COUNT(*) 
            FROM saju_knowledge 
            GROUP BY sentence_type
        """)
        sentence_type_stats = dict(cursor.fetchall())
        
        # 평균 신뢰도
        cursor.execute("SELECT AVG(confidence) FROM saju_knowledge")
        avg_confidence = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_knowledge_entries": total_knowledge,
            "total_videos_processed": total_videos,
            "sentence_type_distribution": sentence_type_stats,
            "average_confidence": round(avg_confidence, 3),
            "database_path": self.knowledge_db_path
        }

    async def get_personalized_knowledge(self, birth_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """개인 맞춤형 사주 지식 조회"""
        
        # 생년월일 기반으로 관련 키워드 생성
        birth_year = birth_info.get('birth_year', 2000)
        birth_month = birth_info.get('birth_month', 1)
        
        # 간단한 개인화 로직 (실제로는 더 정교해야 함)
        keywords = []
        
        # 연도 기반 천간/지지
        year_gan_index = (birth_year - 4) % 10
        year_ji_index = (birth_year - 4) % 12
        
        if year_gan_index < len(self.saju_terms['천간']):
            keywords.append(self.saju_terms['천간'][year_gan_index])
        if year_ji_index < len(self.saju_terms['지지']):
            keywords.append(self.saju_terms['지지'][year_ji_index])
        
        # 계절 기반 오행
        season_elements = {
            1: '수', 2: '수', 3: '목', 4: '목', 5: '목', 6: '화',
            7: '화', 8: '화', 9: '금', 10: '금', 11: '금', 12: '수'
        }
        season_element = season_elements.get(birth_month, '토')
        keywords.append(season_element)
        
        # 키워드 기반 지식 검색
        all_results = []
        for keyword in keywords:
            results = await self.search_knowledge(keyword, 5)
            all_results.extend(results)
        
        # 중복 제거 및 신뢰도순 정렬
        unique_results = {}
        for result in all_results:
            content = result['content']
            if content not in unique_results or unique_results[content]['confidence'] < result['confidence']:
                unique_results[content] = result
        
        return sorted(unique_results.values(), key=lambda x: x['confidence'], reverse=True)[:10]

    def _split_text_into_sentences(self, text: str) -> List[str]:
        """텍스트를 문장으로 분할"""
        # 한국어 문장 분할 (간단한 버전)
        sentences = re.split(r'[.!?。！？]\s*', text)
        return [s.strip() for s in sentences if s.strip()]

    async def _get_video_info(self, video_id: str) -> Dict[str, Any]:
        """YouTube 영상 정보 수집"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f'https://www.youtube.com/watch?v={video_id}',
                    download=False
                )
                
                return {
                    'title': info.get('title', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'channel_name': info.get('uploader', ''),
                    'description': info.get('description', '')[:500]  # 처음 500자만
                }
                
        except Exception as e:
            print(f"영상 정보 수집 실패: {e}")
            return {}

    async def enhance_prediction_with_knowledge(self, user_saju_data: Dict[str, Any], base_prediction: List[int]) -> Dict[str, Any]:
        """학습된 지식을 활용하여 예측 향상"""
        
        # 개인 맞춤형 지식 조회
        personalized_knowledge = await self.get_personalized_knowledge(user_saju_data)
        
        if not personalized_knowledge:
            return {
                "enhanced_prediction": base_prediction,
                "confidence_boost": 0,
                "knowledge_applied": [],
                "recommendations": ["개인 맞춤형 지식이 부족합니다. 더 많은 학습이 필요합니다."]
            }
        
        # 지식 기반 신뢰도 부스트 계산
        total_confidence = sum(k['confidence'] for k in personalized_knowledge[:5])
        confidence_boost = min(total_confidence * 0.1, 0.15)  # 최대 15% 부스트
        
        # 추천사항 생성
        recommendations = []
        for knowledge in personalized_knowledge[:3]:
            if knowledge['sentence_type'] == 'prediction':
                recommendations.append(f"예측 관련: {knowledge['content'][:100]}...")
            elif knowledge['sentence_type'] == 'personality':
                recommendations.append(f"성격 특성: {knowledge['content'][:100]}...")
        
        return {
            "enhanced_prediction": base_prediction,  # 실제로는 지식 기반 조정 로직 적용
            "confidence_boost": round(confidence_boost, 3),
            "knowledge_applied": [k['content'][:100] + "..." for k in personalized_knowledge[:3]],
            "recommendations": recommendations or ["개인화된 추천사항을 생성할 수 없습니다."],
            "knowledge_sources": len(personalized_knowledge)
        }