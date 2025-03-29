from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from pydantic import BaseModel
import json
from pathlib import Path
import uuid
from datetime import datetime
import os

app = FastAPI()

# Enable HTTPS redirect in production
if os.getenv("APP_ENV") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Setup paths
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "vpn_requests.json"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
DATA_FILE.parent.mkdir(exist_ok=True)
DATA_FILE.touch(exist_ok=True)
templates = Jinja2Templates(directory=TEMPLATES_DIR)


class VPNRequest(BaseModel):
    id: str
    telegram_username: str
    configs_count: int
    timestamp: str


def read_requests() -> list:
    try:
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    except FileNotFoundError:
        return []


def save_request(request: VPNRequest):
    requests = read_requests()
    requests.append(request.dict())
    with open(DATA_FILE, "w") as f:
        json.dump(requests, f, indent=2)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/submit_request/")
async def submit_request(
        telegram_username: str = Form(...),
        configs_count: int = Form(...)
):
    if not telegram_username.strip():
        raise HTTPException(status_code=400, detail="Telegram username is required")

    if configs_count < 1 or configs_count > 10:
        raise HTTPException(status_code=400, detail="Number of configurations must be between 1 and 10")

    request_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    vpn_request = VPNRequest(
        id=request_id,
        telegram_username=telegram_username.strip(),
        configs_count=configs_count,
        timestamp=timestamp
    )

    save_request(vpn_request)

    return {"message": "Request submitted successfully", "request_id": request_id}


@app.get("/requests/")
async def list_requests():
    return read_requests()


if __name__ == "__main__":
    import uvicorn

    if os.getenv("APP_ENV") == "production":
        uvicorn.run(
            "app.endpoint:app",
            host="0.0.0.0",
            port=443,
            ssl_keyfile="/etc/letsencrypt/live/netpulse.space/privkey.pem",
            ssl_certfile="/etc/letsencrypt/live/netpulse.space/fullchain.pem"
        )
    else:
        uvicorn.run(
            "app.endpoint:app",
            host="0.0.0.0",
            port=8000
        )