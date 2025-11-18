# ============================================
# LSTM 天氣預測完整範例
# 建立假想天氣資料 → 前處理 → 建立模型 → 預測
# ============================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# ============================================
# 1️⃣ 產生模擬天氣資料（可替換成真實 weather.csv）
# ============================================

np.random.seed(42)
days = 400
dates = pd.date_range("2023-01-01", periods=days)

# 假想的氣溫、濕度、風速、降雨量
temp = 20 + 10 * np.sin(np.linspace(0, 3*np.pi, days)) + np.random.normal(0, 1, days)
humidity = 70 + 10 * np.cos(np.linspace(0, 3*np.pi, days)) + np.random.normal(0, 2, days)
wind = 2 + np.random.normal(0, 0.5, days)
rain = np.abs(np.random.normal(0, 1, days)) * (np.random.rand(days) > 0.8)

df = pd.DataFrame({
    "date": dates,
    "temp": temp,
    "humidity": humidity,
    "wind": wind,
    "rain": rain
})
print("📄 資料前五列：")
print(df.head())

# ============================================
# 2️⃣ 資料前處理
# ============================================

# 移除日期欄並正規化
data = df[['temp', 'humidity', 'wind', 'rain']].values
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(data)

# 使用過去 7 天預測第 8 天溫度
time_step = 7
X, y = [], []
for i in range(len(scaled) - time_step):
    X.append(scaled[i:i+time_step, :])
    y.append(scaled[i+time_step, 0])
X, y = np.array(X), np.array(y)

# 分訓練與測試集 (80%:20%)
split = int(len(X)*0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

print(f"\n✅ 訓練資料形狀: {X_train.shape}, 測試資料形狀: {X_test.shape}")

# ============================================
# 3️⃣ 建立 LSTM 模型
# ============================================

model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
    LSTM(32, return_sequences=False),
    Dense(16, activation='relu'),
    Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()

# ============================================
# 4️⃣ 模型訓練
# ============================================

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=40,
    batch_size=16,
    verbose=1
)

# ============================================
# 5️⃣ 模型預測與結果反轉
# ============================================

pred = model.predict(X_test)

# 反正規化
pred_full = np.concatenate((pred, np.zeros((pred.shape[0], scaled.shape[1]-1))), axis=1)
pred_inverse = scaler.inverse_transform(pred_full)[:, 0]
y_test_full = np.concatenate((y_test.reshape(-1,1), np.zeros((y_test.shape[0], scaled.shape[1]-1))), axis=1)
y_test_inverse = scaler.inverse_transform(y_test_full)[:, 0]

# ============================================
# 6️⃣ 結果視覺化
# ============================================

plt.figure(figsize=(10,5))
plt.plot(y_test_inverse, label="True Temperature")
plt.plot(pred_inverse, label="Predicted Temperature")
plt.title("LSTM 天氣預測（氣溫）")
plt.xlabel("Day Index")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.show()

# 損失函數變化
plt.figure(figsize=(6,4))
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title("Training Loss Curve")
plt.xlabel("Epoch")
plt.ylabel("MSE Loss")
plt.legend()
plt.show()
