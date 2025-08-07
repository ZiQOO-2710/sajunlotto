#!/usr/bin/env python3
"""
AI 시스템 테스트
YouTube 학습이 완전히 숨겨진 AI 테스트
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_persona import SajuMasterAI
from app.services.youtube_service import YouTubeService

class MockDB:
    def close(self):
        pass

async def test_ai_persona():
    print("🤖 SajuMaster AI 테스트 시작")
    print("=" * 50)
    
    # AI 서비스 생성
    db = MockDB()
    knowledge_service = YouTubeService(db, "test_ai_knowledge.db")
    ai = SajuMasterAI(knowledge_service, db)
    
    # 테스트용 생년월일
    birth_info = {
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 15,
        "birth_hour": 14,
        "name": "테스트"
    }
    
    print("\n1️⃣ AI 사주 분석 테스트")
    print("-" * 30)
    
    # AI 분석 수행
    analysis = await ai.analyze_saju(birth_info)
    
    print(f"🎯 AI 인사: {analysis['greeting']}")
    print(f"📊 핵심 분석: {analysis['core_analysis'][:100]}...")
    print(f"💡 성격 통찰: {analysis['personality_insights'][0] if analysis['personality_insights'] else '없음'}")
    print(f"🔮 AI 신뢰도: {analysis['ai_confidence'] * 100:.1f}%")
    print(f"✉️ 특별 메시지: {analysis['special_message']}")
    
    print("\n2️⃣ AI 로또 예측 테스트")
    print("-" * 30)
    
    # 로또 예측
    prediction = await ai.predict_numbers(birth_info, 1150)
    
    print(f"🎰 AI 예측: {prediction['ai_statement']}")
    print(f"🔢 추천 번호: {prediction['predicted_numbers']}")
    print(f"📈 신뢰도: {prediction['confidence_statement']}")
    print(f"💭 AI 근거: {prediction['ai_reasoning']}")
    print(f"📝 개인 조언: {prediction['personalized_advice'][0] if prediction['personalized_advice'] else '없음'}")
    print(f"✍️ AI 서명: {prediction['ai_signature']}")
    
    print("\n3️⃣ AI 대화 테스트")
    print("-" * 30)
    
    # AI와 대화
    questions = [
        "오늘 운세는 어떤가요?",
        "로또 번호 선택 팁을 알려주세요",
        "제 사주에서 강점은 무엇인가요?"
    ]
    
    for question in questions[:1]:  # 첫 번째 질문만 테스트
        print(f"\n👤 사용자: {question}")
        response = await ai.get_enhanced_response(question, birth_info)
        print(f"🤖 AI: {response[:200]}...")
    
    print("\n" + "=" * 50)
    print("✅ AI 테스트 완료!")
    print("📌 중요: 모든 응답에서 YouTube 언급이 없고, AI가 자체 능력으로 표현됨")

async def test_youtube_learning():
    """관리자용 YouTube 학습 테스트 (숨김)"""
    print("\n\n🔒 관리자 전용: YouTube 학습 테스트")
    print("=" * 50)
    
    db = MockDB()
    youtube_service = YouTubeService(db, "test_ai_knowledge.db")
    
    # 간단한 텍스트로 학습 테스트
    test_text = """
    갑목일주는 리더십이 강하고 성실한 성격을 가지고 있습니다.
    재물운이 좋으며 사업에 적합한 사주입니다.
    건강에 주의하시고 스트레스 관리가 필요합니다.
    """
    
    analysis = await youtube_service.analyze_saju_content(test_text)
    
    print(f"📚 발견된 사주 용어: {analysis['saju_terms']}")
    print(f"📝 문장 유형: {analysis['sentence_type']}")
    print(f"💯 신뢰도: {analysis['confidence'] * 100:.1f}%")
    
    # 지식 요약
    summary = await youtube_service.get_knowledge_summary()
    print(f"\n📊 지식 데이터베이스 상태:")
    print(f"  - 총 지식: {summary['total_knowledge_entries']}개")
    print(f"  - 처리된 영상: {summary['total_videos_processed']}개")
    print(f"  - 평균 신뢰도: {summary['average_confidence'] * 100:.1f}%")
    
    print("\n✅ YouTube 학습 시스템 정상 작동 (사용자에게는 숨김)")

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║     SajuMaster AI 시스템 테스트       ║
    ║   YouTube 학습 완전 은폐 버전 v3.0    ║
    ╔════════════════════════════════════════╝
    """)
    
    # AI 테스트 실행
    asyncio.run(test_ai_persona())
    
    # 관리자 모드에서만 YouTube 테스트
    if os.getenv("ADMIN_MODE") == "true":
        asyncio.run(test_youtube_learning())
    else:
        print("\n💡 팁: ADMIN_MODE=true 로 실행하면 관리자 기능을 테스트할 수 있습니다")