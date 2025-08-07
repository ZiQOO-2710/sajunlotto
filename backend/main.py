from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import unquote
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

import crud, models, schemas, crawler
from database import SessionLocal, engine
from prediction_service import prediction_service
from lstm_prediction_service import get_lstm_prediction, lstm_service
from youtube_crawler import YouTubeSajuCrawler
import youtube_crud
# from youtube_content_analyzer import YouTubeContentAnalyzer  # Whisper import issue
from simple_youtube_learner import SimpleYouTubeLearner

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SajuLotto API", 
    description="Korean fortune-telling based lottery prediction API",
    version="1.0.0"
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SajuLotto API is running!", "status": "success", "version": "1.0.0"}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def crawl_lotto_task(start_draw: int, end_draw: int):
    """
    Background task for crawling lotto data.
    A new DB session is created for this task.
    """
    db = SessionLocal()
    try:
        print(f"Starting to crawl lotto draws from {start_draw} to {end_draw}...")
        count = 0
        for draw_no in range(start_draw, end_draw + 1):
            result = crawler.crawl_and_save_lotto_draw(db, draw_no)
            if result:
                count += 1
        print(f"Crawling finished. Saved {count} new draws from {start_draw} to {end_draw}.")
    finally:
        db.close()

# ============================================================================
# User Management API Endpoints  
# ============================================================================

@app.post("/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")
    return crud.create_user(db=db, user=user)

