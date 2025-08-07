#!/usr/bin/env python3
"""
실제 로또 데이터 기반 LSTM 모델 학습 스크립트
데이터베이스에서 수집된 실제 로또 데이터를 사용하여 LSTM 모델을 학습합니다.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import pickle
import os
from datetime import datetime

from database import SessionLocal
from models import LottoDraw

class LottoPredictor:
    def __init__(self, sequence_length=10):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = None
        self.data = None
        
    def load_data_from_db(self):
        """데이터베이스에서 로또 데이터 로드"""
        db = SessionLocal()
        try:
            # 모든 로또 데이터를 회차 순으로 가져오기
            lotto_draws = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).all()
            
            if not lotto_draws:
                raise ValueError("데이터베이스에 로또 데이터가 없습니다. 먼저 collect_lotto_data.py를 실행하세요.")
            
            # DataFrame으로 변환
            data = []
            for draw in lotto_draws:
                data.append([draw.n1, draw.n2, draw.n3, draw.n4, draw.n5, draw.n6])
            
            self.data = np.array(data, dtype=np.float32)
            print(f"데이터 로드 완료: {len(lotto_draws)}회차, shape: {self.data.shape}")
            
            return self.data
            
        finally:
            db.close()
    
    def prepare_sequences(self, data):
        """시계열 시퀀스 데이터 준비"""
        # 데이터 정규화 (1-45 범위를 0-1로)
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(len(scaled_data) - self.sequence_length):
            # 과거 sequence_length개의 회차를 입력으로
            X.append(scaled_data[i:(i + self.sequence_length)])
            # 다음 회차를 출력으로
            y.append(scaled_data[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """LSTM 모델 구축"""
        model = Sequential([
            # 첫 번째 LSTM 레이어
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            
            # 두 번째 LSTM 레이어
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            
            # 세 번째 LSTM 레이어
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            
            # Dense 레이어들
            Dense(50, activation='relu'),
            Dropout(0.2),
            Dense(6, activation='sigmoid')  # 6개 번호 출력
        ])
        
        # 모델 컴파일
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def train(self, X, y, validation_split=0.2, epochs=100, batch_size=32):
        """모델 학습"""
        print(f"모델 학습 시작...")
        print(f"학습 데이터: {X.shape}, 타겟: {y.shape}")
        
        # 조기 종료 콜백 설정
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        )
        
        # 모델 학습
        history = self.model.fit(
            X, y,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping],
            verbose=1
        )
        
        return history
    
    def predict_next_numbers(self, last_sequences, num_predictions=1):
        """다음 회차 번호 예측"""
        if self.model is None or self.scaler is None:
            raise ValueError("모델이 학습되지 않았습니다.")
        
        # 입력 데이터 정규화
        last_sequences_scaled = self.scaler.transform(last_sequences)
        
        predictions = []
        for _ in range(num_predictions):
            # 예측 수행
            input_seq = last_sequences_scaled[-self.sequence_length:].reshape(1, self.sequence_length, 6)
            pred_scaled = self.model.predict(input_seq, verbose=0)
            
            # 역정규화
            pred_numbers = self.scaler.inverse_transform(pred_scaled)[0]
            
            # 1-45 범위로 클리핑하고 정수로 변환
            pred_numbers = np.clip(np.round(pred_numbers), 1, 45).astype(int)
            
            # 중복 제거 및 정렬
            unique_numbers = self._ensure_unique_numbers(pred_numbers)
            predictions.append(unique_numbers)
            
            # 다음 예측을 위해 예측 결과를 시퀀스에 추가
            last_sequences_scaled = np.vstack([last_sequences_scaled, pred_scaled])
        
        return predictions if num_predictions > 1 else predictions[0]
    
    def _ensure_unique_numbers(self, numbers):
        """중복 제거 및 6개 번호 보장"""
        unique_nums = []
        used_nums = set()
        
        # 예측된 번호 중 중복되지 않는 것들 선택
        for num in numbers:
            if num not in used_nums and 1 <= num <= 45:
                unique_nums.append(num)
                used_nums.add(num)
        
        # 6개가 안되면 랜덤으로 채우기
        while len(unique_nums) < 6:
            random_num = np.random.randint(1, 46)
            if random_num not in used_nums:
                unique_nums.append(random_num)
                used_nums.add(random_num)
        
        return sorted(unique_nums[:6])
    
    def save_model(self, filepath_prefix="lotto_lstm_model"):
        """모델과 스케일러 저장"""
        if self.model is None or self.scaler is None:
            raise ValueError("저장할 모델이 없습니다.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 모델 저장
        model_path = f"{filepath_prefix}_{timestamp}.h5"
        self.model.save(model_path)
        
        # 스케일러 저장
        scaler_path = f"{filepath_prefix}_scaler_{timestamp}.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"모델 저장 완료:")
        print(f"  - 모델: {model_path}")
        print(f"  - 스케일러: {scaler_path}")
        
        return model_path, scaler_path
    
    def evaluate_model(self, X_test, y_test):
        """모델 평가"""
        if self.model is None:
            raise ValueError("평가할 모델이 없습니다.")
        
        loss, mae = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"모델 평가 결과:")
        print(f"  - Loss: {loss:.4f}")
        print(f"  - MAE: {mae:.4f}")
        
        return loss, mae

def main():
    """메인 실행 함수"""
    print("="*60)
    print("사주로또 LSTM 모델 학습 시스템")
    print("="*60)
    
    # 예측기 초기화
    predictor = LottoPredictor(sequence_length=10)
    
    # 1. 데이터 로드
    print("\n1. 데이터베이스에서 로또 데이터 로드 중...")
    data = predictor.load_data_from_db()
    
    if len(data) < 15:  # 최소 15회차는 있어야 함
        print("학습을 위한 데이터가 부족합니다. 더 많은 데이터를 수집하세요.")
        return
    
    # 2. 시퀀스 데이터 준비
    print("\n2. 시계열 시퀀스 데이터 준비 중...")
    X, y = predictor.prepare_sequences(data)
    print(f"시퀀스 데이터 준비 완료: X shape: {X.shape}, y shape: {y.shape}")
    
    # 3. 모델 구축
    print("\n3. LSTM 모델 구축 중...")
    model = predictor.build_model(input_shape=(X.shape[1], X.shape[2]))
    model.summary()
    
    # 4. 모델 학습
    print("\n4. 모델 학습 시작...")
    history = predictor.train(X, y, epochs=200, batch_size=16)
    
    # 5. 모델 저장
    print("\n5. 모델 저장 중...")
    model_path, scaler_path = predictor.save_model()
    
    # 6. 예측 테스트
    print("\n6. 예측 테스트...")
    last_sequences = data[-10:]  # 마지막 10회차
    predicted_numbers = predictor.predict_next_numbers(last_sequences)
    print(f"다음 회차 예측 번호: {predicted_numbers}")
    
    # 7. 여러 번 예측해보기
    print("\n7. 추가 예측 (5회):")
    multiple_predictions = predictor.predict_next_numbers(last_sequences, num_predictions=5)
    for i, pred in enumerate(multiple_predictions, 1):
        print(f"  예측 #{i}: {pred}")
    
    print("\n" + "="*60)
    print("LSTM 모델 학습 완료!")
    print("="*60)

if __name__ == "__main__":
    main()