import json
import os
import time
import shutil
import yt_dlp

PASTA_VIDEOS = "videos"
LINKS_JSON   = "links.json"
VIDEOS_JSON  = "videos.json"
STATUS_JSON  = "queue_status.json"
LIMITE_BYTES = 5 * 1024 ** 3  # 5 GB

# ── QUALIDADE DO DOWNLOAD ──────────────────────────────────
# QUALIDADE = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"      # Melhor qualidade
# QUALIDADE = "bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]" # Full HD
QUALIDADE = "bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720]"     # HD 720p (recomendado)
# QUALIDADE = "bestvideo[height<=480][ext=mp4]+bestaudio/best[height<=480]"   # 480p

# ── helpers ───────────────────────────────────────────────
def uso_disco():
    total = 0
    if os.path.exists(PASTA_VIDEOS):
        for f in os.listdir(PASTA_VIDEOS):
            fp = os.path.join(PASTA_VIDEOS, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total

def gb(b):
    return round(b / (1024**3), 2)

def salvar_status(status):
    with open(STATUS_JSON, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False)

def ler_fila():
    if not os.path.exists(LINKS_JSON):
        return []
    with open(LINKS_JSON, "r") as f:
        try:
            return json.load(f).get("urls", [])
        except Exception:
            return []

def remover_da_fila(url):
    urls = ler_fila()
    if url in urls:
        urls.remove(url)
    with open(LINKS_JSON, "w") as f:
        json.dump({"urls": urls}, f, indent=2)

def limpar_tudo():
    print("\n[SISTEMA] Limpando arquivos...")
    if os.path.exists(PASTA_VIDEOS):
        shutil.rmtree(PASTA_VIDEOS)
    for f in [VIDEOS_JSON, LINKS_JSON, STATUS_JSON]:
        if os.path.exists(f):
            os.remove(f)
    print("[SISTEMA] Pronto.")

def atualizar_banco(novo):
    conteudo = []
    if os.path.exists(VIDEOS_JSON):
        with open(VIDEOS_JSON, "r", encoding="utf-8") as f:
            try:
                conteudo = json.load(f)
            except Exception:
                conteudo = []
    conteudo.append(novo)
    with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, indent=4, ensure_ascii=False)

# ── progress hook ─────────────────────────────────────────
def make_progress_hook(titulo, thumb):
    def hook(d):
        fila_atual = len(ler_fila())
        if d["status"] == "downloading":
            total      = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            baixado    = d.get("downloaded_bytes", 0)
            velocidade = d.get("_speed_str", "").strip() or "–"
            eta        = d.get("_eta_str", "").strip() or "–"
            pct        = round((baixado / total) * 100, 1) if total else 0
            salvar_status({
                "ativo":      True,
                "titulo":     titulo,
                "thumb":      thumb,
                "pct":        pct,
                "velocidade": velocidade,
                "eta":        eta,
                "fila":       fila_atual,
            })
        elif d["status"] == "finished":
            salvar_status({
                "ativo":      True,
                "titulo":     titulo,
                "thumb":      thumb,
                "pct":        100,
                "velocidade": "–",
                "eta":        "Finalizando...",
                "fila":       fila_atual,
            })
    return hook

# ── loop principal ─────────────────────────────────────────
def monitorar():
    os.makedirs(PASTA_VIDEOS, exist_ok=True)
    salvar_status({"ativo": False})
    baixados = set()

    print("[WATCHER] Monitorando... (Ctrl+C para sair)")
    print(f"[WATCHER] Limite: 5 GB | Qualidade: {QUALIDADE}")

    try:
        while True:
            if uso_disco() >= LIMITE_BYTES:
                print(f"[WATCHER] Limite atingido ({gb(uso_disco())} GB).")
                salvar_status({"ativo": False})
                time.sleep(30)
                continue

            urls      = ler_fila()
            pendentes = [u for u in urls if u not in baixados]

            if not pendentes:
                salvar_status({"ativo": False})
                time.sleep(3)
                continue

            url = pendentes[0]

            try:
                info_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
                with yt_dlp.YoutubeDL(info_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                titulo = info.get("title", "vídeo")
                thumb  = info.get("thumbnail", "")

                print(f"[DOWNLOAD] {titulo} | fila: {len(pendentes)-1} restantes")

                dl_opts = {
                    "quiet":               True,
                    "no_warnings":         True,
                    "format":              QUALIDADE,
                    "outtmpl":             os.path.join(PASTA_VIDEOS, "%(title)s.%(ext)s"),
                    "merge_output_format": "mp4",
                    "progress_hooks":      [make_progress_hook(titulo, thumb)],
                }
                with yt_dlp.YoutubeDL(dl_opts) as ydl:
                    ydl.download([url])

                arquivo = max(
                    [f for f in os.listdir(PASTA_VIDEOS) if f.endswith(".mp4")],
                    key=lambda f: os.path.getmtime(os.path.join(PASTA_VIDEOS, f))
                )
                atualizar_banco({"titulo": titulo, "arquivo": arquivo, "thumb": thumb})
                baixados.add(url)
                print(f"[OK] {titulo}")

            except Exception as e:
                print(f"[ERRO] {url}: {e}")
                baixados.add(url)

            remover_da_fila(url)

    except KeyboardInterrupt:
        limpar_tudo()

if __name__ == "__main__":
    monitorar()