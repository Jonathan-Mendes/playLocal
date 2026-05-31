FROM python:3.11-slim

WORKDIR /app

RUN pip install flask pytubefix

COPY server.py watcher.py mytube.html start.sh ./
COPY static/ ./static/

RUN echo "[]" > videos.json && echo '{"urls":[]}' > links.json && mkdir -p videos
RUN chmod +x start.sh

EXPOSE 8080
CMD ["./start.sh"]