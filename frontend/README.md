# SajuLotto Frontend

한국 로또 홈페이지 스타일의 모바일 최적화된 사주 기반 로또 예측 서비스 프론트엔드

## 🎨 디자인 특징

### 브랜딩
- **서비스명**: 사주로또 (SajuLotto)
- **컨셉**: "운명과 행운의 만남"
- **타겟**: 모바일 우선 설계

### 색상 체계
```css
Primary: #6366f1 (보라-파랑 그라데이션)
Secondary: #d946ef (자주색)
오행 색상:
- 목(木): #10b981 (초록)
- 화(火): #ef4444 (빨강)  
- 토(土): #f59e0b (노랑)
- 금(金): #6b7280 (회색)
- 수(水): #3b82f6 (파랑)
```

### UI 구성
1. **헤더**: 브랜드 로고 + 사용자 메뉴
2. **히어로 섹션**: 메인 CTA + 서비스 소개
3. **기능 카드**: 4개 주요 서비스 (사주분석, AI예측, 당첨관리, 운세달력)
4. **최근 당첨번호**: 시각적 볼 디스플레이
5. **통계 섹션**: 서비스 신뢰도 지표
6. **CTA 섹션**: 서비스 시작 유도
7. **푸터**: 서비스 정보 + 링크

## 🚀 실행 방법

### 1. 의존성 설치
```bash
cd frontend
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

### 3. 빌드
```bash
npm run build
npm start
```

## 📱 모바일 최적화

- **반응형 디자인**: 모바일 퍼스트 접근
- **터치 최적화**: 44px 이상 터치 타겟
- **성능 최적화**: Lazy loading, 이미지 최적화
- **PWA 준비**: 오프라인 지원 가능

## 🎯 주요 컴포넌트

### MainPage.tsx
메인 페이지 전체 레이아웃과 섹션들을 포함한 컴포넌트

### 스타일링
- **Tailwind CSS**: 유틸리티 기반 CSS 프레임워크
- **Lucide React**: 모던 아이콘 라이브러리
- **Pretendard**: 한국어 최적화 폰트

## 🔧 기술 스택

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Font**: Pretendard (한국어 최적화)

## 📂 폴더 구조

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx      # 전역 레이아웃
│   │   ├── page.tsx        # 홈페이지
│   │   └── globals.css     # 전역 스타일
│   └── components/
│       └── MainPage.tsx    # 메인 페이지 컴포넌트
├── package.json
├── tailwind.config.js      # Tailwind 설정
├── tsconfig.json          # TypeScript 설정
└── next.config.js         # Next.js 설정
```

## 🎨 디자인 시스템

### 컴포넌트 클래스
```css
.btn-primary        # 주요 버튼
.btn-secondary      # 보조 버튼  
.card               # 기본 카드
.card-hover         # 호버 효과 카드
.lotto-ball         # 로또 번호 볼
.text-gradient      # 그라데이션 텍스트
```

### 오행 스타일
```css
.fortune-wood       # 목 요소 스타일
.fortune-fire       # 화 요소 스타일
.fortune-earth      # 토 요소 스타일
.fortune-metal      # 금 요소 스타일
.fortune-water      # 수 요소 스타일
```

## 🌐 접속 정보

- **개발 서버**: http://localhost:3000
- **API 서버**: http://localhost:8000 (백엔드)

## 📋 개발 체크리스트

- [x] 모바일 최적화 레이아웃
- [x] 한국어 폰트 적용
- [x] 브랜드 색상 체계
- [x] 오행 테마 색상
- [x] 반응형 디자인
- [x] 접근성 고려
- [ ] 백엔드 API 연동
- [ ] 사용자 인증
- [ ] PWA 설정
- [ ] 성능 최적화