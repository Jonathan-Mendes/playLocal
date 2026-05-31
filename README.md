# 📺 PlayLocal

> YouTube local — busque vídeos, baixe automaticamente e assista no seu próprio player.

## Como funciona

```
[Busca no front] → [Flask busca no YouTube] → [Watcher baixa] → [Assiste offline]
```

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado

## Rodar

```bash
git clone https://github.com/seu-usuario/playlocal
cd playlocal
docker-compose up --build
```

Acesse: **http://localhost:8080**

---

## Como usar

1. Digite algo na barra de pesquisa (ex: `futebol`, `culinária`) e pressione **Enter**
2. Escolha os vídeos e clique em **Baixar** — entram na fila automaticamente
3. O Watcher (rodando em background no container) baixa um por um
4. Clique em **Atualizar** e os vídeos aparecem prontos pra assistir

---

## Qualidade dos downloads

O padrão é **720p**, mas você pode alterar no topo do `watcher.py`:

```python
# Descomente a linha que quiser:
# QUALIDADE = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"      # Melhor qualidade
# QUALIDADE = "bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]" # Full HD
QUALIDADE = "bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720]"     # HD 720p (padrão)
# QUALIDADE = "bestvideo[height<=480][ext=mp4]+bestaudio/best[height<=480]"   # 480p
```

Após alterar, rode `docker-compose up --build` para aplicar.

---

## Limite de armazenamento

- Máximo de **5 GB** de vídeos
- A barra no topo mostra o uso em tempo real
- Botão 🗑 em cada card para excluir individualmente
- Botão **Excluir tudo** no header para limpar tudo de uma vez

---

## Estrutura

```
playlocal/
├── docker-compose.yml   # Orquestra tudo
├── Dockerfile           # Imagem Python com Flask + yt-dlp + ffmpeg
├── server.py            # API Flask (busca, fila, delete, storage)
├── watcher.py           # Baixa vídeos da fila em background
├── playlocal.html       # Front-end
├── static/
│   ├── css/style.css    # Estilos
│   ├── js/app.js        # Lógica do front
│   └── img/favicon.svg  # Ícone
├── videos.json          # Banco de vídeos baixados
├── links.json           # Fila de downloads
├── queue_status.json    # Status do download em tempo real
└── videos/              # Arquivos .mp4
```

---

## Scanner manual (opcional)

Se preferir capturar vídeos enquanto navega no YouTube:

```bash
pip install selenium webdriver-manager
python scanner.py
```

---

Feito com Python, Flask, [yt-dlp](https://github.com/yt-dlp/yt-dlp) e ffmpeg