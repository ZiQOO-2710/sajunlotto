#!/usr/bin/env python3
"""
간단한 테스트 서버 - 화면 확인용
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SajuLotto 테스트 서버")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "SajuLotto 테스트 서버가 실행 중입니다!",
        "status": "success",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "server": "running"
    }

@app.post("/api/v1/ai/analyze")
async def test_analyze(birth_info: dict):
    """임시 테스트 API - 사주 분석"""
    return {
        "success": True,
        "analysis": {
            "message": f"{birth_info.get('name', '고객님')}의 사주를 분석 중입니다...",
            "calendar_type": birth_info.get('calendar_type', 'solar'),
            "birth_info": birth_info,
            "greeting": f"안녕하세요, {birth_info.get('name', '고객님')}! 사주 분석이 완료되었습니다.",
            "core_analysis": "천간과 지지의 조화를 통해 당신의 운명을 읽어보겠습니다.",
            "personality_insights": [
                "타고난 리더십으로 많은 사람들을 이끌어가는 능력이 있습니다.",
                "창의적이고 독창적인 사고로 새로운 아이디어를 잘 만들어냅니다.",
                "인간관계에서 따뜻함과 포용력을 발휘하여 사랑받는 성격입니다.",
                "꾸준한 노력과 인내력으로 목표를 달성하는 힘이 있습니다.",
                "직감이 뛰어나고 상황 판단력이 매우 우수합니다."
            ],
            "fortune_forecast": {
                "overall": "전체적으로 좋은 운세가 이어지며 새로운 기회가 다가올 것입니다.",
                "wealth": "재물운이 상승하며 투자나 사업에서 좋은 결과를 얻을 수 있습니다.",
                "love": "인연운이 매우 좋아 소중한 만남이나 관계 발전이 기대됩니다.",
                "health": "건강관리에 신경쓰면서 규칙적인 생활을 유지하는 것이 좋겠습니다."
            },
            "ai_confidence": 0.85,
            "special_message": "천기가 당신에게 행운과 성공의 길을 열어줄 것입니다."
        },
        "prediction": {
            "numbers": [7, 14, 21, 28, 35, 42],
            "bonus": 6,
            "confidence": 85.5,
            "ai_statement": f"{birth_info.get('name', '고객님')}의 사주에 따른 행운의 번호입니다."
        },
        "status": "임시 서버 - 정상 작동"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4001)