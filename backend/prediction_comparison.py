#!/usr/bin/env python3
"""
통계 기반 예측 vs LSTM 예측 성능 비교 도구
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Any

from prediction_service import prediction_service
from lstm_prediction_service import get_lstm_prediction

def compare_single_prediction(birth_year: int, birth_month: int, birth_day: int, birth_hour: int, name: str = "테스트") -> Dict[str, Any]:
    """단일 예측 비교"""
    try:
        print(f"\n{'='*60}")
        print(f"예측 비교: {name} ({birth_year}-{birth_month}-{birth_day} {birth_hour}시)")
        print(f"{'='*60}")
        
        # 1. 통계 기반 예측
        print("\n[1] 통계 기반 예측 실행 중...")
        statistical_result = prediction_service.generate_prediction(
            birth_year=birth_year,
            birth_month=birth_month,
            birth_day=birth_day,
            birth_hour=birth_hour,
            name=name
        )
        
        print(f"통계 예측 번호: {statistical_result['predicted_numbers']}")
        print(f"통계 신뢰도: {statistical_result['confidence']:.2%}")
        print(f"통계 방법: {statistical_result['method']}")
        
        # 2. LSTM 기반 예측
        print("\n[2] LSTM 기반 예측 실행 중...")
        lstm_result = get_lstm_prediction(
            birth_year=birth_year,
            birth_month=birth_month,
            birth_day=birth_day,
            birth_hour=birth_hour,
            name=name
        )
        
        print(f"LSTM 예측 번호: {lstm_result['predicted_numbers']}")
        print(f"LSTM 신뢰도: {lstm_result['confidence']:.2%}")
        print(f"LSTM 방법: {lstm_result['method']}")
        
        # 3. 번호 중복도 분석
        statistical_set = set(statistical_result['predicted_numbers'])
        lstm_set = set(lstm_result['predicted_numbers'])
        overlap = statistical_set.intersection(lstm_set)
        
        print(f"\n[3] 번호 중복 분석:")
        print(f"중복 번호: {sorted(list(overlap)) if overlap else '없음'}")
        print(f"중복 개수: {len(overlap)}/6 개")
        print(f"중복률: {len(overlap)/6:.1%}")
        
        # 4. 오행 분포 비교
        print(f"\n[4] 사주 오행 분석:")
        saju_elements = statistical_result['saju_analysis']['oheang']
        for element, strength in saju_elements.items():
            print(f"  {element}: {strength}")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'input': {
                'birth_year': birth_year,
                'birth_month': birth_month,
                'birth_day': birth_day,
                'birth_hour': birth_hour,
                'name': name
            },
            'statistical': {
                'predicted_numbers': statistical_result['predicted_numbers'],
                'confidence': statistical_result['confidence'],
                'method': statistical_result['method']
            },
            'lstm': {
                'predicted_numbers': lstm_result['predicted_numbers'],
                'confidence': lstm_result['confidence'],
                'method': lstm_result['method']
            },
            'comparison': {
                'overlap_numbers': sorted(list(overlap)) if overlap else [],
                'overlap_count': len(overlap),
                'overlap_rate': len(overlap) / 6,
                'confidence_diff': lstm_result['confidence'] - statistical_result['confidence']
            },
            'saju_analysis': saju_elements
        }
        
    except Exception as e:
        print(f"비교 중 오류 발생: {e}")
        return {'error': str(e)}

def run_multiple_comparisons() -> List[Dict[str, Any]]:
    """여러 테스트 케이스로 비교 실행"""
    test_cases = [
        (1990, 5, 15, 10, "테스트1"),
        (1985, 12, 25, 14, "테스트2"), 
        (1995, 3, 8, 9, "테스트3"),
        (1988, 7, 20, 18, "테스트4"),
        (1992, 11, 3, 7, "테스트5")
    ]
    
    results = []
    for birth_year, birth_month, birth_day, birth_hour, name in test_cases:
        result = compare_single_prediction(birth_year, birth_month, birth_day, birth_hour, name)
        results.append(result)
    
    return results

def analyze_overall_performance(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """전체 성능 분석"""
    if not results or any('error' in r for r in results):
        return {'error': '분석할 데이터가 부족합니다'}
    
    print(f"\n{'='*60}")
    print("전체 성능 분석")
    print(f"{'='*60}")
    
    # 통계 수집
    statistical_confidences = [r['statistical']['confidence'] for r in results]
    lstm_confidences = [r['lstm']['confidence'] for r in results]
    overlap_rates = [r['comparison']['overlap_rate'] for r in results]
    
    # 평균 계산
    avg_statistical_confidence = sum(statistical_confidences) / len(statistical_confidences)
    avg_lstm_confidence = sum(lstm_confidences) / len(lstm_confidences)
    avg_overlap_rate = sum(overlap_rates) / len(overlap_rates)
    
    # 결과 출력
    print(f"\n[종합 결과]")
    print(f"테스트 케이스 수: {len(results)}")
    print(f"통계 기반 평균 신뢰도: {avg_statistical_confidence:.2%}")
    print(f"LSTM 기반 평균 신뢰도: {avg_lstm_confidence:.2%}")
    print(f"평균 번호 중복률: {avg_overlap_rate:.1%}")
    
    # 승부 판정
    statistical_wins = sum(1 for r in results if r['statistical']['confidence'] > r['lstm']['confidence'])
    lstm_wins = sum(1 for r in results if r['lstm']['confidence'] > r['statistical']['confidence'])
    ties = len(results) - statistical_wins - lstm_wins
    
    print(f"\n[신뢰도 비교]")
    print(f"통계 방법 우세: {statistical_wins}회")
    print(f"LSTM 방법 우세: {lstm_wins}회")
    print(f"동점: {ties}회")
    
    if avg_lstm_confidence > avg_statistical_confidence:
        winner = "LSTM"
        margin = avg_lstm_confidence - avg_statistical_confidence
    else:
        winner = "통계"
        margin = avg_statistical_confidence - avg_lstm_confidence
    
    print(f"\n[최종 결과]")
    print(f"우승: {winner} 방법")
    print(f"신뢰도 차이: {margin:.2%}")
    
    analysis = {
        'test_count': len(results),
        'statistical': {
            'avg_confidence': avg_statistical_confidence,
            'wins': statistical_wins
        },
        'lstm': {
            'avg_confidence': avg_lstm_confidence,
            'wins': lstm_wins
        },
        'overall': {
            'avg_overlap_rate': avg_overlap_rate,
            'ties': ties,
            'winner': winner,
            'margin': margin
        }
    }
    
    return analysis

def main():
    print("=" * 60)
    print("사주로또 예측 방법 성능 비교")
    print("=" * 60)
    
    try:
        # 1. 단일 비교 테스트
        if len(sys.argv) >= 5:
            birth_year = int(sys.argv[1])
            birth_month = int(sys.argv[2])  
            birth_day = int(sys.argv[3])
            birth_hour = int(sys.argv[4])
            name = sys.argv[5] if len(sys.argv) > 5 else "사용자"
            
            result = compare_single_prediction(birth_year, birth_month, birth_day, birth_hour, name)
            
            # JSON 형태로도 출력
            print(f"\n[JSON 결과]")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 2. 다중 비교 테스트
        else:
            print("다중 테스트 케이스 실행 중...")
            results = run_multiple_comparisons()
            
            # 전체 분석
            analysis = analyze_overall_performance(results)
            
            # 결과 저장
            output_data = {
                'analysis': analysis,
                'detailed_results': results,
                'generated_at': datetime.now().isoformat()
            }
            
            with open('prediction_comparison_results.json', 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n상세 결과가 'prediction_comparison_results.json'에 저장되었습니다.")
            
    except Exception as e:
        print(f"실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()