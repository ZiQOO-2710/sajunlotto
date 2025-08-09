#!/bin/bash

# YouTube 학습 시스템 설정 스크립트
echo "========================================="
echo "🎥 SajuLotto YouTube 학습 시스템 설정"
echo "========================================="

# 1. 필요한 Python 패키지 설치
echo "📦 필요한 패키지 설치 중..."
pip3 install google-api-python-client youtube-transcript-api yt-dlp

# 2. 환경변수 설정 안내
echo ""
echo "⚠️  YouTube API 키 설정이 필요합니다!"
echo "----------------------------------------"
echo "1. Google Cloud Console에서 YouTube Data API v3 활성화"
echo "2. API 키 생성"
echo "3. 아래 명령어로 환경변수 설정:"
echo ""
echo "export YOUTUBE_API_KEY='your-api-key-here'"
echo ""
echo "또는 ~/.bashrc 또는 ~/.zshrc에 추가하세요"
echo "========================================="

# 3. 데이터베이스 초기화
echo ""
echo "📊 데이터베이스 초기화 중..."
python3 - <<EOF
import sqlite3

# 크롤링 데이터베이스
conn = sqlite3.connect('saju_youtube_data.db')
cursor = conn.cursor()
print("✅ saju_youtube_data.db 생성됨")
conn.close()

# 지식 베이스
conn = sqlite3.connect('saju_knowledge_complete.db')
cursor = conn.cursor()
print("✅ saju_knowledge_complete.db 생성됨")
conn.close()
EOF

echo ""
echo "========================================="
echo "✅ 설정 완료!"
echo "========================================="
echo ""
echo "🚀 다음 단계:"
echo "1. YouTube API 키 설정"
echo "2. python3 youtube_crawler_advanced.py 실행 (크롤링)"
echo "3. python3 youtube_learning_pipeline.py 실행 (학습)"
echo "========================================="