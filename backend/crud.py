from sqlalchemy.orm import Session
from . import models, schemas
from .saju import analyze_saju
import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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
