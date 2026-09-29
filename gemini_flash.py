import json
import re
from google import genai
from app.config import GEMINI_API_KEY, GEMINI_FLASH_MODEL

def _extract_json(text: str):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", text, flags=re.S)
        if not match:
            raise ValueError("The story model did not return valid JSON.")
        return json.loads(match.group(0))

def generate_outline(story_prompt: str, character_name: str, setting: str,
                     tone: str, art_style: str) -> list[dict]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
Create exactly 5 connected comic panels. Return ONLY a valid JSON array.
Each item must have: panel_number (integer), title (string), scene_description (string),
image_prompt (string), caption (string).
Keep the story safe, coherent, and visually clear. No markdown.
Story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}
"""
    response = client.models.generate_content(model=GEMINI_FLASH_MODEL, contents=prompt)
    data = _extract_json(response.text or "")
    if isinstance(data, dict):
        data = data.get("panels", [])
    if not isinstance(data, list) or len(data) < 5:
        raise ValueError("The model did not return five panels.")
    panels = []
    for i, item in enumerate(data[:5], start=1):
        panels.append({
            "panel_number": i,
            "title": str(item.get("title", f"Panel {i}"))[:160],
            "scene_description": str(item.get("scene_description", ""))[:1200],
            "image_prompt": str(item.get("image_prompt", ""))[:1500],
            "caption": str(item.get("caption", ""))[:500],
        })
    return panels
