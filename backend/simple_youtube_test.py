#!/usr/bin/env python3
"""
간단한 YouTube 자막 추출 테스트
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.youtube_service import YouTubeService

class MockDB:
    def close(self):
        pass

async def test_transcript():
    print("🎥 YouTube 자막 추출 간단 테스트")
    
    # 알려진 한국어 자막이 있는 공개 영상 ID들
    test_videos = [
        "jNQXAC9IVRw",  # 공개 영상
        "dQw4w9WgXcQ",  # Rick Roll (영어 자막)
    ]
    
    youtube_service = YouTubeService(MockDB(), "simple_test.db")
    
    for video_id in test_videos:
        print(f"\n📺 테스트 영상: {video_id}")
        
        try:
            transcript = await youtube_service.extract_transcript(video_id)
            
            if transcript:
                print(f"✅ 자막 추출 성공!")
                print(f"📝 자막 길이: {len(transcript)} 문자")
                print(f"📝 자막 미리보기: {transcript[:200]}...")
                
                # 간단한 사주 용어 분석
                if any(term in transcript for term in ['갑', '을', '목', '화', '토', '금', '수']):
                    print("🎯 사주 관련 용어 발견!")
                else:
                    print("ℹ️ 사주 관련 용어 없음 (테스트 영상이므로 정상)")
                    
                # 가상의 사주 텍스트로 분석 테스트
                test_text = "갑목 일주는 목의 기운이 강하며, 봄에 태어나면 건강하고 성실한 성격을 보입니다."
                analysis = await youtube_service.analyze_saju_content(test_text)
                print(f"🔍 사주 분석 테스트 (가상 텍스트):")
                print(f"  - 발견 용어: {analysis['saju_terms']}")
                print(f"  - 문장 유형: {analysis['sentence_type']}")
                print(f"  - 신뢰도: {analysis['confidence']:.3f}")
                
                break  # 성공하면 종료
                
            else:
                print("❌ 자막 추출 실패")
                
        except Exception as e:
            print(f"❌ 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_transcript())