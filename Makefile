SHELL = /bin/sh
current-dir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Default options
gpu = true
mp3output = true
model = htdemucs_ft
shifts = 1
overlap = 0.25
jobs = 1
splittrack =

# FastAPI settings
HOST = 0.0.0.0
PORT = 8000
APP_NAME = fastapi-demucs

.DEFAULT_GOAL := help

.PHONY:
init:
ifeq ($(gpu), true)
  docker-gpu-option = --gpus all
endif
ifeq ($(mp3output), true)
  demucs-mp3-option = --mp3
endif
ifneq ($(splittrack),)
  demucs-twostems-option = --two-stems $(splittrack)
endif

# Construct commands
docker-run-command = docker run --rm -i \
--name=demucs \
$(docker-gpu-option) \
-v $(current-dir)input:/data/input \
-v $(current-dir)output:/data/output \
-v $(current-dir)models:/data/models \
xserrat/facebook-demucs:latest

demucs-command = "python3 -m demucs -n $(model) \
--out /data/output \
$(demucs-mp3-option) \
$(demucs-twostems-option) \
--shifts $(shifts) \
--overlap $(overlap) \
-j $(jobs) \
\"/data/input/$(track)\""

# FastAPI container command
docker-run-fastapi = docker run -d \
--name=$(APP_NAME) \
-p $(PORT):$(PORT) \
$(docker-gpu-option) \
-v $(current-dir)app:/app \
-v $(current-dir)input:/data/input \
-v $(current-dir)output:/data/output \
-v $(current-dir)models:/data/models \
xserrat/facebook-demucs:latest \
python3 -m uvicorn main:app --host $(HOST) --port $(PORT) --reload

.PHONY:
.SILENT:
help: ## Display available targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY:
.SILENT:
run: init build ## Run demucs to split the specified track in the input folder
	@echo $(docker-run-command) $(demucs-command)
	$(docker-run-command) $(demucs-command)

.PHONY:
.SILENT:
run-interactive: init build ## Run the docker container interactively to experiment with demucs options
	$(docker-run-command) /bin/bash

.PHONY:
.SILENT:
build: ## Build the docker image which supports running demucs with CPU only or with Nvidia CUDA on a supported GPU
	docker build -t xserrat/facebook-demucs:latest .

.PHONY:
serve: build ## Start the FastAPI server
	-docker rm -f $(APP_NAME) 2>/dev/null || true
	$(docker-run-fastapi)
	@echo "Server starting at http://localhost:$(PORT)"
	@echo "View logs with: make logs"

.PHONY:
stop: ## Stop the FastAPI server
	-docker stop $(APP_NAME)
	-docker rm $(APP_NAME)

.PHONY:
logs: ## View FastAPI server logs
	docker logs -f $(APP_NAME)


