import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# 로또 번호 데이터 (예시)
# 실제로는 DB에서 가져오거나 크롤링한 데이터를 사용합니다.
# 여기서는 간단한 예시를 위해 가상의 데이터를 사용합니다.
# 각 행은 6개의 당첨 번호와 1개의 보너스 번호로 구성됩니다.
# 편의상 보너스 번호는 예측에서 제외하고 6개의 당첨 번호만 사용합니다.
example_lotto_data = [
    [1, 2, 3, 4, 5, 6],
    [7, 8, 9, 10, 11, 12],
    [13, 14, 15, 16, 17, 18],
    [19, 20, 21, 22, 23, 24],
    [25, 26, 27, 28, 29, 30],
    [31, 32, 33, 34, 35, 36],
    [37, 38, 39, 40, 41, 42],
    [1, 10, 20, 30, 40, 45],
    [2, 12, 22, 32, 42, 44],
    [3, 13, 23, 33, 43, 45]
]

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def build_and_train_model(data, seq_length=5, epochs=50, batch_size=1):
    # 데이터 정규화 (0과 1 사이로 스케일링)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # 시퀀스 생성
    X, y = create_sequences(scaled_data, seq_length)

    # LSTM 모델 구축
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(seq_length, data.shape[1])),
        Dense(data.shape[1])
    ])

    model.compile(optimizer='adam', loss='mse')

    # 모델 학습
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)

    return model, scaler

def apply_saju_weights(predicted_numbers, saju_oheang_distribution):
    """
    사주 오행 분포에 따라 예측된 로또 번호에 가중치를 적용합니다.
    """
    # 오행별 번호 범위 및 기본 가중치
    OHEANG_WEIGHTS = {
        '목': {'range': (1, 9), 'weight': 1.2},
        '화': {'range': (10, 19), 'weight': 1.2},
        '토': {'range': (20, 29), 'weight': 1.1},
        '금': {'range': (30, 39), 'weight': 1.2},
        '수': {'range': (40, 45), 'weight': 1.1}
    }

    weighted_numbers = []
    for num in predicted_numbers:
        current_weight = 1.0
        for oheang, info in OHEANG_WEIGHTS.items():
            start, end = info['range']
            if start <= num <= end:
                # 사주 오행 분포에 따라 가중치 조정
                # 예를 들어, 사주에 '목' 기운이 강하면 '목'에 해당하는 번호에 더 큰 가중치를 부여
                # 여기서는 간단히 해당 오행의 기본 가중치를 곱합니다.
                # 실제로는 사주 오행 분포의 비율을 반영하여 더 복잡한 가중치 계산이 필요합니다.
                current_weight *= info['weight']
                break
        weighted_numbers.append((num, current_weight))

    # 가중치에 따라 번호 재정렬 (높은 가중치 우선)
    weighted_numbers.sort(key=lambda x: x[1], reverse=True)

    # 가중치 적용 후 상위 6개 번호 선택 (중복 제거)
    final_numbers = []
    for num, _ in weighted_numbers:
        if num not in final_numbers:
            final_numbers.append(num)
        if len(final_numbers) == 6:
            break
    
    # 6개 번호가 안되면 랜덤으로 채우거나 다시 예측하는 로직 필요
    while len(final_numbers) < 6:
        new_num = np.random.randint(1, 46)
        if new_num not in final_numbers:
            final_numbers.append(new_num)
    
    final_numbers.sort()
    return final_numbers

def predict_lotto_numbers(model, scaler, last_sequence, saju_oheang_distribution=None):
    # 예측을 위한 입력 데이터 전처리
    last_sequence_scaled = scaler.transform(last_sequence)
    last_sequence_scaled = last_sequence_scaled.reshape(1, last_sequence_scaled.shape[0], last_sequence_scaled.shape[1])

    # 예측 수행
    predicted_scaled = model.predict(last_sequence_scaled)

    # 예측 결과 역정규화
    predicted_numbers = scaler.inverse_transform(predicted_scaled)

    # 로또 번호는 정수이므로 반올림하고 1-45 범위로 조정
    predicted_numbers = np.round(predicted_numbers).astype(int).flatten()
    predicted_numbers = np.clip(predicted_numbers, 1, 45)

    # 중복 제거 및 정렬 후 6개 번호 선택
    unique_predicted_numbers = np.unique(predicted_numbers).tolist()
    unique_predicted_numbers.sort()

    # 사주 가중치 적용 (사주 분포가 제공된 경우)
    if saju_oheang_distribution:
        return apply_saju_weights(unique_predicted_numbers, saju_oheang_distribution)
    else:
        # 사주 가중치가 없는 경우, 상위 6개 번호 선택
        final_numbers = unique_predicted_numbers[:6]
        while len(final_numbers) < 6:
            new_num = np.random.randint(1, 46)
            if new_num not in final_numbers:
                final_numbers.append(new_num)
        final_numbers.sort()
        return final_numbers

if __name__ == "__main__":
    # 예시 데이터로 모델 학습 및 예측
    data = np.array(example_lotto_data)
    
    # 모델 학습
    model, scaler = build_and_train_model(data)

    # 마지막 시퀀스로 다음 번호 예측
    last_sequence = data[-5:] # 마지막 5회차 데이터를 사용

    # 사주 오행 분포 예시 (실제로는 saju.py에서 가져온 데이터 사용)
    # 예를 들어, '목' 기운이 강한 사주
    example_saju_oheang = {'목': 2, '화': 1, '토': 1, '금': 1, '수': 1}

    # 사주 가중치 적용하여 예측
    predicted_with_saju = predict_lotto_numbers(model, scaler, last_sequence, saju_oheang_distribution=example_saju_oheang)
    print(f"사주 가중치 적용 예측된 로또 번호: {predicted_with_saju}")

    # 사주 가중치 없이 예측
    predicted_without_saju = predict_lotto_numbers(model, scaler, last_sequence)
    print(f"사주 가중치 없이 예측된 로또 번호: {predicted_without_saju}")