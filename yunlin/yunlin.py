import pandas as pd

# 讀取 Excel
file_path = "C0K430-2024-MinAirTemperature-day.xlsx"
df = pd.ExcelFile(file_path)

# 讀取工作表
data = df.parse('C0K430-2024-MinAirTemperature-d')

# 整理資料
wind_data = []
months = data.iloc[0, 1:].tolist()  # 第一列是月份
year = 2024  # 固定年份

for i in range(1, len(data)):  # 從第 1 列開始 (因為第 0 列是標題)
    day = data.iloc[i, 0]  # 日期（日）
    for j, month in enumerate(months, start=1):
        cell = data.iloc[i, j]
        if isinstance(cell, str) and "/" in cell and not cell.startswith("--"):
            try:
                wind_speed = float(cell.split("/")[0].strip())  # 只取風速
                date_str = f"{year}-{int(month):02d}-{int(day):02d}"
                wind_data.append({
                    "Date": date_str,
                    "Mintemp": wind_speed
                })
            except:
                continue

# 建立 DataFrame 並排序
wind_df = pd.DataFrame(wind_data)
wind_df = wind_df.sort_values(by=["Date"]).reset_index(drop=True)

# 輸出結果
print(wind_df)

# 如果要存成新的 Excel
wind_df.to_excel("Mintemp_by_Date.xlsx", index=False)
