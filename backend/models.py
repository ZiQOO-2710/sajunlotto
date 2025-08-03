from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    saju_profile = relationship("SajuProfile", back_populates="owner")

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
    draw_no = Column(Integer)
    numbers_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class YoutubeRule(Base):
    __tablename__ = "youtube_rules"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    weight = Column(Float)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
