/* =========================================
   PlayLocal — app.js
   ========================================= */

'use strict';

/* ── STATE ── */
var videos   = [];
var idxAtivo = -1;
var toastTimer;


/* ─────────────────────────────────────────
   SKELETON
───────────────────────────────────────── */
function mkSkeleton() {
    return '<div class="card">'
         +   '<div class="thumb-wrap sk sk-thumb"></div>'
         +   '<div class="card-info">'
         +     '<div class="sk sk-line"></div>'
         +     '<div class="sk sk-line w6"></div>'
         +     '<div class="sk sk-line w4"></div>'
         +   '</div>'
         + '</div>';
}


/* ─────────────────────────────────────────
   BUILD — VIDEO CARD (grade principal)
───────────────────────────────────────── */
function mkCard(v, i) {
    var nome    = v.titulo || v.arquivo || 'Vídeo ' + (i + 1);
    var arquivo = v.arquivo || '';

    var el = document.createElement('div');
    el.className = 'card';
    el.innerHTML =
        '<div class="thumb-wrap">'
      +   '<img src="' + (v.thumb || '') + '" alt="" onerror="this.style.display=\'none\'">'
      +   '<div class="play-ov"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div>'
      +   (v.duracao ? '<span class="dur">' + v.duracao + '</span>' : '')
      +   '<button class="del-btn" title="Excluir vídeo">'
      +     '<svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>'
      +   '</button>'
      + '</div>'
      + '<div class="card-info">'
      +   '<div class="card-title">' + nome + '</div>'
      + '</div>';

    el.querySelector('.del-btn').addEventListener('click', function(e) {
        e.stopPropagation();
        excluir(arquivo);
    });
    el.addEventListener('click', function() { abrir(v, i); });

    return el;
}


/* ─────────────────────────────────────────
   BUILD — SIDEBAR ITEM (player lateral)
───────────────────────────────────────── */
function mkItem(v, i) {
    var nome  = v.titulo || v.arquivo || 'Vídeo ' + (i + 1);
    var ativo = (i === idxAtivo);

    var el = document.createElement('div');
    el.className = 'li' + (ativo ? ' ativo' : '');
    el.id = 'li' + i;
    el.innerHTML =
        '<div class="li-thumb">'
      +   '<img src="' + (v.thumb || '') + '" alt="" onerror="this.style.display=\'none\'">'
      +   (v.duracao ? '<span class="li-dur">' + v.duracao + '</span>' : '')
      + '</div>'
      + '<div class="li-info">'
      +   '<div class="li-title">' + nome + '</div>'
      +   (ativo ? '<div class="li-now">▶ Reproduzindo</div>' : '')
      + '</div>';

    if (!ativo) {
        el.addEventListener('click', function() { abrir(v, i); });
    }
    return el;
}


/* ─────────────────────────────────────────
   RENDER
───────────────────────────────────────── */
function renderGrid() {
    var grid = document.getElementById('grid');
    grid.innerHTML = '';

    if (!videos.length) {
        grid.innerHTML =
            '<div class="empty">'
          +   '<svg viewBox="0 0 24 24"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/></svg>'
          +   '<p>Nenhum vídeo. Use a busca para baixar.</p>'
          + '</div>';
    } else {
        var frag = document.createDocumentFragment();
        videos.forEach(function(v, i) { frag.appendChild(mkCard(v, i)); });
        grid.appendChild(frag);
    }

    document.getElementById('count').textContent =
        videos.length ? videos.length + ' vídeo' + (videos.length !== 1 ? 's' : '') : '';
}

function renderSidebar() {
    var sc = document.getElementById('pl-scroll');
    sc.innerHTML = '';
    var frag = document.createDocumentFragment();
    videos.forEach(function(v, i) { frag.appendChild(mkItem(v, i)); });
    sc.appendChild(frag);

    var active = document.getElementById('li' + idxAtivo);
    if (active) active.scrollIntoView({ block: 'nearest' });
}


/* ─────────────────────────────────────────
   DATA — carrega / storage
───────────────────────────────────────── */
async function carregar() {
    try {
        var r = await fetch('/videos.json');
        videos = await r.json();
    } catch (e) {
        videos = [];
    }
    renderGrid();
    atualizarStorage();
}

async function atualizarStorage() {
    try {
        var r    = await fetch('/api/storage');
        var data = await r.json();
        var pct  = Math.min(data.pct, 100);

        var fill = document.getElementById('storage-fill');
        fill.style.width = pct + '%';
        fill.className   = 'storage-fill' + (pct >= 95 ? ' full' : pct >= 75 ? ' warn' : '');
        document.getElementById('storage-label').textContent = data.gb + ' / 5 GB';
    } catch (e) { /* servidor offline */ }
}


/* ─────────────────────────────────────────
   ACTIONS — excluir
───────────────────────────────────────── */
async function excluir(arquivo) {
    if (!confirm('Excluir "' + arquivo + '"?')) return;
    await fetch('/api/delete/' + encodeURIComponent(arquivo), { method: 'DELETE' });
    await carregar();
}

async function excluirTudo() {
    if (!videos.length) return;
    if (!confirm('Excluir TODOS os ' + videos.length + ' vídeos? Essa ação não tem volta.')) return;

    for (var i = 0; i < videos.length; i++) {
        await fetch('/api/delete/' + encodeURIComponent(videos[i].arquivo), { method: 'DELETE' });
    }
    await carregar();
    toast('🗑 Todos os vídeos foram excluídos');
}


