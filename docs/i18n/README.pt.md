# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | [Türkçe](README.tr.md) | [Español](README.es.md) | [中文 (简体)](README.zh.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | **Português** | [Русский](README.ru.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | [Polski](README.pl.md) | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | [Svenska](README.sv.md)

---

> Motor bidirecional de transferência de playlists e correspondência por letras sem chave de API

Cole links do Spotify para buscar no YouTube Music, ou do YouTube Music para buscar no Spotify.

---

## Quick Start

```bash
git clone https://github.com/Myusufbasci/spotify-to-ytmusic.git
cd spotify-to-ytmusic

pip install -r requirements.txt
playwright install chromium
python app.py --web --port 5050
```

Open `http://127.0.0.1:5050` in your browser.

---

## Guia para Salvar na Conta

### 1. Salvar no YouTube Music
1. **Copie o Script do YouTube Music:** Copie o script de console que criará todas as playlists na sua conta.
2. **Abra o YouTube Music em Nova Aba:** Acesse uma aba onde você esteja conectado ao YouTube Music.
3. **Cole no Console e Pressione Enter:** Pressione F12 → aba Console, cole com Ctrl+V e pressione Enter. (Se o navegador pedir permissão na primeira vez, digite allow pasting e pressione Enter.)

### 2. Salvar no Spotify
1. **Copie os Links de Músicas do Spotify:** O aplicativo do Spotify permite colar links de músicas diretamente em qualquer playlist.
2. **Abra uma Playlist Vazia no Spotify e Pressione Ctrl+V:** Crie uma nova playlist no Spotify, clique dentro dela e pressione Ctrl+V.

---

## License

MIT
