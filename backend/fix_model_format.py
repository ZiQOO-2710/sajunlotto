#!/usr/bin/env python3
"""
모델 호환성 수정 스크립트
HDF5 형식의 모델을 Keras 네이티브 형식으로 변환합니다.
"""

import os
import pickle
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
import numpy as np

from database import SessionLocal
from models import LottoDraw

def rebuild_model():
    """호환성 문제를 해결하기 위해 모델을 다시 빌드합니다."""
    print("모델 재구성 중...")
    
    # 새로운 모델 구성 (기존 train_lstm_model.py와 동일)
    model = Sequential([
        # 첫 번째 LSTM 레이어
        LSTM(128, return_sequences=True, input_shape=(10, 6)),
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
    
    return model

def load_training_data():
    """데이터베이스에서 학습 데이터 로드"""
    db = SessionLocal()
    try:
        # 모든 로또 데이터를 회차 순으로 가져오기
        lotto_draws = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).all()
        
        if not lotto_draws:
            raise ValueError("데이터베이스에 로또 데이터가 없습니다.")
        
        # DataFrame으로 변환
        data = []
        for draw in lotto_draws:
            data.append([draw.n1, draw.n2, draw.n3, draw.n4, draw.n5, draw.n6])
        
        return np.array(data, dtype=np.float32)
        
    finally:
        db.close()

def prepare_sequences(data, sequence_length=10):
    """시계열 시퀀스 데이터 준비"""
    # 데이터 정규화 (1-45 범위를 0-1로)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    X, y = [], []
    for i in range(len(scaled_data) - sequence_length):
        # 과거 sequence_length개의 회차를 입력으로
        X.append(scaled_data[i:(i + sequence_length)])
        # 다음 회차를 출력으로
        y.append(scaled_data[i + sequence_length])
    
    return np.array(X), np.array(y), scaler

def main():
    print("=" * 60)
    print("LSTM 모델 호환성 수정")
    print("=" * 60)
    
    try:
        # 1. 새 모델 구성
        print("\n1. 새 모델 구성 중...")
        model = rebuild_model()
        print("모델 구성 완료")
        
        # 2. 학습 데이터 로드
        print("\n2. 학습 데이터 로드 중...")
        data = load_training_data()
        print(f"데이터 로드 완료: {data.shape}")
        
        # 3. 시퀀스 데이터 준비
        print("\n3. 시퀀스 데이터 준비 중...")
        X, y, scaler = prepare_sequences(data)
        print(f"시퀀스 데이터 준비 완료: X {X.shape}, y {y.shape}")
        
        # 4. 모델 학습 (간단한 학습)
        print("\n4. 모델 간단 학습 중...")
        model.fit(X, y, epochs=10, batch_size=16, validation_split=0.2, verbose=1)
        
        # 5. 모델 저장 (Keras 네이티브 형식)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"lotto_lstm_model_fixed_{timestamp}.keras"
        scaler_path = f"lotto_lstm_model_scaler_fixed_{timestamp}.pkl"
        
        print(f"\n5. 모델 저장 중...")
        model.save(model_path)
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        print(f"모델 저장 완료:")
        print(f"  - 모델: {model_path}")
        print(f"  - 스케일러: {scaler_path}")
        
        # 6. 테스트 예측
        print(f"\n6. 테스트 예측...")
        last_sequences = data[-10:]  # 마지막 10회차
        last_sequences_scaled = scaler.transform(last_sequences)
        input_seq = last_sequences_scaled.reshape(1, 10, 6)
        
        pred_scaled = model.predict(input_seq, verbose=0)
        pred_numbers = scaler.inverse_transform(pred_scaled)[0]
        final_numbers = np.clip(np.round(pred_numbers), 1, 45).astype(int)
        
        print(f"테스트 예측 결과: {final_numbers}")
        
        print("\n" + "=" * 60)
        print("모델 수정 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()