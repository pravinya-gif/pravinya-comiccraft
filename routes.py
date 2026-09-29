from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.config import TEMPLATES_DIR, EXPORTS_DIR
from app.schemas import PromptRequest
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
# In-memory job store is sufficient for a local single-user demo.
COMICS: dict[str, dict] = {}

def _generate(payload: PromptRequest) -> dict:
    outline = generate_outline(payload.story_prompt, payload.character_name,
                               payload.setting, payload.tone, payload.art_style)
    story = generate_story(outline, payload.character_name, payload.tone)
    image_paths = [
        generate_image(
            f"{panel['image_prompt']}. Style: {payload.art_style}. Setting: {payload.setting}. Tone: {payload.tone}",
            panel["panel_number"]
        ) for panel in outline
    ]
    layout = build_comic_layout(outline, story, image_paths)
    pdf_path = save_pdf(layout, payload.story_prompt[:60])
    comic_id = uuid4().hex
    result = {"comic_id": comic_id, "layout": layout, "pdf_path": pdf_path,
              "title": payload.story_prompt[:100]}
    COMICS[comic_id] = result
    return result

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate", response_class=HTMLResponse)
async def generate_form(request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Alex"),
    setting: str = Form("Enchanted forest"),
    tone: str = Form("adventurous"),
    art_style: str = Form("comic book")):
    try:
        payload = PromptRequest(story_prompt=story_prompt, character_name=character_name,
                                setting=setting, tone=tone, art_style=art_style)
        result = _generate(payload)
        return templates.TemplateResponse("comic_preview.html", {"request": request, **result})
    except Exception as exc:
        return templates.TemplateResponse("index.html", {
            "request": request, "error": str(exc),
            "form": {"story_prompt": story_prompt, "character_name": character_name,
                     "setting": setting, "tone": tone, "art_style": art_style}
        }, status_code=500)

@router.post("/generate-comic/json")
async def generate_json(payload: PromptRequest):
    try:
        return _generate(payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, comic_id: str):
    if comic_id not in COMICS:
        raise HTTPException(status_code=404, detail="Comic not found. Generate it again.")
    return templates.TemplateResponse("export_success.html", {
        "request": request, "comic": COMICS[comic_id]
    })

@router.get("/download/{comic_id}")
async def download_pdf(comic_id: str):
    comic = COMICS.get(comic_id)
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found. Generate it again.")
    path = Path("static") / comic["pdf_path"].removeprefix("/static/")
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF file is missing.")
    return FileResponse(path, media_type="application/pdf", filename=Path(path).name)

@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        return {"image_path": generate_image(prompt)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
