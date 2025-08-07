#!/usr/bin/env python3
"""
사주 관련 유튜브 영상 크롤링 모듈
yt-dlp와 Google YouTube Data API v3를 사용한 안전한 크롤링
"""

import yt_dlp
import requests
from typing import List, Dict, Optional
import re
from datetime import datetime, timedelta
import time
import json

class YouTubeSajuCrawler:
    """사주 관련 유튜브 영상 크롤러"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        초기화
        Args:
            api_key: YouTube Data API v3 키 (선택사항)
        """
        self.api_key = api_key
        self.base_api_url = "https://www.googleapis.com/youtube/v3"
        
        # 사주 관련 검색 키워드
        self.saju_keywords = [
            "사주풀이", "사주해석", "사주분석", "운세", "팔자",
            "사주명리", "오행", "천간지지", "사주상담", "명리학",
            "사주보는법", "사주 해석", "오늘의 운세", "신년운세",
            "토정비결", "동양철학", "사주 공부", "명리 강의"
        ]
        
        # yt-dlp 설정
        self.ytdl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
            'ignoreerrors': True,
        }
    
    def search_videos_with_api(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        YouTube Data API를 사용한 영상 검색
        """
        if not self.api_key:
            print("YouTube API 키가 없어 API 검색을 건너뜁니다.")
            return []
        
        try:
            url = f"{self.base_api_url}/search"
            params = {
                'part': 'snippet',
                'q': keyword,
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',
                'regionCode': 'KR',
                'relevanceLanguage': 'ko',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                video_info = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:500],  # 처음 500자만
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['medium']['url'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    'keyword': keyword,
                    'crawled_at': datetime.now().isoformat()
                }
                videos.append(video_info)
            
            print(f"API로 '{keyword}' 검색: {len(videos)}개 영상 발견")
            return videos
            
        except Exception as e:
            print(f"API 검색 오류 ({keyword}): {str(e)}")
            return []
    
    def search_videos_with_ytdl(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """
        yt-dlp를 사용한 영상 검색 (백업 방법)
        """
        try:
            # Skip if max_results is 0 or negative
            if max_results <= 0:
                return []
                
            search_query = f"ytsearch{max_results}:{keyword}"
            
            with yt_dlp.YoutubeDL(self.ytdl_opts) as ydl:
                search_results = ydl.extract_info(search_query, download=False)
                
                # Check if search_results is None or doesn't have entries
                if not search_results or not search_results.get('entries'):
                    return []
                
                videos = []
                for entry in search_results.get('entries', []):
                    if entry and isinstance(entry, dict):
                        video_info = {
                            'video_id': entry.get('id', ''),
                            'title': entry.get('title', ''),
                            'description': entry.get('description', '')[:500] if entry.get('description') else '',
                            'channel_title': entry.get('uploader', ''),
                            'published_at': '',  # yt-dlp에서는 정확한 날짜 추출이 어려움
                            'thumbnail_url': entry.get('thumbnail', ''),
                            'url': entry.get('webpage_url', ''),
                            'duration': entry.get('duration', 0),
                            'view_count': entry.get('view_count', 0),
                            'keyword': keyword,
                            'crawled_at': datetime.now().isoformat()
                        }
                        videos.append(video_info)
                
                print(f"yt-dlp로 '{keyword}' 검색: {len(videos)}개 영상 발견")
                return videos
                
        except Exception as e:
            print(f"yt-dlp 검색 오류 ({keyword}): {str(e)}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        특정 영상의 상세 정보 가져오기
        """
        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_api_url}/videos"
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('items'):
                return None
            
            item = data['items'][0]
            
            return {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:1000],
                'channel_title': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail_url': item['snippet']['thumbnails']['medium']['url'],
                'tags': item['snippet'].get('tags', []),
                'view_count': int(item['statistics'].get('viewCount', 0)),
                'like_count': int(item['statistics'].get('likeCount', 0)),
                'comment_count': int(item['statistics'].get('commentCount', 0)),
                'duration': item['contentDetails']['duration'],
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
            
        except Exception as e:
            print(f"영상 상세 정보 오류 ({video_id}): {str(e)}")
            return None
    
    def filter_relevant_videos(self, videos: List[Dict]) -> List[Dict]:
        """
        사주 관련성이 높은 영상만 필터링
        """
        relevant_keywords = [
            '사주', '팔자', '운세', '명리', '오행', '천간', '지지',
            '띠별', '신년', '토정비결', '점', '관상', '수상'
        ]
        
        filtered_videos = []
        
        for video in videos:
            title = video.get('title', '').lower()
            description = video.get('description', '').lower()
            
            # 제목이나 설명에 관련 키워드가 포함된 경우
            relevance_score = 0
            for keyword in relevant_keywords:
                if keyword in title:
                    relevance_score += 3
                if keyword in description:
                    relevance_score += 1
            
            # 최소 점수 이상인 경우만 포함
            if relevance_score >= 2:
                video['relevance_score'] = relevance_score
                filtered_videos.append(video)
        
        # 관련성 점수로 정렬
        filtered_videos.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return filtered_videos
    
    def crawl_saju_videos(self, max_per_keyword: int = 10) -> List[Dict]:
        """
        사주 관련 영상 대량 크롤링
        """
        print("사주 관련 유튜브 영상 크롤링 시작...")
        all_videos = []
        
        for i, keyword in enumerate(self.saju_keywords[:5]):  # 처음 5개 키워드만 사용
            print(f"\n[{i+1}/{len(self.saju_keywords[:5])}] '{keyword}' 검색 중...")
            
            # API 우선 시도
            videos = self.search_videos_with_api(keyword, max_per_keyword)
            
            # API 실패시 yt-dlp 사용
            if not videos:
                videos = self.search_videos_with_ytdl(keyword, max_per_keyword // 2)
            
            all_videos.extend(videos)
            
            # API 요청 제한 준수
            time.sleep(1)
        
        print(f"\n총 {len(all_videos)}개 영상 발견")
        
        # 중복 제거 (video_id 기준)
        unique_videos = {}
        for video in all_videos:
            video_id = video.get('video_id')
            if video_id and video_id not in unique_videos:
                unique_videos[video_id] = video
        
        unique_list = list(unique_videos.values())
        print(f"중복 제거 후: {len(unique_list)}개 영상")
        
        # 관련성 필터링
        filtered_videos = self.filter_relevant_videos(unique_list)
        print(f"관련성 필터링 후: {len(filtered_videos)}개 영상")
        
        return filtered_videos
    
    def extract_saju_content(self, video_info: Dict) -> Dict:
        """
        영상에서 사주 관련 내용 추출 및 분석
        """
        title = video_info.get('title', '')
        description = video_info.get('description', '')
        
        # 사주 용어 추출
        saju_terms = []
        terms_to_find = [
            '갑', '을', '병', '정', '무', '기', '경', '신', '임', '계',  # 천간
            '자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해',  # 지지
            '목', '화', '토', '금', '수',  # 오행
            '양', '음', '태양', '태음'  # 음양
        ]
        
        content = f"{title} {description}".lower()
        for term in terms_to_find:
            if term in content:
                saju_terms.append(term)
        
        # 운세 관련 키워드 추출
        fortune_keywords = []
        fortune_terms = ['좋은', '나쁜', '길한', '흉한', '대운', '소운', '재물', '건강', '연애', '결혼']
        for term in fortune_terms:
            if term in content:
                fortune_keywords.append(term)
        
        return {
            'video_id': video_info.get('video_id'),
            'saju_terms': list(set(saju_terms)),
            'fortune_keywords': list(set(fortune_keywords)),
            'content_type': self._classify_content_type(title, description),
            'target_audience': self._identify_target_audience(title, description)
        }
    
    def _classify_content_type(self, title: str, description: str) -> str:
        """영상 내용 분류"""
        content = f"{title} {description}".lower()
        
        if any(word in content for word in ['강의', '배우', '공부', '기초']):
            return '교육'
        elif any(word in content for word in ['풀이', '해석', '상담']):
            return '해석'
        elif any(word in content for word in ['2024', '2025', '신년', '올해']):
            return '연간운세'
        elif any(word in content for word in ['오늘', '이번주', '이번달']):
            return '단기운세'
        else:
            return '일반'
    
    def _identify_target_audience(self, title: str, description: str) -> str:
        """대상 청중 식별"""
        content = f"{title} {description}".lower()
        
        if any(word in content for word in ['쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양', '원숭이', '닭', '개', '돼지']):
            return '띠별'
        elif any(word in content for word in ['남성', '남자']):
            return '남성'
        elif any(word in content for word in ['여성', '여자']):
            return '여성'
        elif any(word in content for word in ['초보', '입문']):
            return '초보자'
        else:
            return '전체'

def main():
    """테스트 실행"""
    crawler = YouTubeSajuCrawler()
    
    # 사주 관련 영상 크롤링
    videos = crawler.crawl_saju_videos(max_per_keyword=5)
    
    # 결과 출력
    print(f"\n크롤링 완료: {len(videos)}개 영상")
    
    for i, video in enumerate(videos[:3]):  # 처음 3개만 출력
        print(f"\n[{i+1}] {video['title']}")
        print(f"채널: {video['channel_title']}")
        print(f"URL: {video['url']}")
        print(f"관련성 점수: {video.get('relevance_score', 0)}")
    
    # JSON으로 저장
    with open('saju_videos.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    
    print(f"\n결과가 saju_videos.json에 저장되었습니다.")

if __name__ == "__main__":
    main()