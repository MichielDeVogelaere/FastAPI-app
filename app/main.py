from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import subprocess
import shutil
from typing import List
import asyncio

app = FastAPI()

# Mount static files (your index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Constants
INPUT_DIR = "/data/input"
OUTPUT_DIR = "/data/output"

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to the input directory
        file_path = os.path.join(INPUT_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run demucs processing
        cmd = f"python3 -m demucs -n htdemucs_ft --mp3 --out {OUTPUT_DIR} {file_path}"
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Get the output files
            base_name = os.path.splitext(file.filename)[0]
            output_dir = os.path.join(OUTPUT_DIR, "htdemucs_ft", base_name)
            output_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
            
            return JSONResponse({
                "message": "Processing complete",
                "output_files": output_files,
                "base_path": f"download/{base_name}"
            })
        else:
            return JSONResponse({
                "error": "Processing failed",
                "stderr": stderr.decode()
            }, status_code=500)
            
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)

@app.get("/download/{folder}/{filename}")
async def download_file(folder: str, filename: str):
    file_path = os.path.join(OUTPUT_DIR, "htdemucs_ft", folder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return JSONResponse({
        "error": "File not found"
    }, status_code=404)



