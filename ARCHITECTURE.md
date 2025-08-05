# SajuLotto - Architecture Documentation

## 🏗️ System Overview

**SajuLotto**는 사주 분석과 머신러닝을 결합한 로또 번호 예측 앱으로, 깔끔하고 확장 가능한 아키텍처를 기반으로 설계되었습니다.

---

## 📋 Architecture Principles

### 1. Clean Architecture
- **Domain Layer**: 비즈니스 로직과 엔티티
- **Application Layer**: 유스케이스와 서비스
- **Infrastructure Layer**: 데이터베이스, 외부 API
- **Presentation Layer**: REST API, 사용자 인터페이스

### 2. SOLID Principles
- **Single Responsibility**: 각 클래스는 단일 책임
- **Open/Closed**: 확장에 열려있고 수정에 닫혀있음
- **Liskov Substitution**: 파생 클래스는 기본 클래스를 대체 가능
- **Interface Segregation**: 인터페이스 분리
- **Dependency Inversion**: 의존성 역전

### 3. Design Patterns
- **Repository Pattern**: 데이터 접근 추상화
- **Factory Pattern**: 객체 생성 캡슐화
- **Observer Pattern**: 이벤트 기반 통신
- **Strategy Pattern**: 알고리즘 교체 가능

---

## 🚀 Technology Stack

### Backend (Python)
```
FastAPI (Web Framework)
├── SQLAlchemy (ORM)
├── Pydantic (Data Validation)
├── Alembic (Database Migration)
├── Celery (Background Tasks)
├── Redis (Cache & Message Broker)
└── PostgreSQL (Primary Database)
```

### Frontend (Flutter)
```
Flutter 3.x
├── Riverpod (State Management)
├── GoRouter (Navigation)
├── Dio (HTTP Client)
├── Hive (Local Storage)
├── Flutter Bloc (State Pattern)
└── Get It (Dependency Injection)
```

### DevOps & Infrastructure
```
Docker & Docker Compose
├── GitHub Actions (CI/CD)
├── AWS ECS (Container Orchestration)
├── AWS RDS (Database)
├── AWS S3 (File Storage)
└── CloudWatch (Monitoring)
```

---

## 🔧 Backend Architecture

### Directory Structure
```
backend/
├── core/                   # 핵심 공통 기능
│   ├── exceptions.py       # 커스텀 예외
│   ├── response.py         # 표준화된 응답
│   ├── constants.py        # 상수 정의
│   └── middleware.py       # 미들웨어
├── models/                 # 데이터베이스 모델
│   ├── user.py
│   ├── saju.py
│   ├── lotto.py
│   └── prediction.py
├── schemas/                # Pydantic 스키마
│   ├── user.py
│   ├── saju.py
│   └── prediction.py
├── services/               # 비즈니스 로직
│   ├── saju_service.py
│   ├── prediction_service.py
│   ├── ml_service.py
│   └── crawler_service.py
├── repositories/           # 데이터 접근 계층
│   ├── user_repository.py
│   ├── saju_repository.py
│   └── lotto_repository.py
├── api/                    # API 엔드포인트
│   ├── v1/
│   │   ├── users.py
│   │   ├── saju.py
│   │   └── predictions.py
│   └── dependencies.py
├── ml/                     # 머신러닝 모듈
│   ├── models/
│   ├── training/
│   └── prediction/
└── utils/                  # 유틸리티 함수
    ├── validators.py
    ├── formatters.py
    └── helpers.py
```

### Data Flow
```
Client Request → API Gateway → Service Layer → Repository → Database
                     ↓              ↓
               Validation      Business Logic
                     ↓              ↓
              Response Format  Error Handling
```

---

## 📱 Frontend Architecture

### Flutter Directory Structure
```
lib/
├── core/                   # 핵심 기능
│   ├── constants/
│   ├── errors/
│   ├── network/
│   └── utils/
├── features/               # 기능별 모듈
│   ├── auth/
│   │   ├── data/
│   │   │   ├── datasources/
│   │   │   ├── models/
│   │   │   └── repositories/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── repositories/
│   │   │   └── usecases/
│   │   └── presentation/
│   │       ├── pages/
│   │       ├── widgets/
│   │       └── bloc/
│   ├── saju/
│   ├── prediction/
│   └── profile/
├── shared/                 # 공통 컴포넌트
│   ├── widgets/
│   ├── themes/
│   ├── services/
│   └── utils/
└── main.dart
```

