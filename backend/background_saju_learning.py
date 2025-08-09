#!/usr/bin/env python3
"""
개선된 백그라운드 사주 학습 시스템
실제 사주 텍스트 데이터로 지속적 학습
"""

import asyncio
import sqlite3
import json
import logging
import signal
from datetime import datetime
from typing import Dict, List

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('saju_learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackgroundSajuLearner:
    """백그라운드 사주 학습 시스템"""
    
    def __init__(self):
        self.running = True
        self.knowledge_db = 'saju_knowledge_complete.db'
        
        # 실제 사주 학습 텍스트들
        self.learning_texts = [
            "갑목 일주는 큰 나무의 기운을 가진 사람으로, 리더십이 강하고 정직합니다. 봄에 태어나면 더욱 왕성한 에너지를 발휘하며, 사업가나 리더 역할에 적합합니다.",
            
            "을목 일주 사람은 작은 나무, 풀의 기운으로 섬세하고 예술적 감각이 뛰어납니다. 적응력이 좋고 부드러운 성격으로 많은 사람들과 잘 어울립니다.",
            
            "병화 일주는 태양의 기운을 가진 사람으로 밝고 활발한 성격입니다. 표현력이 좋고 사교적이며 많은 사람들에게 에너지를 주는 타입입니다.",
            
            "정화 일주는 촛불의 기운으로 따뜻하고 정이 많습니다. 예술 분야나 서비스업에 재능이 있으며 감성이 풍부한 사람입니다.",
            
            "무토 일주는 산의 기운을 가진 사람으로 든든하고 안정적입니다. 책임감이 강하고 신뢰할 수 있으며 꾸준한 노력으로 성과를 이룹니다.",
            
            "기토 일주는 들판의 흙 기운으로 포용력이 크고 따뜻한 마음을 가졌습니다. 농업이나 요리 분야에 재능이 있고 사람들을 돌보는 일에 적합합니다.",
            
            "경금 일주는 쇠의 기운을 가진 사람으로 강직하고 의지가 강합니다. 원칙을 중시하고 도전 정신이 강하며 기술 분야에 재능이 있습니다.",
            
            "신금 일주는 보석의 기운으로 세련되고 감각적입니다. 예술적 재능이 뛰어나고 미적 감각이 좋으며 패션이나 디자인 분야에 적합합니다.",
            
            "임수 일주는 바다의 기운을 가진 사람으로 포용력이 크고 지혜롭습니다. 학습 능력이 뛰어나고 연구직이나 학자의 길에 적합합니다.",
            
            "계수 일주는 이슬이나 빗물의 기운으로 섬세하고 감성적입니다. 직감력이 뛰어나고 예술 분야나 상담업에 재능이 있습니다.",
            
            "정관이 있으면 책임감이 강하고 사회적 지위를 얻을 가능성이 높습니다. 공무원이나 관리직에 적합하며 안정된 삶을 추구하는 경향이 있습니다.",
            
            "편재가 있으면 돈을 버는 능력이 뛰어납니다. 사업가적 기질이 있고 투자나 장사에 재능이 있습니다. 하지만 돈 관리에는 주의가 필요합니다.",
            
            "식신이 강하면 표현력이 좋고 창의적입니다. 예술가, 요리사, 방송인 등 자신을 표현하는 직업에 어울리며 자유로운 환경에서 능력을 발휘합니다.",
            
            "화가 너무 강하면 심장이나 혈압에 주의해야 합니다. 스트레스를 받으면 열이 오르기 쉽고 불면증이 생길 수 있으니 마음의 안정이 중요합니다.",
            
            "수가 부족하면 신장이나 방광 계통이 약할 수 있습니다. 충분한 수분 섭취와 하체 운동이 도움되며 짠 음식은 피하는 것이 좋습니다."
        ]
        
        self.stats = {
            'cycles_completed': 0,
            'total_learned': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # 시그널 핸들러
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """종료 시그널 처리"""
        logger.info("🛑 종료 신호 받음. 안전하게 종료 중...")
        self.running = False
    
    def process_text(self, text: str) -> Dict:
        """텍스트 분석 및 처리"""
        # 사주 용어 추출
        saju_terms = {}
        
        # 천간 검색
        천간 = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
        found_천간 = [term for term in 천간 if term in text]
        if found_천간:
            saju_terms['천간'] = found_천간
        
        # 오행 검색
        오행 = ['목', '화', '토', '금', '수']
        found_오행 = [term for term in 오행 if term in text]
        if found_오행:
            saju_terms['오행'] = found_오행
        
        # 십신 검색
        십신 = ['정관', '편관', '정재', '편재', '식신', '상관', '정인', '편인', '비견', '겁재']
        found_십신 = [term for term in 십신 if term in text]
        if found_십신:
            saju_terms['십신'] = found_십신
        
        # 문장 유형 분류
        sentence_type = 'general'
        if any(word in text for word in ['성격', '성향', '기질']):
            sentence_type = 'personality'
        elif any(word in text for word in ['재능', '직업', '적합']):
            sentence_type = 'interpretation'
        elif any(word in text for word in ['건강', '주의', '질병']):
            sentence_type = 'health'
        elif any(word in text for word in ['돈', '재물', '사업']):
            sentence_type = 'wealth'
        
        # 신뢰도 계산
        confidence = 0.7  # 기본
        confidence += len(saju_terms) * 0.05  # 용어 수에 따라 증가
        confidence += len(text) / 500  # 텍스트 길이에 따라 증가
        confidence = min(confidence, 1.0)
        
        return {
            'content': text,
            'saju_terms': saju_terms,
            'sentence_type': sentence_type,
            'confidence': confidence
        }
    
    def save_to_database(self, processed_data: Dict) -> bool:
        """데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.knowledge_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO saju_knowledge 
                (video_id, video_title, content, saju_terms, 
                 sentence_type, confidence, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'background_learning_' + str(datetime.now().timestamp()),
                '백그라운드 사주 학습',
                processed_data['content'],
                json.dumps(processed_data['saju_terms']),
                processed_data['sentence_type'],
                processed_data['confidence'],
                'background_learning'
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 저장 실패: {e}")
            return False
    
    def get_current_stats(self) -> Dict:
        """현재 통계 조회"""
        try:
            conn = sqlite3.connect(self.knowledge_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM saju_knowledge")
            total_knowledge = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(confidence) FROM saju_knowledge")
            avg_confidence = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT sentence_type, COUNT(*) 
                FROM saju_knowledge 
                GROUP BY sentence_type
            """)
            type_distribution = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_knowledge': total_knowledge,
                'avg_confidence': avg_confidence,
                'type_distribution': type_distribution
            }
            
        except Exception as e:
            logger.error(f"❌ 통계 조회 실패: {e}")
            return {}
    
    async def learning_cycle(self):
        """학습 사이클 실행"""
        cycle_learned = 0
        
        for text in self.learning_texts:
            if not self.running:
                break
            
            # 텍스트 처리
            processed = self.process_text(text)
            
            # 데이터베이스 저장
            if self.save_to_database(processed):
                cycle_learned += 1
                logger.info(f"  ✅ 학습: {text[:50]}... (신뢰도: {processed['confidence']:.2f})")
            
            # 짧은 지연
            await asyncio.sleep(0.1)
        
        self.stats['cycles_completed'] += 1
        self.stats['total_learned'] += cycle_learned
        
        return cycle_learned
    
    async def run(self):
        """메인 실행 루프"""
        logger.info("🚀 백그라운드 사주 학습 시스템 시작")
        
        while self.running:
            try:
                logger.info(f"\n📊 학습 사이클 #{self.stats['cycles_completed'] + 1} 시작")
                
                # 학습 사이클 실행
                learned_count = await self.learning_cycle()
                
                # 현재 통계 출력
                current_stats = self.get_current_stats()
                logger.info(f"""
                📈 학습 완료:
                - 이번 사이클: {learned_count}개
                - 총 지식: {current_stats.get('total_knowledge', 0)}개
                - 평균 신뢰도: {current_stats.get('avg_confidence', 0):.2f}
                - 유형 분포: {current_stats.get('type_distribution', {})}
                """)
                
                # 다음 사이클까지 대기 (10분)
                if self.running:
                    logger.info("⏰ 10분 후 다음 사이클 시작...")
                    await asyncio.sleep(600)  # 10분
                
            except Exception as e:
                logger.error(f"❌ 학습 사이클 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기
        
        logger.info("👋 백그라운드 학습 종료")

async def main():
    learner = BackgroundSajuLearner()
    await learner.run()

if __name__ == "__main__":
    print("""
    ========================================
    🎯 사주 백그라운드 학습 시스템
    ========================================
    전문가 수준 사주 해석 데이터 학습 중...
    종료: Ctrl+C
    
    로그: saju_learning.log
    데이터베이스: saju_knowledge_complete.db
    ========================================
    """)
    
    asyncio.run(main())