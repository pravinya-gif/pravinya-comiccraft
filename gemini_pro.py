import json
import re
from google import genai
from app.config import GEMINI_API_KEY, GEMINI_PRO_MODEL

def generate_story(outline: list[dict], character_name: str, tone: str) -> list[dict]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
Expand this outline into short comic narration and dialogue for each panel.
Return ONLY a JSON array of 5 objects with keys panel_number, narration, dialogue.
Keep each narration to 1-3 sentences and dialogue to 1-2 short lines.
Character name: {character_name}; tone: {tone}
Outline JSON:
{json.dumps(outline, ensure_ascii=False)}
"""
    response = client.models.generate_content(model=GEMINI_PRO_MODEL, contents=prompt)
    text = (response.text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, flags=re.S)
        if not match:
            raise ValueError("The narration model did not return valid JSON.")
        data = json.loads(match.group(0))
    if isinstance(data, dict):
        data = data.get("panels", [])
    by_num = {int(p.get("panel_number", i+1)): p for i, p in enumerate(data)}
    result = []
    for i in range(1, 6):
        item = by_num.get(i, {})
        result.append({
            "panel_number": i,
            "narration": str(item.get("narration", ""))[:1800],
            "dialogue": str(item.get("dialogue", ""))[:1000],
        })
    return result
