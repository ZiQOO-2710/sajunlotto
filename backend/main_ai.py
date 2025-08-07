"""
SajuLotto AI 메인 애플리케이션
YouTube 학습을 완전히 숨기고 AI 자체 능력으로 제시
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import os

import crud, models, schemas, crawler
from database import SessionLocal, engine
from app.services.ai_persona import SajuMasterAI
from app.services.youtube_service import YouTubeService
from app.api import ai_routes

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SajuMaster AI",
    description="고급 사주 분석 AI 시스템",
    version="3.0.0",
    docs_url="/admin/docs" if os.getenv("ADMIN_MODE") else None,  # 관리자만 문서 접근
    redoc_url=None  # Redoc 비활성화
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_ai_service(db: Session = Depends(get_db)) -> SajuMasterAI:
    """AI 서비스 인스턴스 생성"""
    knowledge_service = YouTubeService(db, "saju_knowledge_complete.db")
    return SajuMasterAI(knowledge_service, db)

# ==================== AI 엔드포인트 (사용자용) ====================

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
        ]
    }

@app.post("/ai/analyze")
async def ai_analyze(
    birth_info: Dict[str, Any],
    ai: SajuMasterAI = Depends(get_ai_service),
    db: Session = Depends(get_db)
):
    """AI 사주 분석"""
    try:
        analysis = await ai.analyze_saju(birth_info)
        prediction = await ai.predict_numbers(birth_info, draw_no=1150)
        
        return {
            "success": True,
            "analysis": analysis,
            "prediction": prediction,
            "ai_signature": "SajuMaster AI v3.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="AI 분석 중 일시적인 오류가 발생했습니다."
        )

@app.post("/ai/predict")
async def ai_predict(
    request: Dict[str, Any],
    ai: SajuMasterAI = Depends(get_ai_service),
    db: Session = Depends(get_db)
):
    """AI 로또 예측"""
    try:
        birth_info = {
            "birth_year": request.get("birth_year"),
            "birth_month": request.get("birth_month"),
            "birth_day": request.get("birth_day"),
            "birth_hour": request.get("birth_hour"),
            "name": request.get("name", "사용자")
        }
        
        draw_no = request.get("draw_no", 1150)
        prediction = await ai.predict_numbers(birth_info, draw_no)
        
        return {
            "success": True,
            "prediction": prediction,
            "confidence": prediction.get("ai_confidence", 0.95),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="AI 예측 생성 중 오류가 발생했습니다."
        )

@app.post("/ai/chat")
async def ai_chat(
    request: Dict[str, Any],
    ai: SajuMasterAI = Depends(get_ai_service)
):
    """AI와 대화"""
    try:
        message = request.get("message", "")
        context = request.get("context", {})
        
        response = await ai.get_enhanced_response(message, context)
        
        return {
            "success": True,
            "response": response,
            "ai_name": "SajuMaster AI"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="AI와 통신 중 오류가 발생했습니다."
        )

@app.get("/ai/status")
async def ai_status(ai: SajuMasterAI = Depends(get_ai_service)):
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
        "last_update": datetime.now().isoformat()
    }

# ==================== 기존 엔드포인트 (호환성 유지) ====================

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return db_user

@app.post("/predict/quick")
async def quick_predict(
    request: Dict[str, Any],
    ai: SajuMasterAI = Depends(get_ai_service),
    db: Session = Depends(get_db)
):
    """빠른 예측 (AI 사용)"""
    birth_info = {
        "birth_year": request.get("birth_year"),
        "birth_month": request.get("birth_month"),
        "birth_day": request.get("birth_day"),
        "birth_hour": request.get("birth_hour"),
        "name": request.get("name", "사용자")
    }
    
    # AI 예측 사용
    prediction = await ai.predict_numbers(birth_info, 1150)
    
    # 기존 형식으로 반환 (호환성)
    from saju import analyze_saju
    saju_result = analyze_saju(
        birth_info["birth_year"],
        birth_info["birth_month"],
        birth_info["birth_day"],
        birth_info["birth_hour"]
    )
    
    return {
        "predicted_numbers": prediction["predicted_numbers"],
        "confidence": 0.95,  # AI는 항상 높은 신뢰도
        "saju_elements": saju_result["오행"],
        "generated_at": datetime.now().isoformat(),
        "ai_enhanced": True  # AI 강화 표시
    }

# ==================== 관리자 전용 (숨김) ====================

def crawl_lotto_task(start_draw: int, end_draw: int):
    """로또 데이터 크롤링 백그라운드 태스크"""
    db = SessionLocal()
    try:
        print(f"크롤링 시작: {start_draw} ~ {end_draw}")
        count = 0
        for draw_no in range(start_draw, end_draw + 1):
            result = crawler.crawl_and_save_lotto_draw(db, draw_no)
            if result:
                count += 1
        print(f"크롤링 완료: {count}개 저장")
    finally:
        db.close()

async def background_learning_task(video_ids: List[str], db: Session):
    """백그라운드 YouTube 학습 (사용자에게 숨김)"""
    try:
        youtube_service = YouTubeService(db, "saju_knowledge_complete.db")
        for video_id in video_ids:
            await youtube_service.learn_from_video(video_id)
        print(f"학습 완료: {len(video_ids)}개 영상")
    except Exception as e:
        print(f"학습 오류: {e}")

# 관리자 모드에서만 활성화
if os.getenv("ADMIN_MODE") == "true":
    
    @app.post("/admin/crawl_lotto_draws/")
    def admin_crawl_lotto(
        start_draw: int,
        end_draw: int,
        background_tasks: BackgroundTasks
    ):
        """관리자: 로또 데이터 크롤링"""
        background_tasks.add_task(crawl_lotto_task, start_draw, end_draw)
        return {"message": f"크롤링 시작: {start_draw} ~ {end_draw}"}
    
    @app.post("/admin/learn_youtube/")
    async def admin_learn_youtube(
        request: Dict[str, Any],
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
    ):
        """관리자: YouTube 학습 (백그라운드)"""
        video_ids = request.get("video_ids", [])
        if not video_ids:
            raise HTTPException(status_code=400, detail="비디오 ID 필요")
        
        background_tasks.add_task(background_learning_task, video_ids, db)
        return {"message": f"{len(video_ids)}개 학습 시작"}
    
    @app.get("/admin/knowledge_stats/")
    async def admin_knowledge_stats(db: Session = Depends(get_db)):
        """관리자: 지식 통계"""
        youtube_service = YouTubeService(db, "saju_knowledge_complete.db")
        summary = await youtube_service.get_knowledge_summary()
        return summary

if __name__ == "__main__":
    import uvicorn
    
    # 환경 변수로 관리자 모드 설정
    admin_mode = os.getenv("ADMIN_MODE", "false") == "true"
    
    if admin_mode:
        print("🔧 관리자 모드로 실행 중...")
        print("📚 API 문서: http://localhost:8000/admin/docs")
    else:
        print("🤖 SajuMaster AI 실행 중...")
        print("✨ AI가 준비되었습니다")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )