# ComicCraft — AI Comic Story Creator

ComicCraft turns a prompt into a five-panel comic with story narration, dialogue, illustrations, and a PDF export. It uses FastAPI + Jinja2, Google Gemini for text, and optionally Hugging Face Inference for illustrations.

## Requirements
- Python 3.10 or newer (Python 3.11 recommended)
- A Gemini API key from Google AI Studio
- Optional Hugging Face token for hosted image generation

## VS Code setup (Windows)
1. Install Python and VS Code. In VS Code, open this `ComicCraft` folder.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt and run:
   ```bat
   .venv\Scripts\activate.bat
   ```
4. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to a new file named `.env`. Add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_real_key_here
   ```
   Keep `.env` private; do not commit or share it.
6. Start the server from the project root:
   ```bash
   uvicorn app.main:app --reload
   ```
7. Open:
   - Website: http://127.0.0.1:8000
   - Interactive API docs: http://127.0.0.1:8000/docs

## macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GEMINI_API_KEY
uvicorn app.main:app --reload
```

## Image generation
- Without `HF_API_KEY`, the app creates locally rendered comic-style placeholder illustrations. This lets you test the complete flow without downloading large AI models.
- For generated images, add a Hugging Face token to `HF_API_KEY`. The selected model/provider must be available to your account; hosted inference availability and latency can vary.
- Image API errors fall back to local artwork rather than stopping the comic.

## Test the application
1. Open the homepage and enter a story prompt of at least five characters.
2. Choose character, setting, tone, and art style, then click **Create my comic**.
3. Confirm five panels appear.
4. Click **Download your comic as PDF** and open the downloaded PDF.
5. Open `/docs`, expand `POST /generate-comic/json`, click **Try it out**, and submit:
   ```json
   {
     "story_prompt": "A curious robot finds a tiny garden on Mars",
     "character_name": "Milo",
     "setting": "Mars",
     "tone": "hopeful",
     "art_style": "comic book"
   }
   ```
6. Test image generation from `/docs` using `POST /test-image` and a `prompt` form field.

## API endpoints
- `GET /` — homepage
- `POST /generate` — HTML form comic generation
- `POST /generate-comic/json` — JSON comic generation
- `POST /test-image` — image-generation smoke test
- `GET /download/{comic_id}` — download a generated PDF
- `GET /export-success?comic_id=...` — export confirmation page
- `GET /docs` — Swagger UI

## Project structure
```text
ComicCraft/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes.py
│   ├── schemas.py
│   └── services/
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── image_generator.py
│       ├── layout_builder.py
│       └── exporters.py
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── style.css
│   ├── panels/
│   └── exports/
├── .env.example
├── .gitignore
└── requirements.txt
```

## Notes
- The model names are configurable in `.env`; availability can vary by Google account/API release.
- The JSON endpoint returns a local PDF URL and panel layout. Use the `/download/{comic_id}` route for a direct file download.
- The in-memory comic store is intended for local development. Restarting the server clears generated comic IDs.
