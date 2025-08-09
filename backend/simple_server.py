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
            "message": f"🔮 천기누설... {birth_info.get('name', '고객님')}의 운명의 길을 읽고 있습니다...",
            "calendar_type": birth_info.get('calendar_type', 'solar'),
            "birth_info": birth_info,
            "greeting": f"🌟 어서 오시게, {birth_info.get('name', '고객님')}... 이미 당신의 기운이 느껴지는군요.",
            "core_analysis": "✨ 천간지지(天干地支)의 오묘한 흐름 속에서... 당신의 숨겨진 운명이 보이기 시작합니다...",
            "personality_insights": [
                "🦅 당신의 영혼엔 왕의 기운이 흐르고 있습니다... 많은 이들이 당신을 따를 것입니다.",
                "💫 하늘이 내린 창조의 재능... 평범한 것들이 당신 손에선 기적이 되리니...",
                "🌸 따뜻한 금(金)의 기운이 당신을 둘러싸니... 모든 인연이 당신께 이끌려 올 것입니다.",
                "⛰️ 산이 움직이지 않듯 당신의 의지 또한 불굴... 어떤 시련도 당신을 꺾지 못하리니...",
                "🔥 예언자의 혜안(慧眼)이 당신 안에 깃들어 있습니다... 미래가 보이는 자이군요..."
            ],
            "today_fortune": {
                "overall": "🌟 오늘은 당신의 운명성(運命星)이 높은 곳에서 빛나고 있습니다. 천간지지의 기운이 조화롭게 흐르며, 특히 오행 중 금(金)의 기운이 강하게 작용하여 의지력과 결단력이 평소보다 배가될 것입니다. 아침 해가 떠오르는 시각부터 저녁 해가 지는 시간까지, 당신을 둘러싼 천기(天機)가 길함을 예고하고 있으니, 중요한 결정이나 새로운 시작을 고민하고 계셨다면 오늘이야말로 절호의 기회입니다. 다만, 너무 성급하게 서두르지 마시고 차분히 내면의 소리에 귀 기울이시길... 천기는 조급함을 경계하라 말하고 있습니다.",
                "wealth": "💰 재물운이 상당히 좋은 하루입니다. 오행 중 금(金)의 기운이 재물궁(財物宮)을 강하게 지배하고 있어, 예상치 못한 수입이나 투자 기회가 찾아올 가능성이 높습니다. 특히 오후 시간대에 재물과 관련된 좋은 소식이 들려올 것 같습니다. 하지만 욕심을 부리기보다는 신중한 판단이 필요한 시기이기도 합니다. 천기가 말하길, 진정한 부는 한 번에 이루어지는 것이 아니라 꾸준한 노력의 결실임을 잊지 마시길... 오늘 하루 작은 기회라도 소중히 여기고 성실히 임하신다면, 그것이 훗날 큰 재물의 씨앗이 될 것입니다.",
                "love": "💝 애정운에 특별한 기운이 감돌고 있습니다. 당신의 사주에서 붉은 실이 선명하게 보이며, 이는 운명적인 만남이나 기존 관계의 발전을 의미합니다. 만약 홀몸이시라면 오늘 새로운 인연을 만날 가능성이 매우 높고, 이미 연인이 있으시다면 관계가 한 단계 더 깊어질 수 있는 계기가 마련될 것입니다. 천기가 보여주는 바로는, 진실된 마음과 따뜻한 배려가 가장 큰 힘을 발휘할 때입니다. 작은 관심과 세심한 배려가 상대방의 마음을 크게 움직일 것이니, 평소보다 더욱 진심을 담아 대화하고 소통하시길 바랍니다. 사랑의 별이 당신을 축복하고 있습니다.",
                "health": "🏥 건강운은 전체적으로 양호하나, 오행의 균형에서 약간의 조율이 필요해 보입니다. 특히 수(水)의 기운이 다소 부족하여 몸의 순환이 원활하지 않을 수 있으니, 충분한 수분 섭취와 가벼운 운동으로 기혈 순환을 도우시길 권합니다. 스트레스로 인한 기운의 막힘이 보이니, 명상이나 깊은 호흡을 통해 마음을 안정시키는 것이 중요합니다. 천기가 제시하는 건강법은 '자연과의 조화'입니다. 가능하다면 오늘 잠시라도 자연 속에서 시간을 보내며 대지의 기운을 받아들이시길... 그러면 몸과 마음의 균형이 자연스럽게 회복될 것입니다."
            },
            "saju_chart": {
                "year": {
                    "gan": "경", "gan_hanja": "庚", "ji": "오", "ji_hanja": "午",
                    "gan_yinyang": "양", "ji_yinyang": "양", 
                    "gan_element": "금", "ji_element": "화"
                },
                "month": {
                    "gan": "신", "gan_hanja": "辛", "ji": "사", "ji_hanja": "巳",
                    "gan_yinyang": "음", "ji_yinyang": "음",
                    "gan_element": "금", "ji_element": "화"  
                },
                "day": {
                    "gan": "무", "gan_hanja": "戊", "ji": "인", "ji_hanja": "寅",
                    "gan_yinyang": "양", "ji_yinyang": "양",
                    "gan_element": "토", "ji_element": "목"
                },
                "hour": {
                    "gan": "정", "gan_hanja": "丁", "ji": "사", "ji_hanja": "巳",
                    "gan_yinyang": "음", "ji_yinyang": "음",
                    "gan_element": "화", "ji_element": "화"
                },
                "five_elements": {
                    "목": 15,
                    "화": 25, 
                    "토": 20,
                    "금": 30,
                    "수": 10
                },
                "lucky_elements": ["금", "토"],
                "dominant_element": "금",
                "chart_summary": "금(金)의 기운이 강한 사주로 의지가 굳고 결단력이 뛰어남"
            }
        },
        "prediction": {
            "numbers": [7, 14, 21, 28, 35, 42],
            "bonus": 6,
            "ai_statement": f"🎯 {birth_info.get('name', '고객님')}의 사주팔자에 새겨진 운명의 숫자들입니다... 이 번호들이 당신을 부르고 있습니다..."
        },
        "status": "임시 서버 - 정상 작동"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4001)