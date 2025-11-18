import requests
import json
import csv
import os
from datetime import datetime

# ==================== 設定區 (Configuration) ====================
# *** 請替換為您自己的 Google Weather API Key ***
# (請注意：由於安全限制，在此環境中您需要使用有效的金鑰才能實際執行 API 呼叫)
API_KEY = "AIzaSyBzKAesMHJWigGQtyuVMfPh-ujXJmFXKi4"

LATITUDE = 23.6978  # 台灣雲林縣的緯度 (舉例)
LONGITUDE = 120.5400  # 台灣雲林縣的經度 (舉例)
DAYS = 10  # 抓取未來 10 天的預測

# --- 輸出路徑設定 ---
# 請確保此目錄存在。由於環境限制，建議在本地測試時使用此路徑。
ABSOLUTE_OUTPUT_DIR = r"C:\\Users\\Apppl\\PycharmProjects\\PythonProject\\water accounting"
CSV_FILENAME = "forecast.csv"
JSON_FILENAME = "forecast.json"

# 完整路徑的組合
ABSOLUTE_CSV_PATH = os.path.join(ABSOLUTE_OUTPUT_DIR, CSV_FILENAME)
ABSOLUTE_JSON_PATH = os.path.join(ABSOLUTE_OUTPUT_DIR, JSON_FILENAME)
# ===============================================


def get_forecast():
    """
    從 Google Weather API 抓取未來多天的天氣預報資料。
    """
    url = (
        f"https://weather.googleapis.com/v1/forecast/days:lookup?"
        f"key={API_KEY}&location.latitude={LATITUDE}&location.longitude={LONGITUDE}&days={DAYS}"
    )

    try:
        print(f"📡 嘗試連線至 API: {url.split('?')[0]}...")
        response = requests.get(url)
        response.raise_for_status()  # 如果狀態碼不是 200，則拋出 HTTPError

    except requests.exceptions.HTTPError as err:
        print(f"📡 抓取失敗，HTTP 錯誤: {err}")
        print(f"請檢查您的 API Key ({API_KEY}) 或 API 權限是否正確。")
        return None
    except requests.exceptions.RequestException as e:
        print(f"📡 抓取失敗，發生連線錯誤: {e}")
        return None

    return response.json()


def save_to_json(data):
    """
    將原始 JSON 資料儲存到檔案中 (用於除錯)。
    此函式現使用設定區定義的 ABSOLUTE_JSON_PATH。
    """
    full_path = ABSOLUTE_JSON_PATH
    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON 檔案儲存成功: {full_path}")
    except Exception as e:
        print(f"⚠️ 寫入 JSON 檔案時發生錯誤: {e}")


