from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

import crud, models, schemas, crawler
from database import SessionLocal, engine
from prediction_service import prediction_service
from lstm_prediction_service import get_lstm_prediction, lstm_service

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SajuLotto API", 
    description="Korean fortune-telling based lottery prediction API",
    version="1.0.0"
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:4000"],
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
        result = prediction_service.generate_prediction(
            birth_year=request.birth_year,
            birth_month=request.birth_month,
            birth_day=request.birth_day,
            birth_hour=request.birth_hour,
            name=request.name
        )
        
        # 스키마에 맞게 응답 데이터 변환
        number_scores = [
            schemas.NumberScore(
                number=score['number'],
                score=score['score'],
                element=score['element']
            )
            for score in result['number_scores'][:10]  # 상위 10개만
        ]
        
        return schemas.PredictionResponse(
            predicted_numbers=result['predicted_numbers'],
            saju_analysis=result['saju_analysis'],
            number_scores=number_scores,
            method=result['method'],
            confidence=result['confidence'],
            generated_at=result['generated_at']
        )
        
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
