import requests
import json
import csv
from datetime import datetime

API_KEY = "AIzaSyBzKAesMHJWigGQtyuVMfPh-ujXJmFXKi4"
LATITUDE = 23.6978   # 雲林緯度
LONGITUDE = 120.5400 # 雲林經度
DAYS = 10              # 抓取天數


def get_forecast():
    url = f"https://weather.googleapis.com/v1/forecast/days:lookup?key={API_KEY}&location.latitude={LATITUDE}&location.longitude={LONGITUDE}&days={DAYS}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"抓取失敗，狀態碼: {response.status_code}")
        return None
    return response.json()


def get_current_weather():
    url = f"https://weather.googleapis.com/v1/currentConditions:lookup?key={API_KEY}&location.latitude={LATITUDE}&location.longitude={LONGITUDE}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"抓取即時天氣失敗，狀態碼: {response.status_code}")
        return None
    return response.json()


def save_to_json(data, filename="forecast.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"已儲存 JSON: {filename}")


def save_to_csv(forecast_data, current_data=None, filename="forecast.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Max Temperature (C)", "Min Temperature (C)", "Total Rain (mm)"])

        # 加入即時天氣資料
        if current_data:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            temp = current_data.get("temperature", {}).get("degrees", "")
            feels_like = current_data.get("feelsLikeTemperature", {}).get("degrees", "")
            writer.writerow([f"{now} (Current)", temp, feels_like, "N/A"])

        # 加入預報資料
        for day in forecast_data.get("forecastDays", []):
            date = f"{day['displayDate']['year']}-{day['displayDate']['month']:02}-{day['displayDate']['day']:02}"
            daytime_rain = day.get("daytimeForecast", {}).get("precipitation", {}).get("qpf", {}).get("quantity", 0)
            nighttime_rain = day.get("nighttimeForecast", {}).get("precipitation", {}).get("qpf", {}).get("quantity", 0)
            total_rain = float(daytime_rain or 0) + float(nighttime_rain or 0)

            writer.writerow([
                date,
                day.get("maxTemperature", {}).get("degrees", ""),
                day.get("minTemperature", {}).get("degrees", ""),
                total_rain
            ])

    print(f"CSV file saved: {filename}")


def main():
    print("📡 開始抓取天氣資料...")
    forecast_data = get_forecast()
    current_data = get_current_weather()

    if forecast_data:
        save_to_json(forecast_data, "forecast.json")
    if current_data:
        save_to_json(current_data, "current_weather.json")

    if forecast_data:
        save_to_csv(forecast_data, current_data, "forecast1.csv")


if __name__ == "__main__":
    main()
