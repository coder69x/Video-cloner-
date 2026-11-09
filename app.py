import os
import re
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

load_dotenv()

app = FastAPI(
    title="Video Clone AI",
    description="Analyze available public captions and create an original video script.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


def extract_video_id(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    video_id = ""
    if host in ("youtube.com", "m.youtube.com", "music.youtube.com"):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith(("/shorts/", "/embed/")):
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2:
                video_id = parts[1]
    elif host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id or ""):
        raise ValueError("Valid YouTube video URL enter karein.")
    return video_id


class AnalyzeRequest(BaseModel):
    url: str = Field(min_length=8, max_length=500)


class ScriptRequest(BaseModel):
    transcript: str = Field(min_length=30, max_length=30000)
    language: str = Field(default="Hindi", max_length=40)
    style: str = Field(default="engaging explainer", max_length=100)
    target_minutes: int = Field(default=5, ge=1, le=30)


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze_video(data: AnalyzeRequest):
    try:
        video_id = extract_video_id(data.url)
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=["hi", "en"])
        transcript_text = " ".join(
            segment.text for segment in transcript.snippets
        ).strip()

        if not transcript_text:
            raise ValueError("Captions/transcript is empty.")

        return {
            "video_id": video_id,
            "transcript": transcript_text[:30000],
        }
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Transcript nahi mil saka. Video par captions available hone chahiye "
                "aur YouTube access allow hona chahiye. "
                f"Details: {str(exc)[:500]}"
            ),
        )


@app.post("/api/generate-script")
def generate_script(data: ScriptRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Render Environment me OPENAI_API_KEY set nahi hai.",
        )

    try:
        client = OpenAI(api_key=api_key)
        prompt = f"""
You are an expert YouTube scriptwriter.
Use the supplied transcript only to understand the topic and broad content structure.
Create a substantially original script. Do not copy sentences, distinctive jokes,
catchphrases, or unique expression. Do not reproduce the source video.
Use fresh wording, examples, transitions, and a suitable structure.

Output language: {data.language}
Style: {data.style}
Target duration: approximately {data.target_minutes} minutes.
Include:
- A strong but truthful opening hook
- Clear sections and smooth transitions
- Useful explanations and fresh examples
- A natural closing

Do not invent factual claims. Mark claims that need fact-checking.

Source transcript:
{data.transcript}
"""
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=prompt,
        )
        return {"script": response.output_text}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI script generation failed: {str(exc)[:500]}",
        )
