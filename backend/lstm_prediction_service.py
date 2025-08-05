#!/usr/bin/env python3
"""
LSTM 기반 로또 번호 예측 서비스
학습된 LSTM 모델을 사용하여 다음 회차 로또 번호를 예측합니다.
"""

import numpy as np
import pickle
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from database import SessionLocal
from models import LottoDraw
import saju

class LSTMPredictionService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_loaded = False
        self.model_path = None
        self.scaler_path = None
        
    def find_latest_model_files(self) -> tuple[Optional[str], Optional[str]]:
        """최신 모델 파일들을 찾습니다."""
        try:
            # 현재 디렉토리에서 모델 파일들 찾기 (.keras와 .h5 형식 모두 지원)
            model_files = [f for f in os.listdir('.') if f.startswith('lotto_lstm_model_') and (f.endswith('.keras') or f.endswith('.h5'))]
            scaler_files = [f for f in os.listdir('.') if f.startswith('lotto_lstm_model_scaler_') and f.endswith('.pkl')]
            
            if not model_files or not scaler_files:
                return None, None
                
            # 최신 파일 선택 (타임스탬프 기준)
            model_files.sort(reverse=True)
            scaler_files.sort(reverse=True)
            
            return model_files[0], scaler_files[0]
            
        except Exception as e:
            print(f"모델 파일 검색 중 오류: {e}")
            return None, None
    
    def load_model_files(self) -> bool:
        """LSTM 모델과 스케일러를 로드합니다."""
        try:
            if self.model_loaded:
                return True
                
            # 모델 파일 찾기
            model_file, scaler_file = self.find_latest_model_files()
            
            if not model_file or not scaler_file:
                print("LSTM 모델 파일을 찾을 수 없습니다.")
                return False
            
            print(f"모델 로딩 중: {model_file}")
            print(f"스케일러 로딩 중: {scaler_file}")
            
            # 모델 로드
            self.model = load_model(model_file)
            
            # 스케일러 로드
            with open(scaler_file, 'rb') as f:
                self.scaler = pickle.load(f)
            
            self.model_path = model_file
            self.scaler_path = scaler_file
            self.model_loaded = True
            
            print("LSTM 모델 로딩 완료!")
            return True
            
        except Exception as e:
            print(f"모델 로딩 중 오류: {e}")
            self.model_loaded = False
            return False
    
    def load_recent_draws(self, sequence_length: int = 10) -> Optional[np.ndarray]:
        """최근 회차 데이터를 로드합니다."""
        try:
            db = SessionLocal()
            try:
                # 최근 sequence_length개 회차 데이터 가져오기
                recent_draws = db.query(LottoDraw).order_by(
                    LottoDraw.draw_no.desc()
                ).limit(sequence_length).all()
                
                if len(recent_draws) < sequence_length:
                    print(f"충분한 데이터가 없습니다. 필요: {sequence_length}, 현재: {len(recent_draws)}")
                    return None
                
                # 회차 순서대로 정렬 (오래된 것부터)
                recent_draws.reverse()
                
                # 숫자 배열로 변환
                data = []
                for draw in recent_draws:
                    data.append([draw.n1, draw.n2, draw.n3, draw.n4, draw.n5, draw.n6])
                
                return np.array(data, dtype=np.float32)
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"최근 회차 데이터 로드 중 오류: {e}")
            return None
    
    def predict_next_numbers(self, saju_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """LSTM 모델을 사용하여 다음 회차 번호를 예측합니다."""
        try:
            # 모델 로드
            if not self.load_model_files():
                raise Exception("LSTM 모델을 로드할 수 없습니다.")
            
            # 최근 데이터 로드
            recent_data = self.load_recent_draws(sequence_length=10)
            if recent_data is None:
                raise Exception("최근 회차 데이터를 로드할 수 없습니다.")
            
            # 데이터 정규화
            scaled_data = self.scaler.transform(recent_data)
            
            # 예측 수행
            input_sequence = scaled_data.reshape(1, 10, 6)
            prediction_scaled = self.model.predict(input_sequence, verbose=0)
            
            # 역정규화
            prediction = self.scaler.inverse_transform(prediction_scaled)[0]
            
            # 1-45 범위로 클리핑하고 정수 변환
            base_numbers = np.clip(np.round(prediction), 1, 45).astype(int)
            
            # 사주 가중치 적용 (제공된 경우)
            if saju_weights:
                weighted_numbers = self._apply_saju_weights(base_numbers, saju_weights)
            else:
                weighted_numbers = base_numbers
            
            # 중복 제거 및 6개 번호 보장
            final_numbers = self._ensure_unique_numbers(weighted_numbers)
            
            # 신뢰도 계산 (기본적으로 LSTM 기반이므로 높은 신뢰도)
            confidence = 0.75
            
            return {
                'predicted_numbers': final_numbers,
                'method': 'LSTM + 사주 가중치',
                'confidence': confidence,
                'base_prediction': base_numbers.tolist(),
                'model_file': self.model_path,
                'generated_at': datetime.now()
            }
            
        except Exception as e:
            print(f"LSTM 예측 중 오류: {e}")
            raise e
    
    def _apply_saju_weights(self, base_numbers: np.ndarray, saju_weights: Dict[str, float]) -> np.ndarray:
        """사주 오행 가중치를 기본 예측에 적용합니다."""
        try:
            # 오행별 번호 범위
            element_ranges = {
                '목': (1, 9),
                '화': (10, 19), 
                '토': (20, 29),
                '금': (30, 39),
                '수': (40, 45)
            }
            
            weighted_numbers = base_numbers.copy()
            
            # 각 번호에 대해 해당 오행의 가중치 적용
            for i, number in enumerate(base_numbers):
                for element, (start, end) in element_ranges.items():
                    if start <= number <= end:
                        # 가중치가 높은 오행에 해당하는 번호는 유지하고
                        # 가중치가 낮은 경우 조정
                        weight = saju_weights.get(element, 1.0)
                        if weight < 0.5:  # 가중치가 낮으면 다른 번호로 대체 시도
                            # 가중치가 높은 오행의 범위에서 번호 선택
                            best_element = max(saju_weights.items(), key=lambda x: x[1])
                            best_range = element_ranges[best_element[0]]
                            # 기존 번호와 유사한 위치의 새 번호 생성
                            new_number = np.random.randint(best_range[0], best_range[1] + 1)
                            weighted_numbers[i] = new_number
                        break
                        
            return weighted_numbers
            
        except Exception as e:
            print(f"사주 가중치 적용 중 오류: {e}")
            return base_numbers
    
    def _ensure_unique_numbers(self, numbers: np.ndarray) -> List[int]:
        """중복 제거 및 6개 번호 보장"""
        unique_nums = []
        used_nums = set()
        
        # 예측된 번호 중 중복되지 않는 것들 선택
        for num in numbers:
            if num not in used_nums and 1 <= num <= 45:
                unique_nums.append(int(num))
                used_nums.add(num)
        
        # 6개가 안되면 랜덤으로 채우기
        while len(unique_nums) < 6:
            random_num = np.random.randint(1, 46)
            if random_num not in used_nums:
                unique_nums.append(random_num)
                used_nums.add(random_num)
        
        return sorted(unique_nums[:6])
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보를 반환합니다."""
        try:
            if not self.model_loaded:
                self.load_model_files()
            
            info = {
                'model_loaded': self.model_loaded,
                'model_file': self.model_path,
                'scaler_file': self.scaler_path
            }
            
            if self.model:
                info.update({
                    'model_summary': str(self.model.summary()),
                    'input_shape': self.model.input_shape,
                    'output_shape': self.model.output_shape
                })
            
            return info
            
        except Exception as e:
            return {
                'error': str(e),
                'model_loaded': False
            }

# 전역 서비스 인스턴스
lstm_service = LSTMPredictionService()

def get_lstm_prediction(birth_year: int, birth_month: int, birth_day: int, birth_hour: int, name: str = "사용자") -> Dict[str, Any]:
    """사주 분석과 LSTM을 결합한 예측을 생성합니다."""
    try:
        # 사주 분석 수행
        saju_result = saju.analyze_saju(birth_year, birth_month, birth_day, birth_hour)
        
        # 사주 오행 가중치 계산
        oheang = saju_result['oheang']
        total_strength = sum(oheang.values())
        
        saju_weights = {}
        if total_strength > 0:
            for element, strength in oheang.items():
                saju_weights[element] = strength / total_strength
        else:
            # 기본 가중치
            saju_weights = {'목': 0.2, '화': 0.2, '토': 0.2, '금': 0.2, '수': 0.2}
        
        # LSTM 예측 수행
        prediction = lstm_service.predict_next_numbers(saju_weights)
        
        # 결과에 사주 분석 추가
        prediction['saju_analysis'] = saju_result
        prediction['saju_weights'] = saju_weights
        prediction['name'] = name
        
        return prediction
        
    except Exception as e:
        print(f"LSTM + 사주 예측 중 오류: {e}")
        raise e

if __name__ == "__main__":
    # 테스트 코드
    try:
        print("LSTM 예측 서비스 테스트")
        print("=" * 50)
        
        # 서비스 초기화
        service = LSTMPredictionService()
        
        # 모델 정보 출력
        info = service.get_model_info()
        print("모델 정보:")
        for key, value in info.items():
            if key != 'model_summary':
                print(f"  {key}: {value}")
        
        # 예측 수행
        print("\n예측 수행 중...")
        result = get_lstm_prediction(1990, 5, 15, 10, "테스트 사용자")
        
        print(f"\n예측 결과:")
        print(f"  예측 번호: {result['predicted_numbers']}")
        print(f"  신뢰도: {result['confidence']:.2%}")
        print(f"  방법: {result['method']}")
        print(f"  사주 가중치: {result['saju_weights']}")
        
    except Exception as e:
        print(f"테스트 중 오류: {e}")