### State Management Flow
```
UI Event → BLoC → UseCase → Repository → DataSource
    ↑                                        ↓
    └──── State Update ←── Entity ←── Model ←┘
```

---

## 🔄 Data Models

### Enhanced Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

#### Saju Profiles Table
```sql
CREATE TABLE saju_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    birth_year INTEGER NOT NULL,
    birth_month INTEGER NOT NULL,
    birth_day INTEGER NOT NULL,
    birth_hour INTEGER NOT NULL,
    birth_minute INTEGER DEFAULT 0,
    birth_timezone VARCHAR(50) DEFAULT 'Asia/Seoul',
    name VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    year_pillar VARCHAR(10),
    month_pillar VARCHAR(10),
    day_pillar VARCHAR(10),
    hour_pillar VARCHAR(10),
    wuxing_scores JSONB,
    dominant_element VARCHAR(10),
    ten_gods JSONB,
    lucky_numbers JSONB,
    personality_traits TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Predictions Table
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    draw_no INTEGER NOT NULL,
    predicted_numbers JSONB NOT NULL,
    bonus_number INTEGER,
    prediction_method VARCHAR(50) DEFAULT 'saju_ml',
    confidence_score FLOAT,
    saju_weights JSONB,
    matched_numbers INTEGER DEFAULT 0,
    bonus_matched BOOLEAN DEFAULT FALSE,
    prize_rank INTEGER,
    prize_amount FLOAT DEFAULT 0.0,
    is_processed BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🤖 ML Architecture

### Model Pipeline
```
Data Collection → Preprocessing → Feature Engineering → Model Training → Validation → Deployment
      ↓               ↓               ↓                  ↓            ↓          ↓
  Lotto Data    Normalization   Saju Features      LSTM Model   Cross-Val   TF Serving
  YouTube Data  Missing Values  Time Series        Random Forest  Metrics   Model Store
```

### Prediction Flow
```
User Input (Saju) → Feature Extraction → Model Inference → Post-processing → Final Numbers
      ↓                    ↓                   ↓              ↓              ↓
Birth Info        Wuxing Mapping      Base Predictions   Weight Application  6 Numbers + Bonus
```

---

## 🔐 Security Architecture

### Authentication & Authorization
```
JWT Token Based Authentication
├── Access Token (15 min TTL)
├── Refresh Token (7 days TTL)
├── Role-Based Access Control
└── Rate Limiting per User
```

### Data Protection
- **Encryption**: AES-256 for sensitive data
- **Hashing**: bcrypt for passwords
- **HTTPS**: TLS 1.3 for all communications
- **Input Validation**: Comprehensive data validation
- **SQL Injection Prevention**: ORM-based queries

---

## 📊 Monitoring & Observability

### Logging Strategy
```
Application Logs → Structured JSON → Log Aggregation → Analytics
     ↓                 ↓                 ↓              ↓
FastAPI Logs      Standardized      CloudWatch      Dashboards
Flutter Logs        Format          Elasticsearch   Alerts
```

### Metrics Collection
- **Performance**: Response times, throughput
- **Business**: User engagement, prediction accuracy
- **System**: CPU, memory, disk usage
- **Error**: Exception rates, failed requests

---

## 🚀 Deployment Architecture

### Container Strategy
```
Docker Multi-Stage Builds
├── Development: Hot reload, debug symbols
├── Testing: Test runner, coverage tools
└── Production: Minimal image, optimized
```

### Infrastructure as Code
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: sajulotto
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backend Tests
        run: |
          cd backend
          pip install -r requirements-dev.txt
          pytest --cov=./ --cov-report=xml
      
      - name: Run Frontend Tests
        run: |
          cd frontend
          flutter test --coverage
          
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to AWS ECS
        # Deployment steps
```

---

## 📈 Scalability Considerations

### Horizontal Scaling
- **API**: Multiple FastAPI instances behind load balancer
- **Database**: Read replicas for query distribution
- **Cache**: Redis cluster for high availability
- **ML**: Model serving with auto-scaling

### Performance Optimization
- **Database**: Proper indexing, query optimization
- **API**: Response caching, compression
- **Frontend**: Code splitting, lazy loading
- **CDN**: Static asset distribution

---

이 아키텍처는 확장 가능하고 유지보수가 용이하며, 깔끔한 코드 구조를 제공합니다. 각 구성 요소가 명확한 책임을 가지고 있어 개발과 운영이 효율적입니다.