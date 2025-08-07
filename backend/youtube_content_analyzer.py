#!/usr/bin/env python3
"""
유튜브 영상 전체 콘텐츠 분석 및 사주 지식 학습 시스템
- 자막 추출 및 분석
- 영상 다운로드 및 음성 추출
- STT(Speech-to-Text) 변환
- 통합 콘텐츠 분석 및 지식 학습
"""

import os
import re
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import sqlite3

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

# AI/NLP
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("sentence-transformers 설치 필요: pip install sentence-transformers")

from youtube_crawler import YouTubeSajuCrawler

class YouTubeContentAnalyzer:
    """유튜브 영상 전체 콘텐츠 분석 및 학습 시스템"""
    
    def __init__(self, knowledge_db_path: str = "saju_knowledge_complete.db", temp_dir: str = None):
        """
        초기화
        Args:
            knowledge_db_path: 지식 데이터베이스 경로
            temp_dir: 임시 파일 저장 디렉토리
        """
        self.knowledge_db_path = knowledge_db_path
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        Path(self.temp_dir).mkdir(exist_ok=True)
        
        self.setup_knowledge_database()
        self.setup_ai_models()
        
        # 사주 관련 핵심 용어들 (확장)
        self.saju_terms = {
            '천간': ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'],
            '지지': ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'],
            '오행': ['목', '화', '토', '금', '수', '목행', '화행', '토행', '금행', '수행'],
            '음양': ['양', '음', '양간', '음간', '양지', '음지'],
            '십신': ['비견', '겁재', '식신', '상관', '편재', '정재', '편관', '정관', '편인', '정인'],
            '운세_개념': ['대운', '세운', '월운', '일운', '신살', '공망', '형충파해', '원진', '육합', '삼합'],
            '사주_구성': ['년주', '월주', '일주', '시주', '일간', '월령', '년간', '월간', '시간'],
            '띠별': ['쥐띠', '소띠', '호랑이띠', '토끼띠', '용띠', '뱀띠', '말띠', '양띠', '원숭이띠', '닭띠', '개띠', '돼지띠'],
            '운세_영역': ['재물운', '건강운', '연애운', '결혼운', '직장운', '학업운', '인간관계'],
            '사주_해석': ['좋다', '나쁘다', '길하다', '흉하다', '발전', '쇠퇴', '성공', '실패', '조심', '주의']
        }
        
        # yt-dlp 설정 (음성만 추출)
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.temp_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
    
    def setup_ai_models(self):
        """AI 모델들 초기화"""
        print("🤖 AI 모델 로딩 중...")
        
        # Whisper STT 모델 (한국어 지원) - 선택적
        if AUDIO_PROCESSING_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")  # base, small, medium, large 선택 가능
                print("✅ Whisper STT 모델 로드 완료")
            except Exception as e:
                print(f"⚠️ Whisper 모델 로드 실패 (자막 기반 학습만 사용): {e}")
                self.whisper_model = None
        else:
            print("ℹ️ 음성 처리 라이브러리 없음 - 자막 기반 학습만 사용")
            self.whisper_model = None
        
        # 한국어 문장 임베딩 모델
        try:
            self.embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
            print("✅ 한국어 임베딩 모델 로드 완료")
        except Exception as e:
            print(f"⚠️ 임베딩 모델 로드 실패 (기본 분석만 사용): {e}")
            self.embedding_model = None
    
    def setup_knowledge_database(self):
        """확장된 지식 베이스 데이터베이스 초기화"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # 영상 메타데이터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT,
                channel_title TEXT,
                duration_seconds INTEGER,
                view_count INTEGER,
                like_count INTEGER,
                
                -- 자막 관련
                has_transcript BOOLEAN DEFAULT FALSE,
                transcript_text TEXT,
                transcript_language TEXT,
                
                -- 음성 관련  
                has_audio_extracted BOOLEAN DEFAULT FALSE,
                audio_transcription TEXT,
                audio_quality_score REAL,
                
                -- 통합 분석
                combined_text TEXT, -- 자막 + STT 통합
                total_word_count INTEGER,
                saju_relevance_score REAL,
                content_quality_score REAL,
                
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size_mb REAL
            )
        ''')
        
        # 지식 덩어리들 (문장/문단 단위)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                segment_text TEXT,
                segment_type TEXT, -- transcript, audio_stt, combined
                time_start REAL, -- 영상 내 시작 시간 (초)
                time_end REAL,   -- 영상 내 끝 시간 (초)
                
                -- 사주 분석
                saju_terms TEXT, -- JSON array
                knowledge_category TEXT, -- 예측, 해석, 이론, 실전 등
                confidence_score REAL,
                
                -- 임베딩
                embedding BLOB,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES video_content (video_id)
            )
        ''')
        
        # 학습된 사주 지식 패턴
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saju_knowledge_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT, -- 해석패턴, 예측패턴, 궁합패턴 등
                condition_elements TEXT, -- JSON: 조건 사주 요소
                result_interpretation TEXT, -- 결과 해석
                confidence_level REAL,
                source_videos TEXT, -- JSON: 출처 영상들
                example_sentences TEXT, -- JSON: 실제 예시 문장들
                frequency_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 사주 용어 사전 (확장)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saju_dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT UNIQUE NOT NULL,
                category TEXT,
                meaning TEXT,
                detailed_explanation TEXT,
                usage_examples TEXT, -- JSON array
                related_terms TEXT, -- JSON array
                frequency INTEGER DEFAULT 0,
                confidence REAL DEFAULT 1.0,
                sources TEXT, -- JSON: 출처 영상들
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 실시간 학습 로그
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                processing_stage TEXT, -- download, transcript, stt, analysis, learning
                status TEXT, -- success, failed, processing
                details TEXT, -- JSON with detailed info
                processing_time_seconds REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("📊 확장된 지식 데이터베이스 초기화 완료")
    
    def download_audio(self, video_id: str) -> Optional[str]:
        """
        YouTube 영상에서 음성만 추출해서 다운로드
        
        Args:
            video_id: YouTube 영상 ID
            
        Returns:
            다운로드된 오디오 파일 경로 또는 None
        """
        try:
            self._log_progress(video_id, 'download', 'processing', {'message': '영상 다운로드 시작'})
            
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(self.ytdl_opts) as ydl:
                # 메타데이터 추출
                info = ydl.extract_info(url, download=False)
                duration = info.get('duration', 0)
                
                # 너무 긴 영상은 건너뛰기 (30분 이상)
                if duration > 1800:
                    self._log_progress(video_id, 'download', 'failed', 
                                     {'message': f'영상이 너무 깁니다: {duration/60:.1f}분'})
                    return None
                
                # 실제 다운로드
                ydl.download([url])
                
                # 다운로드된 파일 찾기
                for file in os.listdir(self.temp_dir):
                    if video_id in file and (file.endswith('.m4a') or file.endswith('.webm') or file.endswith('.mp3')):
                        audio_path = os.path.join(self.temp_dir, file)
                        file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
                        
                        self._log_progress(video_id, 'download', 'success', 
                                         {'duration': duration, 'file_size_mb': file_size})
                        return audio_path
                
                return None
                
        except Exception as e:
            self._log_progress(video_id, 'download', 'failed', {'error': str(e)})
            print(f"❌ 오디오 다운로드 실패 ({video_id}): {str(e)}")
            return None
    
    def extract_transcript(self, video_id: str) -> Optional[Dict]:
        """자막 추출 (기존 방식 개선)"""
        try:
            self._log_progress(video_id, 'transcript', 'processing', {'message': '자막 추출 시작'})
            
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 한국어 자막 우선
            transcript = None
            language_used = None
            
            try:
                transcript = transcript_list.find_transcript(['ko'])
                language_used = 'ko'
            except:
                try:
                    transcript = transcript_list.find_generated_transcript(['ko'])
                    language_used = 'ko-auto'
                except:
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                        language_used = 'en'
                    except:
                        self._log_progress(video_id, 'transcript', 'failed', {'message': '자막을 찾을 수 없습니다'})
                        return None
            
            # 시간 정보와 함께 자막 추출
            transcript_data = transcript.fetch()
            
            # 텍스트만 추출
            formatter = TextFormatter()
            full_text = formatter.format_transcript(transcript_data)
            
            result = {
                'text': full_text,
                'language': language_used,
                'word_count': len(full_text.split()),
                'segments': transcript_data  # 시간 정보 포함
            }
            
            self._log_progress(video_id, 'transcript', 'success', 
                             {'language': language_used, 'word_count': result['word_count']})
            
            return result
            
        except Exception as e:
            self._log_progress(video_id, 'transcript', 'failed', {'error': str(e)})
            print(f"❌ 자막 추출 실패 ({video_id}): {str(e)}")
            return None
    
    def transcribe_audio(self, audio_path: str, video_id: str) -> Optional[Dict]:
        """
        오디오 파일을 STT로 텍스트 변환
        
        Args:
            audio_path: 오디오 파일 경로
            video_id: 영상 ID
            
        Returns:
            변환된 텍스트와 메타데이터
        """
        if not self.whisper_model:
            return None
        
        try:
            self._log_progress(video_id, 'stt', 'processing', {'message': 'STT 변환 시작'})
            
            # Whisper로 음성 인식
            result = self.whisper_model.transcribe(
                audio_path,
                language='ko',  # 한국어 강제 지정
                task='transcribe',
                word_timestamps=True  # 단어별 시간 정보
            )
            
            transcription_data = {
                'text': result['text'],
                'language': result['language'],
                'segments': result.get('segments', []),
                'word_count': len(result['text'].split()),
                'confidence': self._calculate_confidence(result)
            }
            
            self._log_progress(video_id, 'stt', 'success', 
                             {'word_count': transcription_data['word_count'], 
                              'confidence': transcription_data['confidence']})
            
            return transcription_data
            
        except Exception as e:
            self._log_progress(video_id, 'stt', 'failed', {'error': str(e)})
            print(f"❌ STT 변환 실패 ({video_id}): {str(e)}")
            return None
    
    def _calculate_confidence(self, whisper_result: Dict) -> float:
        """Whisper 결과에서 신뢰도 계산"""
        if 'segments' not in whisper_result:
            return 0.5
        
        confidences = []
        for segment in whisper_result['segments']:
            if 'avg_logprob' in segment:
                # log probability를 0-1 신뢰도로 변환
                confidence = max(0, min(1, (segment['avg_logprob'] + 1) / 1))
                confidences.append(confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def combine_and_analyze_content(self, video_id: str, transcript_data: Dict = None, 
                                  stt_data: Dict = None, video_info: Dict = None) -> Dict:
        """
        자막과 STT 결과를 통합하여 종합 분석
        
        Args:
            video_id: 영상 ID
            transcript_data: 자막 데이터
            stt_data: STT 데이터
            video_info: 영상 메타데이터
            
        Returns:
            통합 분석 결과
        """
        try:
            self._log_progress(video_id, 'analysis', 'processing', {'message': '통합 분석 시작'})
            
            # 텍스트 통합
            combined_text = ""
            text_sources = []
            
            if transcript_data:
                combined_text += transcript_data['text'] + "\n"
                text_sources.append("transcript")
            
            if stt_data:
                combined_text += stt_data['text'] + "\n"
                text_sources.append("stt")
            
            if not combined_text.strip():
                return None
            
            # 사주 관련 내용 분석
            analysis = self._analyze_saju_content_advanced(combined_text)
            
            # 지식 세그먼트 생성
            segments = self._create_knowledge_segments(
                combined_text, transcript_data, stt_data, video_id
            )
            
            # 학습 패턴 추출
            patterns = self._extract_learning_patterns(combined_text, analysis)
            
            result = {
                'video_id': video_id,
                'combined_text': combined_text,
                'text_sources': text_sources,
                'total_word_count': len(combined_text.split()),
                'saju_analysis': analysis,
                'knowledge_segments': segments,
                'learned_patterns': patterns,
                'content_quality_score': self._calculate_content_quality(analysis, combined_text),
                'processing_summary': {
                    'has_transcript': transcript_data is not None,
                    'has_stt': stt_data is not None,
                    'transcript_quality': transcript_data.get('language') if transcript_data else None,
                    'stt_confidence': stt_data.get('confidence') if stt_data else None
                }
            }
            
            self._log_progress(video_id, 'analysis', 'success', {
                'word_count': result['total_word_count'],
                'relevance_score': analysis['relevance_score'],
                'segments_count': len(segments),
                'patterns_count': len(patterns)
            })
            
            return result
            
        except Exception as e:
            self._log_progress(video_id, 'analysis', 'failed', {'error': str(e)})
            print(f"❌ 통합 분석 실패 ({video_id}): {str(e)}")
            return None
    
    def _analyze_saju_content_advanced(self, text: str) -> Dict:
        """고급 사주 내용 분석"""
        analysis = {
            'saju_terms_found': {},
            'relevance_score': 0.0,
            'content_categories': {},
            'interpretation_patterns': [],
            'prediction_statements': [],
            'expert_indicators': []
        }
        
        # 1. 사주 용어 추출 및 빈도 분석
        total_terms_found = 0
        for category, terms in self.saju_terms.items():
            found_terms = []
            for term in terms:
                count = text.count(term)
                if count > 0:
                    found_terms.append({'term': term, 'count': count, 'positions': self._find_term_positions(text, term)})
                    total_terms_found += count
            
            if found_terms:
                analysis['saju_terms_found'][category] = found_terms
        
        # 2. 관련성 점수 계산 (개선된 알고리즘)
        text_length = len(text.split())
        if text_length > 0:
            base_score = min(total_terms_found / text_length * 100, 10.0)
            
            # 전문성 보너스
            expert_keywords = ['명리학', '사주학', '동양철학', '전문가', '선생님', '마스터']
            expert_bonus = sum(1 for keyword in expert_keywords if keyword in text) * 0.5
            
            # 구체성 보너스 (구체적인 해석이나 예측이 있는지)
            specific_bonus = 0
            if any(word in text for word in ['예를 들어', '구체적으로', '실제로']):
                specific_bonus += 0.3
            
            analysis['relevance_score'] = min(base_score + expert_bonus + specific_bonus, 10.0)
        
        # 3. 내용 카테고리 분류
        categories = {
            '기초이론': ['기초', '원리', '개념', '이론'],
            '실전해석': ['해석', '분석', '풀이', '보는법'],
            '운세예측': ['운세', '올해', '내년', '앞으로', '미래'],
            '궁합분석': ['궁합', '인연', '결혼', '연애'],
            '직업진로': ['직업', '진로', '사업', '적성'],
            '건강': ['건강', '몸', '질병', '주의'],
            '재물': ['돈', '재물', '재운', '투자', '사업']
        }
        
        for category, keywords in categories.items():
            score = sum(text.lower().count(keyword) for keyword in keywords)
            if score > 0:
                analysis['content_categories'][category] = score
        
        # 4. 해석 패턴 추출
        interpretation_patterns = re.findall(
            r'([가-힣\s]+이면|[가-힣\s]+일때|[가-힣\s]+경우)\s*([가-힣\s,\.]+[다니])', 
            text
        )
        analysis['interpretation_patterns'] = [
            {'condition': cond.strip(), 'result': res.strip()} 
            for cond, res in interpretation_patterns 
            if self._contains_saju_terms(cond) or self._contains_saju_terms(res)
        ]
        
        # 5. 예측 진술 추출
        prediction_patterns = re.findall(
            r'(올해|내년|앞으로|미래에)\s*([가-힣\s,\.]+[다니])', 
            text
        )
        analysis['prediction_statements'] = [
            {'timeframe': time.strip(), 'prediction': pred.strip()}
            for time, pred in prediction_patterns
        ]
        
        return analysis
    
    def _find_term_positions(self, text: str, term: str) -> List[int]:
        """텍스트에서 용어의 위치들을 찾기"""
        positions = []
        start = 0
        while True:
            pos = text.find(term, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + len(term)
        return positions
    
    def _create_knowledge_segments(self, combined_text: str, transcript_data: Dict, 
                                 stt_data: Dict, video_id: str) -> List[Dict]:
        """지식 세그먼트 생성"""
        segments = []
        
        # 문장 단위로 분할
        sentences = self._split_into_sentences(combined_text)
        
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:
                continue
                
            if self._is_saju_knowledge_sentence(sentence):
                segment = {
                    'text': sentence.strip(),
                    'sequence_number': i,
                    'saju_terms': self._extract_terms_from_sentence(sentence),
                    'category': self._classify_knowledge_type(sentence),
                    'confidence': self._calculate_segment_confidence(sentence),
                    'embedding': self._get_sentence_embedding(sentence)
                }
                
                segments.append(segment)
        
        return segments
    
    def _extract_learning_patterns(self, text: str, analysis: Dict) -> List[Dict]:
        """학습 패턴 추출"""
        patterns = []
        
        # 해석 패턴들을 학습용으로 변환
        for pattern in analysis['interpretation_patterns']:
            learning_pattern = {
                'type': '해석패턴',
                'condition': pattern['condition'],
                'result': pattern['result'],
                'confidence': 0.7,
                'source_context': self._extract_context(text, pattern['condition'])
            }
            patterns.append(learning_pattern)
        
        # 예측 패턴들도 추가
        for prediction in analysis['prediction_statements']:
            learning_pattern = {
                'type': '예측패턴',
                'timeframe': prediction['timeframe'],
                'prediction': prediction['prediction'],
                'confidence': 0.6,
                'source_context': self._extract_context(text, prediction['prediction'])
            }
            patterns.append(learning_pattern)
        
        return patterns
    
    def _extract_context(self, text: str, target_phrase: str, context_words: int = 20) -> str:
        """대상 구문 주변의 컨텍스트 추출"""
        words = text.split()
        target_words = target_phrase.split()
        
        for i in range(len(words) - len(target_words) + 1):
            if ' '.join(words[i:i+len(target_words)]) == target_phrase:
                start = max(0, i - context_words)
                end = min(len(words), i + len(target_words) + context_words)
                return ' '.join(words[start:end])
        
        return target_phrase
    
    def _calculate_content_quality(self, analysis: Dict, text: str) -> float:
        """콘텐츠 품질 점수 계산"""
        quality_score = 0.0
        
        # 1. 사주 관련성 (40%)
        quality_score += analysis['relevance_score'] * 0.4
        
        # 2. 내용 다양성 (30%)
        category_diversity = len(analysis['content_categories']) / 7.0  # 최대 7개 카테고리
        quality_score += category_diversity * 3.0
        
        # 3. 구체성 (20%)
        specific_indicators = ['예를 들어', '구체적으로', '실제로', '예시', '사례']
        specificity = sum(1 for indicator in specific_indicators if indicator in text) / len(specific_indicators)
        quality_score += specificity * 2.0
        
        # 4. 구조화 정도 (10%)
        structure_indicators = len(analysis['interpretation_patterns']) + len(analysis['prediction_statements'])
        structure_score = min(structure_indicators / 5.0, 1.0)  # 최대 5개 패턴
        quality_score += structure_score * 1.0
        
        return min(quality_score, 10.0)
    
    def _get_sentence_embedding(self, sentence: str) -> Optional[bytes]:
        """문장 임베딩 생성"""
        if not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode(sentence)
            return embedding.tobytes()
        except:
            return None
    
    def _calculate_segment_confidence(self, sentence: str) -> float:
        """세그먼트 신뢰도 계산"""
        confidence = 0.5
        
        # 사주 용어 밀도
        saju_term_count = sum(1 for terms in self.saju_terms.values() 
                             for term in terms if term in sentence)
        term_density = saju_term_count / len(sentence.split())
        confidence += min(term_density * 2, 0.3)
        
        # 구체성
        if any(word in sentence for word in ['구체적으로', '예를 들어', '실제로']):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def save_complete_analysis(self, analysis_result: Dict):
        """완전한 분석 결과를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        try:
            video_id = analysis_result['video_id']
            
            # 1. 영상 콘텐츠 메인 정보 저장
            cursor.execute('''
                INSERT OR REPLACE INTO video_content 
                (video_id, combined_text, total_word_count, saju_relevance_score, 
                 content_quality_score, has_transcript, has_audio_extracted)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_id,
                analysis_result['combined_text'],
                analysis_result['total_word_count'],
                analysis_result['saju_analysis']['relevance_score'],
                analysis_result['content_quality_score'],
                analysis_result['processing_summary']['has_transcript'],
                analysis_result['processing_summary']['has_stt']
            ))
            
            # 2. 지식 세그먼트들 저장
            for segment in analysis_result['knowledge_segments']:
                cursor.execute('''
                    INSERT INTO knowledge_segments 
                    (video_id, segment_text, saju_terms, knowledge_category, confidence_score, embedding)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    video_id,
                    segment['text'],
                    json.dumps(segment['saju_terms'], ensure_ascii=False),
                    segment['category'],
                    segment['confidence'],
                    segment['embedding']
                ))
            
            # 3. 학습된 패턴들 저장
            for pattern in analysis_result['learned_patterns']:
                cursor.execute('''
                    INSERT INTO saju_knowledge_patterns 
                    (pattern_type, condition_elements, result_interpretation, confidence_level, source_videos)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    pattern['type'],
                    pattern.get('condition', ''),
                    pattern.get('result', pattern.get('prediction', '')),
                    pattern['confidence'],
                    json.dumps([video_id])
                ))
            
            # 4. 사주 용어 사전 업데이트
            for category, terms in analysis_result['saju_analysis']['saju_terms_found'].items():
                for term_data in terms:
                    cursor.execute('''
                        INSERT OR IGNORE INTO saju_dictionary (term, category, frequency)
                        VALUES (?, ?, 0)
                    ''', (term_data['term'], category))
                    
                    cursor.execute('''
                        UPDATE saju_dictionary 
                        SET frequency = frequency + ?, updated_at = CURRENT_TIMESTAMP
                        WHERE term = ?
                    ''', (term_data['count'], term_data['term']))
            
            conn.commit()
            self._log_progress(video_id, 'learning', 'success', {
                'segments_saved': len(analysis_result['knowledge_segments']),
                'patterns_saved': len(analysis_result['learned_patterns']),
                'relevance_score': analysis_result['saju_analysis']['relevance_score']
            })
            
            print(f"✅ 학습 결과 저장 완료: {video_id}")
            
        except Exception as e:
            conn.rollback()
            self._log_progress(video_id, 'learning', 'failed', {'error': str(e)})
            print(f"❌ 학습 결과 저장 실패 ({video_id}): {str(e)}")
        finally:
            conn.close()
    
    def process_complete_video(self, video_id: str, video_info: Dict = None) -> bool:
        """
        영상 전체 처리: 다운로드 → 자막추출 → STT → 통합분석 → 학습
        
        Args:
            video_id: YouTube 영상 ID  
            video_info: 영상 메타데이터
            
        Returns:
            처리 성공 여부
        """
        print(f"\n🎬 영상 전체 처리 시작: {video_id}")
        
        try:
            # 1. 자막 추출
            transcript_data = self.extract_transcript(video_id)
            if transcript_data:
                print(f"✅ 자막 추출: {transcript_data['word_count']}단어 ({transcript_data['language']})")
            
            # 2. 오디오 다운로드
            audio_path = self.download_audio(video_id)
            stt_data = None
            
            if audio_path:
                print(f"✅ 오디오 다운로드: {os.path.getsize(audio_path)/(1024*1024):.1f}MB")
                
                # 3. STT 변환
                stt_data = self.transcribe_audio(audio_path, video_id)
                if stt_data:
                    print(f"✅ STT 변환: {stt_data['word_count']}단어 (신뢰도: {stt_data['confidence']:.2f})")
                
                # 임시 파일 정리
                try:
                    os.remove(audio_path)
                except:
                    pass
            
            # 자막도 STT도 없으면 실패
            if not transcript_data and not stt_data:
                print(f"❌ 자막과 STT 모두 실패: {video_id}")
                return False
            
            # 4. 통합 분석
            analysis_result = self.combine_and_analyze_content(
                video_id, transcript_data, stt_data, video_info
            )
            
            if not analysis_result:
                print(f"❌ 통합 분석 실패: {video_id}")
                return False
            
            print(f"📊 분석 완료:")
            print(f"  - 총 단어 수: {analysis_result['total_word_count']}")
            print(f"  - 사주 관련성: {analysis_result['saju_analysis']['relevance_score']:.2f}/10")
            print(f"  - 콘텐츠 품질: {analysis_result['content_quality_score']:.2f}/10")
            print(f"  - 지식 세그먼트: {len(analysis_result['knowledge_segments'])}개")
            print(f"  - 학습된 패턴: {len(analysis_result['learned_patterns'])}개")
            
            # 관련성이 너무 낮으면 건너뛰기
            if analysis_result['saju_analysis']['relevance_score'] < 0.5:
                print(f"⚠️ 관련성이 너무 낮아 학습하지 않음")
                return False
            
            # 5. 데이터베이스에 학습 결과 저장
            self.save_complete_analysis(analysis_result)
            
            return True
            
        except Exception as e:
            print(f"❌ 영상 처리 중 오류 ({video_id}): {str(e)}")
            return False
    
    def batch_learn_from_videos(self, video_list: List[Dict], max_videos: int = 10) -> Dict:
        """
        여러 영상에서 일괄 학습
        
        Args:
            video_list: 영상 정보 리스트
            max_videos: 최대 처리 영상 수
            
        Returns:
            학습 결과 통계
        """
        results = {
            'total_videos': min(len(video_list), max_videos),
            'success_count': 0,
            'failed_count': 0,
            'total_knowledge_segments': 0,
            'total_patterns_learned': 0,
            'avg_relevance_score': 0.0,
            'avg_quality_score': 0.0,
            'processing_time': 0
        }
        
        start_time = datetime.now()
        processed_videos = video_list[:max_videos]
        
        print(f"🚀 일괄 학습 시작: {len(processed_videos)}개 영상")
        print("=" * 60)
        
        relevance_scores = []
        quality_scores = []
        
        for i, video_info in enumerate(processed_videos, 1):
            print(f"\n[{i}/{len(processed_videos)}] 처리 중...")
            
            video_id = video_info.get('video_id')
            if not video_id:
                results['failed_count'] += 1
                continue
            
            success = self.process_complete_video(video_id, video_info)
            
            if success:
                results['success_count'] += 1
                
                # 통계 수집
                conn = sqlite3.connect(self.knowledge_db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT saju_relevance_score, content_quality_score 
                    FROM video_content WHERE video_id = ?
                ''', (video_id,))
                row = cursor.fetchone()
                if row:
                    relevance_scores.append(row[0])
                    quality_scores.append(row[1])
                
                conn.close()
            else:
                results['failed_count'] += 1
        
        # 최종 통계 계산
        end_time = datetime.now()
        results['processing_time'] = (end_time - start_time).total_seconds()
        
        if relevance_scores:
            results['avg_relevance_score'] = sum(relevance_scores) / len(relevance_scores)
        if quality_scores:
            results['avg_quality_score'] = sum(quality_scores) / len(quality_scores)
        
        # 데이터베이스 전체 통계
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_segments')
        results['total_knowledge_segments'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM saju_knowledge_patterns')
        results['total_patterns_learned'] = cursor.fetchone()[0]
        
        conn.close()
        
        # 결과 출력
        print(f"\n" + "=" * 60)
        print(f"🎉 일괄 학습 완료!")
        print(f"⏱️  처리 시간: {results['processing_time']:.1f}초")
        print(f"✅ 성공: {results['success_count']}개")
        print(f"❌ 실패: {results['failed_count']}개")
        print(f"📊 평균 사주 관련성: {results['avg_relevance_score']:.2f}/10")
        print(f"🎯 평균 콘텐츠 품질: {results['avg_quality_score']:.2f}/10")
        print(f"🧠 총 지식 세그먼트: {results['total_knowledge_segments']}개")
        print(f"🔄 총 학습 패턴: {results['total_patterns_learned']}개")
        
        return results
    
    def get_learned_knowledge_summary(self) -> Dict:
        """학습된 지식 요약 정보 반환"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        summary = {}
        
        # 기본 통계
        cursor.execute('SELECT COUNT(*) FROM video_content WHERE saju_relevance_score > 0')
        summary['total_processed_videos'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM knowledge_segments')
        summary['total_knowledge_segments'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM saju_knowledge_patterns')
        summary['total_patterns'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM saju_dictionary WHERE frequency > 0')
        summary['learned_terms_count'] = cursor.fetchone()[0]
        
        # 품질 통계
        cursor.execute('SELECT AVG(saju_relevance_score), AVG(content_quality_score) FROM video_content')
        row = cursor.fetchone()
        summary['avg_relevance_score'] = row[0] or 0
        summary['avg_quality_score'] = row[1] or 0
        
        # 카테고리별 지식 분포
        cursor.execute('''
            SELECT knowledge_category, COUNT(*) 
            FROM knowledge_segments 
            GROUP BY knowledge_category 
            ORDER BY COUNT(*) DESC
        ''')
        summary['knowledge_by_category'] = dict(cursor.fetchall())
        
        # 자주 나오는 사주 용어 TOP 10
        cursor.execute('''
            SELECT term, frequency 
            FROM saju_dictionary 
            WHERE frequency > 0 
            ORDER BY frequency DESC 
            LIMIT 10
        ''')
        summary['top_saju_terms'] = dict(cursor.fetchall())
        
        conn.close()
        return summary
    
    def _log_progress(self, video_id: str, stage: str, status: str, details: Dict):
        """처리 과정 로그 저장"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_progress 
            (video_id, processing_stage, status, details)
            VALUES (?, ?, ?, ?)
        ''', (video_id, stage, status, json.dumps(details, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
    
    def cleanup_temp_files(self):
        """임시 파일들 정리"""
        try:
            shutil.rmtree(self.temp_dir)
            print("🧹 임시 파일 정리 완료")
        except:
            pass
    
    def __del__(self):
        """소멸자에서 임시 파일 정리"""
        self.cleanup_temp_files()

# 기존 함수들 (유지)
    def _split_into_sentences(self, text: str) -> List[str]:
        """텍스트를 문장으로 분할"""
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
    
    def _contains_saju_terms(self, text: str) -> bool:
        """텍스트에 사주 용어가 포함되어 있는지 확인"""
        for terms in self.saju_terms.values():
            if any(term in text for term in terms):
                return True
        return False

def main():
    """테스트 실행"""
    print("🎬 YouTube 영상 완전 분석 및 학습 시스템 시작")
    
    # 분석기 초기화
    analyzer = YouTubeContentAnalyzer()
    
    # 사주 영상 검색
    crawler = YouTubeSajuCrawler()
    print("\n🔍 사주 관련 영상 검색 중...")
    videos = crawler.crawl_saju_videos(max_per_keyword=2)  # 테스트용
    
    if not videos:
        print("❌ 검색된 영상이 없습니다.")
        return
    
    print(f"✅ {len(videos)}개 영상 발견")
    
    # 영상들 완전 분석 및 학습
    results = analyzer.batch_learn_from_videos(videos, max_videos=3)
    
    # 학습된 지식 요약
    summary = analyzer.get_learned_knowledge_summary()
    
    print(f"\n📚 학습된 지식 요약:")
    print(f"  - 처리된 영상: {summary['total_processed_videos']}개")
    print(f"  - 지식 세그먼트: {summary['total_knowledge_segments']}개")
    print(f"  - 학습된 패턴: {summary['total_patterns']}개")
    print(f"  - 사주 용어: {summary['learned_terms_count']}개")
    print(f"  - 평균 품질: {summary['avg_quality_score']:.2f}/10")
    
    # 상위 사주 용어들 출력
    if summary['top_saju_terms']:
        print(f"\n🔥 자주 나오는 사주 용어:")
        for term, freq in list(summary['top_saju_terms'].items())[:5]:
            print(f"  - {term}: {freq}회")
    
    # 카테고리별 지식 분포
    if summary['knowledge_by_category']:
        print(f"\n📂 지식 카테고리 분포:")
        for category, count in list(summary['knowledge_by_category'].items())[:5]:
            print(f"  - {category}: {count}개")
    
    # 정리
    analyzer.cleanup_temp_files()
    print(f"\n🎉 학습 완료!")

if __name__ == "__main__":
    main()