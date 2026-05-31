#!/bin/bash
# Garante arquivos base
[ ! -f videos.json ] && echo "[]" > videos.json
[ ! -f links.json ]  && echo '{"urls":[]}' > links.json
mkdir -p videos

echo "Iniciando Watcher..."
python watcher.py &

echo "Iniciando Flask em http://localhost:8080"
python server.py
