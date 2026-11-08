# spotify-youtube-music-transfer

[English](../../README.md) · [Türkçe](README.tr.md) · [Español](README.es.md) · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · [العربية](README.ar.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [日本語](README.ja.md) · [Deutsch](README.de.md) · **Français** · [한국어](README.ko.md) · [Italiano](README.it.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Українська](README.uk.md) · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

Transfert bidirectionnel de playlists et correspondance par paroles sans clé API

Collez des liens Spotify pour chercher sur YouTube Music, ou des liens YouTube Music pour chercher sur Spotify.

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

## Guide d'enregistrement

### Enregistrer sur YouTube Music
1. **Copier le script YouTube Music** — Copiez le script console qui créera automatiquement vos playlists.
2. **Ouvrir YouTube Music dans un nouvel onglet** — Allez sur un onglet connecté à votre compte YouTube Music.
3. **Coller dans la Console et appuyer sur Entrée** — Appuyez sur F12 → onglet Console, collez avec Ctrl+V et validez avec Entrée. (Si le navigateur demande une confirmation, tapez allow pasting puis Entrée.)

### Enregistrer sur Spotify
1. **Copier les liens de titres Spotify** — Spotify permet de coller directement une liste de liens dans n'importe quelle playlist.
2. **Ouvrir une playlist vide sur Spotify et faire Ctrl+V** — Créez une nouvelle playlist dans Spotify, cliquez dedans et faites Ctrl+V.

## License

MIT
