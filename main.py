from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

BASE_PROJECT_DIR = Path("project_files")
BASE_PROJECT_DIR.mkdir(parents=True, exist_ok=True)

# --- Helper to load descriptions for a specific project ---
def load_descriptions(project_path: Path):
    descriptions_file = project_path / "descriptions.json"
    if descriptions_file.exists():
        with open(descriptions_file, "r") as f:
            return json.load(f)
    return {}

# --- Helper to load general description for a specific project ---
def load_general_description(project_path: Path):
    general_description_file = project_path / "general_description.json"
    if general_description_file.exists():
        with open(general_description_file, "r") as f:
            # Assuming the JSON contains a single string or a dictionary with a 'text' key
            data = json.load(f)
            return data.get("text", "") if isinstance(data, dict) else data
    return "No general description available for this project."


# --- Main Landing Page Route ---
@app.get("/")
def main_index(request: Request):
    project_folders = [
        folder.name for folder in BASE_PROJECT_DIR.iterdir()
        if folder.is_dir() and not folder.name.startswith("__")
    ]
    return templates.TemplateResponse(
        "main_index.html",
        {"request": request, "project_folders": project_folders, "now": datetime.now()}
    )

# --- Project-Specific Page Route ---
@app.get("/project/{project_name}")
def project_page(project_name: str, request: Request):
    project_path = BASE_PROJECT_DIR / project_name

    if not project_path.is_dir():
        raise HTTPException(status_code=404, detail="Project not found")

    files = [
        file.name for file in project_path.iterdir()
        if file.is_file() and file.name not in ["descriptions.json", "general_description.json"]
    ]

    descriptions = load_descriptions(project_path)
    general_description = load_general_description(project_path) # Load the general description

    file_data = []
    for filename in files:
        file_data.append({
            "name": filename,
            "description": descriptions.get(filename, "No description available.")
        })

    return templates.TemplateResponse(
        "project_page.html",
        {
            "request": request,
            "project_name": project_name,
            "file_data": file_data,
            "general_description": general_description, # Pass the general description
            "now": datetime.now()
        }
    )

# --- Download File Route ---
@app.get("/download/{project_name}/{filename}")
def download_file(project_name: str, filename: str):
    file_path = BASE_PROJECT_DIR / project_name / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(path=file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")