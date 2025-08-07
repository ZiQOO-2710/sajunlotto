#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
예측 서비스 모듈
로또 번호 예측 관련 로직을 제공합니다.
"""

import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from database import SessionLocal
from models import LottoDraw
from saju import analyze_saju
from saju_knowledge_enhancer import SajuKnowledgeEnhancer


class PredictionService:
    """로또 예측 서비스 클래스"""
    
    def __init__(self):
        self.oheang_ranges = {
            '목': {'range': (1, 9), 'weight': 1.0},
            '화': {'range': (10, 19), 'weight': 1.0},
            '토': {'range': (20, 29), 'weight': 1.0},
            '금': {'range': (30, 39), 'weight': 1.0},
            '수': {'range': (40, 45), 'weight': 1.0}
        }
        # YouTube 학습 지식 향상 시스템 초기화
        try:
            self.knowledge_enhancer = SajuKnowledgeEnhancer()
            self.use_knowledge_enhancement = True
        except Exception as e:
            print(f"[WARNING] 지식 향상 시스템 초기화 실패: {e}")
            self.knowledge_enhancer = None
            self.use_knowledge_enhancement = False
    
    def load_historical_data(self) -> Tuple[List[LottoDraw], Dict]:
        """데이터베이스에서 로또 데이터 로드 및 기본 분석"""
        db = SessionLocal()
        try:
            lotto_draws = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).all()
            
            if not lotto_draws:
                raise ValueError("데이터베이스에 로또 데이터가 없습니다.")
            
            # 기본 통계 생성
            stats = {
                'total_draws': len(lotto_draws),
                'draw_range': f"{lotto_draws[0].draw_no}회 ~ {lotto_draws[-1].draw_no}회",
                'latest_draws': lotto_draws[-5:] if len(lotto_draws) >= 5 else lotto_draws
            }
            
            return lotto_draws, stats
            
        finally:
            db.close()
    
    def analyze_number_patterns(self, lotto_draws: List[LottoDraw]) -> Dict:
        """번호 패턴 분석"""
        if not lotto_draws:
            return {}
        
        # 모든 번호 수집
        all_numbers = []
        for draw in lotto_draws:
            all_numbers.extend([draw.n1, draw.n2, draw.n3, draw.n4, draw.n5, draw.n6])
        
        # 번호별 출현 빈도
        number_freq = {}
        for num in range(1, 46):
            number_freq[num] = all_numbers.count(num)
        
        # 가장 자주 나온 번호 top 15
        top_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)[:15]
        
        # 오행별 분석
        element_analysis = {}
        for element, info in self.oheang_ranges.items():
            start, end = info['range']
            count = sum(1 for num in all_numbers if start <= num <= end)
            element_analysis[element] = {
                'range': f"{start}-{end}",
                'count': count,
                'percentage': (count / len(all_numbers)) * 100 if all_numbers else 0
            }
        
        return {
            'top_numbers': [{'number': num, 'frequency': freq} for num, freq in top_numbers],
            'element_distribution': element_analysis,
            'total_numbers_analyzed': len(all_numbers)
        }
    
    def calculate_saju_weights(self, saju_oheang: Dict[str, int]) -> Dict[str, float]:
        """사주 오행 분포에 따른 가중치 계산"""
        weights = {}
        max_count = max(saju_oheang.values()) if saju_oheang.values() else 1
        
        for element, count in saju_oheang.items():
            if count > 0:
                # 해당 오행이 강할수록 가중치 증가 (최대 1.5배)
                weight_boost = 1.0 + (count / max_count) * 0.5
                weights[element] = weight_boost
            else:
                weights[element] = 1.0
        
        return weights
    
    def predict_with_saju_weighting(self, 
                                  top_numbers: List[Tuple[int, int]], 
                                  saju_oheang: Dict[str, int]) -> Dict:
        """사주 기반 가중치 예측"""
        
        # 사주 가중치 계산
        element_weights = self.calculate_saju_weights(saju_oheang)
        
        # 번호별 점수 계산
        number_scores = []
        max_score = 0
        
        for num, freq in top_numbers:
            base_score = freq  # 기본 점수는 출현 빈도
            element = self._get_number_element(num)
            weight = element_weights.get(element, 1.0)
            weighted_score = base_score * weight
            max_score = max(max_score, weighted_score)
            
            number_scores.append({
                'number': num,
                'score': weighted_score,
                'element': element,
                'frequency': freq,
                'weight': weight
            })
        
        # 적합도 계산 및 사주 풀이 추가
        for score_info in number_scores:
            compatibility = min(100, (score_info['score'] / max_score * 100)) if max_score > 0 else 50
            score_info['compatibility'] = round(compatibility, 1)
            score_info['saju_explanation'] = self._generate_saju_explanation(
                score_info['number'], score_info['element'], saju_oheang, score_info['weight']
            )
        
        # 점수 순으로 정렬
        number_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # 상위 7개 번호 선택 (중복 제거)
        predicted_numbers = []
        used_numbers = set()
        
        for score_info in number_scores:
            num = score_info['number']
            if num not in used_numbers and 1 <= num <= 45:
                predicted_numbers.append(num)
                used_numbers.add(num)
                if len(predicted_numbers) == 7:
                    break
        
        # 7개가 안되면 추가 번호 선택
        while len(predicted_numbers) < 7:
            for num in range(1, 46):
                if num not in used_numbers:
                    predicted_numbers.append(num)
                    used_numbers.add(num)
                    if len(predicted_numbers) == 7:
                        break
        
        predicted_numbers.sort()
        
        # 신뢰도 계산 (상위 7개 번호의 평균 점수 기준)
        top_7_scores = [score['score'] for score in number_scores[:7]]
        confidence = np.mean(top_7_scores) / max_score if max_score > 0 else 0.5
        
        return {
            'predicted_numbers': predicted_numbers,
            'number_scores': number_scores[:15],  # 상위 15개만 반환
            'element_weights': element_weights,
            'confidence': min(confidence, 1.0)
        }
    
    def _get_number_element(self, number: int) -> str:
        """번호에 해당하는 오행 요소 반환"""
        for element, info in self.oheang_ranges.items():
            start, end = info['range']
            if start <= number <= end:
                return element
        return '기타'
    
    def get_saju_analysis(self, birth_year: int, birth_month: int, 
                         birth_day: int, birth_hour: int) -> Dict:
        """사주 분석 수행"""
        try:
            saju_result = analyze_saju(birth_year, birth_month, birth_day, birth_hour)
            
            # oheang 데이터 추출 및 검증
            if isinstance(saju_result, dict) and 'oheang' in saju_result:
                oheang_data = saju_result['oheang']
                if isinstance(oheang_data, dict):
                    # 모든 오행 요소가 있는지 확인하고 없으면 0으로 초기화
                    complete_oheang = {}
                    for element in ['목', '화', '토', '금', '수']:
                        complete_oheang[element] = oheang_data.get(element, 0)
                    
                    return {
                        'oheang': complete_oheang,
                        'raw_result': saju_result
                    }
            
            # 기본값 반환
            return {
                'oheang': {'목': 1, '화': 1, '토': 1, '금': 1, '수': 1},
                'raw_result': saju_result,
                'warning': '사주 분석 결과를 파싱할 수 없어 기본값을 사용합니다.'
            }
            
        except Exception as e:
            # 에러 발생시 기본값 반환
            return {
                'oheang': {'목': 1, '화': 1, '토': 1, '금': 1, '수': 1},
                'raw_result': {},
                'error': f'사주 분석 중 오류 발생: {str(e)}'
            }
    
    def generate_prediction(self, birth_year: int, birth_month: int, 
                          birth_day: int, birth_hour: int, 
                          name: Optional[str] = None) -> Dict:
        """종합 예측 생성 (YouTube 학습 지식 통합)"""
        try:
            # 1. 히스토리컬 데이터 로드
            lotto_draws, stats = self.load_historical_data()
            
            # 2. 패턴 분석
            pattern_analysis = self.analyze_number_patterns(lotto_draws)
            
            # 3. 기본 사주 분석
            saju_analysis = self.get_saju_analysis(birth_year, birth_month, birth_day, birth_hour)
            
            # 4. YouTube 학습 지식 적용 (가능한 경우)
            knowledge_insights = None
            enhanced_saju_analysis = saju_analysis
            
            if self.use_knowledge_enhancement and self.knowledge_enhancer:
                try:
                    # 학습된 사주 지식 추출
                    knowledge_insights = self.knowledge_enhancer.get_learned_saju_insights(
                        birth_year, birth_month, birth_day
                    )
                    
                    # 사주 분석에 지식 적용
                    enhanced_saju_analysis = self.knowledge_enhancer.enhance_prediction_weights(
                        saju_analysis, knowledge_insights
                    )
                    
                    print(f"[KNOWLEDGE] YouTube 학습 지식 적용됨: {len(knowledge_insights.get('relevant_knowledge', []))}개 지식 활용")
                    
                except Exception as e:
                    print(f"[WARNING] 지식 향상 적용 실패: {e}")
            
            # 5. 예측 수행 (향상된 사주 분석 사용)
            top_numbers = [(item['number'], item['frequency']) 
                          for item in pattern_analysis['top_numbers']]
            
            prediction_result = self.predict_with_saju_weighting(
                top_numbers, enhanced_saju_analysis['oheang']
            )
            
            # 6. 지식 향상 정보를 결과에 추가
            result = {
                'predicted_numbers': prediction_result['predicted_numbers'],
                'saju_analysis': enhanced_saju_analysis,
                'number_scores': prediction_result['number_scores'],
                'historical_stats': stats,
                'pattern_analysis': pattern_analysis,
                'method': 'saju_weighted_frequency_with_youtube_knowledge' if knowledge_insights else 'saju_weighted_frequency',
                'confidence': prediction_result['confidence'],
                'generated_at': datetime.now()
            }
            
            # YouTube 지식 정보 추가
            if knowledge_insights:
                result['knowledge_enhancement'] = {
                    'insights_applied': len(knowledge_insights.get('relevant_knowledge', [])),
                    'element_adjustments': knowledge_insights.get('element_adjustments', {}),
                    'confidence_boost': knowledge_insights.get('confidence_modifiers', {}).get('base_confidence_adjustment', 0.0),
                    'recommendations': knowledge_insights.get('additional_recommendations', []),
                    'knowledge_source': 'YouTube 사주 영상 학습 데이터'
                }
                
                # 신뢰도 향상 적용
                confidence_boost = knowledge_insights.get('confidence_modifiers', {}).get('base_confidence_adjustment', 0.0)
                if confidence_boost > 0:
                    result['confidence'] = min(1.0, result['confidence'] + confidence_boost)
            
            return result
            
        except Exception as e:
            raise ValueError(f"예측 생성 중 오류 발생: {str(e)}")
    
    def _generate_saju_explanation(self, number: int, element: str, 
                                 saju_oheang: Dict[str, int], weight: float) -> str:
        """번호별 사주 기반 풀이 생성"""
        
        # 단순 한글 설명 (인코딩 안전)
        element_names = {
            '목': '나무',
            '화': '불', 
            '토': '흙',
            '금': '금속',
            '수': '물'
        }
        
        element_traits = {
            '목': '성장운',
            '화': '열정운', 
            '토': '안정운',
            '금': '결단운',
            '수': '지혜운'
        }
        
        # 사용자의 해당 원소 강도
        user_element_count = saju_oheang.get(element, 0)
        
        # 원소 정보
        elem_name = element_names.get(element, element)
        trait = element_traits.get(element, '특별운')
        
        # 간단한 설명
        if user_element_count >= 2:
            reason = f"{elem_name} 기운이 강함"
        elif user_element_count >= 1:
            reason = f"{elem_name} 기운과 조화"
        else:
            reason = f"{elem_name} 기운 보완"
        
        explanation = f"{trait}의 {number}번 - {reason}"
        return explanation


# 전역 예측 서비스 인스턴스
prediction_service = PredictionService()# Force reload
# Force reload 2025년 08월  6일 수 오후  2:52:32
