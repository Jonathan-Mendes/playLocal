import json
import os
import yt_dlp
from flask import Flask, send_from_directory, jsonify, request

app = Flask(__name__, static_folder="static", static_url_path="/static")

PASTA_VIDEOS = "videos"
LINKS_JSON   = "links.json"
VIDEOS_JSON  = "videos.json"
LIMITE_BYTES = 5 * 1024 ** 3  # 5 GB

# ── FRONT ─────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "mytube.html")

@app.route("/videos.json")
def videos_json():
    if not os.path.exists(VIDEOS_JSON):
        return jsonify([])
    with open(VIDEOS_JSON, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/videos/<path:filename>")
def serve_video(filename):
    return send_from_directory(PASTA_VIDEOS, filename)

# ── BUSCA NO YOUTUBE ───────────────────────────────────────
@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", 20))
    if not q:
        return jsonify([])
    try:
        opts = {
            "quiet":           True,
            "no_warnings":     True,
            "extract_flat":    True,
            "playlist_items":  f"1:{limit}",
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{q}", download=False)

        resultados = []
        for v in (info.get("entries") or []):
            dur = v.get("duration") or 0
            resultados.append({
                "titulo":  v.get("title", ""),
                "url":     f"https://www.youtube.com/watch?v={v.get('id', '')}",
                "thumb":   v.get("thumbnail") or f"https://i.ytimg.com/vi/{v.get('id','')}/hqdefault.jpg",
                "duracao": f"{dur // 60}:{str(dur % 60).zfill(2)}" if dur else "",
            })
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ── ENFILEIRAR PARA DOWNLOAD ───────────────────────────────
@app.route("/api/queue", methods=["POST"])
def queue():
    data = request.get_json()
    url  = (data or {}).get("url", "").strip()
    if not url:
        return jsonify({"erro": "url vazia"}), 400

    # Checa limite de disco
    total = sum(
        os.path.getsize(os.path.join(PASTA_VIDEOS, f))
        for f in os.listdir(PASTA_VIDEOS)
        if os.path.isfile(os.path.join(PASTA_VIDEOS, f))
    ) if os.path.exists(PASTA_VIDEOS) else 0

    if total >= LIMITE_BYTES:
        return jsonify({"erro": "Limite de 5 GB atingido. Exclua alguns vídeos primeiro."}), 400

    links = []
    if os.path.exists(LINKS_JSON):
        with open(LINKS_JSON, "r") as f:
            links = json.load(f).get("urls", [])

    if url not in links:
        links.append(url)
        with open(LINKS_JSON, "w") as f:
            json.dump({"urls": links}, f, indent=2)

    return jsonify({"ok": True})

# ── DELETE ─────────────────────────────────────────────────
@app.route("/api/delete/<path:filename>", methods=["DELETE"])
def delete_video(filename):
    fp = os.path.join(PASTA_VIDEOS, filename)
    if os.path.exists(fp):
        os.remove(fp)
    if os.path.exists(VIDEOS_JSON):
        with open(VIDEOS_JSON, "r", encoding="utf-8") as f:
            videos = json.load(f)
        videos = [v for v in videos if v.get("arquivo") != filename]
        with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=4, ensure_ascii=False)
    return jsonify({"ok": True})

# ── STORAGE ────────────────────────────────────────────────
@app.route("/api/storage")
def storage():
    total = 0
    if os.path.exists(PASTA_VIDEOS):
        for f in os.listdir(PASTA_VIDEOS):
            fp = os.path.join(PASTA_VIDEOS, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return jsonify({
        "bytes": total,
        "gb":    round(total / (1024**3), 2),
        "pct":   round((total / (5 * 1024**3)) * 100, 1)
    })

if __name__ == "__main__":
    os.makedirs(PASTA_VIDEOS, exist_ok=True)
    print("MyTube em http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)