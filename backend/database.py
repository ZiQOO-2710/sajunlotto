from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스 사용 (개발용)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sajulotto.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # SQL 쿼리 로깅 (개발시에만 True)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 데이터베이스 테이블 생성 함수
def create_tables():
    Base.metadata.create_all(bind=engine)

# 데이터베이스 세션 의존성
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()