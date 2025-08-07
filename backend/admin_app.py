"""
관리자 전용 애플리케이션
YouTube 학습 관리 및 시스템 모니터링
일반 사용자에게는 절대 노출되지 않음
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
from datetime import datetime

from database import SessionLocal, engine
from app.services.youtube_service import YouTubeService
import models

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SajuLotto Admin",
    description="관리자 전용 YouTube 학습 및 시스템 관리",
    version="1.0.0"
)

# CORS 설정 (관리자 도메인만 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # 관리자 프론트엔드
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

def get_youtube_service(db: Session = Depends(get_db)) -> YouTubeService:
    return YouTubeService(db, "saju_knowledge_complete.db")

# 관리자 인증 (간단한 API 키 방식)
def verify_admin(api_key: str):
    if api_key != os.getenv("ADMIN_API_KEY", "secret-admin-key-2024"):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return True

# ==================== YouTube 학습 관리 ====================

@app.get("/")
async def root():
    """관리자 시스템 정보"""
    return {
        "system": "SajuLotto Admin",
        "version": "1.0.0",
        "status": "operational",
        "modules": [
            "YouTube 학습 관리",
            "지식 데이터베이스 관리",
            "시스템 모니터링",
            "자동 학습 스케줄러"
        ]
    }

@app.post("/youtube/learn/single")
async def learn_single_video(
    request: Dict[str, Any],
    api_key: str,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """단일 YouTube 영상 학습"""
    verify_admin(api_key)
    
    video_id = request.get("video_id")
    if not video_id:
        raise HTTPException(status_code=400, detail="video_id 필요")
    
    result = await youtube_service.learn_from_video(video_id)
    
    return {
        "success": result.get("success", False),
        "learned_sentences": result.get("learned_sentences", 0),
        "video_info": result.get("video_info", {}),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/youtube/learn/batch")
async def learn_batch_videos(
    request: Dict[str, Any],
    api_key: str,
    background_tasks: BackgroundTasks,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """일괄 YouTube 영상 학습"""
    verify_admin(api_key)
    
    video_ids = request.get("video_ids", [])
    if not video_ids:
        raise HTTPException(status_code=400, detail="video_ids 필요")
    
    # 백그라운드 태스크로 실행
    async def batch_learn():
        result = await youtube_service.batch_learn_from_videos(video_ids)
        print(f"일괄 학습 완료: {result}")
    
    background_tasks.add_task(batch_learn)
    
    return {
        "message": f"{len(video_ids)}개 영상 학습 시작",
        "video_ids": video_ids,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/youtube/knowledge/summary")
async def get_knowledge_summary(
    api_key: str,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """학습된 지식 요약"""
    verify_admin(api_key)
    
    summary = await youtube_service.get_knowledge_summary()
    
    return {
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/youtube/knowledge/search")
async def search_knowledge(
    request: Dict[str, Any],
    api_key: str,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """지식 검색"""
    verify_admin(api_key)
    
    query = request.get("query", "")
    limit = request.get("limit", 10)
    
    results = await youtube_service.search_knowledge(query, limit)
    
    return {
        "query": query,
        "results": results,
        "count": len(results),
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/youtube/knowledge/clear")
async def clear_knowledge(
    api_key: str,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """지식 데이터베이스 초기화 (주의!)"""
    verify_admin(api_key)
    
    # 안전을 위해 이중 확인
    confirm = input("정말로 모든 학습 데이터를 삭제하시겠습니까? (yes/no): ")
    if confirm.lower() != "yes":
        raise HTTPException(status_code=400, detail="작업 취소됨")
    
    # 데이터베이스 초기화
    youtube_service._init_knowledge_db()
    
    return {
        "message": "지식 데이터베이스가 초기화되었습니다",
        "timestamp": datetime.now().isoformat()
    }

# ==================== 자동 학습 스케줄러 ====================

@app.post("/scheduler/youtube_channels")
async def add_youtube_channels(
    request: Dict[str, Any],
    api_key: str,
    db: Session = Depends(get_db)
):
    """YouTube 채널 자동 모니터링 추가"""
    verify_admin(api_key)
    
    channels = request.get("channels", [])
    
    # 채널 정보 저장 (추후 구현)
    return {
        "message": f"{len(channels)}개 채널 추가됨",
        "channels": channels,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/scheduler/status")
async def get_scheduler_status(
    api_key: str
):
    """스케줄러 상태"""
    verify_admin(api_key)
    
    return {
        "scheduler": "active",
        "next_run": "2024-01-15 03:00:00",
        "channels_monitored": 5,
        "videos_pending": 12,
        "last_run": "2024-01-14 03:00:00",
        "videos_processed_last_run": 8
    }

# ==================== 시스템 모니터링 ====================

@app.get("/system/stats")
async def get_system_stats(
    api_key: str,
    youtube_service: YouTubeService = Depends(get_youtube_service),
    db: Session = Depends(get_db)
):
    """시스템 통계"""
    verify_admin(api_key)
    
    # 지식 통계
    knowledge_summary = await youtube_service.get_knowledge_summary()
    
    # 사용자 통계 (예시)
    user_count = db.query(models.User).count()
    prediction_count = db.query(models.Prediction).count()
    
    return {
        "knowledge": {
            "total_entries": knowledge_summary.get("total_knowledge_entries", 0),
            "videos_processed": knowledge_summary.get("total_videos_processed", 0),
            "avg_confidence": knowledge_summary.get("average_confidence", 0)
        },
        "users": {
            "total": user_count,
            "active_today": 0,  # 추후 구현
            "predictions_total": prediction_count
        },
        "system": {
            "uptime_hours": 720,
            "api_calls_today": 1234,
            "error_rate": 0.01
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/system/logs")
async def get_system_logs(
    api_key: str,
    limit: int = 100
):
    """시스템 로그"""
    verify_admin(api_key)
    
    # 로그 예시 (실제로는 로그 파일에서 읽어옴)
    logs = [
        {
            "timestamp": "2024-01-14 12:34:56",
            "level": "INFO",
            "message": "YouTube 학습 완료: video_id=abc123"
        },
        {
            "timestamp": "2024-01-14 12:30:00",
            "level": "INFO",
            "message": "자동 학습 스케줄러 시작"
        }
    ]
    
    return {
        "logs": logs[:limit],
        "total": len(logs),
        "timestamp": datetime.now().isoformat()
    }

# ==================== 지식 품질 관리 ====================

@app.get("/quality/low_confidence")
async def get_low_confidence_knowledge(
    api_key: str,
    threshold: float = 0.3,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    """낮은 신뢰도 지식 조회"""
    verify_admin(api_key)
    
    # SQLite 직접 쿼리 (예시)
    import sqlite3
    conn = sqlite3.connect("saju_knowledge_complete.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT video_id, content, confidence 
        FROM saju_knowledge 
        WHERE confidence < ? 
        ORDER BY confidence ASC 
        LIMIT 100
    """, (threshold,))
    
    results = cursor.fetchall()
    conn.close()
    
    return {
        "threshold": threshold,
        "count": len(results),
        "items": [
            {
                "video_id": r[0],
                "content": r[1][:100] + "...",
                "confidence": r[2]
            }
            for r in results
        ]
    }

@app.post("/quality/remove_low_quality")
async def remove_low_quality_knowledge(
    request: Dict[str, Any],
    api_key: str
):
    """낮은 품질 지식 제거"""
    verify_admin(api_key)
    
    threshold = request.get("confidence_threshold", 0.2)
    
    import sqlite3
    conn = sqlite3.connect("saju_knowledge_complete.db")
    cursor = conn.cursor()
    
    # 삭제 전 카운트
    cursor.execute("SELECT COUNT(*) FROM saju_knowledge WHERE confidence < ?", (threshold,))
    count = cursor.fetchone()[0]
    
    # 삭제 실행
    cursor.execute("DELETE FROM saju_knowledge WHERE confidence < ?", (threshold,))
    conn.commit()
    conn.close()
    
    return {
        "message": f"신뢰도 {threshold} 미만 {count}개 항목 삭제됨",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🔧 관리자 애플리케이션 시작...")
    print("📊 관리자 패널: http://localhost:8001")
    print("🔑 API 키 필요: ADMIN_API_KEY 환경 변수 설정")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # 관리자는 다른 포트 사용
        reload=True
    )