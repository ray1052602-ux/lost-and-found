import datetime
import os
import subprocess
import pandas as pd
import re

# 你的檔案路徑
tnx_path = r"C:\GUIAC71\GUIAC7\AquaCropV71No13102023\DATA\AquaCrop_climate_avg_update.Tnx"
plu_path = r"C:\GUIAC71\GUIAC7\AquaCropV71No13102023\DATA\AquaCrop_climate_avg_update.PLU"
aquacrop_exe = r"C:\Users\Apppl\Documents\aquacrop71x8664windows\aquacrop.exe"
work_dir = r"C:\aquacrop71x8664windows2\aquacrop71x8664windows"
file_path = r"C:\aquacrop71x8664windows2\aquacrop71x8664windows\OUTP\test4_updatePROseason.OUT"

def update_tnx(file_path, date_str, tmin, tmax):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("="):
            data_start = i + 1
            break

    date = datetime.datetime.strptime(date_str, "%Y/%m/%d")
    day_of_year = date.timetuple().tm_yday
    line_index = data_start + day_of_year - 1

    old_line = lines[line_index].rstrip("\n")
    lines[line_index] = f"{' '*5}{float(tmin):5.1f}{' '*5}{float(tmax):5.1f}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"[Tnx] {date_str}: {old_line} → {lines[line_index].strip()}")


def update_plu(file_path, date_str, rain):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("="):
            data_start = i + 1
            break

    date = datetime.datetime.strptime(date_str, "%Y/%m/%d")
    day_of_year = date.timetuple().tm_yday
    line_index = data_start + day_of_year - 1

    old_line = lines[line_index].rstrip("\n")
    lines[line_index] = f"{' '*5}{float(rain):5.1f}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"[PLU] {date_str}: {old_line} → {lines[line_index].strip()}")


# 主程式
date_str = input("請輸入日期 (YYYY/MM/DD): ")
tmin = input("請輸入新的 Tmin: ")
tmax = input("請輸入新的 Tmax: ")
rain = input("請輸入新的 Rain: ")

update_tnx(tnx_path, date_str, tmin, tmax)
update_plu(plu_path, date_str, rain)

print("✅ 兩個檔案都已更新完成！")


# 確認 LIST 資料夾存在
list_folder = os.path.join("LIST")
os.makedirs(list_folder, exist_ok=True)

# 執行 AquaCrop
subprocess.run([aquacrop_exe], cwd=work_dir)
print("執行完成 AquaCrop...")

# 確認檔案存在
if not os.path.exists(file_path):
    raise FileNotFoundError(f"檔案不存在：{file_path}")

# ----------------------------
# 逐行讀檔
# ----------------------------
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# ----------------------------
# 找到標題列（包含 Irri）
# ----------------------------
header_line = None
for i, line in enumerate(lines):
    if re.search(r"\bIrri\b", line):
        header_line = i
        headers = re.split(r"\s+", line.strip())
        break

if header_line is None:
    raise ValueError("找不到包含 'Irri' 的標題列！")

# ----------------------------
# 數據行
# ----------------------------
data_lines = lines[header_line + 1 :]

# 轉成表格，處理欄位多/少問題
rows = []
for l in data_lines:
    if l.strip():
        values = re.split(r"\s+", l.strip())
        # 資料列比標題少，補空值
        if len(values) < len(headers):
            values += [""] * (len(headers) - len(values))
        # 資料列比標題多，截斷
        elif len(values) > len(headers):
            values = values[:len(headers)]
        rows.append(values)

df = pd.DataFrame(rows, columns=headers)

# ----------------------------
# 自動抓日期相關欄位 + Irri
# ----------------------------
date_cols = [col for col in df.columns if re.match(r"^(Day|Month|Year)\d+", col)]
columns_to_extract = date_cols + ["Irri"]

# 檢查欄位是否存在
missing_cols = [col for col in columns_to_extract if col not in df.columns]
if missing_cols:
    raise ValueError(f"缺少欄位：{missing_cols}")

# 取出需要的欄位
irri_date_df = df[columns_to_extract]

# ----------------------------
# 存成 Excel
# ----------------------------
output_file = r"C:\aquacrop71x8664windows2\aquacrop71x8664windows\OUTP\irri_date_output.xlsx"
irri_date_df.to_excel(output_file, index=False)

print(f"已存成 Excel：{output_file}")
