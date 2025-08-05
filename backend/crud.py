from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import models, schemas
from saju import analyze_saju
import datetime
from typing import List, Optional

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        name=user.name,
        last_login=datetime.datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def login_user(db: Session, email: str):
    """사용자 로그인 처리 (간단 버전)"""
    user = get_user_by_email(db, email)
    if user:
        user.last_login = datetime.datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def get_user_profile(db: Session, user_id: int):
    """사용자 프로필 정보 가져오기"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    
    # 예측 횟수 계산
    prediction_count = db.query(func.count(models.Prediction.id)).filter(
        models.Prediction.user_id == user_id
    ).scalar()
    
    return {
        'user': user,
        'prediction_count': prediction_count
    }

def create_saju_profile(db: Session, user_id: int, saju_profile: schemas.SajuProfileCreate):
    saju_result = analyze_saju(
        year=saju_profile.birth_year,
        month=saju_profile.birth_month,
        day=saju_profile.birth_day,
        hour=saju_profile.birth_hour
    )

    birth_ymdh = f"{saju_profile.birth_year}-{saju_profile.birth_month:02d}-{saju_profile.birth_day:02d} {saju_profile.birth_hour:02d}:00"

    db_saju_profile = models.SajuProfile(
        user_id=user_id,
        name=saju_profile.name,
        gender=saju_profile.gender,
        birth_ymdh=birth_ymdh,
        oheng_json=saju_result['oheang']
    )
    db.add(db_saju_profile)
    db.commit()
    db.refresh(db_saju_profile)
    return db_saju_profile

def get_lotto_draw(db: Session, draw_no: int):
    return db.query(models.LottoDraw).filter(models.LottoDraw.draw_no == draw_no).first()

def create_lotto_draw(db: Session, lotto_data: dict):
    draw_date_str = lotto_data["draw_date"].replace("년", "").replace("월", "").replace("일", "").strip()
    draw_date = datetime.datetime.strptime(draw_date_str, "%Y %m %d")

    db_lotto_draw = models.LottoDraw(
        draw_no=lotto_data["draw_no"],
        draw_date=draw_date,
        n1=lotto_data["win_numbers"][0],
        n2=lotto_data["win_numbers"][1],
        n3=lotto_data["win_numbers"][2],
        n4=lotto_data["win_numbers"][3],
        n5=lotto_data["win_numbers"][4],
        n6=lotto_data["win_numbers"][5],
        bonus=lotto_data["bonus_number"]
    )
    db.add(db_lotto_draw)
    db.commit()
    db.refresh(db_lotto_draw)
    return db_lotto_draw

# 예측 히스토리 관련 함수들
def save_prediction(db: Session, user_id: int, predicted_numbers: List[int], method: str, confidence: float, saju_weights: dict = None, draw_no: int = None):
    """사용자 예측을 데이터베이스에 저장"""
    db_prediction = models.Prediction(
        user_id=user_id,
        draw_no=draw_no,
        predicted_numbers=predicted_numbers,
        method=method,
        confidence=confidence,
        saju_weights=saju_weights or {}
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_user_predictions(db: Session, user_id: int, limit: int = 20):
    """사용자의 예측 히스토리 가져오기"""
    return db.query(models.Prediction).filter(
        models.Prediction.user_id == user_id
    ).order_by(desc(models.Prediction.created_at)).limit(limit).all()

def get_user_stats(db: Session, user_id: int):
    """사용자 통계 정보"""
    predictions = db.query(models.Prediction).filter(models.Prediction.user_id == user_id).all()
    
    if not predictions:
        return {
            'total_predictions': 0,
            'total_matches': 0,
            'best_match_count': 0,
            'avg_confidence': 0.0,
            'favorite_method': 'statistical',
            'recent_predictions': []
        }
    
    total_predictions = len(predictions)
    total_matches = sum(p.match_count for p in predictions)
    best_match_count = max(p.match_count for p in predictions)
    avg_confidence = sum(p.confidence for p in predictions) / total_predictions
    
    # 가장 많이 사용한 방법
    method_counts = {}
    for p in predictions:
        method_counts[p.method] = method_counts.get(p.method, 0) + 1
    favorite_method = max(method_counts, key=method_counts.get) if method_counts else 'statistical'
    
    # 최근 예측들
    recent_predictions = sorted(predictions, key=lambda x: x.created_at, reverse=True)[:5]
    
    return {
        'total_predictions': total_predictions,
        'total_matches': total_matches,
        'best_match_count': best_match_count,
        'avg_confidence': avg_confidence,
        'favorite_method': favorite_method,
        'recent_predictions': recent_predictions
    }

def check_winning_results(db: Session):
    """예측 결과를 실제 당첨 번호와 비교하여 업데이트"""
    # 당첨 결과가 확인되지 않은 예측들 찾기
    predictions = db.query(models.Prediction).filter(
        models.Prediction.is_winning.is_(None),
        models.Prediction.draw_no.isnot(None)
    ).all()
    
    updated_count = 0
    for prediction in predictions:
        # 해당 회차의 당첨 번호 찾기
        winning_draw = db.query(models.LottoDraw).filter(
            models.LottoDraw.draw_no == prediction.draw_no
        ).first()
        
        if winning_draw:
            winning_numbers = [
                winning_draw.n1, winning_draw.n2, winning_draw.n3,
                winning_draw.n4, winning_draw.n5, winning_draw.n6
            ]
            
            predicted_numbers = prediction.predicted_numbers
            matched_numbers = list(set(winning_numbers) & set(predicted_numbers))
            match_count = len(matched_numbers)
            
            # 예측 결과 업데이트
            prediction.match_count = match_count
            prediction.is_winning = match_count >= 3  # 3개 이상 맞으면 당첨으로 간주
            
            # 당첨 히스토리 생성
            if match_count >= 3:
                prize_rank = get_prize_rank(match_count)
                winning_history = models.WinningHistory(
                    user_id=prediction.user_id,
                    prediction_id=prediction.id,
                    draw_no=prediction.draw_no,
                    match_count=match_count,
                    winning_numbers=winning_numbers,
                    predicted_numbers=predicted_numbers,
                    matched_numbers=matched_numbers,
                    prize_rank=prize_rank
                )
                db.add(winning_history)
            
            updated_count += 1
    
    if updated_count > 0:
        db.commit()
    
    return updated_count

def get_prize_rank(match_count: int) -> str:
    """일치 개수에 따른 당첨 등수 반환"""
    if match_count == 6:
        return "1등"
    elif match_count == 5:
        return "2등"  # 보너스 번호 확인은 생략
    elif match_count == 4:
        return "4등"
    elif match_count == 3:
        return "5등"
    else:
        return "등외"

def get_user_winning_history(db: Session, user_id: int):
    """사용자의 당첨 히스토리"""
    return db.query(models.WinningHistory).filter(
        models.WinningHistory.user_id == user_id
    ).order_by(desc(models.WinningHistory.created_at)).all()
