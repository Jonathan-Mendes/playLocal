FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install flask yt-dlp

COPY server.py watcher.py playlocal.html ./
COPY static/ ./static/

RUN mkdir -p videos