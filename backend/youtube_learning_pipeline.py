#!/usr/bin/env python3
"""
YouTube 사주 콘텐츠 자동 학습 파이프라인
크롤링된 데이터를 AI 지식베이스에 통합하고 지속적으로 학습
"""

import sqlite3
import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import numpy as np
from app.services.youtube_service import YouTubeService

class SajuLearningPipeline:
    """사주 학습 파이프라인"""
    
    def __init__(self):
        self.crawled_db = 'saju_youtube_data.db'
        self.knowledge_db = 'saju_knowledge_complete.db'
        
        # 학습 통계
        self.stats = {
            'total_processed': 0,
            'successful_integrations': 0,
            'failed_integrations': 0,
            'average_confidence': 0
        }
    
    def load_structured_data(self) -> List[Dict]:
        """크롤링된 구조화 데이터 로드"""
        conn = sqlite3.connect(self.crawled_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sld.*, 
                cv.title as video_title, 
                cv.channel_name,
                cv.view_count,
                cv.subscriber_count
            FROM structured_learning_data sld
            JOIN crawled_videos cv ON sld.video_id = cv.video_id
            WHERE sld.confidence_score > 0.6
            ORDER BY cv.view_count DESC
        """)
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'id': row[0],
                'video_id': row[1],
                'question': row[2],
                'answer': row[3],
                'saju_info': row[4],
                'interpretation': row[5],
                'confidence_score': row[6],
                'video_title': row[8],
                'channel_name': row[9],
                'view_count': row[10],
                'subscriber_count': row[11]
            })
        
        conn.close()
        return data
    
    def enhance_with_saju_terms(self, text: str) -> Dict[str, List[str]]:
        """텍스트에서 사주 전문용어 추출 및 강화"""
        found_terms = {}
        
        # 천간 매칭
        천간 = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
        found_terms['천간'] = [term for term in 천간 if term in text]
        
        # 지지 매칭
        지지 = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
        found_terms['지지'] = [term for term in 지지 if term in text]
        
        # 오행 매칭
        오행 = ['목', '화', '토', '금', '수']
        found_terms['오행'] = [term for term in 오행 if term in text]
        
        # 십신 매칭
        십신 = ['비견', '겁재', '식신', '상관', '편재', '정재', '편관', '정관', '편인', '정인']
        found_terms['십신'] = [term for term in 십신 if term in text]
        
        # 일주 패턴 매칭
        import re
        일주_pattern = r'([갑을병정무기경신임계][목화토금수])\s*일주'
        일주_matches = re.findall(일주_pattern, text)
        if 일주_matches:
            found_terms['일주'] = 일주_matches
        
        return found_terms
    
    def calculate_enhanced_confidence(self, data: Dict) -> float:
        """향상된 신뢰도 계산"""
        base_confidence = data.get('confidence_score', 0.5)
        
        # 조회수 기반 가중치
        view_weight = min(data['view_count'] / 1000000, 0.2)  # 최대 0.2
        
        # 구독자 기반 가중치
        subscriber_weight = min(data['subscriber_count'] / 100000, 0.1)  # 최대 0.1
        
        # 답변 길이 기반 가중치
        answer_length = len(data.get('answer', ''))
        length_weight = min(answer_length / 500, 0.1)  # 최대 0.1
        
        # 전문용어 포함 가중치
        terms = self.enhance_with_saju_terms(data.get('answer', ''))
        term_count = sum(len(v) for v in terms.values())
        term_weight = min(term_count * 0.02, 0.1)  # 최대 0.1
        
        # 최종 신뢰도 계산
        enhanced_confidence = base_confidence + view_weight + subscriber_weight + length_weight + term_weight
        
        return min(enhanced_confidence, 1.0)
    
    def integrate_to_knowledge_base(self, data: Dict) -> bool:
        """지식베이스에 통합"""
        try:
            conn = sqlite3.connect(self.knowledge_db)
            cursor = conn.cursor()
            
            # 사주 전문용어 추출
            saju_terms = self.enhance_with_saju_terms(data['answer'])
            
            # 문장 유형 분류
            sentence_type = self.classify_sentence_type(data['question'], data['answer'])
            
            # 향상된 신뢰도 계산
            enhanced_confidence = self.calculate_enhanced_confidence(data)
            
            # 지식베이스에 삽입
            cursor.execute("""
                INSERT INTO saju_knowledge 
                (video_id, video_title, content, saju_terms, 
                 sentence_type, confidence, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data['video_id'],
                data['video_title'],
                json.dumps({
                    'question': data['question'],
                    'answer': data['answer']
                }),
                json.dumps(saju_terms),
                sentence_type,
                enhanced_confidence,
                'youtube_crawler'
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 통합 실패: {e}")
            return False
    
    def classify_sentence_type(self, question: str, answer: str) -> str:
        """문장 유형 분류"""
        combined_text = f"{question} {answer}".lower()
        
        if any(word in combined_text for word in ['성격', '기질', '성향', '특성']):
            return 'personality'
        elif any(word in combined_text for word in ['운세', '미래', '예측', '앞으로']):
            return 'prediction'
        elif any(word in combined_text for word in ['관계', '궁합', '만남', '연애']):
            return 'relationship'
        elif any(word in combined_text for word in ['건강', '체질', '질병']):
            return 'health'
        elif any(word in combined_text for word in ['재물', '돈', '사업', '투자']):
            return 'wealth'
        elif any(word in combined_text for word in ['해석', '의미', '뜻']):
            return 'interpretation'
        else:
            return 'general'
    
    async def run_pipeline(self):
        """전체 파이프라인 실행"""
        print("🚀 사주 학습 파이프라인 시작...")
        
        # 1. 구조화된 데이터 로드
        structured_data = self.load_structured_data()
        print(f"📊 로드된 데이터: {len(structured_data)}개")
        
        # 2. 각 데이터를 지식베이스에 통합
        for data in structured_data:
            success = self.integrate_to_knowledge_base(data)
            
            if success:
                self.stats['successful_integrations'] += 1
            else:
                self.stats['failed_integrations'] += 1
            
            self.stats['total_processed'] += 1
            
            # 진행상황 표시
            if self.stats['total_processed'] % 10 == 0:
                print(f"  처리 중... {self.stats['total_processed']}/{len(structured_data)}")
        
        # 3. 통계 출력
        self.print_statistics()
    
    def print_statistics(self):
        """학습 통계 출력"""
        print(f"""
        ========================================
        📈 학습 파이프라인 완료
        ========================================
        총 처리: {self.stats['total_processed']}개
        성공: {self.stats['successful_integrations']}개
        실패: {self.stats['failed_integrations']}개
        성공률: {self.stats['successful_integrations']/max(self.stats['total_processed'], 1)*100:.1f}%
        ========================================
        """)
    
    def query_learned_knowledge(self, query: str, limit: int = 5):
        """학습된 지식 검색"""
        conn = sqlite3.connect(self.knowledge_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content, saju_terms, confidence, video_title
            FROM saju_knowledge
            WHERE content LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        
        results = cursor.fetchall()
        conn.close()
        
        print(f"\n🔍 '{query}' 검색 결과:")
        for i, (content, terms, confidence, title) in enumerate(results, 1):
            content_data = json.loads(content)
            print(f"""
            {i}. [{confidence:.2f}] {title[:50]}...
               Q: {content_data.get('question', '')[:100]}
               A: {content_data.get('answer', '')[:200]}...
            """)

class AutomaticLearningScheduler:
    """자동 학습 스케줄러"""
    
    def __init__(self):
        self.pipeline = SajuLearningPipeline()
        self.crawling_interval = 86400  # 24시간마다 크롤링
        self.learning_interval = 3600    # 1시간마다 학습
    
    async def continuous_learning(self):
        """지속적 학습 루프"""
        while True:
            try:
                # 학습 파이프라인 실행
                await self.pipeline.run_pipeline()
                
                # 대기
                await asyncio.sleep(self.learning_interval)
                
            except Exception as e:
                print(f"❌ 학습 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기

async def main():
    # 학습 파이프라인 실행
    pipeline = SajuLearningPipeline()
    await pipeline.run_pipeline()
    
    # 테스트 쿼리
    pipeline.query_learned_knowledge("갑목 일주")
    pipeline.query_learned_knowledge("재물운")
    pipeline.query_learned_knowledge("연애운")

if __name__ == "__main__":
    asyncio.run(main())