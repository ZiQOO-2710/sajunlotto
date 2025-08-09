# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SajuLotto is a Korean fortune-telling (Saju) based lottery number prediction application that combines traditional Korean astrology with machine learning to generate personalized lottery number predictions.

**Core Technologies:**
- **Backend**: FastAPI with SQLAlchemy ORM, running on port 4001 (temporary server) or 8000 (main)
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS, running on port 4003
- **ML/AI**: LSTM neural network with TensorFlow, YouTube learning pipeline for knowledge accumulation
- **Database**: SQLite for development, PostgreSQL for production

## Architecture

### Backend Structure
```
backend/
├── main.py              # FastAPI main application (port 8000)
├── simple_server.py     # Temporary test server for UI development (port 4001)
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic models for API validation
├── crud.py              # Database CRUD operations
├── saju.py              # Korean astrology calculations using korean-lunar-calendar
├── predictor.py         # LSTM model for lottery prediction with saju weighting
├── crawler.py           # Web scraper for lottery data from dhlottery.co.kr
├── database.py          # Database connection and session management
├── app/                 # Enhanced AI system modules
│   ├── api/            # AI-enhanced API routes
│   └── services/       # AI persona and YouTube learning services
└── core/               # Core modules (exceptions, responses, constants)
```

### Frontend Structure
```
frontend/
├── src/
│   ├── app/            # Next.js app router
│   └── components/     # React components
│       ├── AIPrediction.tsx     # Main AI prediction interface (mobile-optimized)
│       ├── MainPage.tsx          # Landing page with lottery info
│       └── SajuPillars.tsx      # Saju chart visualization
```

## Development Commands

### Quick Start (Current Development Setup)
```bash
# Backend - Temporary test server (currently active)
cd backend
python3 simple_server.py  # Runs on port 4001

# Frontend
cd frontend
npm run dev  # Runs on port 4003
```

### Main Backend Server
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run main FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run AI-enhanced server
python run_ai_server.py  # Port 8000 with AI capabilities
```

### Database Operations
```bash
# Initialize database
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Check YouTube learning status
python check_learning_status.py

# Start YouTube learning pipeline
python start_youtube_learning.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev     # Development server on port 4003
npm run build   # Production build
npm run lint    # Run linter
```

### Testing and Debugging
```bash
# Test saju analysis
python -c "from saju import analyze_saju; print(analyze_saju(1990, 5, 15, 10))"

# Test server health
curl http://localhost:4001/health  # Temporary server
curl http://localhost:8000/health  # Main server

# Test AI analysis endpoint
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"테스트","birth_year":"1990","birth_month":"5","birth_day":"15","birth_hour":"10","calendar_type":"solar"}' \
  http://localhost:4001/api/v1/ai/analyze
```

## Key Technical Details

### Saju System
- **Lunar Calendar**: Uses `korean-lunar-calendar` for accurate Korean lunar calculations
- **Five Elements Mapping**: 
  - 목(Wood): 1-9
  - 화(Fire): 10-19
  - 토(Earth): 20-29
  - 금(Metal): 30-39
  - 수(Water): 40-45
- **Four Pillars**: Year, Month, Day, Hour pillars (년주, 월주, 일주, 시주)

### AI Enhancement Features
- **YouTube Learning Pipeline**: Continuously learns from Korean saju/fortune-telling videos
- **Knowledge Database**: `saju_knowledge_complete.db` with 1400+ learned entries
- **AI Persona System**: Mystical fortune-teller personality for user interactions
- **Today's Fortune**: Detailed 200+ character fortunes for overall, wealth, love, and health

### Mobile Optimization
- **Mobile-First Design**: All UI components optimized for touch interfaces
- **Responsive Layout**: Vertical stacking, compact components (12x12px pillars)
- **Touch-Friendly**: Large buttons (py-4), increased input fields (py-3)
- **Removed Desktop Elements**: No desktop-specific grids or layouts

### API Response Structure
```json
{
  "analysis": {
    "greeting": "AI greeting message",
    "core_analysis": "Saju analysis summary",
    "personality_insights": ["insight1", "insight2"],
    "today_fortune": {
      "overall": "200+ character fortune",
      "wealth": "200+ character fortune",
      "love": "200+ character fortune",
      "health": "200+ character fortune"
    },
    "saju_chart": {
      "year_pillar": {"gan": "경", "ji": "오", "element": "금"},
      "month_pillar": {...},
      "day_pillar": {...},
      "hour_pillar": {...},
      "five_elements": {"목": 15, "화": 25, ...}
    }
  },
  "prediction": {
    "numbers": [7, 14, 21, 28, 35, 42],
    "bonus": 6,
    "ai_statement": "Prediction message"
  }
}
```

## Configuration Requirements

### Port Configuration
- **Backend Temporary Server**: 4001 (simple_server.py)
- **Backend Main Server**: 8000 (main.py)
- **Frontend Dev Server**: 4003 (Next.js)

### Environment Dependencies
- Python 3.11+ with TensorFlow 2.15+
- Node.js 18+ for frontend
- SQLite for development (automatic)
- Korean locale support for lunar calendar

## Development Notes

### Current Active Configuration
- Backend runs on port 4001 using `simple_server.py` for rapid UI development
- Frontend runs on port 4003 with mobile-optimized interface
- Direct API communication between frontend (4003) and backend (4001)

### Saju Calculation Specifics
- Time zone: "Asia/Seoul" for accurate Korean calendar
- Solar/Lunar calendar support with automatic conversion
- Hour pillar calculation may be incomplete in current implementation

### YouTube Learning System
- Background process for continuous knowledge acquisition
- Stores learned content in `saju_knowledge_complete.db`
- Can be monitored via `check_learning_status.py`

### Data Integration
- Saju analysis results stored as JSON for flexibility
- Background crawling for lottery data from dhlottery.co.kr
- Prediction confidence scores preserved for analysis