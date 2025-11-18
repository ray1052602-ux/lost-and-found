import pandas as pd
import glob
import os
import re
import calendar

def convert_temp_csv(file_list, value_name):
    all_data = []
    for f in file_list:
        year_match = re.search(r'(\d{4})', os.path.basename(f))
        if not year_match:
            continue
        year = int(year_match.group(1))

        df = pd.read_csv(f, index_col=0)
        df = df.drop(df.index[-1])  # 去掉最後一列總和

        # 拆出數值，改用 map 避免 applymap 警告
        df = df.apply(lambda col: col.map(lambda x: str(x).split('/')[0].strip() if pd.notna(x) else pd.NA))
        df = df.replace('--', pd.NA)
        df = df.apply(pd.to_numeric, errors='coerce')

        df_long = df.reset_index().melt(id_vars=df.index.name, var_name='Month', value_name='Value')
        df_long.rename(columns={df.index.name: 'Day'}, inplace=True)
        df_long['Year'] = year
        df_long['Month'] = df_long['Month'].astype(int)
        df_long['Day'] = df_long['Day'].astype(int)
        df_long = df_long.rename(columns={'Value': value_name})
        all_data.append(df_long[['Year','Month','Day',value_name]])

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame(columns=['Year','Month','Day',value_name])

# --------------------------
# 設定資料夾路徑
base_path = r"C:\Users\Apppl\Downloads\GUI_AC7.1 (1)\GUI_AC71"
tmin_files = sorted(glob.glob(os.path.join(base_path, "Tmin", "*.csv")))
tmax_files = sorted(glob.glob(os.path.join(base_path, "Tmax", "*.csv")))
pre_files  = sorted(glob.glob(os.path.join(base_path, "Pre", "*.csv")))

# 轉換 CSV
tmin_all = convert_temp_csv(tmin_files, 'Tmin')
tmax_all = convert_temp_csv(tmax_files, 'Tmax')
pre_all  = convert_temp_csv(pre_files, 'Pre')

# 合併氣候變數
merged_df = tmin_all.merge(tmax_all, on=['Year','Month','Day'], how='outer')
merged_df = merged_df.merge(pre_all, on=['Year','Month','Day'], how='outer')

# 每日平均 (忽略年份)
daily_avg = merged_df.groupby(['Month','Day']).mean().reset_index()

# 補 NaN（線性插值）
for var in ['Tmin','Tmax','Pre']:
    daily_avg[var] = daily_avg[var].interpolate(limit_direction='both')

# 過濾不合法日期（每月天數正確，2 月只到 28 天）
def valid_date(row):
    month = int(row['Month'])
    day = int(row['Day'])
    if month == 2 and day > 28:
        return False
    last_day = calendar.monthrange(2000, month)[1]
    if day > last_day:
        return False
    return True

daily_avg = daily_avg[daily_avg.apply(valid_date, axis=1)]

# --------------------------
# 輸出純文字 txt 給 AquaCrop (只保留 Tmin Tmax Pre)
output_file = os.path.join(base_path, "AquaCrop_climate_avg.txt")
with open(output_file, 'w') as f:
    for _, row in daily_avg.iterrows():
        f.write(f"{row['Tmin']:.2f} {row['Tmax']:.2f} {row['Pre']:.2f}\n")

print(f"8 年每日平均 AquaCrop txt 檔已輸出: {output_file}")
print(daily_avg.head(10))
