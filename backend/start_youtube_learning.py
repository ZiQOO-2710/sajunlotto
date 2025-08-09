#!/usr/bin/env python3
"""
YouTube 학습 시스템 백그라운드 실행 스크립트
자동으로 크롤링하고 학습을 진행합니다.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
import signal
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 테스트용 YouTube 영상 ID 리스트 (실제 사주 관련 영상들)
TEST_VIDEO_IDS = [
    # 예시 영상 ID들 (실제 사주 콘텐츠)
    "dQw4w9WgXcQ",  # 테스트용 (실제로는 사주 영상 ID로 교체)
]

class BackgroundLearningSystem:
    """백그라운드 학습 시스템"""
    
    def __init__(self):
        self.running = True
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'videos_processed': 0,
            'knowledge_entries': 0,
            'errors': 0
        }
        
        # 시그널 핸들러 설정 (graceful shutdown)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """종료 시그널 처리"""
        logger.info("🛑 종료 신호 받음. 안전하게 종료 중...")
        self.running = False
    
    async def initialize_youtube_service(self):
        """YouTube 서비스 초기화"""
        try:
            from app.services.youtube_service import YouTubeService
            
            class MockDB:
                def close(self):
                    pass
            
            self.youtube_service = YouTubeService(MockDB(), "saju_knowledge_complete.db")
            logger.info("✅ YouTube 서비스 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"❌ YouTube 서비스 초기화 실패: {e}")
            return False
    
    async def crawl_and_learn(self, video_id: str):
        """단일 영상 크롤링 및 학습"""
        try:
            logger.info(f"📺 처리 중: {video_id}")
            
            # 자막 추출
            subtitle = await self.youtube_service.extract_transcript(video_id)
            
            if subtitle:
                # 텍스트 분석 및 학습
                learned = await self.youtube_service.analyze_and_learn(subtitle)
                
                if learned:
                    self.stats['knowledge_entries'] += learned.get('learned_sentences', 0)
                    logger.info(f"  ✅ 학습 완료: {learned.get('learned_sentences', 0)}개 문장")
                else:
                    logger.warning(f"  ⚠️ 학습 가능한 내용 없음")
            else:
                logger.warning(f"  ⚠️ 자막 추출 실패")
            
            self.stats['videos_processed'] += 1
            
        except Exception as e:
            logger.error(f"❌ 처리 중 오류 ({video_id}): {e}")
            self.stats['errors'] += 1
    
    async def continuous_learning_loop(self):
        """지속적 학습 루프"""
        logger.info("🚀 백그라운드 학습 시작...")
        
        # YouTube 서비스 초기화
        if not await self.initialize_youtube_service():
            return
        
        # 학습 사이클
        cycle = 0
        while self.running:
            cycle += 1
            logger.info(f"\n📊 학습 사이클 #{cycle} 시작")
            
            # 테스트 영상들 처리
            for video_id in TEST_VIDEO_IDS:
                if not self.running:
                    break
                    
                await self.crawl_and_learn(video_id)
                
                # API 제한 방지를 위한 지연
                await asyncio.sleep(2)
            
            # 통계 저장
            self.save_statistics()
            
            # 현재 지식베이스 요약
            summary = await self.youtube_service.get_knowledge_summary()
            logger.info(f"""
            📈 현재 상태:
            - 총 지식: {summary['total_knowledge_entries']}개
            - 처리된 영상: {summary['total_videos_processed']}개
            - 평균 신뢰도: {summary['average_confidence']:.2f}
            """)
            
            # 다음 사이클까지 대기 (1시간)
            if self.running:
                logger.info("⏰ 다음 사이클까지 1시간 대기...")
                await asyncio.sleep(3600)  # 1시간
    
    def save_statistics(self):
        """통계 저장"""
        self.stats['last_update'] = datetime.now().isoformat()
        
        with open('learning_stats.json', 'w') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 통계 저장됨: {self.stats['videos_processed']}개 영상, {self.stats['knowledge_entries']}개 지식")
    
    async def run(self):
        """메인 실행"""
        try:
            await self.continuous_learning_loop()
        except Exception as e:
            logger.error(f"❌ 치명적 오류: {e}")
        finally:
            self.save_statistics()
            logger.info("👋 백그라운드 학습 종료")

async def main():
    """메인 함수"""
    system = BackgroundLearningSystem()
    await system.run()

if __name__ == "__main__":
    print("""
    ========================================
    🎥 YouTube 사주 학습 시스템
    ========================================
    백그라운드에서 실행 중...
    종료하려면 Ctrl+C를 누르세요.
    
    로그 파일: youtube_learning.log
    통계 파일: learning_stats.json
    ========================================
    """)
    
    asyncio.run(main())