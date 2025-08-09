#!/usr/bin/env python3
"""
고급 YouTube 사주 콘텐츠 크롤러
대중적으로 검증된 전문가 콘텐츠를 자동으로 수집하고 학습
"""

import asyncio
import os
import re
import json
import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

class AdvancedSajuCrawler:
    """사주 전문 YouTube 콘텐츠 크롤러"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.youtube = None
        if self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        
        # 검색 키워드 정의
        self.search_keywords = [
            "사주풀이",
            "명리학 강의", 
            "사주 상담",
            "일간별 운세",
            "신년운세",
            "갑목 일주",
            "을목 일주",
            "병화 일주",
            "정화 일주",
            "무토 일주",
            "기토 일주",
            "경금 일주",
            "신금 일주",
            "임수 일주",
            "계수 일주",
            "사주팔자 해석",
            "십신 해석",
            "대운 풀이",
            "궁합 사주"
        ]
        
        # 필터링 기준
        self.min_view_count = 100000  # 10만 회 이상
        self.min_subscriber_count = 10000  # 1만 명 이상
        
        # 제거할 패턴들
        self.removal_patterns = [
            r"안녕하세요.*?입니다",
            r"구독.*?좋아요.*?부탁",
            r"알림.*?설정",
            r"광고.*?문의",
            r"후원.*?링크",
            r"음+\.\.\.",
            r"어+\.\.\.",
            r"그+\.\.\.",
            r"\n{3,}",  # 과도한 줄바꿈
        ]
        
        # 데이터베이스 초기화
        self._init_database()
    
    def _init_database(self):
        """크롤링 데이터베이스 초기화"""
        conn = sqlite3.connect('saju_youtube_data.db')
        cursor = conn.cursor()
        
        # 크롤링된 영상 정보
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crawled_videos (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                channel_name TEXT,
                channel_id TEXT,
                view_count INTEGER,
                subscriber_count INTEGER,
                duration INTEGER,
                upload_date TEXT,
                description TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 추출된 텍스트 데이터
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                source_type TEXT,  -- 'subtitle' or 'stt'
                raw_text TEXT,
                cleaned_text TEXT,
                extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES crawled_videos(video_id)
            )
        """)
        
        # 구조화된 학습 데이터
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS structured_learning_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                question TEXT,
                answer TEXT,
                saju_info TEXT,  -- JSON
                interpretation TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES crawled_videos(video_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def search_videos(self, keyword: str, max_results: int = 50) -> List[Dict]:
        """YouTube API를 사용한 영상 검색"""
        if not self.youtube:
            print("❌ YouTube API 키가 설정되지 않았습니다.")
            return []
        
        try:
            search_response = self.youtube.search().list(
                q=keyword,
                part='id,snippet',
                type='video',
                maxResults=max_results,
                order='viewCount',
                regionCode='KR',
                relevanceLanguage='ko'
            ).execute()
            
            videos = []
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                
                # 영상 상세 정보 가져오기
                video_details = self.youtube.videos().list(
                    part='statistics,contentDetails',
                    id=video_id
                ).execute()
                
                if video_details['items']:
                    stats = video_details['items'][0]['statistics']
                    view_count = int(stats.get('viewCount', 0))
                    
                    # 조회수 필터링
                    if view_count >= self.min_view_count:
                        # 채널 정보 가져오기
                        channel_id = item['snippet']['channelId']
                        channel_info = self.youtube.channels().list(
                            part='statistics',
                            id=channel_id
                        ).execute()
                        
                        if channel_info['items']:
                            subscriber_count = int(
                                channel_info['items'][0]['statistics'].get('subscriberCount', 0)
                            )
                            
                            # 구독자 수 필터링
                            if subscriber_count >= self.min_subscriber_count:
                                videos.append({
                                    'video_id': video_id,
                                    'title': item['snippet']['title'],
                                    'channel_name': item['snippet']['channelTitle'],
                                    'channel_id': channel_id,
                                    'view_count': view_count,
                                    'subscriber_count': subscriber_count,
                                    'upload_date': item['snippet']['publishedAt'],
                                    'description': item['snippet']['description']
                                })
            
            return videos
            
        except Exception as e:
            print(f"❌ 검색 중 오류: {e}")
            return []
    
    async def extract_subtitle(self, video_id: str) -> Optional[str]:
        """영상 자막 추출"""
        try:
            # 한국어 자막 우선 시도
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 수동 한국어 자막 우선
            try:
                transcript = transcript_list.find_manually_created_transcript(['ko'])
            except:
                # 자동 생성 한국어 자막
                try:
                    transcript = transcript_list.find_generated_transcript(['ko'])
                except:
                    return None
            
            # 자막 텍스트 추출
            subtitle_data = transcript.fetch()
            full_text = ' '.join([item['text'] for item in subtitle_data])
            
            return full_text
            
        except Exception as e:
            print(f"⚠️ 자막 추출 실패 ({video_id}): {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """텍스트 정제"""
        cleaned = text
        
        # 불필요한 패턴 제거
        for pattern in self.removal_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # 연속된 공백 제거
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # 앞뒤 공백 제거
        cleaned = cleaned.strip()
        
        return cleaned
    
    def extract_structured_data(self, text: str) -> List[Dict]:
        """텍스트를 구조화된 학습 데이터로 변환"""
        structured_data = []
        
        # 사주 관련 패턴 찾기
        patterns = {
            'question_answer': r'(.*?[는은이가]\s+어떤.*?[\?？])\s*([^？\?]+)',
            'saju_interpretation': r'([갑을병정무기경신임계][목화토금수]\s+일주[는은이가])\s*([^。.]+[。.])',
            'element_description': r'([목화토금수]\s+기운[이가])\s*([^。.]+[。.])',
            'personality_trait': r'(성격[은이]|성향[은이])\s*([^。.]+[。.])',
            'fortune_prediction': r'(운세[는은이가]|대운[은이])\s*([^。.]+[。.])'
        }
        
        for pattern_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.MULTILINE)
            
            for match in matches:
                if len(match) == 2:
                    structured_data.append({
                        'type': pattern_type,
                        'question': match[0].strip(),
                        'answer': match[1].strip(),
                        'confidence_score': self._calculate_confidence(match[1])
                    })
        
        return structured_data
    
    def _calculate_confidence(self, text: str) -> float:
        """텍스트 신뢰도 계산"""
        confidence = 0.5  # 기본값
        
        # 전문 용어 포함 여부
        saju_terms = ['천간', '지지', '십신', '오행', '일주', '대운', '세운']
        for term in saju_terms:
            if term in text:
                confidence += 0.05
        
        # 텍스트 길이
        if len(text) > 100:
            confidence += 0.1
        if len(text) > 300:
            confidence += 0.1
        
        # 구체적인 설명 포함
        if any(word in text for word in ['따라서', '그러므로', '왜냐하면', '예를 들어']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def save_to_database(self, video_data: Dict, subtitle_text: str, structured_data: List[Dict]):
        """데이터베이스에 저장"""
        conn = sqlite3.connect('saju_youtube_data.db')
        cursor = conn.cursor()
        
        try:
            # 영상 정보 저장
            cursor.execute("""
                INSERT OR REPLACE INTO crawled_videos 
                (video_id, title, channel_name, channel_id, view_count, 
                 subscriber_count, upload_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_data['video_id'],
                video_data['title'],
                video_data['channel_name'],
                video_data['channel_id'],
                video_data['view_count'],
                video_data['subscriber_count'],
                video_data['upload_date'],
                video_data['description']
            ))
            
            # 추출된 텍스트 저장
            if subtitle_text:
                cleaned_text = self.clean_text(subtitle_text)
                cursor.execute("""
                    INSERT INTO extracted_texts 
                    (video_id, source_type, raw_text, cleaned_text)
                    VALUES (?, ?, ?, ?)
                """, (
                    video_data['video_id'],
                    'subtitle',
                    subtitle_text,
                    cleaned_text
                ))
            
            # 구조화된 학습 데이터 저장
            for data in structured_data:
                cursor.execute("""
                    INSERT INTO structured_learning_data
                    (video_id, question, answer, confidence_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    video_data['video_id'],
                    data.get('question', ''),
                    data.get('answer', ''),
                    data.get('confidence_score', 0.5)
                ))
            
            conn.commit()
            print(f"✅ 저장 완료: {video_data['title']}")
            
        except Exception as e:
            print(f"❌ 저장 실패: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    async def crawl_all_keywords(self):
        """모든 키워드로 크롤링 실행"""
        total_videos = 0
        total_structured_data = 0
        
        for keyword in self.search_keywords:
            print(f"\n🔍 검색 중: {keyword}")
            videos = await self.search_videos(keyword, max_results=20)
            
            for video in videos:
                print(f"  📺 처리 중: {video['title'][:50]}...")
                
                # 자막 추출
                subtitle = await self.extract_subtitle(video['video_id'])
                
                if subtitle:
                    # 구조화된 데이터 추출
                    structured_data = self.extract_structured_data(subtitle)
                    
                    # 데이터베이스 저장
                    self.save_to_database(video, subtitle, structured_data)
                    
                    total_videos += 1
                    total_structured_data += len(structured_data)
                
                # API 제한 방지를 위한 지연
                await asyncio.sleep(1)
        
        print(f"""
        ========================================
        크롤링 완료!
        ----------------------------------------
        총 처리된 영상: {total_videos}개
        추출된 학습 데이터: {total_structured_data}개
        ========================================
        """)
    
    def get_statistics(self):
        """크롤링 통계 확인"""
        conn = sqlite3.connect('saju_youtube_data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM crawled_videos")
        video_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM structured_learning_data")
        data_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence_score) FROM structured_learning_data")
        avg_confidence = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT channel_name, COUNT(*) as cnt 
            FROM crawled_videos 
            GROUP BY channel_name 
            ORDER BY cnt DESC 
            LIMIT 5
        """)
        top_channels = cursor.fetchall()
        
        conn.close()
        
        print(f"""
        📊 크롤링 데이터 통계
        ========================================
        총 영상 수: {video_count}개
        학습 데이터: {data_count}개
        평균 신뢰도: {avg_confidence:.2f}
        
        상위 채널:
        """)
        for channel, count in top_channels:
            print(f"  - {channel}: {count}개")

async def main():
    # API 키 설정 (환경변수 또는 직접 입력)
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("⚠️ YOUTUBE_API_KEY 환경변수를 설정하세요")
        print("export YOUTUBE_API_KEY='your-api-key'")
        return
    
    crawler = AdvancedSajuCrawler(api_key)
    
    # 전체 크롤링 실행
    await crawler.crawl_all_keywords()
    
    # 통계 확인
    crawler.get_statistics()

if __name__ == "__main__":
    asyncio.run(main())