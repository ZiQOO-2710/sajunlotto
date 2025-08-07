from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: Optional[str] = None
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    birth_hour: Optional[int] = None
    gender: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr

class User(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    created_at: datetime.datetime
    last_login: Optional[datetime.datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    created_at: datetime.datetime
    last_login: Optional[datetime.datetime] = None
    saju_profile: Optional['SajuProfile'] = None
    prediction_count: int = 0

    class Config:
        from_attributes = True

class SajuProfileCreate(BaseModel):
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    name: str
    gender: str # "male" or "female"

class SajuProfile(BaseModel):
    id: int
    user_id: int
    birth_ymdh: str
    name: str
    gender: str
    oheng_json: dict
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# Prediction schemas
class PredictionRequest(BaseModel):
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    name: Optional[str] = None

class NumberScore(BaseModel):
    number: int
    score: float
    element: str
    compatibility: float
    saju_explanation: str
    frequency: int
    weight: float

class PredictionResponse(BaseModel):
    predicted_numbers: List[int]
    saju_analysis: Dict
    number_scores: List[NumberScore]
    method: str
    confidence: float
    generated_at: datetime.datetime

class HistoricalAnalysisResponse(BaseModel):
    total_draws: int
    draw_range: str
    top_numbers: List[Dict[str, int]]
    element_distribution: Dict[str, Dict]
    last_5_draws: List[Dict]

class LSTMPredictionResponse(BaseModel):
    predicted_numbers: List[int]
    model_confidence: float
    training_data_count: int
    prediction_method: str
    generated_at: datetime.datetime

# User prediction history schemas
class SavePredictionRequest(BaseModel):
    user_id: int
    predicted_numbers: List[int]
    method: str
    confidence: float
    saju_weights: Optional[Dict] = None
    draw_no: Optional[int] = None

class PredictionHistory(BaseModel):
    id: int
    draw_no: Optional[int] = None
    predicted_numbers: List[int]
    method: str
    confidence: float
    is_winning: Optional[bool] = None
    match_count: int = 0
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class WinningHistoryResponse(BaseModel):
    id: int
    draw_no: int
    match_count: int
    winning_numbers: List[int]
    predicted_numbers: List[int]
    matched_numbers: List[int]
    prize_rank: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    total_predictions: int
    total_matches: int
    best_match_count: int
    avg_confidence: float
    favorite_method: str
    recent_predictions: List[PredictionHistory]
