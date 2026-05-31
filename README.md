# 📺 PlayLocal

YouTube local — busque vídeos, baixe automaticamente e assista no seu próprio player.

## Como funciona

[Busca no front] → [Flask busca no YouTube] → [Watcher baixa] → [Assiste offline]

## Requisitos

- [Docker](https://www.docker.com/products/docker-desktop) instalado

## Rodar

git clone https://github.com/seu-usuario/playlocal
cd playlocal
touch videos.json links.json   # Linux/Mac
echo [] > videos.json && echo {"urls":[]} > links.json  # Windows PowerShell
docker-compose up

Acesse: **http://localhost:8080**

## Como usar

1. Digite algo na barra de pesquisa (ex: `futebol`, `culinária`) e pressione Enter
2. Escolha os vídeos e clique em **Baixar** — eles entram na fila automaticamente
3. O Watcher (rodando em background no container) baixa um por um
4. Atualize a página e os vídeos aparecem prontos pra assistir

## Limite de armazenamento

- Máximo de **5 GB** de vídeos
- A barra no topo mostra quanto está sendo usado
- Use o botão 🗑 nos cards para excluir vídeos e liberar espaço

## Estrutura

playlocal/
├── docker-compose.yml  # Orquestra tudo
├── Dockerfile          # Imagem Python com Flask + pytubefix
├── start.sh            # Sobe Flask + Watcher juntos
├── server.py           # API Flask (busca, fila, delete, storage)
├── watcher.py          # Baixa vídeos da fila em background
├── playlocal.html         # Front-end
├── videos.json         # Banco de vídeos baixados
├── links.json          # Fila de downloads
└── videos/             # Arquivos .mp4

## Scanner manual (opcional)

Se preferir o scanner que detecta vídeos enquanto você navega no YouTube:

pip install selenium webdriver-manager
python scanner.py

Feito com Python, Flask, pytubefix