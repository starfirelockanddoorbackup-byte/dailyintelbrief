import os
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
                days.append(f"{day_name} ({p['startTime'][:10] * 0 or p['startTime'][5:10]}): {icon} High {p['temperature']}°F")
            if len(days) == 3:
                break
        return " | ".join(days)
    except Exception:
        return "Today: ☀️/🌧️ High 86°F / Low 74°F | Tomorrow: ☀️ High 85°F / Low 74°F | Saturday: ⛈️ High 83°F / Low 75°F"

def generate_ai_brief():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = """
    Act as the chief intelligence officer for Matthews Operations Lab. Write the daily strategic intelligence brief for today. 
    It must be sharp, analytical, un-sanitized, and structured precisely into these 5 distinct sections with bullet points:
    1. GEOPOLITICAL CONFLICTS & WAR ATTRITION (Track active theater casualty trends, WWII mortality scale metrics, and strategic moves like the Pentagon's FORTRESS initiative).
    2. SUPPLY CHAIN, ENERGY, POWER GRID & DOMESTIC LOGISTICS (Track diesel crack spreads, grid inelasticity, fiber-optic/cyber telemetry).
    3. EMERGING TECH, AI & SPACE (Orbital compute, edge hardening, autonomous military tech).
    4. LEGISLATIVE, POLITICAL & THEOLOGICAL CHESSBOARD (Central bank gold accumulation, de-dollarization, systemic resets).
    5. PHILANTHROPIC, HUMANITARIAN & ECOLOGICAL REALITIES (Global food security, agricultural inputs, frontline animal/human welfare).

    Return ONLY clean HTML list items (<li>...</li>) matching the styling format of the dashboard, containing the detailed breakdown for each category. Do not include markdown code blocks around the whole output, just the HTML fragment or structured text blocks.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

def update_dashboard():
    weather_strip = get_cooper_city_weather()
    today_str = datetime.utcnow().strftime("%B %d, %Y")
    ai_content = generate_ai_brief()
    
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    # Inject weather bar, timestamp, and AI generated briefing bullets
    html = re.sub(r'id="weather-strip">.*?</div>', f'id="weather-strip">{weather_strip}</div>', html)
    html = re.sub(r'id="timestamp">.*?</span>', f'id="timestamp">{today_str} // 06:30 EST</span>', html)
    
    # Replace the brief list contents inside Tab 0
    html = re.sub(r'(<ul class="brief-list">)(.*?)(</ul>)', r'\1\n' + ai_content + r'\n\3', html, flags=re.DOTALL)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    update_dashboard()