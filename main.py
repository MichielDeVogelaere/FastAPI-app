from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import subprocess
import os

app = FastAPI()

# Path for input and output files
INPUT_DIR = 'demucs/input'
OUTPUT_DIR = 'demucs/output'

# Ensure the directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Save the uploaded file to the input directory
    file_path = os.path.join(INPUT_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call the Makefile 'run' target to process the audio file
    try:
        result = subprocess.run(
            ['make', 'run', 'track=' + file.filename],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Return the separated tracks (example for vocals)
        separated_file = os.path.join(OUTPUT_DIR, file.filename.replace('.mp3', '_vocals.mp3'))  # Example for vocals
        return FileResponse(separated_file)
    except subprocess.CalledProcessError as e:
        return {"error": f"Error processing file: {e.stderr.decode()}"}
