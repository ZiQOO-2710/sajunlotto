#!/usr/bin/env python3
"""
실제 YouTube 영상으로 학습 테스트
사주 관련 YouTube 영상에서 자막을 추출하고 학습하는 테스트
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.youtube_service import YouTubeService

class MockDB:
    """데이터베이스 모킹을 위한 클래스"""
    def close(self):
        pass

async def test_real_video_learning():
    """실제 YouTube 영상에서 학습 테스트"""
    print("🎥 실제 YouTube 영상 학습 테스트")
    print("=" * 50)
    
    try:
        # YouTube 서비스 초기화
        db = MockDB()
        youtube_service = YouTubeService(db, "real_test_knowledge.db")
        
        # 테스트할 영상 ID들 (짧은 사주 관련 영상들)
        # 실제 존재하는 한국어 자막이 있는 사주 관련 영상들로 변경 필요
        test_videos = [
            # "wvEQMmrcbvs",  # 사주 기초 설명 영상 (예시)
            # "자막이 있는 사주 관련 영상 ID를 넣어주세요"
        ]
        
        # 공개적으로 사용 가능한 테스트 영상 ID
        # (실제 사주 영상이 아니더라도 한국어 자막 테스트용)
        test_videos = [
            "jNQXAC9IVRw"  # 한국어 자막이 있는 공개 영상
        ]
        
        print(f"📺 테스트할 영상 수: {len(test_videos)}")
        
        for i, video_id in enumerate(test_videos, 1):
            print(f"\n🔍 [{i}/{len(test_videos)}] 영상 처리 중: {video_id}")
            
            try:
                # 영상에서 학습
                result = await youtube_service.learn_from_video(video_id)
                
                if result.get("success"):
                    print(f"✅ 학습 성공!")
                    print(f"  - 학습된 문장 수: {result['learned_sentences']}")
                    print(f"  - 전체 문장 수: {result['total_sentences']}")
                    print(f"  - 영상 제목: {result['video_info'].get('title', '제목 없음')[:50]}...")
                    
                    # 학습된 내용 확인
                    if result['learned_sentences'] > 0:
                        knowledge_results = await youtube_service.search_knowledge("", 3)
                        print(f"  - 최근 학습된 지식 샘플:")
                        for j, knowledge in enumerate(knowledge_results[:2], 1):
                            print(f"    [{j}] {knowledge['content'][:80]}...")
                            print(f"        용어: {knowledge['saju_terms']}")
                            print(f"        신뢰도: {knowledge['confidence']:.3f}")
                
                else:
                    print(f"❌ 학습 실패: {result.get('error', '알 수 없는 오류')}")
                    
            except Exception as e:
                print(f"❌ 영상 처리 오류: {str(e)}")
                continue
        
        # 최종 지식 요약
        print(f"\n📊 최종 학습 결과:")
        summary = await youtube_service.get_knowledge_summary()
        for key, value in summary.items():
            print(f"  - {key}: {value}")
            
        # 개인화된 지식 테스트
        birth_info = {"birth_year": 1990, "birth_month": 5}
        personalized = await youtube_service.get_personalized_knowledge(birth_info)
        print(f"  - 개인화된 지식 항목: {len(personalized)}개")
        
        return summary['total_knowledge_entries'] > 0
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_knowledge_search():
    """학습된 지식 검색 테스트"""
    print("\n🔍 지식 검색 기능 테스트")
    print("=" * 30)
    
    try:
        db = MockDB()
        youtube_service = YouTubeService(db, "real_test_knowledge.db")
        
        # 다양한 검색어로 테스트
        search_queries = [
            "갑", "목", "성격", "운세", "건강"
        ]
        
        for query in search_queries:
            results = await youtube_service.search_knowledge(query, 3)
            print(f"'{query}' 검색 결과: {len(results)}개")
            
            for result in results[:1]:  # 첫 번째 결과만 출력
                print(f"  - {result['content'][:60]}...")
                print(f"    신뢰도: {result['confidence']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 검색 테스트 실패: {str(e)}")
        return False

async def test_prediction_enhancement():
    """예측 강화 기능 테스트"""
    print("\n🎯 예측 강화 기능 테스트")
    print("=" * 30)
    
    try:
        db = MockDB()
        youtube_service = YouTubeService(db, "real_test_knowledge.db")
        
        # 가상의 사용자 사주 데이터
        user_saju_data = {
            "birth_year": 1990,
            "birth_month": 5,
            "birth_day": 15
        }
        
        # 기본 예측 번호 (예시)
        base_prediction = [7, 14, 23, 31, 38, 42]
        
        # 예측 강화 테스트
        enhancement = await youtube_service.enhance_prediction_with_knowledge(
            user_saju_data, base_prediction
        )
        
        print("예측 강화 결과:")
        print(f"  - 기본 예측: {base_prediction}")
        print(f"  - 신뢰도 부스트: +{enhancement['confidence_boost']:.1%}")
        print(f"  - 적용된 지식 수: {len(enhancement['knowledge_applied'])}")
        print(f"  - 지식 소스 수: {enhancement['knowledge_sources']}")
        
        if enhancement['recommendations']:
            print("  - 추천사항:")
            for i, rec in enumerate(enhancement['recommendations'][:2], 1):
                print(f"    [{i}] {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ 예측 강화 테스트 실패: {str(e)}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🎯 SajuLotto YouTube 실제 학습 테스트")
    print("=" * 60)
    
    # 실제 영상 학습 테스트
    learning_test = await test_real_video_learning()
    
    # 지식 검색 테스트
    search_test = await test_knowledge_search()
    
    # 예측 강화 테스트
    enhancement_test = await test_prediction_enhancement()
    
    # 결과 요약
    print(f"\n{'=' * 60}")
    print("📋 종합 테스트 결과:")
    print(f"  - YouTube 영상 학습: {'✅ 성공' if learning_test else '❌ 실패'}")
    print(f"  - 지식 검색 기능: {'✅ 성공' if search_test else '❌ 실패'}")
    print(f"  - 예측 강화 기능: {'✅ 성공' if enhancement_test else '❌ 실패'}")
    
    if learning_test and search_test and enhancement_test:
        print("\n🎉 모든 실제 테스트 성공!")
        print("💡 이제 프론트엔드와 연결할 준비가 되었습니다.")
    else:
        print("\n⚠️ 일부 테스트에서 문제 발생. 로그를 확인해주세요.")
        
    print(f"\n📄 생성된 파일:")
    print(f"  - 지식 데이터베이스: real_test_knowledge.db")

if __name__ == "__main__":
    asyncio.run(main())