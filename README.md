# FastAPI-Demucs: Music Separator Service

FastAPI-Demucs is a web application for audio source separation using [Facebook's Demucs](https://github.com/facebookresearch/demucs) model. This project runs the Demucs model inside a Docker container, exposing a FastAPI-based interface to interact with the service.

## Features

- **Music Separation**: Split audio into stems (e.g., vocals, drums, bass).
- **GPU Support**: Leverage GPU for accelerated processing.
- **MP3 Output**: Option to generate MP3 files for outputs.
- **Configurable Options**: Customize model, overlap, shifts, and other parameters.
- **FastAPI Integration**: A RESTful API to manage audio separation tasks.
- **Dockerized**: Simplified deployment using Docker.

---

## Prerequisites

1. **Docker** installed and running on your system.
2. **NVIDIA GPU (optional)**: For GPU acceleration, ensure `nvidia-docker` is set up.
3. **Make**: For managing the service via Makefile commands.

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/MichielDeVogelaere/FastAPI-app.git
cd <repository-folder>
```
---

## Project Structure
```
project-root/
├── app/
│   ├── static/                 # Static files (e.g., index.html)
│   └── main.py                 # FastAPI application
├── input/                      # Directory for input audio files
├── output/                     # Directory for processed audio outputs
├── models/                     # Directory for Demucs models
├── Dockerfile                  # Docker configuration file
├── Makefile                    # Makefile with commands for the project
└── README.md                   # Documentation (this file)
```

---


## Usage

### Start the Service
To start the FastAPI service:
```bash
sudo make serve
```
This will:
- Build the Docker image (if not already built).
- Start the FastAPI server on [http://localhost:8000](http://localhost:8000).

### View Logs
To monitor server logs:
```bash
sudo make logs
```

### Stop the Service
To stop the FastAPI server:
```bash
sudo make stop
```

---

## Configuration

You can configure the behavior of Demucs by editing the `Makefile` options:

| Option          | Default Value   | Description                                  |
|------------------|-----------------|----------------------------------------------|
| `gpu`           | `true`          | Use GPU if available (`true`/`false`).       |
| `mp3output`     | `true`          | Output files in MP3 format.                 |
| `model`         | `htdemucs_ft`   | The model used for audio separation.         |
| `shifts`        | `1`             | Number of random shifts for processing.      |
| `overlap`       | `0.25`          | Overlap percentage during processing.        |
| `jobs`          | `1`             | Number of parallel jobs for separation.      |
| `splittrack`    | `""`            | Specify which stems to separate (e.g., vocals). |

---

## API Endpoints

The FastAPI application exposes the following endpoints:

### `GET /`
Returns the static `index.html` file for the application.

### `POST /upload/`
Uploads an audio file and processes it with Demucs. Upon success, it:
- Saves the separated files to the `output` directory.
- Renames the "no_vocals.mp3" file to "[songname]_karaoke-version.mp3".

**Request:**
- File: Upload an audio file (e.g., `.mp3`, `.wav`).

**Response:**
- `200 OK`: Returns the path to the processed file.
- `500 Internal Server Error`: If processing fails or the output file is not found.

### `GET /static`
Serves static files from the `/app/static` directory.

### `GET /download`
Provides access to processed output files in the `/data/output` directory.

---

## License

This project uses Facebook's Demucs under its respective license. Ensure compliance with all licensing terms when deploying or distributing this application.