@app.post("/auth/login", response_model=schemas.User)
def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """사용자 로그인 (간단 버전)"""
    db_user = crud.login_user(db, email=login_data.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return db_user

@app.get("/users/{user_id}/profile")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """사용자 프로필 조회"""
    profile_data = crud.get_user_profile(db, user_id=user_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    user = profile_data['user']
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "saju_profile": user.saju_profile,
        "prediction_count": profile_data['prediction_count']
    }

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """사용자 생성 (호환성 유지)"""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/users/{user_id}/saju/", response_model=schemas.SajuProfile)
def create_saju_profile_for_user(
    user_id: int, saju_profile: schemas.SajuProfileCreate, db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_saju_profile(db=db, user_id=user_id, saju_profile=saju_profile)

@app.post("/admin/crawl_lotto_draws/")
def admin_crawl_lotto_draws(
    start_draw: int,
    end_draw: int,
    background_tasks: BackgroundTasks
):
    """
    Triggers a background task to crawl and save lotto draws for a given range.
    """
    background_tasks.add_task(crawl_lotto_task, start_draw, end_draw)
    return {"message": f"Crawling for draws {start_draw} to {end_draw} has been initiated in the background."}

# ============================================================================
# Prediction API Endpoints
# ============================================================================

@app.post("/predict/", response_model=schemas.PredictionResponse)
def predict_lotto_numbers(request: schemas.PredictionRequest):
    """
    사주 기반 로또 번호 예측
    생년월일시를 입력받아 사주 분석과 통계적 패턴을 결합한 로또 번호를 예측합니다.
    """
    try:
        # URL 인코딩된 이름 디코딩
        decoded_name = unquote(request.name) if request.name else None
        
        result = prediction_service.generate_prediction(
            birth_year=request.birth_year,
            birth_month=request.birth_month,
            birth_day=request.birth_day,
            birth_hour=request.birth_hour,
            name=decoded_name
        )
        
        # 직접 dict 형태로 응답 반환 (스키마 검증 우회)
        return {
            'predicted_numbers': result['predicted_numbers'],
            'saju_analysis': result['saju_analysis'], 
            'number_scores': result['number_scores'][:10],  # 상위 10개만
            'method': result['method'],
            'confidence': result['confidence'],
            'generated_at': result['generated_at'].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 생성 중 오류 발생: {str(e)}")

@app.get("/analysis/historical", response_model=schemas.HistoricalAnalysisResponse)
def get_historical_analysis():
    """
    히스토리컬 로또 데이터 분석
    수집된 과거 로또 데이터의 패턴과 통계를 분석합니다.
    """
    try:
        lotto_draws, stats = prediction_service.load_historical_data()
        pattern_analysis = prediction_service.analyze_number_patterns(lotto_draws)
        
        # 최근 5회차 데이터 변환
        last_5_draws = []
        for draw in stats['latest_draws']:
            last_5_draws.append({
                'draw_no': draw.draw_no,
                'numbers': [draw.n1, draw.n2, draw.n3, draw.n4, draw.n5, draw.n6],
                'bonus': draw.bonus,
                'draw_date': draw.draw_date.isoformat() if draw.draw_date else None
            })
        
        return schemas.HistoricalAnalysisResponse(
            total_draws=stats['total_draws'],
            draw_range=stats['draw_range'],
            top_numbers=pattern_analysis['top_numbers'],
            element_distribution=pattern_analysis['element_distribution'],
            last_5_draws=last_5_draws
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리컬 분석 중 오류 발생: {str(e)}")

@app.post("/predict/quick")
def quick_predict(request: schemas.PredictionRequest):
    """
    빠른 예측 (간소화된 응답)
    기본적인 예측 번호만 반환합니다.
    """
    try:
        result = prediction_service.generate_prediction(
            birth_year=request.birth_year,
            birth_month=request.birth_month,
            birth_day=request.birth_day,
            birth_hour=request.birth_hour,
            name=request.name
        )
        
        return {
            "predicted_numbers": result['predicted_numbers'],
            "confidence": result['confidence'],
            "method": result['method'],
            "generated_at": result['generated_at'].isoformat(),
            "saju_elements": result['saju_analysis']['oheang']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"빠른 예측 중 오류 발생: {str(e)}")

@app.post("/predict/save")
def save_user_prediction(request: schemas.SavePredictionRequest, db: Session = Depends(get_db)):
    """
    사용자 예측을 데이터베이스에 저장
    """
    try:
        prediction = crud.save_prediction(
            db=db,
            user_id=request.user_id,
            predicted_numbers=request.predicted_numbers,
            method=request.method,
            confidence=request.confidence,
            saju_weights=request.saju_weights,
            draw_no=request.draw_no
        )
        
        return {
            "id": prediction.id,
            "message": "예측이 성공적으로 저장되었습니다",
            "created_at": prediction.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 저장 중 오류 발생: {str(e)}")

@app.get("/users/{user_id}/predictions")
def get_user_prediction_history(user_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """
    사용자의 예측 히스토리 조회
    """
    try:
        predictions = crud.get_user_predictions(db, user_id=user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "predictions": [
                {
                    "id": p.id,
                    "draw_no": p.draw_no,
                    "predicted_numbers": p.predicted_numbers,
                    "method": p.method,
                    "confidence": p.confidence,
                    "is_winning": p.is_winning,
                    "match_count": p.match_count,
                    "created_at": p.created_at.isoformat()
                }
                for p in predictions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 히스토리 조회 중 오류 발생: {str(e)}")

@app.get("/users/{user_id}/stats")
def get_user_statistics(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 통계 정보 조회
    """
    try:
        stats = crud.get_user_stats(db, user_id=user_id)
        
        return {
            "user_id": user_id,
            "total_predictions": stats['total_predictions'],
            "total_matches": stats['total_matches'],
            "best_match_count": stats['best_match_count'],
            "avg_confidence": round(stats['avg_confidence'], 2),
            "favorite_method": stats['favorite_method'],
            "recent_predictions": [
                {
                    "id": p.id,
                    "predicted_numbers": p.predicted_numbers,
                    "method": p.method,
                    "confidence": p.confidence,
                    "match_count": p.match_count,
                    "created_at": p.created_at.isoformat()
                }
                for p in stats['recent_predictions']
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 통계 조회 중 오류 발생: {str(e)}")

@app.get("/users/{user_id}/winnings")
def get_user_winning_history(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 당첨 히스토리 조회
    """
    try:
        winnings = crud.get_user_winning_history(db, user_id=user_id)
        
        return {
            "user_id": user_id,
            "winnings": [
                {
                    "id": w.id,
                    "draw_no": w.draw_no,
                    "match_count": w.match_count,
                    "winning_numbers": w.winning_numbers,
                    "predicted_numbers": w.predicted_numbers,
                    "matched_numbers": w.matched_numbers,
                    "prize_rank": w.prize_rank,
                    "created_at": w.created_at.isoformat()
                }
                for w in winnings
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"당첨 히스토리 조회 중 오류 발생: {str(e)}")

@app.post("/admin/check-winnings")
def check_winning_results(db: Session = Depends(get_db)):
    """
    관리자용: 예측 결과와 실제 당첨 번호 비교
    """
    try:
        updated_count = crud.check_winning_results(db)
        
        return {
            "message": f"{updated_count}개의 예측 결과가 업데이트되었습니다",
            "updated_count": updated_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"당첨 결과 확인 중 오류 발생: {str(e)}")

@app.post("/predict/lstm")
def lstm_predict(request: schemas.PredictionRequest):
    """
    LSTM 기반 로또 번호 예측
    학습된 LSTM 모델과 사주 분석을 결합하여 번호를 예측합니다.
    """
    try:
        result = get_lstm_prediction(
            birth_year=request.birth_year,
            birth_month=request.birth_month,
            birth_day=request.birth_day,
            birth_hour=request.birth_hour,
            name=request.name
        )
        
        return {
            "predicted_numbers": result['predicted_numbers'],
            "confidence": result['confidence'],
            "method": result['method'],
            "generated_at": result['generated_at'].isoformat(),
            "saju_elements": result['saju_analysis']['오행'],
            "saju_weights": result['saju_weights'],
            "base_prediction": result.get('base_prediction', []),
            "model_info": {
                "model_file": result.get('model_file', 'unknown'),
                "prediction_type": "lstm_neural_network"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LSTM 예측 중 오류 발생: {str(e)}")

@app.get("/predict/compare/{birth_year}/{birth_month}/{birth_day}/{birth_hour}")
def compare_predictions(birth_year: int, birth_month: int, birth_day: int, birth_hour: int, name: str = "사용자"):
    """
    통계 기반 예측과 LSTM 예측을 비교합니다.
    """
    try:
        # 통계 기반 예측
        statistical_result = prediction_service.generate_prediction(
            birth_year=birth_year,
            birth_month=birth_month,
            birth_day=birth_day,
            birth_hour=birth_hour,
            name=name
        )
        
        # LSTM 기반 예측
        lstm_result = get_lstm_prediction(
            birth_year=birth_year,
            birth_month=birth_month,
            birth_day=birth_day,
            birth_hour=birth_hour,
            name=name
        )
        
        return {
            "comparison": {
                "statistical": {
                    "predicted_numbers": statistical_result['predicted_numbers'],
                    "confidence": statistical_result['confidence'],
                    "method": statistical_result['method']
                },
                "lstm": {
                    "predicted_numbers": lstm_result['predicted_numbers'],
                    "confidence": lstm_result['confidence'],
                    "method": lstm_result['method']
                }
            },
            "saju_analysis": statistical_result['saju_analysis'],
            "generated_at": datetime.now().isoformat(),
            "name": name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 비교 중 오류 발생: {str(e)}")

@app.get("/model/lstm/info")
def lstm_model_info():
    """
    LSTM 모델 정보를 반환합니다.
    """
    try:
        info = lstm_service.get_model_info()
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 정보 조회 중 오류 발생: {str(e)}")

@app.get("/health/prediction")
def prediction_health_check():
    """
    예측 시스템 상태 확인
    데이터베이스 연결과 기본 기능을 확인합니다.
    """
    try:
        # 데이터 로드 테스트
        lotto_draws, stats = prediction_service.load_historical_data()
        
        # 사주 분석 테스트
        test_saju = prediction_service.get_saju_analysis(1990, 5, 15, 10)
        
        # LSTM 모델 상태 확인
        lstm_info = lstm_service.get_model_info()
        
        return {
            "status": "healthy",
            "database_connection": "ok",
            "historical_data_count": stats['total_draws'],
            "saju_analysis": "ok",
            "lstm_model": "loaded" if lstm_info.get('model_loaded') else "not_loaded",
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

# ============================================================================
# YouTube Saju Video API Endpoints
# ============================================================================

@app.get("/saju/videos/")
def get_saju_videos(
    skip: int = 0,
    limit: int = 20,
    content_type: str = None,
    target_audience: str = None,
    keyword: str = None,
    db: Session = Depends(get_db)
):
    """
    사주 관련 유튜브 영상 목록 조회
    """
    try:
        videos = youtube_crud.get_saju_videos(
            db=db,
            skip=skip,
            limit=limit,
            content_type=content_type,
            target_audience=target_audience,
            keyword=keyword
        )
        
        return {
            "videos": [
                {
                    "id": video.id,
                    "video_id": video.video_id,
                    "title": video.title,
                    "description": video.description[:200] + "..." if len(video.description) > 200 else video.description,
                    "channel_title": video.channel_title,
                    "thumbnail_url": video.thumbnail_url,
                    "url": video.url,
                    "relevance_score": video.relevance_score,
                    "view_count": video.view_count,
                    "content_type": video.content_type,
                    "target_audience": video.target_audience,
                    "saju_terms": video.saju_terms,
                    "published_at": video.published_at,
                    "crawled_at": video.crawled_at.isoformat() if video.crawled_at else None
                }
                for video in videos
            ],
            "total_count": len(videos),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사주 영상 조회 중 오류 발생: {str(e)}")

@app.get("/saju/videos/popular")
def get_popular_saju_videos(limit: int = 10, db: Session = Depends(get_db)):
    """
    인기 사주 영상 조회 (조회수 기준)
    """
    try:
        videos = youtube_crud.get_popular_saju_videos(db=db, limit=limit)
        
        return {
            "popular_videos": [
                {
                    "id": video.id,
                    "video_id": video.video_id,
                    "title": video.title,
                    "channel_title": video.channel_title,
                    "thumbnail_url": video.thumbnail_url,
                    "url": video.url,
                    "view_count": video.view_count,
                    "like_count": video.like_count,
                    "relevance_score": video.relevance_score,
                    "content_type": video.content_type,
                    "published_at": video.published_at
                }
                for video in videos
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인기 영상 조회 중 오류 발생: {str(e)}")

@app.get("/saju/videos/recent")
def get_recent_saju_videos(limit: int = 10, db: Session = Depends(get_db)):
    """
    최신 사주 영상 조회
    """
    try:
        videos = youtube_crud.get_recent_saju_videos(db=db, limit=limit)
        
        return {
            "recent_videos": [
                {
                    "id": video.id,
                    "video_id": video.video_id,
                    "title": video.title,
                    "channel_title": video.channel_title,
                    "thumbnail_url": video.thumbnail_url,
                    "url": video.url,
                    "content_type": video.content_type,
                    "target_audience": video.target_audience,
                    "crawled_at": video.crawled_at.isoformat() if video.crawled_at else None
                }
                for video in videos
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최신 영상 조회 중 오류 발생: {str(e)}")

@app.get("/saju/videos/by-type/{content_type}")
def get_videos_by_content_type(content_type: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    컨텐츠 타입별 사주 영상 조회
    """
    try:
        videos = youtube_crud.get_videos_by_content_type(db=db, content_type=content_type, limit=limit)
        
        return {
            "content_type": content_type,
            "videos": [
                {
                    "id": video.id,
                    "video_id": video.video_id,
                    "title": video.title,
                    "channel_title": video.channel_title,
                    "thumbnail_url": video.thumbnail_url,
                    "url": video.url,
                    "relevance_score": video.relevance_score,
                    "saju_terms": video.saju_terms,
                    "target_audience": video.target_audience
                }
                for video in videos
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"타입별 영상 조회 중 오류 발생: {str(e)}")

@app.get("/saju/videos/search")
def search_saju_videos(q: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    사주 영상 검색
    """
    try:
        videos = youtube_crud.search_saju_videos(db=db, search_term=q, limit=limit)
        
        return {
            "query": q,
            "results": [
                {
                    "id": video.id,
                    "video_id": video.video_id,
                    "title": video.title,
                    "description": video.description[:300] + "..." if len(video.description) > 300 else video.description,
                    "channel_title": video.channel_title,
                    "thumbnail_url": video.thumbnail_url,
                    "url": video.url,
                    "relevance_score": video.relevance_score,
                    "content_type": video.content_type,
                    "saju_terms": video.saju_terms
                }
                for video in videos
            ],
            "total_results": len(videos)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"영상 검색 중 오류 발생: {str(e)}")

@app.get("/saju/videos/stats")
def get_video_statistics(db: Session = Depends(get_db)):
    """
    사주 영상 통계 정보
    """
    try:
        stats = youtube_crud.get_video_statistics(db)
        
        return {
            "statistics": {
                "total_videos": stats['total_videos'],
                "content_type_distribution": stats['content_types'],
                "target_audience_distribution": stats['target_audiences'],
                "top_channels": stats['top_channels']
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류 발생: {str(e)}")

@app.post("/admin/crawl-saju-videos")
def crawl_saju_videos(
    max_per_keyword: int = 10,
    api_key: str = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    관리자용: 사주 관련 유튜브 영상 크롤링
    """
    try:
        # 백그라운드 작업으로 크롤링 실행
        if background_tasks:
            background_tasks.add_task(
                crawl_saju_videos_task,
                db,
                max_per_keyword,
                api_key
            )
            return {
                "message": "사주 영상 크롤링이 백그라운드에서 시작되었습니다.",
                "max_per_keyword": max_per_keyword
            }
        else:
            # 직접 실행
            crawler = YouTubeSajuCrawler(api_key=api_key)
            videos = crawler.crawl_saju_videos(max_per_keyword=max_per_keyword)
            
            # 데이터베이스에 저장
            saved_videos = youtube_crud.bulk_create_saju_videos(db, videos)
            
            return {
                "message": "사주 영상 크롤링이 완료되었습니다.",
                "crawled_videos": len(videos),
                "saved_videos": len(saved_videos),
                "videos_sample": [
                    {
                        "title": video.title,
                        "channel": video.channel_title,
                        "relevance_score": video.relevance_score
                    }
                    for video in saved_videos[:5]  # 처음 5개만 미리보기
                ]
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"영상 크롤링 중 오류 발생: {str(e)}")

@app.post("/users/{user_id}/saju-videos/{video_id}/interact")
def create_video_interaction(
    user_id: int,
    video_id: int,
    interaction_type: str,
    db: Session = Depends(get_db)
):
    """
    사용자 영상 상호작용 기록 (조회, 좋아요, 공유 등)
    """
    try:
        # 유효한 상호작용 타입 확인
        valid_types = ['view', 'like', 'share', 'save']
        if interaction_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"유효하지 않은 상호작용 타입입니다. 가능한 값: {valid_types}"
            )
        
        interaction = youtube_crud.create_video_interaction(
            db=db,
            user_id=user_id,
            video_id=video_id,
            interaction_type=interaction_type
        )
        
        return {
            "message": "상호작용이 기록되었습니다.",
            "interaction_id": interaction.id,
            "interaction_type": interaction_type,
            "created_at": interaction.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상호작용 기록 중 오류 발생: {str(e)}")

@app.get("/users/{user_id}/saju-videos/history")
def get_user_video_history(user_id: int, interaction_type: str = None, db: Session = Depends(get_db)):
    """
    사용자의 영상 상호작용 히스토리 조회
    """
    try:
        interactions = youtube_crud.get_user_video_interactions(
            db=db,
            user_id=user_id,
            interaction_type=interaction_type
        )
        
        return {
            "user_id": user_id,
            "interaction_type": interaction_type,
            "interactions": [
                {
                    "id": interaction.id,
                    "video_id": interaction.video_id,
                    "interaction_type": interaction.interaction_type,
                    "created_at": interaction.created_at.isoformat(),
                    "video": {
                        "title": interaction.video.title,
                        "channel_title": interaction.video.channel_title,
                        "url": interaction.video.url
                    } if interaction.video else None
                }
                for interaction in interactions
            ],
            "total_interactions": len(interactions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상호작용 히스토리 조회 중 오류 발생: {str(e)}")

# 백그라운드 작업 함수
def crawl_saju_videos_task(db: Session, max_per_keyword: int, api_key: str = None):
    """
    백그라운드에서 실행되는 사주 영상 크롤링 작업
    """
    try:
        crawler = YouTubeSajuCrawler(api_key=api_key)
        videos = crawler.crawl_saju_videos(max_per_keyword=max_per_keyword)
        
        # 데이터베이스에 저장
        saved_videos = youtube_crud.bulk_create_saju_videos(db, videos)
        
        print(f"사주 영상 크롤링 완료: {len(videos)}개 발견, {len(saved_videos)}개 저장")
        
    except Exception as e:
        print(f"백그라운드 크롤링 오류: {str(e)}")

def learn_from_videos_task(video_ids: List[str], max_videos: int = 10):
    """
    백그라운드에서 실행되는 영상 학습 작업
    """
    try:
        analyzer = YouTubeContentAnalyzer()
        
        # 영상 정보 준비
        video_list = [{'video_id': vid} for vid in video_ids[:max_videos]]
        
        # 일괄 학습 실행
        results = analyzer.batch_learn_from_videos(video_list, max_videos)
        
        print(f"영상 학습 완료: {results['success_count']}/{results['total_videos']} 성공")
        
    except Exception as e:
        print(f"백그라운드 학습 오류: {str(e)}")

# ============================================================================
# YouTube Content Learning API Endpoints
# ============================================================================

@app.post("/admin/learn-from-videos")
def learn_from_videos(
    video_ids: List[str] = None,
    max_videos: int = 10,
    auto_find_videos: bool = False,
    background_tasks: BackgroundTasks = None
):
    """
    관리자용: YouTube 영상에서 사주 지식 학습
    """
    try:
        if auto_find_videos or not video_ids:
            # 자동으로 사주 영상 검색
            crawler = YouTubeSajuCrawler()
            videos = crawler.crawl_saju_videos(max_per_keyword=3)
            video_ids = [v.get('video_id') for v in videos if v.get('video_id')][:max_videos]
        
        if not video_ids:
            raise HTTPException(status_code=400, detail="학습할 영상 ID가 없습니다")
        
        # 백그라운드 작업으로 실행
        if background_tasks:
            background_tasks.add_task(learn_from_videos_task, video_ids, max_videos)
            return {
                "message": f"{len(video_ids)}개 영상 학습이 백그라운드에서 시작되었습니다.",
                "video_ids": video_ids[:5],  # 처음 5개만 표시
                "total_videos": len(video_ids)
            }
        else:
            # 간단한 학습 시스템 사용 (더 안정적)
            learner = SimpleYouTubeLearner("saju_knowledge_api.db")
            video_list = [{'video_id': vid, 'title': f'Video {vid}'} for vid in video_ids]
            
            results = learner.batch_learn(video_list, max_videos)
            
            return {
                "message": "영상 학습이 완료되었습니다.",
                "results": {
                    "success_count": results['success_count'],
                    "failed_count": results['failed_count'], 
                    "total_videos": results['total_videos']
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"영상 학습 중 오류 발생: {str(e)}")

@app.get("/saju/learned-knowledge/summary")
def get_learned_knowledge_summary():
    """
    학습된 사주 지식 요약 정보 조회
    """
    try:
        # 간단한 학습 시스템 사용
        learner = SimpleYouTubeLearner("saju_knowledge_api.db")
        summary = learner.get_learning_summary()
        
        return {
            "knowledge_summary": {
                "total_processed_videos": summary['total_videos'],
                "total_knowledge_sentences": summary['total_sentences'],
                "avg_relevance_score": summary['avg_relevance_score']
            },
            "top_saju_terms": [
                {"term": term, "category": cat, "frequency": freq} 
                for term, freq, cat in summary['top_terms']
            ][:10],
            "sentence_types": summary['sentence_types'],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지식 요약 조회 중 오류 발생: {str(e)}")

@app.get("/saju/learned-knowledge/search")
def search_learned_knowledge(
    query: str,
    limit: int = 20
):
    """
    학습된 사주 지식에서 검색
    """
    try:
        # 간단한 학습 시스템 사용
        learner = SimpleYouTubeLearner("saju_knowledge_api.db")
        results = learner.search_learned_knowledge(query, limit)
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지식 검색 중 오류 발생: {str(e)}")

@app.post("/predict/enhanced")
def enhanced_prediction(request: schemas.PredictionRequest):
    """
    YouTube 학습 지식이 적용된 향상된 예측
    """
    try:
        result = prediction_service.generate_prediction(
            birth_year=request.birth_year,
            birth_month=request.birth_month,
            birth_day=request.birth_day,
            birth_hour=request.birth_hour,
            name=request.name
        )
        
        return {
            "predicted_numbers": result['predicted_numbers'],
            "confidence": result['confidence'],
            "method": result['method'],
            "generated_at": result['generated_at'].isoformat(),
            "saju_elements": result['saju_analysis']['oheang'],
            "knowledge_enhancement": result.get('knowledge_enhancement', None),
            "number_analysis": result['number_scores'][:6]  # 상위 6개만
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"향상된 예측 중 오류 발생: {str(e)}")

@app.get("/saju/knowledge-status")
def get_knowledge_system_status():
    """
    YouTube 학습 지식 시스템 상태 조회
    """
    try:
        from saju_knowledge_enhancer import SajuKnowledgeEnhancer
        enhancer = SajuKnowledgeEnhancer()
        summary = enhancer.get_knowledge_summary()
        
        return {
            "system_status": "active",
            "knowledge_summary": summary,
            "last_checked": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "system_status": "inactive",
            "error": str(e),
            "last_checked": datetime.now().isoformat()
        }

@app.post("/saju/analyze-video/{video_id}")
def analyze_single_video(video_id: str):
    """
    특정 YouTube 영상 하나를 분석하고 학습
    """
    try:
        analyzer = YouTubeContentAnalyzer()
        
        # 영상 정보 가져오기 (제목 등)
        crawler = YouTubeSajuCrawler()
        video_info = {'video_id': video_id, 'title': f'Video {video_id}'}
        
        # 영상 처리
        success = analyzer.process_complete_video(video_id, video_info)
        
        if success:
            # 결과 조회
            import sqlite3
            conn = sqlite3.connect(analyzer.knowledge_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    saju_relevance_score, 
                    content_quality_score, 
                    total_word_count,
                    has_transcript,
                    has_audio_extracted
                FROM video_content 
                WHERE video_id = ?
            ''', (video_id,))
            
            row = cursor.fetchone()
            
            if row:
                cursor.execute('SELECT COUNT(*) FROM knowledge_segments WHERE video_id = ?', (video_id,))
                segments_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM saju_knowledge_patterns WHERE source_videos LIKE ?', (f'%{video_id}%',))
                patterns_count = cursor.fetchone()[0]
                
                result = {
                    "video_id": video_id,
                    "analysis_success": True,
                    "relevance_score": row[0],
                    "quality_score": row[1],
                    "word_count": row[2],
                    "has_transcript": bool(row[3]),
                    "has_audio_extracted": bool(row[4]),
                    "knowledge_segments": segments_count,
                    "learned_patterns": patterns_count
                }
            else:
                result = {"video_id": video_id, "analysis_success": False, "error": "분석 결과를 찾을 수 없습니다"}
            
            conn.close()
            return result
        else:
            return {
                "video_id": video_id,
                "analysis_success": False,
                "error": "영상 분석에 실패했습니다"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"영상 분석 중 오류 발생: {str(e)}")