def save_to_csv(forecast_data):
    """
    將天氣預報資料整理、合併、並寫入 CSV 檔案。
    - 它會讀取現有的 CSV 檔案。
    - 用新的預報資料覆蓋日期重複的舊資料。
    - 將合併後的完整資料按日期排序後寫回檔案。
    """
    if not forecast_data or not forecast_data.get("forecastDays"):
        print("⚠️ 無法寫入 CSV：預報資料為空。")
        return

    full_path = ABSOLUTE_CSV_PATH
    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # 預設標題行
    header = ["Date", "Max Temperature (C)", "Min Temperature (C)", "Total Rain (mm)"]
    existing_data = {} # 用來儲存和合併資料 {日期: [資料行]}

    # 1. 讀取現有資料
    try:
        with open(full_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 讀取並儲存標題行
            try:
                header = next(reader)
            except StopIteration:
                # 檔案為空，使用預設標題
                pass

            for row in reader:
                if row and len(row) > 0:
                    date = row[0]
                    existing_data[date] = row # 儲存整行資料
        print(f"📁 成功讀取現有 {len(existing_data)} 筆資料，準備合併。")
    except FileNotFoundError:
        print("📁 這是第一次執行，未找到舊的 CSV 檔案。將創建新檔案。")
    except Exception as e:
        print(f"⚠️ 讀取舊 CSV 檔案時發生錯誤: {e}。將以新資料覆蓋。")
        # 讀取失敗，則從空資料開始


    # 2. 處理新資料並合併 (覆蓋重複日期)
    newly_added_count = 0
    for day in forecast_data.get("forecastDays", []):
        # 處理日期格式 (格式：YYYY-MM-DD)
        date_obj = day.get("displayDate", {})
        date = f"{date_obj.get('year')}-{date_obj.get('month', 0):02}-{date_obj.get('day', 0):02}"

        # 處理降雨量 (Quantity of Precipitation Forecast, QPF)
        daytime_rain_qpf = day.get("daytimeForecast", {}).get("precipitation", {}).get("qpf", {})
        nighttime_rain_qpf = day.get("nighttimeForecast", {}).get("precipitation", {}).get("qpf", {})

        # 提取降雨量 (quantity) 並計算總和
        daytime_rain = daytime_rain_qpf.get("quantity", 0)
        nighttime_rain = nighttime_rain_qpf.get("quantity", 0)
        total_rain = float(daytime_rain or 0) + float(nighttime_rain or 0)

        # 準備新資料行
        new_row = [
            date,
            day.get("maxTemperature", {}).get("degrees", "N/A"),
            day.get("minTemperature", {}).get("degrees", "N/A"),
            f"{total_rain:.2f}"
        ]

        # 覆蓋/更新現有資料 (如果日期已存在，則用最新的預測覆蓋它)
        if date not in existing_data:
             newly_added_count += 1

        existing_data[date] = new_row


    # 3. 準備最終寫入資料：按日期排序
    # 這裡將字典的值 (所有資料行) 提取出來，並按照第一個元素 (日期) 進行排序
    final_data_to_write = sorted(existing_data.values(), key=lambda x: x[0])

    # 4. 寫入合併後的資料 (覆蓋整個檔案)
    try:
        # 使用 "w" 模式覆蓋舊檔案，但內容是合併且排序後的完整資料
        with open(full_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # 寫入標題行
            writer.writerow(header)

            # 寫入排序後的完整資料
            writer.writerows(final_data_to_write)

        print(f"✅ CSV 檔案儲存成功，已更新並覆蓋舊檔案。")
        print(f"   - 總記錄數: {len(final_data_to_write)} 筆。")
        print(f"   - 本次新增/更新: {len(forecast_data.get('forecastDays', []))} 筆 (其中 {newly_added_count} 筆是全新日期)。")

    except PermissionError:
        print(f"*** 寫入錯誤：權限被拒絕。請檢查檔案 '{full_path}' 是否正在被 Excel 或其他程式開啟。 ***")
    except Exception as e:
        print(f"發生其他寫入錯誤: {e}")


def main():
    """
    主函數，執行抓取和儲存流程。
    """
    # 檢查設定的路徑是否存在，如果不存在則創建
    if not os.path.isdir(ABSOLUTE_OUTPUT_DIR):
        try:
            os.makedirs(ABSOLUTE_OUTPUT_DIR)
            print(f"🔧 已創建輸出目錄: {ABSOLUTE_OUTPUT_DIR}")
        except Exception as e:
            print(f"*** 錯誤：無法創建輸出目錄 '{ABSOLUTE_OUTPUT_DIR}'。請檢查路徑設定和權限。錯誤: {e} ***")
            return

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📡 開始抓取 {DAYS} 天天氣預報...")

    # 1. 抓取預報資料
    forecast_data = get_forecast()

    if forecast_data:
        # 2. 儲存原始 JSON (用於除錯)
        save_to_json(forecast_data)

        # 3. 儲存 CSV (自動處理日期合併和覆蓋)
        save_to_csv(forecast_data)

    print("--- 任務完成 ---")


if __name__ == "__main__":
    main()
