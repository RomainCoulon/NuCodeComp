from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import json # Import the json module

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

PROJECT_FILES_DIR = Path("project_files/list_mode_data")
UPLOADS_DIR = Path("uploads")
PROJECT_FILES_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Path to the descriptions file
DESCRIPTIONS_FILE = PROJECT_FILES_DIR / "descriptions.json"

# Load descriptions
def load_descriptions():
    if DESCRIPTIONS_FILE.exists():
        with open(DESCRIPTIONS_FILE, "r") as f:
            return json.load(f)
    return {}

@app.get("/")
def index(request: Request):
    # Get list of all files in project_files directory (excluding the descriptions file itself)
    files = [file.name for file in PROJECT_FILES_DIR.iterdir() if file.is_file() and file.name != DESCRIPTIONS_FILE.name]
    
    # Load descriptions
    descriptions = load_descriptions()

    # Create a list of dictionaries, each containing filename and its description
    file_data = []
    for filename in files:
        file_data.append({
            "name": filename,
            "description": descriptions.get(filename, "No description available.") # Get description or default
        })

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "file_data": file_data, "now": datetime.now()} # Pass the list of file_data
    )

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = PROJECT_FILES_DIR / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(path=file_path, filename=filename)
    return {"error": "File not found"}

#@app.post("/upload")
#async def upload_file(file: UploadFile = File(...)):
#    destination = UPLOADS_DIR / file.filename
#    with open(destination, "wb") as buffer:
#        shutil.copyfileobj(file.file, buffer)
#    return RedirectResponse("/", status_code=303)