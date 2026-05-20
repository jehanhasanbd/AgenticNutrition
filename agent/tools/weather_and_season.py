import requests, datetime
from langchain_core.tools import tool

# Utility Function
def infer_season(month:int, hemisphere: str="north") -> str:
    if hemisphere.lower() == 'south':
        if month in (12, 1, 2): return "summer"
        if month in (3, 4, 5): return "autumn"
        if month in (6, 7, 8): return "winter"
    else:
        if month in (12, 1, 2): return "winter"
        if month in (3, 4, 5): return "spring"
        if month in (6, 7, 8): return "summer"
        return "autumn"


@tool("get_weather_and_season")
def get_weather_and_season(latitude: float = 23.71, longitude: float = 90.42, hemisphere: str = "north"):
    season = infer_season(month=datetime.utcnow().month(), hemisphere=hemisphere)
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,relative_humidity_2m"
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        current_weather = data.get("current_weather", {})
        return {
            "status": "ok",
            "season": season,
            'temperature': current_weather.get("temperature"),
            'windspeed': current_weather.get("windspeed"),
            'weathercode': current_weather.get("weathercode"),
            "source": "open-meteo.com"
        }
    except Exception as e:
        return {
            "status": "error",
            "season": season,
            "error": str(e)
        }



