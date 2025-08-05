# 사주로또 (SajuLotto)

🔮 **한국 전통 사주학과 AI가 만나는 개인 맞춤형 로또 번호 예측 시스템**

## 📋 프로젝트 개요

SajuLotto는 한국 전통 사주학(四柱學)과 현대 AI 기술을 결합하여 개인의 운세에 맞는 로또 번호를 예측하는 웹 애플리케이션입니다. 사용자의 출생 정보를 바탕으로 사주팔자를 분석하고, 오행(五行) 에너지와 LSTM 신경망을 활용해 맞춤형 번호를 제공합니다.

## ✨ 주요 기능

### 🎯 사주 분석 시스템
- 한국 음력 달력 기반 정확한 사주팔자 계산
- 오행(목화토금수) 에너지 분석
- 개인별 행운 요소 도출

### 🤖 AI 예측 모델
- LSTM 신경망 기반 로또 번호 패턴 학습
- 사주 오행 가중치 적용한 개인화 예측
- 과거 당첨 데이터 기반 확률 계산

### 📱 사용자 인터페이스
- 모바일 최적화 반응형 디자인
- 한국 로또 공식 홈페이지 스타일 참조
- 직관적인 사주 정보 입력 폼

### 📊 데이터 관리
- 사용자별 예측 기록 저장
- 당첨 결과 추적 및 분석
- 실시간 로또 당첨 번호 크롤링

## 🏗️ 기술 스택

### Backend
- **FastAPI** - 고성능 Python 웹 프레임워크
- **SQLAlchemy** - ORM 및 데이터베이스 관리
- **PostgreSQL/SQLite** - 관계형 데이터베이스
- **TensorFlow/Keras** - LSTM 신경망 모델
- **korean-lunar-calendar** - 한국 음력 계산

### Frontend
- **Next.js 14** - React 기반 프레임워크
- **TypeScript** - 정적 타입 검사
- **Tailwind CSS** - 유틸리티 기반 CSS 프레임워크
- **Lucide React** - 아이콘 라이브러리

### Data Processing
- **BeautifulSoup** - 웹 스크래핑
- **NumPy/Pandas** - 데이터 처리
- **scikit-learn** - 머신러닝 유틸리티

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd sajulotto
```

### 2. 백엔드 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 데이터베이스 초기화
```bash
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

### 4. 백엔드 서버 실행
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 프론트엔드 설정 및 실행
```bash
cd ../frontend
npm install
npm run dev
```

## 📡 API 엔드포인트

### 사용자 관리
- `POST /users/` - 새 사용자 생성
- `GET /users/{user_id}` - 사용자 정보 조회

### 사주 분석
- `POST /users/{user_id}/saju/` - 사주 프로필 생성
- `GET /users/{user_id}/saju` - 사주 프로필 조회

### 로또 예측
- `POST /users/{user_id}/predictions/` - 번호 예측 생성
- `GET /users/{user_id}/predictions/` - 예측 기록 조회

### 당첨 번호
- `GET /lotto/draws/` - 최근 당첨 번호 조회
- `POST /admin/crawl_lotto_draws/` - 당첨 번호 크롤링

## 🎲 사주-번호 매핑 시스템

오행 에너지와 로또 번호 구간 매핑:
- **목(木)**: 1-9번 (성장과 발전의 에너지)
- **화(火)**: 10-19번 (열정과 활동의 에너지)
- **토(土)**: 20-29번 (안정과 중심의 에너지)
- **금(金)**: 30-39번 (수확과 완성의 에너지)
- **수(水)**: 40-45번 (지혜와 순환의 에너지)

## 📁 프로젝트 구조

```
sajulotto/
├── backend/                 # FastAPI 백엔드
│   ├── main.py             # API 엔트리포인트
│   ├── models.py           # 데이터베이스 모델
│   ├── schemas.py          # Pydantic 스키마
│   ├── crud.py             # CRUD 연산
│   ├── saju.py             # 사주 분석 로직
│   ├── predictor.py        # AI 예측 모델
│   ├── crawler.py          # 데이터 크롤링
│   ├── database.py         # DB 연결 관리
│   └── core/               # 핵심 모듈
├── frontend/               # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/           # Next.js 앱 라우터
│   │   └── components/    # React 컴포넌트
│   ├── tailwind.config.js
│   └── package.json
├── CLAUDE.md              # 개발 가이드
└── README.md              # 프로젝트 문서
```

## 🔮 사주학 배경

사주팔자는 한국 전통 명리학으로, 출생 연월일시를 기반으로 개인의 운명과 성향을 분석하는 학문입니다. 이 프로젝트는 전통적인 사주 분석 방법론을 현대적인 확률론과 결합하여 새로운 형태의 개인화 서비스를 제공합니다.

### 사주팔자 구성 요소
- **년주(年柱)**: 출생년도의 간지
- **월주(月柱)**: 출생월의 간지  
- **일주(日柱)**: 출생일의 간지
- **시주(時柱)**: 출생시간의 간지

### 오행 이론
오행(五行)은 우주의 모든 사물이 다섯 가지 기본 요소로 구성되어 있다는 동양철학의 핵심 개념입니다.

## ⚠️ 주의사항

- 본 애플리케이션은 엔터테인먼트 목적으로 제작되었습니다
- 로또 구매는 적절한 선에서 즐기시기 바랍니다
- 예측 결과는 확률적 추정이며 당첨을 보장하지 않습니다
- 책임감 있는 복권 문화를 권장합니다

## 📄 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 기여하기

프로젝트 개선에 참여하고 싶으시다면:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의나 제안사항이 있으시면 이슈를 등록해 주세요.

---

**🔮 운명과 기술의 만남, 사주로또에서 여러분의 행운 번호를 찾아보세요! ✨**