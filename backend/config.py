from pydantic_settings import BaseSettings
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = BASE_DIR / ".env"

settings = Settings()
