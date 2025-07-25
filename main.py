from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="templates")

PROJECT_FILES_DIR = Path("project_files")
UPLOADS_DIR = Path("uploads")
PROJECT_FILES_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def index(request: Request):
    files = list(PROJECT_FILES_DIR.iterdir())
    filename = files[0].name if files else None
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "filename": filename}
    )

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = PROJECT_FILES_DIR / filename
    if file_path.exists():
        return FileResponse(path=file_path, filename=filename)
    return {"error": "File not found"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    destination = UPLOADS_DIR / file.filename
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return RedirectResponse("/", status_code=303)
