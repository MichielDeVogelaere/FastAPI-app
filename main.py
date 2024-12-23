from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import shutil
from typing import Optional
import uuid
import time
import logging

app = FastAPI(title="Demucs Audio Separator API")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configure paths
INPUT_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/separate")
async def separate_audio(
        file: UploadFile,
        gpu: bool = False,
        mp3output: bool = False,
        model: str = "htdemucs",
        shifts: int = 1,
        overlap: float = 0.25,
        jobs: int = 1,
        splittrack: Optional[str] = None
):
    """ Separate an audio file into its components using Demucs """
    logger.info("Received request to separate audio")
    # Generate unique ID for this separation job
    job_id = str(uuid.uuid4())
    logger.info(f"Generated job ID: {job_id}")

    # Save uploaded file
    file_path = os.path.join(INPUT_DIR, f"{job_id}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved uploaded file to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to save file: {str(e)}")

    # Construct make command with parameters
    cmd = ["make", "run", f"track={job_id}_{file.filename}"]
    if gpu:
        cmd.append("gpu=true")
    if mp3output:
        cmd.append("mp3output=true")
    if splittrack:
        cmd.append(f"splittrack={splittrack}")
    cmd.extend([
        f"model={model}",
        f"shifts={shifts}",
        f"overlap={overlap}",
        f"jobs={jobs}"
    ])
    logger.info(f"Constructed command: {' '.join(cmd)}")

    try:
        start_time = time.time()
        # Run the make command
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        duration = time.time() - start_time
        logger.info(f"Demucs processing time: {duration} seconds")
        logger.info(f"Command output: {process.stdout}")

        # Create zip file of output
        output_path = os.path.join(OUTPUT_DIR, model, os.path.splitext(file.filename)[0])
        if not os.path.exists(output_path):
            logger.error("Processing failed - no output generated")
            raise HTTPException(status_code=500, detail="Processing failed - no output generated")

        # Create zip file containing the separated tracks
        zip_path = f"{output_path}.zip"
        shutil.make_archive(output_path, 'zip', output_path)
        logger.info(f"Created zip file at {zip_path}")

        # Clean up input file
        os.remove(file_path)
        logger.info(f"Removed input file {file_path}")

        # Return the zip file
        return FileResponse(
            zip_path, media_type="application/zip", filename=f"{os.path.splitext(file.filename)[0]}_separated.zip"
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Processing failed: {e.stderr}")
        raise HTTPException(
            status_code=500, detail=f"Processing failed: {e.stderr}"
        )
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file {file_path}")


@app.get("/health")
async def health_check():
    """Check if the service is running"""
    return {"status": "healthy"}