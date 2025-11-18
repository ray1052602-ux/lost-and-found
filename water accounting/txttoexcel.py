import pandas as pd

input_file = r"C:\aquacrop71x8664windows2\aquacrop71x8664windows\OUTP\test4_updatePROday.OUT"
output_file =r"C:\aquacrop71x8664windows2\aquacrop71x8664windows\OUTP\test4_updatePROdayoutput.xlsx"

# 讀檔
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 找到標題列
header_line = None
for i, line in enumerate(lines):
    if "Day" in line:
        header_line = i
        break

# 標題與單位
columns = lines[header_line].split()[:-1]   # 移除最後一欄
units = lines[header_line + 1].split()[:len(columns)]

# 資料行
data_lines = lines[header_line + 2:]

# 先讀資料，不指定欄位
df = pd.read_csv(
    pd.io.common.StringIO("".join(data_lines)),
    sep=r"\s+",
    engine="python",
    header=None
)

# 🔹 在資料最前面插入兩欄空白
df_shifted = pd.DataFrame([["", ""] + row.tolist() for row in df.values])

# 生成最終欄位名稱：前兩欄空白 + 原始 columns
full_columns = ["", ""] + columns
# 如果資料比 full_columns 多，生成 extra 欄位
if df_shifted.shape[1] > len(full_columns):
    full_columns += [f"extra_{i}" for i in range(df_shifted.shape[1]-len(full_columns))]
df_shifted.columns = full_columns

# 🔹 單位行前面有六個空格
df_units = pd.DataFrame([[""]*6 + units + [""]*(df_shifted.shape[1]-len(units)-6)], columns=full_columns)

# 合併
df_final = pd.concat([df_units, df_shifted], ignore_index=True)

# 輸出 Excel
df_final.to_excel(output_file, index=False)

print(f"✅ 已經轉換完成！輸出檔案: {output_file}")
