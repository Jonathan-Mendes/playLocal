FROM python:3.11-slim

WORKDIR /app

# ffmpeg é necessário para o yt-dlp fazer merge de vídeo+áudio
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install flask yt-dlp

COPY server.py watcher.py playlocal.html start.sh ./
COPY static/ ./static/

RUN echo "[]" > videos.json && echo '{"urls":[]}' > links.json && mkdir -p videos
RUN chmod +x start.sh

EXPOSE 8080
CMD ["./start.sh"]