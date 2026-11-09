# Video Clone AI — GitHub + Render deployment

A starter web app that accepts a public YouTube URL, retrieves accessible captions,
and uses an AI API to write a substantially original script inspired by the topic.
It does not download/copy the original video, audio, voice, or footage.

## Files
- `app.py`: FastAPI backend and API endpoints
- `static/index.html`: website frontend
- `requirements.txt`: Python dependencies
- `render.yaml`: Render Blueprint configuration
- `Procfile`: web service start command
- `.env.example`: local environment variable template

## Run locally
Use Python 3.11 or newer.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your secret API key:
```env
OPENAI_API_KEY=your_real_api_key
OPENAI_MODEL=gpt-4.1-mini
```

Start:
```bash
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`.

## Upload to GitHub
1. Create a new empty repository on GitHub.
2. Extract this ZIP on your computer.
3. Open a terminal inside the extracted folder.
4. Run:

```bash
git init
git add .
git commit -m "Initial Video Clone AI app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own GitHub repository URL.
Do not upload `.env` or any API key. `.gitignore` excludes `.env`.

## Deploy on Render
1. Sign in to Render and choose **New +** → **Blueprint** (or create a **Web Service**).
2. Connect the GitHub repository containing this project.
3. If using Blueprint, Render reads `render.yaml`.
4. If creating Web Service manually:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. In Render → your service → **Environment**, add:
   - `OPENAI_API_KEY` = your secret API key
   - `OPENAI_MODEL` = `gpt-4.1-mini`
6. Deploy. Open the generated `onrender.com` URL.
7. Test `https://YOUR-SERVICE.onrender.com/health`; it should return `{"status":"ok"}`.

## Important
- An OpenAI API key is separate from a ChatGPT subscription and API usage may incur charges.
- Keep the API key only in Render Environment Variables, never in browser JavaScript or GitHub.
- Caption extraction may fail if a video has no accessible captions or YouTube blocks access.
- This version generates a script only. AI narration, licensed/original visuals, subtitles, MP4 rendering, user login, payment, and job queues are not included yet.
- Before public launch, add authentication, rate limiting, per-user quotas, abuse protection, monitoring, and secure secret management.
- Respect copyright and YouTube terms. Do not clone another creator's distinctive expression, voice, or footage without permission.
