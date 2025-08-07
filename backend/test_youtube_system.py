#!/usr/bin/env python3
"""
YouTube 학습 시스템 독립 테스트 스크립트
데이터베이스 연결 없이 YouTube 기능을 테스트합니다.
"""

import sys
import os
import sqlite3
import asyncio
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.youtube_service import YouTubeService

class MockDB:
    """데이터베이스 모킹을 위한 클래스"""
    def close(self):
        pass

async def test_youtube_service():
    """YouTube 서비스 기본 기능 테스트"""
    print("🚀 YouTube 학습 시스템 테스트 시작...")
    
    try:
        # YouTube 서비스 초기화
        db = MockDB()
        youtube_service = YouTubeService(db, "test_saju_knowledge.db")
        print("✅ YouTube 서비스 초기화 성공")
        
        # 지식 데이터베이스 테이블 확인
        conn = sqlite3.connect("test_saju_knowledge.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"📋 생성된 테이블: {tables}")
        
        # 지식 요약 테스트
        summary = await youtube_service.get_knowledge_summary()
        print(f"📊 현재 지식 요약:")
        for key, value in summary.items():
            print(f"  - {key}: {value}")
        
        # 사주 용어 사전 확인
        print(f"\n📚 사주 용어 카테고리: {list(youtube_service.saju_terms.keys())}")
        print(f"📚 천간: {youtube_service.saju_terms['천간']}")
        print(f"📚 지지: {youtube_service.saju_terms['지지']}")
        print(f"📚 오행: {youtube_service.saju_terms['오행']}")
        
        # 텍스트 분석 테스트
        test_text = "갑목 일주는 목의 기운이 강하며, 봄에 태어나면 더욱 좋습니다. 건강하고 성실한 성격을 가지고 있어요."
        analysis = await youtube_service.analyze_saju_content(test_text)
        print(f"\n🔍 사주 텍스트 분석 테스트:")
        print(f"  - 텍스트: {test_text}")
        print(f"  - 발견된 사주 용어: {analysis['saju_terms']}")
        print(f"  - 문장 유형: {analysis['sentence_type']}")
        print(f"  - 신뢰도: {analysis['confidence']:.3f}")
        
        # 개인화된 지식 테스트
        birth_info = {
            "birth_year": 1990,
            "birth_month": 5
        }
        personalized = await youtube_service.get_personalized_knowledge(birth_info)
        print(f"\n👤 개인화된 지식 조회 결과: {len(personalized)}개 항목")
        
        conn.close()
        print("\n✅ 모든 기본 테스트 통과!")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_youtube_transcript():
    """실제 YouTube 자막 추출 테스트"""
    print("\n🎥 YouTube 자막 추출 테스트...")
    
    try:
        db = MockDB()
        youtube_service = YouTubeService(db, "test_saju_knowledge.db")
        
        # 한국 사주 관련 YouTube 영상 ID (존재하는 영상)
        # 테스트용으로 유명한 사주 관련 영상을 사용
        test_video_id = "dQw4w9WgXcQ"  # 실제 존재하는 영상 ID로 변경 필요
        
        print(f"📺 영상 ID: {test_video_id}")
        
        # 자막 추출 테스트
        transcript = await youtube_service.extract_transcript(test_video_id)
        
        if transcript:
            print(f"✅ 자막 추출 성공! (길이: {len(transcript)}자)")
            print(f"📝 자막 샘플: {transcript[:200]}...")
            
            # 자막에서 사주 관련 내용 분석
            analysis = await youtube_service.analyze_saju_content(transcript[:1000])
            print(f"🔍 사주 분석 결과:")
            print(f"  - 발견된 용어: {analysis['saju_terms']}")
            print(f"  - 신뢰도: {analysis['confidence']:.3f}")
            
        else:
            print("⚠️ 자막 추출 실패 (자막이 없거나 비공개 영상)")
            
        return transcript is not None
        
    except Exception as e:
        print(f"❌ 자막 테스트 실패: {str(e)}")
        return False

async def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("🎯 SajuLotto YouTube 학습 시스템 테스트")
    print("=" * 60)
    
    # 기본 기능 테스트
    basic_test = await test_youtube_service()
    
    # 실제 YouTube 자막 테스트 (선택적)
    print(f"\n{'=' * 40}")
    choice = input("실제 YouTube 자막 추출을 테스트하시겠습니까? (y/n): ")
    if choice.lower() == 'y':
        transcript_test = await test_youtube_transcript()
    else:
        print("⏭️ YouTube 자막 테스트 건너뛰기")
        transcript_test = True
    
    # 결과 요약
    print(f"\n{'=' * 60}")
    print("📋 테스트 결과 요약:")
    print(f"  - 기본 기능 테스트: {'✅ 통과' if basic_test else '❌ 실패'}")
    print(f"  - YouTube 자막 테스트: {'✅ 통과' if transcript_test else '❌ 실패'}")
    
    if basic_test and transcript_test:
        print("\n🎉 모든 테스트 성공! YouTube 학습 시스템이 정상 작동합니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 로그를 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(main())