/* ─────────────────────────────────────────
   BUSCA YOUTUBE
───────────────────────────────────────── */
async function buscarYT() {
    var q = document.getElementById('busca').value.trim();
    if (!q) return;

    document.getElementById('search-box-title').textContent = 'Resultados: "' + q + '"';
    document.getElementById('search-results').innerHTML = '';
    document.getElementById('search-loading').classList.add('show');
    document.getElementById('search-modal').classList.add('open');

    try {
        var r     = await fetch('/api/search?q=' + encodeURIComponent(q) + '&limit=20');
        var itens = await r.json();
        document.getElementById('search-loading').classList.remove('show');

        if (!itens.length || itens.erro) {
            document.getElementById('search-results').innerHTML =
                '<div style="padding:40px;text-align:center;color:#555;font-size:14px;">Nenhum resultado encontrado.</div>';
            return;
        }

        var frag = document.createDocumentFragment();
        itens.forEach(function(v) {
            var item  = document.createElement('div');
            item.className = 'result-item';

            var btn = document.createElement('button');
            btn.className = 'dl-btn';
            btn.innerHTML =
                '<svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>'
              + 'Baixar';

            item.innerHTML =
                '<div class="result-thumb">'
              +   '<img src="' + (v.thumb || '') + '" alt="" onerror="this.style.display=\'none\'">'
              +   (v.duracao ? '<span class="result-dur">' + v.duracao + '</span>' : '')
              + '</div>'
              + '<div class="result-info"><div class="result-title">' + v.titulo + '</div></div>';
            item.appendChild(btn);

            btn.addEventListener('click', async function() {
                btn.disabled  = true;
                btn.innerHTML = '⏳ Na fila...';
                try {
                    var res  = await fetch('/api/queue', {
                        method:  'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body:    JSON.stringify({ url: v.url })
                    });
                    var data = await res.json();
                    if (data.erro) {
                        btn.innerHTML = '⚠ ' + data.erro;
                    } else {
                        btn.innerHTML = '✓ Adicionado';
                        toast('📥 "' + v.titulo.slice(0, 40) + '..." adicionado à fila');
                    }
                } catch (err) {
                    btn.disabled  = false;
                    btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>Baixar';
                }
            });

            frag.appendChild(item);
        });
        document.getElementById('search-results').appendChild(frag);

    } catch (e) {
        document.getElementById('search-loading').classList.remove('show');
        document.getElementById('search-results').innerHTML =
            '<div style="padding:40px;text-align:center;color:#555;font-size:14px;">Erro ao buscar. Verifique o servidor.</div>';
    }
}

function fecharBusca() {
    document.getElementById('search-modal').classList.remove('open');
}


/* ─────────────────────────────────────────
   PLAYER
───────────────────────────────────────── */
function abrir(v, i) {
    idxAtivo = i;
    document.getElementById('p-title').textContent = v.titulo || v.arquivo || 'Vídeo';
    document.getElementById('p-sub').textContent   = v.duracao ? 'Duração: ' + v.duracao : '';

    var player = document.getElementById('player');
    player.src = '/videos/' + v.arquivo;
    player.play();

    document.getElementById('tela-player').classList.add('aberta');
    document.body.style.overflow = 'hidden';
    renderSidebar();
}

function fechar() {
    var player = document.getElementById('player');
    player.pause();
    player.removeAttribute('src');
    player.load();
    idxAtivo = -1;

    document.getElementById('tela-player').classList.remove('aberta');
    document.body.style.overflow = '';
}


/* ─────────────────────────────────────────
   TOAST
───────────────────────────────────────── */
function toast(msg) {
    var el = document.getElementById('toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function() { el.classList.remove('show'); }, 3000);
}


/* ─────────────────────────────────────────
   EVENTOS GLOBAIS
───────────────────────────────────────── */
document.getElementById('busca').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') buscarYT();
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') { fecharBusca(); fechar(); }
});

document.getElementById('search-modal').addEventListener('click', function(e) {
    if (e.target === this) fecharBusca();
});


/* ─────────────────────────────────────────
   INIT
───────────────────────────────────────── */
document.getElementById('grid').innerHTML = Array(8).fill(mkSkeleton()).join('');
carregar();
iniciarPollStatus();


/* ─────────────────────────────────────────
   DOWNLOAD PANEL
───────────────────────────────────────── */
var dlPollTimer = null;

function iniciarPollStatus() {
    if (dlPollTimer) return;
    dlPollTimer = setInterval(atualizarDownloadPanel, 2000);
    atualizarDownloadPanel(); // imediato
}

async function atualizarDownloadPanel() {
    try {
        var r    = await fetch('/api/queue_status');
        var data = await r.json();
        var panel = document.getElementById('dl-panel');

        if (!data.ativo) {
            panel.classList.remove('show');
            // Se terminou um download, atualiza a grade
            if (panel.dataset.wasActive === 'true') {
                panel.dataset.wasActive = 'false';
                carregar();
            }
            return;
        }

        panel.dataset.wasActive = 'true';
        panel.classList.add('show');

        document.getElementById('dl-pct-text').textContent = (data.pct || 0) + '%';
        document.getElementById('dl-eta').textContent      = data.eta || '–';
        document.getElementById('dl-speed').textContent    = data.velocidade || '–';
        document.getElementById('dl-fill').style.width     = (data.pct || 0) + '%';
        document.getElementById('dl-title').textContent    = data.titulo || '';
        document.getElementById('dl-fila').textContent     = data.fila > 0 ? data.fila + ' na fila' : '';

        var img = document.getElementById('dl-thumb-img');
        if (data.thumb && img.src !== data.thumb) img.src = data.thumb;

    } catch (e) { /* servidor offline */ }
}