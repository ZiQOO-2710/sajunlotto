#!/usr/bin/env python3
"""
사주 지식 기반 예측 시스템 향상 모듈
YouTube에서 학습한 사주 지식을 활용하여 예측 정확도를 높입니다.
"""

import sqlite3
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from simple_youtube_learner import SimpleYouTubeLearner

class SajuKnowledgeEnhancer:
    """YouTube에서 학습한 사주 지식으로 예측 시스템을 향상시키는 클래스"""
    
    def __init__(self, knowledge_db_path: str = "saju_knowledge_api.db"):
        self.knowledge_db_path = knowledge_db_path
        self.learner = SimpleYouTubeLearner(knowledge_db_path)
        
        # 사주 요소와 숫자 범위 매핑 (기존 시스템과 동일)
        self.element_ranges = {
            '목': (1, 9),
            '화': (10, 19), 
            '토': (20, 29),
            '금': (30, 39),
            '수': (40, 45)
        }
        
        print(f"[INIT] 사주 지식 향상 시스템 초기화 완료 (DB: {knowledge_db_path})")
    
    def get_learned_saju_insights(self, birth_year: int, birth_month: int, birth_day: int) -> Dict:
        """
        생년월일을 기반으로 학습된 사주 지식에서 관련 정보 추출
        """
        insights = {
            'relevant_knowledge': [],
            'element_adjustments': {},
            'confidence_modifiers': {},
            'additional_recommendations': []
        }
        
        try:
            # 1. 천간/지지 관련 지식 검색
            birth_elements = self._get_birth_elements(birth_year, birth_month, birth_day)
            
            for element_type, element_value in birth_elements.items():
                if element_value:
                    # 각 요소에 대한 학습된 지식 검색
                    knowledge_results = self.learner.search_learned_knowledge(element_value, 5)
                    
                    for result in knowledge_results:
                        insight = {
                            'source_element': element_value,
                            'element_type': element_type,
                            'knowledge_text': result['text'],
                            'knowledge_type': result['type'],
                            'source_video': result.get('video_title', 'Unknown'),
                            'relevance': self._calculate_knowledge_relevance(result['text'], birth_elements)
                        }
                        insights['relevant_knowledge'].append(insight)
            
            # 2. 오행 균형 분석 및 조정
            element_adjustments = self._analyze_element_balance_from_knowledge(insights['relevant_knowledge'])
            insights['element_adjustments'] = element_adjustments
            
            # 3. 신뢰도 수정자 계산
            insights['confidence_modifiers'] = self._calculate_confidence_modifiers(insights['relevant_knowledge'])
            
            # 4. 추가 권장사항
            insights['additional_recommendations'] = self._generate_additional_recommendations(insights['relevant_knowledge'])
            
        except Exception as e:
            print(f"[ERROR] 사주 지식 추출 실패: {e}")
        
        return insights
    
    def _get_birth_elements(self, birth_year: int, birth_month: int, birth_day: int) -> Dict:
        """생년월일로부터 기본 사주 요소 추출"""
        try:
            # 간단한 사주 요소 매핑 (실제로는 더 복잡한 계산 필요)
            year_gan = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'][birth_year % 10]
            year_ji = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'][birth_year % 12]
            month_ji = ['인', '묘', '진', '사', '오', '미', '신', '유', '술', '해', '자', '축'][birth_month - 1]
            
            return {
                'year_gan': year_gan,
                'year_ji': year_ji,
                'month_ji': month_ji
            }
        except:
            return {'year_gan': None, 'year_ji': None, 'month_ji': None}
    
    def _calculate_knowledge_relevance(self, knowledge_text: str, birth_elements: Dict) -> float:
        """지식 텍스트와 출생 요소의 관련성 계산"""
        relevance_score = 0.0
        
        # 출생 요소가 지식 텍스트에 얼마나 언급되는지 확인
        for element in birth_elements.values():
            if element and element in knowledge_text:
                relevance_score += 0.3
        
        # 성격분석, 예측 관련 키워드 추가 점수
        high_value_keywords = ['성격', '특징', '운세', '예측', '궁합', '재물', '직업']
        for keyword in high_value_keywords:
            if keyword in knowledge_text:
                relevance_score += 0.1
        
        return min(relevance_score, 1.0)
    
    def _analyze_element_balance_from_knowledge(self, relevant_knowledge: List[Dict]) -> Dict:
        """학습된 지식을 바탕으로 오행 균형 조정값 계산"""
        adjustments = {}
        
        for knowledge in relevant_knowledge:
            text = knowledge['knowledge_text'].lower()
            
            # 각 오행에 대한 언급과 긍정/부정적 맥락 분석
            for element_kor in ['목', '화', '토', '금', '수']:
                if element_kor in text:
                    # 긍정적 맥락: 강화 필요
                    positive_words = ['왕성', '강함', '좋', '발달', '성장', '번영']
                    negative_words = ['부족', '약함', '나쁨', '억제', '문제', '결핍']
                    
                    adjustment = 0.0
                    for word in positive_words:
                        if word in text:
                            adjustment += 0.1
                    
                    for word in negative_words:
                        if word in text:
                            adjustment -= 0.1
                    
                    # 기존 조정값에 누적
                    if element_kor in adjustments:
                        adjustments[element_kor] += adjustment
                    else:
                        adjustments[element_kor] = adjustment
        
        # 조정값을 -0.5 ~ +0.5 범위로 정규화
        for element in adjustments:
            adjustments[element] = max(-0.5, min(0.5, adjustments[element]))
        
        return adjustments
    
    def _calculate_confidence_modifiers(self, relevant_knowledge: List[Dict]) -> Dict:
        """학습된 지식을 바탕으로 신뢰도 수정자 계산"""
        modifiers = {
            'base_confidence_adjustment': 0.0,
            'element_specific_confidence': {}
        }
        
        # 관련 지식의 양과 품질에 따라 신뢰도 조정
        knowledge_count = len(relevant_knowledge)
        avg_relevance = sum(k['relevance'] for k in relevant_knowledge) / max(knowledge_count, 1)
        
        # 많은 관련 지식과 높은 관련성 = 신뢰도 향상
        if knowledge_count >= 3 and avg_relevance >= 0.5:
            modifiers['base_confidence_adjustment'] = 0.1
        elif knowledge_count >= 1 and avg_relevance >= 0.3:
            modifiers['base_confidence_adjustment'] = 0.05
        
        return modifiers
    
    def _generate_additional_recommendations(self, relevant_knowledge: List[Dict]) -> List[str]:
        """학습된 지식을 바탕으로 추가 권장사항 생성"""
        recommendations = []
        
        # 지식 유형별 권장사항
        knowledge_types = {}
        for knowledge in relevant_knowledge:
            k_type = knowledge['knowledge_type']
            if k_type not in knowledge_types:
                knowledge_types[k_type] = []
            knowledge_types[k_type].append(knowledge['knowledge_text'])
        
        if '성격분석' in knowledge_types:
            recommendations.append("성격 분석 결과를 바탕으로 번호 선택 방식을 개인화했습니다.")
        
        if '예측' in knowledge_types:
            recommendations.append("운세 예측 지식을 활용하여 시기적 요소를 고려했습니다.")
        
        if '관계' in knowledge_types:
            recommendations.append("인간관계 궁합을 고려하여 조화로운 번호 조합을 선택했습니다.")
        
        return recommendations
    
    def enhance_prediction_weights(self, saju_analysis: Dict, insights: Dict) -> Dict:
        """
        사주 분석 결과에 학습된 지식을 적용하여 가중치 향상
        """
        enhanced_weights = saju_analysis.copy()
        
        try:
            # 1. 오행 균형 조정 적용
            element_adjustments = insights.get('element_adjustments', {})
            oheang = enhanced_weights.get('oheang', {})
            
            for element_kor, adjustment in element_adjustments.items():
                if element_kor in oheang:
                    # 기존 오행값에 조정값 적용
                    current_value = oheang[element_kor]
                    adjusted_value = max(0, current_value + adjustment)
                    enhanced_weights['oheang'][element_kor] = adjusted_value
            
            # 2. 신뢰도 수정자 적용
            confidence_modifiers = insights.get('confidence_modifiers', {})
            base_adjustment = confidence_modifiers.get('base_confidence_adjustment', 0.0)
            
            # 새로운 필드 추가
            enhanced_weights['knowledge_enhancement'] = {
                'applied_adjustments': element_adjustments,
                'confidence_boost': base_adjustment,
                'knowledge_sources_count': len(insights.get('relevant_knowledge', [])),
                'recommendations': insights.get('additional_recommendations', [])
            }
            
        except Exception as e:
            print(f"[ERROR] 가중치 향상 실패: {e}")
        
        return enhanced_weights
    
    def get_knowledge_summary(self) -> Dict:
        """현재 학습된 지식 요약"""
        summary = self.learner.get_learning_summary()
        
        # top_terms 형태 변환 (tuple을 dict으로)
        top_terms_dict = {}
        if summary['top_terms']:
            for term, freq, cat in summary['top_terms'][:10]:
                top_terms_dict[term] = {'frequency': freq, 'category': cat}
        
        return {
            'total_videos_processed': summary['total_videos'],
            'total_knowledge_sentences': summary['total_sentences'],
            'avg_relevance_score': summary['avg_relevance_score'],
            'top_saju_terms': top_terms_dict,
            'sentence_types_distribution': summary['sentence_types'],
            'knowledge_db_path': self.knowledge_db_path,
            'last_updated': datetime.now().isoformat()
        }
    
    def search_relevant_knowledge(self, query: str, limit: int = 10) -> List[Dict]:
        """특정 쿼리에 대한 관련 지식 검색"""
        return self.learner.search_learned_knowledge(query, limit)

# 테스트 함수
def test_knowledge_enhancer():
    print("[TEST] 사주 지식 향상 시스템 테스트")
    
    enhancer = SajuKnowledgeEnhancer()
    
    # 테스트용 생년월일
    birth_year, birth_month, birth_day = 1990, 5, 15
    
    # 지식 추출
    insights = enhancer.get_learned_saju_insights(birth_year, birth_month, birth_day)
    
    print(f"[INSIGHTS] 관련 지식: {len(insights['relevant_knowledge'])}개")
    print(f"[INSIGHTS] 오행 조정: {insights['element_adjustments']}")
    print(f"[INSIGHTS] 신뢰도 수정: {insights['confidence_modifiers']}")
    print(f"[INSIGHTS] 추가 권장: {len(insights['additional_recommendations'])}개")
    
    # 지식 요약
    summary = enhancer.get_knowledge_summary()
    print(f"[SUMMARY] 학습된 영상: {summary['total_videos_processed']}개")
    print(f"[SUMMARY] 지식 문장: {summary['total_knowledge_sentences']}개")
    
    return True

if __name__ == "__main__":
    test_knowledge_enhancer()