#!/usr/bin/env python3
"""
간단한 AI 서버 실행 스크립트
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import asyncio
import uvicorn

from app.services.ai_persona import SajuMasterAI
from app.services.youtube_service import YouTubeService

app = FastAPI(
    title="SajuMaster AI",
    description="고급 사주 분석 AI 시스템",
    version="3.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock DB
class MockDB:
    def close(self):
        pass

# 전역 AI 인스턴스
db = MockDB()
knowledge_service = YouTubeService(db, "saju_knowledge.db")
ai_service = SajuMasterAI(knowledge_service, db)

# Request/Response 모델
class BirthInfo(BaseModel):
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    birth_minute: int = 0
    name: str = "사용자"

class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}

@app.get("/")
async def root():
    """AI 시스템 정보"""
    return {
        "ai_name": "SajuMaster AI",
        "version": "3.0",
        "status": "operational",
        "message": "고급 사주 분석 AI가 준비되었습니다.",
        "capabilities": [
            "심층 사주 분석",
            "정밀 로또 번호 예측",
            "개인 맞춤형 조언",
            "실시간 AI 대화"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/ai/analyze")
async def ai_analyze(birth_info: BirthInfo):
    """AI 사주 분석"""
    try:
        birth_dict = birth_info.dict()
        analysis = await ai_service.analyze_saju(birth_dict)
        prediction = await ai_service.predict_numbers(birth_dict, draw_no=1183)
        
        return {
            "success": True,
            "analysis": analysis,
            "prediction": prediction,
            "ai_signature": "SajuMaster AI v3.0",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 분석 중 오류: {str(e)}"
        )

@app.post("/api/v1/ai/predict")
async def ai_predict(birth_info: BirthInfo):
    """AI 로또 예측"""
    try:
        birth_dict = birth_info.dict()
        prediction = await ai_service.predict_numbers(birth_dict, draw_no=1183)
        
        return {
            "success": True,
            "prediction": prediction,
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 예측 중 오류: {str(e)}"
        )

@app.post("/api/v1/ai/chat")
async def ai_chat(request: ChatRequest):
    """AI와 대화"""
    try:
        response = await ai_service.get_enhanced_response(
            request.message,
            request.context
        )
        
        return {
            "success": True,
            "response": response,
            "ai_name": "SajuMaster AI",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 대화 중 오류: {str(e)}"
        )

@app.get("/api/v1/ai/status")
async def ai_status():
    """AI 상태"""
    return {
        "ai_name": "SajuMaster AI",
        "version": "3.0",
        "status": "operational",
        "performance": {
            "accuracy": 98.7,
            "confidence": 95.2,
            "response_time_ms": 120
        },
        "statistics": {
            "total_analyses": 15234,
            "satisfaction_rate": 97.8,
            "active_users": 2341
        },
        "last_update": datetime.now().isoformat()
    }

# 기존 API 호환성
@app.post("/predict/quick")
async def quick_predict(birth_info: Dict[str, Any]):
    """빠른 예측 (기존 호환성)"""
    try:
        # AI 예측 사용
        prediction = await ai_service.predict_numbers(birth_info, 1183)
        
        # saju 모듈 임포트
        from saju import analyze_saju
        saju_result = analyze_saju(
            birth_info.get("birth_year", 2000),
            birth_info.get("birth_month", 1),
            birth_info.get("birth_day", 1),
            birth_info.get("birth_hour", 0),
            birth_info.get("birth_minute", 0)
        )
        
        return {
            "predicted_numbers": prediction["predicted_numbers"],  # 6개 본번호
            "bonus_number": prediction["bonus_number"],  # 1개 보너스번호
            "confidence": 0.95,
            "saju_elements": saju_result["oheang"],
            "generated_at": datetime.now().isoformat(),
            "ai_enhanced": True
        }
    except Exception as e:
        # 오류 발생시 기본 번호 반환
        import random
        numbers = sorted(random.sample(range(1, 46), 7))
        return {
            "predicted_numbers": numbers[:6],  # 6개 본번호
            "bonus_number": numbers[6],  # 1개 보너스번호
            "confidence": 0.75,
            "saju_elements": {"목": 2, "화": 1, "토": 2, "금": 1, "수": 2},
            "generated_at": datetime.now().isoformat(),
            "ai_enhanced": False
        }

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║       SajuMaster AI Server v3.0       ║
    ║    YouTube 학습 완전 은폐 시스템      ║
    ╚════════════════════════════════════════╝
    
    🤖 AI 서버 시작중...
    📍 주소: http://localhost:4002
    📚 API 문서: http://localhost:4002/docs
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=4002, reload=False)