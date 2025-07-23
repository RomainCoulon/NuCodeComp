from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import shutil

app = FastAPI()

UPLOAD_DIR = "uploads"
PROJECT_FILES_DIR = "project_files" # Make sure you have some files in this directory for testing

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROJECT_FILES_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    uploaded_files = os.listdir(UPLOAD_DIR)
    project_files = os.listdir(PROJECT_FILES_DIR) # <--- This line is crucial
    return templates.TemplateResponse("index.html", {
        "request": request,
        "uploaded_files": uploaded_files, # <--- And this one
        "project_files": project_files   # <--- And this one
    })


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return RedirectResponse(url="/", status_code=303)


@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/project_files/{filename}")
async def get_project_file(filename: str):
    file_path = os.path.join(PROJECT_FILES_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="Project file not found")