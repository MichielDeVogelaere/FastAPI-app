from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import subprocess
import shutil
from typing import List
import asyncio
import logging

app = FastAPI()

# Constants
INPUT_DIR = "/data/input"
OUTPUT_DIR = "/data/output"

# Mount static files (your index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount static files for the output directory (for download)
app.mount("/download", StaticFiles(directory=OUTPUT_DIR), name="download")


@app.get("/")
async def root():
    return FileResponse("static/index.html")

async def run_demucs_command(cmd: str):
    """Run the Demucs command and stream the output to FastAPI logs."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Read and log stdout and stderr in real-time
    while True:
        stdout_line = await process.stdout.readline()
        if stdout_line:
            logging.info(stdout_line.decode().strip())
        else:
            break

    while True:
        stderr_line = await process.stderr.readline()
        if stderr_line:
            logging.error(stderr_line.decode().strip())
        else:
            break

    await process.wait()
    return process.returncode

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to the input directory
        file_path = os.path.join(INPUT_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logging.info(f"Uploaded file saved at: {file_path}")

        # Define the output directory before running Demucs
        base_name = os.path.splitext(file.filename)[0]
        output_dir = os.path.join(OUTPUT_DIR, "htdemucs", base_name)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Run Demucs processing
        cmd = f"python3 -m demucs -n htdemucs --mp3 -j 2 --overlap 0.25 --shifts 1 --two-stems=vocals --out {OUTPUT_DIR} {file_path}"
        logging.info(f"Running command: {cmd}")
        returncode = await run_demucs_command(cmd)

        if returncode == 0:
            # Get the output files
            output_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]

            logging.info(f"Output directory: {output_dir}")
            logging.info(f"Generated output files: {output_files}")

            return JSONResponse({
                "message": "Processing complete",
                "output_files": output_files,
                "base_path": f"htdemucs/{base_name}"
            })
        else:
            logging.error("Demucs processing failed.")
            return JSONResponse({
                "error": "Processing failed"
            }, status_code=500)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return JSONResponse({
            "error": str(e)
        }, status_code=500)