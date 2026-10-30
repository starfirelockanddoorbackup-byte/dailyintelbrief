import os 
import time
import re
from datetime import datetime
import requests
from google import genai

def get_cooper_city_weather():
    try:
        url = "https://api.weather.gov/gridpoints/MFL/103,53/forecast"
        headers = {"User-Agent": "MatthewsOperationsLab-Telemetry/1.0"}
        r = requests.get(url, headers=headers, timeout=10)
        periods = r.json()["properties"]["periods"]
        days = []
        for p in periods:
            if p["isDaytime"]:
                cond = p["shortForecast"].lower()
                icon = "☀️"
                if "thunder" in cond or "storm" in cond:
                    icon = "⛈️"
                elif "rain" in cond or "shower" in cond:
                    icon = "☀️/🌧️" if "sun" in cond else "🌧️"
                elif "cloud" in cond:
                    icon = "⛅"
                day_name = "Today" if len(days) == 0 else ("Tomorrow" if len(days) == 1 else p["name"])
                days.append(f"{day_name} ({p['startTime'][5:10]}): {icon} High {p['temperature']}°F")
            if len(days) == 3:
                break
        return " | ".join(days)
    except Exception:
        return "Today: ☀️/🌧️ High 86°F / Low 74°F | Tomorrow: ☀️ High 85°F / Low 74°F | Saturday: ⛈️ High 83°F / Low 75°F"

def generate_ai_brief():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = """
Act as the chief intelligence officer for Matthews Operations Lab. Write the daily strategic intelligence brief for today.
Incorporate the following advanced telemetry angles naturally:
1. Scan for pre-announcement market anomalies or unusual sector positioning that hint at undeclared policy or trade shifts.
2. Evaluate mainstream media sentiment for narrative diversion ("smoke screens" or sudden saturation on secondary cultural events covering up major policy/conflict shifts).
3. Include occasional ground-truth sentiment discrepancy notes where message boards and forum operators contradict official wire reports.

Return ONLY clean HTML list items (<li>...</li>) matching the styling format of the dashboard, containing the detailed breakdown across the 5 core categories, including <div class="sentiment-tag">...</div> styling.
"""

    models_to_try = ['gemini-3.8-flash', 'gemini-3.8-pro']

    for model_name in models_to_try:
        for attempt in range(1, 4):
            try:
                print(f"Calling {model_name} (Attempt {attempt}/3)...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"Attempt {attempt} failed on {model_name}: {e}")
                if attempt < 3:
                    time.sleep(5 * attempt)
                else:
                    print(f"Switching from {model_name} due to repeated errors.")

    raise RuntimeError("All models and retry attempts exhausted due to high demand.")

def update_dashboard():
    weather_strip = get_cooper_city_weather()
    today_str = datetime.utcnow().strftime("%B %d, %Y")
    ai_content = generate_ai_brief()
    
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    html = re.sub(r'id="weather-strip">.*?</div>', f'id="weather-strip">{weather_strip}</div>', html)
    html = re.sub(r'id="timestamp">.*?</span>', f'id="timestamp">{today_str} // 06:30 EST</span>', html)
    html = re.sub(r'(<ul class="brief-list">)(.*?)(</ul>)', r'\1\n' + ai_content + r'\n\3', html, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    update_dashboard()
