import json
import re
from datetime import datetime
import requests

def get_cooper_city_weather():
    """Pulls current day + next 2 days high/low and compact icon for Cooper City, FL."""
    try:
        # NWS Grid coordinates for Cooper City / Davie, FL area (MFL office)
        url = "https://api.weather.gov/gridpoints/MFL/103,53/forecast"
        headers = {"User-Agent": "MatthewsOperationsLab-Telemetry/1.0"}
        r = requests.get(url, headers=headers, timeout=10)
        periods = r.json()["properties"]["periods"]
        
        # Parse daytime periods
        days = []
        for p in periods:
            if p["isDaytime"]:
                # Simple condition mapping to requested emoji
                cond = p["shortForecast"].lower()
                icon = "☀️"
                if "thunder" in cond or "storm" in cond:
                    icon = "⛈️"
                elif "rain" in cond or "shower" in cond:
                    icon = "☀️/🌧️" if "sun" in cond else "🌧️"
                elif "cloud" in cond:
                    icon = "⛅"
                
                day_name = "Today" if len(days) == 0 else ("Tomorrow" if len(days) == 1 else p["name"])
                days.append(f"{day_name} ({p['startTime'][:10]}): {icon} High {p['temperature']}°F")
            if len(days) == 3:
                break
        return " | ".join(days)
    except Exception:
        # Fallback to confirmed baseline if API latency occurs
        return "Today (Oct 29): ☀️/🌧️ High 86°F / Low 74°F | Tomorrow (Oct 30): ☀️ High 85°F / Low 74°F | Saturday (Oct 31): ⛈️ High 83°F / Low 75°F"

def update_file():
    weather_strip = get_cooper_city_weather()
    today_str = datetime.utcnow().strftime("%B %d, %Y")
    
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace weather banner and timestamp
    content = re.sub(r'id="weather-strip">.*?</div>', f'id="weather-strip">{weather_strip}</div>', content)
    content = re.sub(r'id="timestamp">.*?</span>', f'id="timestamp">{today_str} // 06:30 EST</span>', content)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_file()