import pandas as pd
import glob
import os

# 1. 設定資料夾路徑（請依實際路徑修改）
folder_path = r"C:\Users\Apppl\PycharmProjects\PythonProject\yunlin farm"
output_file = os.path.join(folder_path, "雲林每日整理彙總.xlsx")

# 2. 自動搜尋所有 .xlsx 檔案（排除彙總檔本身）
# 修正排除邏輯，排除檔名結尾為 "每日整理彙總.xlsx" 的檔案
input_files = [f for f in glob.glob(os.path.join(folder_path, "*.xlsx")) if not f.endswith("每日整理彙總.xlsx")]

# 3. 欄位分類
# 將 '室外溫度 (1)' 從平均欄位中移除
average_cols = ['室外濕度 (2)', '室外光度 (3)', '室外風速 (4)', '室外風向 (5)',
                '土壤溫度 (8)', '土壤濕度 (9)', '土壤電導度 (10)']
# 新增最高/最低溫度的欄位
temp_cols = ['室外溫度 (1)']
sum_cols = ['當日時雨量 (6)', '單次自動灌溉總量 (15)', '瞬時灌溉水量 (13)']
max_cols = ['當日累積雨量 (7)', '總累積灌溉水量 (11)']

# 4. 合併所有檔案的資料
all_data = pd.DataFrame()

for file in input_files:
    try:
        df = pd.read_excel(file)
        # 確保 '日期時間' 欄位存在
        if '日期時間' in df.columns:
            df['日期'] = pd.to_datetime(df['日期時間']).dt.date
            all_data = pd.concat([all_data, df], ignore_index=True)
            print(f"✅ 已讀取：{os.path.basename(file)}")
        else:
            print(f"⚠️ 檔案 {os.path.basename(file)} 缺少 '日期時間' 欄位，跳過。")
    except Exception as e:
        print(f"⚠️ 無法讀取 {os.path.basename(file)}：{e}")

# 檢查是否有資料
if all_data.empty:
    print("\n🚨 沒有成功讀取任何資料，程式結束。")
else:
    # 5. 分組統計

    # 溫度：計算每日最高溫和最低溫
    max_temp_df = all_data.groupby('日期')[temp_cols].max().rename(
        columns={'室外溫度 (1)': '室外最高溫度 (1)'}
    )
    min_temp_df = all_data.groupby('日期')[temp_cols].min().rename(
        columns={'室外溫度 (1)': '室外最低溫度 (1)'}
    )

    # 其他欄位：計算平均值、加總、最大值
    avg_df = all_data.groupby('日期')[average_cols].mean()
    sum_df = all_data.groupby('日期')[sum_cols].sum()
    max_df = all_data.groupby('日期')[max_cols].max()

    # 6. 合併結果
    final_df = pd.concat([
        max_temp_df, min_temp_df, # 新增最高/最低溫
        avg_df, sum_df, max_df
    ], axis=1).reset_index()

    # 7. 輸出到 Excel
    final_df.to_excel(output_file, index=False)
    print(f"\n📁 所有統計完成 (已包含每日最高/最低溫)，結果已輸出至：{output_file}")