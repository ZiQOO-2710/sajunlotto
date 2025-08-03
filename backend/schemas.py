from pydantic import BaseModel
import datetime

class UserCreate(BaseModel):
    email: str

class User(BaseModel):
    id: int
    email: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True

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
        orm_mode = True
