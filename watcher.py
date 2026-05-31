import json
import os
import time
import shutil
import yt_dlp

PASTA_VIDEOS = "videos"
LINKS_JSON   = "links.json"
VIDEOS_JSON  = "videos.json"
LIMITE_BYTES = 5 * 1024 ** 3  # 5 GB

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

def limpar_tudo():
    print("\n[SISTEMA] Encerrando e limpando arquivos...")
    if os.path.exists(PASTA_VIDEOS):
        shutil.rmtree(PASTA_VIDEOS)
    for f in [VIDEOS_JSON, LINKS_JSON]:
        if os.path.exists(f):
            os.remove(f)
    print("[SISTEMA] Tudo limpo. Até logo!")

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

def monitorar():
    os.makedirs(PASTA_VIDEOS, exist_ok=True)
    baixados = set()

    print("[WATCHER] Monitorando... (Ctrl+C para sair e apagar tudo)")
    print(f"[WATCHER] Limite de armazenamento: 5 GB")

    try:
        while True:
            # Checa limite de disco antes de qualquer download
            atual = uso_disco()
            if atual >= LIMITE_BYTES:
                print(f"[WATCHER] Limite atingido ({gb(atual)} GB). Aguardando espaço ser liberado...")
                time.sleep(30)
                continue

            if not os.path.exists(LINKS_JSON):
                time.sleep(5)
                continue

            with open(LINKS_JSON, "r") as f:
                try:
                    urls = json.load(f).get("urls", [])
                except Exception:
                    urls = []

            links_restantes = []
            for url in urls:
                if url in baixados:
                    continue

                # Verifica espaço antes de cada download
                if uso_disco() >= LIMITE_BYTES:
                    print(f"[WATCHER] Limite atingido. Vídeo pulado: {url}")
                    links_restantes.append(url)
                    continue

                try:
                    info_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
                    with yt_dlp.YoutubeDL(info_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                    titulo = info.get("title", "video")
                    thumb  = info.get("thumbnail", "")
                    print(f"[DOWNLOAD] {titulo} ({gb(uso_disco())} GB usados)")

                    dl_opts = {
                        "quiet":      True,
                        "no_warnings": True,
                        "format":     "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                        "outtmpl":    os.path.join(PASTA_VIDEOS, "%(title)s.%(ext)s"),
                        "merge_output_format": "mp4",
                    }
                    with yt_dlp.YoutubeDL(dl_opts) as ydl:
                        ydl.download([url])

                    # Descobre o arquivo gerado
                    arquivo = max(
                        [f for f in os.listdir(PASTA_VIDEOS) if f.endswith(".mp4")],
                        key=lambda f: os.path.getmtime(os.path.join(PASTA_VIDEOS, f))
                    )
                    atualizar_banco({
                        "titulo":  titulo,
                        "arquivo": arquivo,
                        "thumb":   thumb,
                    })
                    baixados.add(url)
                    print(f"[OK] {titulo}")
                except Exception as e:
                    print(f"[ERRO] {url}: {e}")
                    links_restantes.append(url)

            with open(LINKS_JSON, "w") as f:
                json.dump({"urls": links_restantes}, f, indent=4)

            time.sleep(5)

    except KeyboardInterrupt:
        limpar_tudo()

if __name__ == "__main__":
    monitorar()