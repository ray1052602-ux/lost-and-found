import os
import pandas as pd
import re

# 輸入母資料夾（底下有很多月份資料夾）
base_folder = r"C:\Users\Apppl\Downloads\Direct"

# 要處理的月份資料夾清單
months = ["01-2020","02-2020","01-2021上","01-2021中","01-2021下","01-2022上","01-2022中","01-2022下","01-2023上","01-2023中","01-2023下","01-2024上","01-2024中","01-2024下","01-2025上","01-2025中","01-2025下","02-2021上","02-2021中","02-2021下","02-2022上","02-2022中","02-2022下","02-2023上","02-2023中","02-2023下","02-2024上","02-2024中","02-2024下","02-2025上","02-2025中","02-2025下"]

for m in months:
    input_file = os.path.join(base_folder, m, "T_Level.out")
    output_file = os.path.join(base_folder, m, "daily runoff.xlsx")  # 每個月一份

    if not os.path.exists(input_file):
        print(f"{input_file} 不存在，跳過")
        continue

    with open(input_file, "r") as f:
        lines = f.readlines()

    # === 找到標題列 ===
    header_line = None
    for i, line in enumerate(lines):
        if re.search(r"\bTime\b", line) and re.search(r"sum\(RunOff\)", line):
            header_line = i
            break

    if header_line is None:
        print(f"{input_file} 找不到標題列，跳過")
        continue

    # === 解析欄位名稱 ===
    columns = re.findall(r"[A-Za-z0-9()./]+", lines[header_line])

    # === 讀取為 DataFrame ===
    df = pd.read_csv(
        input_file,
        sep=r"\s+",  # ✅ 改成新語法
        skiprows=header_line + 1,
        names=columns,
        comment="*",
        engine="python"
    )

    # === 只保留 Time 與 sum(RunOff) ===
    df = df[["Time", "sum(RunOff)"]].dropna()

    # === 強制轉為數值 ===
    df["Time"] = pd.to_numeric(df["Time"], errors="coerce")
    df["sum(RunOff)"] = pd.to_numeric(df["sum(RunOff)"], errors="coerce")

    # 移除非數值行
    df = df.dropna(subset=["Time", "sum(RunOff)"])

    # === 篩選時間為 24、48、72…（整天倍數）===
    df = df[df["Time"] % 24 == 0].reset_index(drop=True)

    # === 轉換成「日」單位 ===
    df["Day"] = (df["Time"] / 24).astype(int)

    # === 計算每日（非累積）逕流 ===
    df["Daily_RunOff"] = df["sum(RunOff)"].diff().fillna(df["sum(RunOff)"])

    # === 刪除沒有逕流的日期 ===
    df = df[df["Daily_RunOff"] > 0].reset_index(drop=True)

    # === 重新排序欄位 ===
    df = df[["Day", "sum(RunOff)", "Daily_RunOff"]]

    # === 輸出成 Excel ===
    df.to_excel(output_file, index=False)
    print(f"✅ {m} 已完成轉換並輸出：{output_file}")
