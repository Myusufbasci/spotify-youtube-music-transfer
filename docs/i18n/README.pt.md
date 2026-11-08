# spotify-youtube-music-transfer

[English](../../README.md) · [Türkçe](README.tr.md) · [Español](README.es.md) · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · [العربية](README.ar.md) · **Português** · [Русский](README.ru.md) · [日本語](README.ja.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Українська](README.uk.md) · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

Motor bidirecional de transferência de playlists e correspondência por letras sem chave de API

Cole links do Spotify para buscar no YouTube Music, ou do YouTube Music para buscar no Spotify.

![Web UI Preview](../preview.png)

## Quick Start

- **Windows (.exe):** [https://github.com/Myusufbasci/spotify-youtube-music-transfer/releases/latest](https://github.com/Myusufbasci/spotify-youtube-music-transfer/releases/latest) → `Spotify-YouTube-Music-Transfer.exe`
- **Windows (Script):** `Start-Windows.bat`
- **macOS / Linux:** `start-mac-linux.command`

```bash
git clone https://github.com/Myusufbasci/spotify-youtube-music-transfer.git
cd spotify-youtube-music-transfer

pip install -r requirements.txt
python app.py --web --open --port 5050
```

## Guia para Salvar na Conta

### Salvar no YouTube Music
1. **Copie o Script do YouTube Music** — Copie o script de console que criará todas as playlists na sua conta.
2. **Abra o YouTube Music em Nova Aba** — Acesse uma aba onde você esteja conectado ao YouTube Music.
3. **Cole no Console e Pressione Enter** — Pressione F12 → aba Console, cole com Ctrl+V e pressione Enter. (Se o navegador pedir permissão na primeira vez, digite allow pasting e pressione Enter.)

### Salvar no Spotify
1. **Copie os Links de Músicas do Spotify** — O aplicativo do Spotify permite colar links de músicas diretamente em qualquer playlist.
2. **Abra uma Playlist Vazia no Spotify e Pressione Ctrl+V** — Crie uma nova playlist no Spotify, clique dentro dela e pressione Ctrl+V.

## License

MIT
