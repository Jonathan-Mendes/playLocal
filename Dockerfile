FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install flask yt-dlp

COPY server.py watcher.py playlocal.html ./
COPY static/ ./static/

EXPOSE 8080

CMD ["sh", "-c", "python watcher.py & python server.py"]