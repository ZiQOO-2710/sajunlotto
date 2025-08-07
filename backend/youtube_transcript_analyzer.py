#!/usr/bin/env python3
"""
유튜브 자막 추출 및 사주 지식 학습 시스템
YouTube 영상의 자막을 분석하여 사주 관련 지식을 추출하고 학습합니다.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import sqlite3
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError:
    print("youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("sentence-transformers not installed. Install with: pip install sentence-transformers")

from youtube_crawler import YouTubeSajuCrawler

class SajuTranscriptAnalyzer:
    """사주 관련 YouTube 자막 분석 및 학습 시스템"""
    
    def __init__(self, knowledge_db_path: str = "saju_knowledge.db"):
        """
        초기화
        Args:
            knowledge_db_path: 지식 데이터베이스 경로
        """
        self.knowledge_db_path = knowledge_db_path
        self.setup_knowledge_database()
        
        # 사주 관련 핵심 용어들
        self.saju_terms = {
            '천간': ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'],
            '지지': ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'],
            '오행': ['목', '화', '토', '금', '수'],
            '음양': ['양', '음', '양간', '음간'],
            '십신': ['비견', '겁재', '식신', '상관', '편재', '정재', '편관', '정관', '편인', '정인'],
            '운세_개념': ['대운', '세운', '월운', '일운', '신살', '공망', '형충파해'],
            '사주_구성': ['년주', '월주', '일주', '시주', '일간', '월령']
        }
        
        # 문장 임베딩 모델 (한국어 지원)
        try:
            self.embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        except:
            print("임베딩 모델 로드 실패. 기본 분석 기능만 사용됩니다.")
            self.embedding_model = None
    
    def setup_knowledge_database(self):
        """지식 베이스 데이터베이스 초기화"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # 자막 원본 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT,
                channel_title TEXT,
                transcript_text TEXT,
                language TEXT DEFAULT 'ko',
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                word_count INTEGER,
                saju_relevance_score REAL
            )
        ''')
        
        # 추출된 사주 지식 조각들
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saju_knowledge_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                chunk_text TEXT,
                saju_terms TEXT, -- JSON array of extracted terms
                knowledge_category TEXT, -- 예측, 해석, 이론, 실전 등
                confidence_score REAL,
                embedding BLOB, -- sentence embedding
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES video_transcripts (video_id)
            )
        ''')
        
        # 사주 용어 사전
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saju_terminology (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT UNIQUE NOT NULL,
                category TEXT, -- 천간, 지지, 오행 등
                definition TEXT,
                examples TEXT, -- JSON array
                frequency INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 학습된 패턴들
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT, -- 해석_패턴, 예측_패턴 등
                condition_terms TEXT, -- JSON: 조건이 되는 사주 요소들
                result_description TEXT, -- 결과 설명
                confidence REAL,
                source_count INTEGER DEFAULT 1, -- 이 패턴을 뒷받침하는 소스 개수
                examples TEXT, -- JSON: 실제 예시들
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def extract_transcript(self, video_id: str) -> Optional[str]:
        """
        YouTube 영상의 자막을 추출합니다.
        
        Args:
            video_id: YouTube 영상 ID
            
        Returns:
            추출된 자막 텍스트 또는 None
        """
        try:
            # 한국어 자막 우선, 없으면 다른 언어
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            transcript = None
            language_used = None
            
            # 한국어 자막 찾기
            try:
                transcript = transcript_list.find_transcript(['ko'])
                language_used = 'ko'
            except:
                # 한국어가 없으면 자동 생성 자막이나 다른 언어
                try:
                    transcript = transcript_list.find_generated_transcript(['ko'])
                    language_used = 'ko-generated'
                except:
                    # 영어라도 있으면 가져오기
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                        language_used = 'en'
                    except:
                        return None
            
            # 자막 텍스트 추출
            transcript_data = transcript.fetch()
            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript_data)
            
            return {
                'text': transcript_text,
                'language': language_used,
                'word_count': len(transcript_text.split())
            }
            
        except Exception as e:
            print(f"자막 추출 실패 ({video_id}): {str(e)}")
            return None
    
    def analyze_saju_content(self, text: str) -> Dict:
        """
        텍스트에서 사주 관련 내용을 분석합니다.
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            분석 결과 딕셔너리
        """
        analysis = {
            'saju_terms_found': {},
            'relevance_score': 0.0,
            'knowledge_chunks': [],
            'patterns': []
        }
        
        text_lower = text.lower()
        
        # 1. 사주 용어 추출
        total_terms_found = 0
        for category, terms in self.saju_terms.items():
            found_terms = []
            for term in terms:
                if term in text:
                    count = text.count(term)
                    found_terms.append({'term': term, 'count': count})
                    total_terms_found += count
            
            if found_terms:
                analysis['saju_terms_found'][category] = found_terms
        
        # 2. 관련성 점수 계산
        text_length = len(text.split())
        if text_length > 0:
            analysis['relevance_score'] = min(total_terms_found / text_length * 100, 10.0)
        
        # 3. 지식 덩어리 추출 (문장 단위)
        sentences = self._split_into_sentences(text)
        for sentence in sentences:
            if self._is_saju_knowledge_sentence(sentence):
                chunk = {
                    'text': sentence.strip(),
                    'terms': self._extract_terms_from_sentence(sentence),
                    'category': self._classify_knowledge_type(sentence)
                }
                analysis['knowledge_chunks'].append(chunk)
        
        # 4. 패턴 분석 (간단한 규칙 기반)
        patterns = self._extract_patterns(text)
        analysis['patterns'] = patterns
        
        return analysis
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """텍스트를 문장으로 분할"""
        # 한국어 문장 구분자
        sentences = re.split(r'[.!?。！？]\s*', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _is_saju_knowledge_sentence(self, sentence: str) -> bool:
        """문장이 사주 지식을 포함하는지 판단"""
        saju_indicator_words = [
            '사주', '팔자', '운세', '명리', '오행', '천간', '지지',
            '갑을병정', '자축인묘', '대운', '세운', '일간', '월령',
            '해석', '분석', '의미', '특징', '성격', '운명'
        ]
        
        sentence_lower = sentence.lower()
        return any(word in sentence_lower for word in saju_indicator_words)
    
    def _extract_terms_from_sentence(self, sentence: str) -> List[str]:
        """문장에서 사주 용어 추출"""
        found_terms = []
        for category, terms in self.saju_terms.items():
            for term in terms:
                if term in sentence:
                    found_terms.append(term)
        return found_terms
    
    def _classify_knowledge_type(self, sentence: str) -> str:
        """지식 유형 분류"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['예측', '앞으로', '미래', '올해', '내년']):
            return '예측'
        elif any(word in sentence_lower for word in ['해석', '의미', '뜻', '나타내']):
            return '해석'
        elif any(word in sentence_lower for word in ['성격', '성향', '특징', '기질']):
            return '성격분석'
        elif any(word in sentence_lower for word in ['궁합', '인연', '결혼', '연애']):
            return '관계'
        elif any(word in sentence_lower for word in ['직업', '진로', '사업', '돈', '재물']):
            return '진로재물'
        else:
            return '일반'
    
    def _extract_patterns(self, text: str) -> List[Dict]:
        """간단한 패턴 추출"""
        patterns = []
        
        # "A이면 B다" 형태의 패턴 찾기
        condition_patterns = re.findall(r'([가-힣\s]+이면|[가-힣\s]+일때|[가-힣\s]+경우)\s*([가-힣\s,]+[다니])', text)
        
        for condition, result in condition_patterns:
            if self._contains_saju_terms(condition) or self._contains_saju_terms(result):
                patterns.append({
                    'type': '조건부_해석',
                    'condition': condition.strip(),
                    'result': result.strip(),
                    'confidence': 0.7
                })
        
        return patterns
    
    def _contains_saju_terms(self, text: str) -> bool:
        """텍스트에 사주 용어가 포함되어 있는지 확인"""
        for terms in self.saju_terms.values():
            if any(term in text for term in terms):
                return True
        return False
    
    def save_transcript_analysis(self, video_id: str, video_info: Dict, transcript_data: Dict, analysis: Dict):
        """분석 결과를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        try:
            # 1. 자막 원본 저장
            cursor.execute('''
                INSERT OR REPLACE INTO video_transcripts 
                (video_id, title, channel_title, transcript_text, language, word_count, saju_relevance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_id,
                video_info.get('title', ''),
                video_info.get('channel_title', ''),
                transcript_data['text'],
                transcript_data['language'],
                transcript_data['word_count'],
                analysis['relevance_score']
            ))
            
            # 2. 지식 덩어리들 저장
            for chunk in analysis['knowledge_chunks']:
                embedding = None
                if self.embedding_model:
                    try:
                        embedding = self.embedding_model.encode(chunk['text'])
                        embedding = embedding.tobytes()
                    except:
                        pass
                
                cursor.execute('''
                    INSERT INTO saju_knowledge_chunks 
                    (video_id, chunk_text, saju_terms, knowledge_category, confidence_score, embedding)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    video_id,
                    chunk['text'],
                    json.dumps(chunk['terms'], ensure_ascii=False),
                    chunk['category'],
                    0.8,  # 기본 신뢰도
                    embedding
                ))
            
            # 3. 용어 빈도 업데이트
            for category, terms in analysis['saju_terms_found'].items():
                for term_data in terms:
                    cursor.execute('''
                        INSERT OR IGNORE INTO saju_terminology (term, category, frequency)
                        VALUES (?, ?, 0)
                    ''', (term_data['term'], category))
                    
                    cursor.execute('''
                        UPDATE saju_terminology 
                        SET frequency = frequency + ?, updated_at = CURRENT_TIMESTAMP
                        WHERE term = ?
                    ''', (term_data['count'], term_data['term']))
            
            # 4. 패턴 저장
            for pattern in analysis['patterns']:
                cursor.execute('''
                    INSERT INTO learned_patterns 
                    (pattern_type, condition_terms, result_description, confidence)
                    VALUES (?, ?, ?, ?)
                ''', (
                    pattern['type'],
                    pattern['condition'],
                    pattern['result'],
                    pattern['confidence']
                ))
            
            conn.commit()
            print(f"✅ 분석 결과 저장 완료: {video_id}")
            
        except Exception as e:
            print(f"❌ 저장 실패 ({video_id}): {str(e)}")
            conn.rollback()
        finally:
            conn.close()
    
    def process_video(self, video_id: str, video_info: Dict = None) -> bool:
        """
        영상 하나의 전체 처리 과정
        
        Args:
            video_id: YouTube 영상 ID
            video_info: 영상 메타데이터 (선택사항)
            
        Returns:
            처리 성공 여부
        """
        try:
            print(f"🎥 영상 처리 시작: {video_id}")
            
            # 1. 자막 추출
            transcript_data = self.extract_transcript(video_id)
            if not transcript_data:
                print(f"❌ 자막 추출 실패: {video_id}")
                return False
            
            print(f"✅ 자막 추출 성공: {transcript_data['word_count']}단어, {transcript_data['language']}")
            
            # 2. 내용 분석
            analysis = self.analyze_saju_content(transcript_data['text'])
            
            print(f"📊 분석 결과:")
            print(f"  - 관련성 점수: {analysis['relevance_score']:.2f}")
            print(f"  - 발견된 사주 용어: {len(analysis['saju_terms_found'])}개 카테고리")
            print(f"  - 지식 덩어리: {len(analysis['knowledge_chunks'])}개")
            print(f"  - 패턴: {len(analysis['patterns'])}개")
            
            # 관련성이 너무 낮으면 건너뛰기
            if analysis['relevance_score'] < 0.1:
                print(f"⚠️ 관련성 점수가 너무 낮아 저장하지 않음: {analysis['relevance_score']:.2f}")
                return False
            
            # 3. 결과 저장
            if not video_info:
                video_info = {'title': f'Video {video_id}', 'channel_title': 'Unknown'}
            
            self.save_transcript_analysis(video_id, video_info, transcript_data, analysis)
            
            return True
            
        except Exception as e:
            print(f"❌ 영상 처리 실패 ({video_id}): {str(e)}")
            return False
    
    def batch_process_videos(self, video_list: List[Dict], max_videos: int = 20) -> Dict:
        """
        여러 영상을 일괄 처리
        
        Args:
            video_list: 영상 정보 리스트 [{'video_id': ..., 'title': ..., ...}, ...]
            max_videos: 최대 처리할 영상 개수
            
        Returns:
            처리 결과 통계
        """
        results = {
            'total_videos': min(len(video_list), max_videos),
            'success_count': 0,
            'failed_count': 0,
            'total_knowledge_chunks': 0,
            'avg_relevance_score': 0.0
        }
        
        processed_videos = video_list[:max_videos]
        
        print(f"🚀 일괄 처리 시작: {len(processed_videos)}개 영상")
        
        relevance_scores = []
        
        for i, video_info in enumerate(processed_videos, 1):
            print(f"\n[{i}/{len(processed_videos)}] 처리 중...")
            
            video_id = video_info.get('video_id')
            if not video_id:
                results['failed_count'] += 1
                continue
            
            success = self.process_video(video_id, video_info)
            
            if success:
                results['success_count'] += 1
                # 관련성 점수는 데이터베이스에서 가져오기
                conn = sqlite3.connect(self.knowledge_db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT saju_relevance_score FROM video_transcripts WHERE video_id = ?', (video_id,))
                row = cursor.fetchone()
                if row:
                    relevance_scores.append(row[0])
                conn.close()
            else:
                results['failed_count'] += 1
        
        # 통계 계산
        if relevance_scores:
            results['avg_relevance_score'] = sum(relevance_scores) / len(relevance_scores)
        
        # 총 지식 덩어리 개수
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM saju_knowledge_chunks')
        results['total_knowledge_chunks'] = cursor.fetchone()[0]
        conn.close()
        
        print(f"\n🎉 일괄 처리 완료!")
        print(f"  - 성공: {results['success_count']}개")
        print(f"  - 실패: {results['failed_count']}개") 
        print(f"  - 평균 관련성: {results['avg_relevance_score']:.2f}")
        print(f"  - 총 지식 덩어리: {results['total_knowledge_chunks']}개")
        
        return results

def main():
    """테스트 및 예시 실행"""
    analyzer = SajuTranscriptAnalyzer()
    
    # YouTube 크롤러로 사주 영상 찾기
    crawler = YouTubeSajuCrawler()
    print("🔍 사주 관련 영상 검색 중...")
    
    videos = crawler.crawl_saju_videos(max_per_keyword=3)  # 테스트용으로 적은 수
    
    if not videos:
        print("❌ 검색된 영상이 없습니다.")
        return
    
    print(f"✅ {len(videos)}개 영상 발견")
    
    # 자막 분석 및 학습
    results = analyzer.batch_process_videos(videos, max_videos=5)
    
    # 결과 출력
    print(f"\n📈 최종 결과:")
    print(f"  - 처리된 영상: {results['success_count']}/{results['total_videos']}")
    print(f"  - 학습된 지식 덩어리: {results['total_knowledge_chunks']}개")
    print(f"  - 평균 관련성 점수: {results['avg_relevance_score']:.2f}")
    
    # 데이터베이스 현황
    conn = sqlite3.connect(analyzer.knowledge_db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM saju_terminology WHERE frequency > 0')
    term_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM learned_patterns')
    pattern_count = cursor.fetchone()[0]
    
    print(f"  - 학습된 사주 용어: {term_count}개")
    print(f"  - 추출된 패턴: {pattern_count}개")
    
    conn.close()

if __name__ == "__main__":
    main()