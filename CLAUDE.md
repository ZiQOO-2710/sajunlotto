# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SajuLotto is a Korean fortune-telling (Saju) based lottery number prediction application. It combines traditional Korean astrology calculations with machine learning to generate personalized lottery number predictions.

**Core Components:**
- **Backend**: FastAPI application with SQLAlchemy ORM for database operations
- **Saju Analysis**: Korean lunar calendar calculations with Five Elements (오행/WuXing) analysis  
- **ML Prediction**: LSTM neural network for lottery number prediction with saju-based weighting
- **Data Management**: PostgreSQL database with models for users, saju profiles, lottery draws, and predictions

## Architecture

The application follows a layered architecture:

```
backend/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy database models (User, SajuProfile, LottoDraw, Prediction, etc.)
├── schemas.py           # Pydantic models for API serialization
├── crud.py              # Database CRUD operations
├── saju.py              # Korean astrology calculations using korean-lunar-calendar
├── predictor.py         # LSTM model for lottery prediction with saju weighting
├── crawler.py           # Web scraper for lottery data from dhlottery.co.kr
├── database.py          # Database connection and session management
└── core/                # Enhanced core modules (exceptions, responses, constants)
```

**Key Data Flow:**
1. User provides birth information (year, month, day, hour) and personal details
2. `saju.py` calculates Four Pillars (사주팔자) and Five Elements distribution
3. `predictor.py` uses LSTM model trained on historical lottery data
4. Saju analysis weights are applied to ML predictions to personalize results
5. Final predictions stored in database with confidence scores and metadata

## Development Commands

### Backend Setup and Execution
```bash
# Setup virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Test individual components
python saju.py          # Test saju analysis with sample data
python predictor.py     # Test ML prediction model
```

### Database Operations
```bash
# Initialize database (creates tables)
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Test database connection
python -c "from database import SessionLocal; db = SessionLocal(); print('DB connected')"
```

### Data Collection
```bash
# Crawl lottery data (admin endpoint)
curl -X POST "http://localhost:8000/admin/crawl_lotto_draws/?start_draw=1000&end_draw=1100"
```

### Testing Components
```bash
# Test saju analysis
python -c "from saju import analyze_saju; print(analyze_saju(1990, 5, 15, 10))"

# Test ML prediction  
python -c "from predictor import example_lotto_data, build_and_train_model; import numpy as np; model, scaler = build_and_train_model(np.array(example_lotto_data)); print('Model trained')"
```

## Key Technical Details

### Saju Analysis System
- Uses `korean-lunar-calendar` library for accurate lunar calendar calculations
- Maps Korean celestial stems (천간) and earthly branches (지지) to Five Elements
- Generates personality traits and lucky numbers based on elemental balance
- **Core mapping tables**: `GAN_OHEANG` and `JI_OHEANG` in `saju.py`

### ML Prediction System
- LSTM model trained on historical lottery data sequences
- Applies saju-derived weights to favor numbers corresponding to user's dominant elements
- **Element-to-number mapping**: 목(1-9), 화(10-19), 토(20-29), 금(30-39), 수(40-45)
- Includes fallback logic for insufficient predictions and duplicate number handling

### Database Schema
- **User**: Basic user information with relationships to saju profiles and predictions
- **SajuProfile**: Detailed birth information and calculated saju analysis results
- **LottoDraw**: Historical lottery results with helper methods for number extraction
- **Prediction**: User predictions with confidence scores, saju weights, and result tracking
- **MLModel**: Model versioning and performance tracking

### API Endpoints
Current endpoints in `main.py`:
- `POST /users/` - Create new user
- `POST /users/{user_id}/saju/` - Create saju profile for user
- `POST /admin/crawl_lotto_draws/` - Background task to crawl lottery data

## Configuration Requirements

### Environment Setup
- Python 3.11+ with TensorFlow 2.15+
- PostgreSQL database for production (SQLite for development)
- Korean locale support for proper lunar calendar calculations

### External Dependencies
- **korean-lunar-calendar**: Korean traditional calendar calculations
- **TensorFlow/Keras**: LSTM neural network implementation  
- **BeautifulSoup**: Web scraping for lottery data
- **SQLAlchemy**: Database ORM with JSON field support for complex data structures

## Development Notes

### Saju Calculation Specifics
- Time zone defaulted to "Asia/Seoul" for accurate Korean calendar calculations
- Hour pillar (시주) calculation is mentioned as incomplete in current implementation
- Five Elements analysis includes both strength values and simple counts

### ML Model Considerations
- Current implementation uses example data; production requires real lottery history
- Saju weighting system applies multiplicative factors to element-corresponding number ranges
- Model includes sequence generation for time series prediction with configurable lookback periods

### Data Integration Points
- Saju analysis results stored as JSON in database for flexibility
- Prediction confidence scores and saju weights preserved for analysis
- Background task system implemented for data crawling operations