import pandas as pd
from datetime import datetime

# 檔案路徑
tmax_path = r"C:\Users\Apppl\Downloads\C0K430-2025-MaxAirTemperature-day1.csv"
tmin_path = r"C:\Users\Apppl\Downloads\C0K430-2025-MinAirTemperature-day1.csv"
tnx_path  = "C:\GUIAC71\GUIAC7\AquaCropV71No13102023\DATA\AquaCrop_climate_avg_update.Tnx"
output_path = "C:\GUIAC71\GUIAC7\AquaCropV71No13102023\DATA\AquaCrop_climate_avg_update.Tnx"

# 讀取 Tmax/Tmin CSV
df_max = pd.read_csv(tmax_path)
df_min = pd.read_csv(tmin_path)

# 擷取溫度數值
def extract_temp(value):
    try:
        return float(str(value).split("/")[0].strip())
    except:
        return None

def is_int(x):
    try:
        int(x)
        return True
    except:
        return False

# 只取 2–6 月
months = ["2", "3" ]

data = []
for m in months:
    for day, tmax_val, tmin_val in zip(df_max["日/月"], df_max[m], df_min[m]):
        if not is_int(day):
            continue
        tmax = extract_temp(tmax_val)
        tmin = extract_temp(tmin_val)
        if tmax is not None and tmin is not None:
            date = datetime(2025, int(m), int(day))
            data.append({"date": date, "tmax": tmax, "tmin": tmin})

df_temp = pd.DataFrame(data).sort_values("date").reset_index(drop=True)

# 讀取 Tnx
with open(tnx_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# 找到資料開始的位置
start_idx = 0
for i, line in enumerate(lines):
    if line.strip().startswith("Tmin"):
        start_idx = i + 2  # 下一行開始是數據
        break

# 把 Tnx 的數據區塊讀出來
data_lines = lines[start_idx:]
assert len(data_lines) >= 365, "Tnx daily data 不完整!"

# 覆蓋 2–6 月的數據
for _, row in df_temp.iterrows():
    day_of_year = row["date"].timetuple().tm_yday
    idx = start_idx + day_of_year - 1
    lines[idx] = f"{row['tmin']:10.1f}{row['tmax']:10.1f}\n"

# 輸出新檔案
with open(output_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"✅ 已完成覆蓋，輸出檔案：{output_path}")
