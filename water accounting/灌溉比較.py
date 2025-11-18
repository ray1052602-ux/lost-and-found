import pandas as pd
import re
from io import StringIO

# 檔案名稱設定
file_name = 'test4_2025PROday.OUT'
output_csv = 'test4_2025PROday_output.csv'

# AquaCrop 每日輸出檔案的標準欄位名稱
column_names = [
    'Day', 'Month', 'Year', 'DAP', 'Stage',
    'WC(2.30) (mm)', 'Rain (mm)', 'Irri (mm)', 'Surf (mm)', 'Infilt (mm)',
    'RO (mm)', 'Drain (mm)', 'CR (mm)', 'Zgwt (m)',
    'Ex (mm)', 'E (mm)', 'E/Ex (%)',
    'Trx (mm)', 'Tr (mm)', 'Tr/Trx (%)',
    'ETx (mm)', 'ET (mm)', 'ET/ETx (%)'
]

try:
    # 讀取原始檔案內容
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data_lines = []
    data_started = False

    for line in lines:
        # 移除 AquaCrop 檔案中可能出現的 '' 標記
        line = re.sub(r'\', '', line).strip()

        # 偵測數據開始行：以數字開始的行，表示是實際的數據
        # (Day Month Year 都是數字)
        if re.match(r'^\s*\d+\s+\d+\s+\d+', line):
            data_lines.append(line)
        data_started = True
        elif data_started:
        # 如果數據已經開始，繼續加入後續行（如果沒有空行）
        if line:
            data_lines.append(line)

        # 將清理後的數據行合併並使用 StringIO 讓 pandas 讀取
        data_io = StringIO('\n'.join(data_lines))

        # 使用 read_csv 讀取數據：sep='\s+' 處理不規則的空白分隔符
        df = pd.read_csv(data_io, sep='\s+', header=None)

        # 刪除可能由不規則的空白產生的全 NaN 列
        df.dropna(axis=1, how='all', inplace=True)

        # 設定欄位名稱
        if df.shape[1] == len(column_names):
            df.columns = column_names
        else:
            print(f"警告：偵測到的欄位數 {df.shape[1]} 與預期的欄位數 {len(column_names)} 不符。請手動檢查原始檔案。")

        # 將 DataFrame 儲存為 CSV 檔案
        df.to_csv(output_csv, index=False)

        print(f"檔案已成功轉換並儲存為 {output_csv}")

except FileNotFoundError:
    print(f"錯誤：找不到檔案 {file_name}。請確保檔案已上傳且名稱正確。")
except Exception as e:
    print(f"發生錯誤: {e}")
    print("請檢查 AquaCrop 輸出檔案的格式是否與預期一致。")