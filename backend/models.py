from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    saju_profile = relationship("SajuProfile", back_populates="owner", uselist=False)
    predictions = relationship("Prediction", back_populates="user")

class SajuProfile(Base):
    __tablename__ = "saju_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    birth_ymdh = Column(String)
    name = Column(String)
    gender = Column(String)
    oheng_json = Column(JSON)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="saju_profile")

class LottoDraw(Base):
    __tablename__ = "lotto_draws"

    draw_no = Column(Integer, primary_key=True, index=True)
    draw_date = Column(DateTime)
    n1 = Column(Integer)
    n2 = Column(Integer)
    n3 = Column(Integer)
    n4 = Column(Integer)
    n5 = Column(Integer)
    n6 = Column(Integer)
    bonus = Column(Integer)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    draw_no = Column(Integer)  # 예측 대상 회차
    predicted_numbers = Column(JSON)  # 예측된 6개 번호
    method = Column(String)  # 예측 방법 (statistical, lstm)
    confidence = Column(Float)  # 신뢰도
    saju_weights = Column(JSON)  # 사주 가중치
    is_winning = Column(Boolean, default=None)  # 당첨 여부 (추후 업데이트)
    match_count = Column(Integer, default=0)  # 일치 번호 개수
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="predictions")

class WinningHistory(Base):
    __tablename__ = "winning_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prediction_id = Column(Integer, ForeignKey("predictions.id"))
    draw_no = Column(Integer)
    match_count = Column(Integer)  # 일치한 번호 개수
    winning_numbers = Column(JSON)  # 실제 당첨 번호
    predicted_numbers = Column(JSON)  # 예측한 번호
    matched_numbers = Column(JSON)  # 일치한 번호들
    prize_rank = Column(String)  # 당첨 등수 (1등, 2등, 등외 등)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class YoutubeRule(Base):
    __tablename__ = "youtube_rules"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    weight = Column(Float)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
