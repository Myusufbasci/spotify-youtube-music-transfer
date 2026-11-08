# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | [Türkçe](README.tr.md) | [Español](README.es.md) | [中文 (简体)](README.zh.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | **Deutsch** | [Français](README.fr.md) | [한국어](README.ko.md) | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | [Polski](README.pl.md) | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | [Svenska](README.sv.md)

---

> Bidirektionaler Playlist-Transfer & Songtext-Abgleich ohne API-Schlüssel

Spotify-Links einfügen für YouTube Music-Abgleich, oder YouTube Music-Links für Spotify-Abgleich.

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

## Anleitung zum Speichern

### 1. In YouTube Music speichern
1. **YouTube Music Transfer-Skript kopieren:** Kopiere das Konsolen-Skript, das alle Playlists in deinem Konto erstellt.
2. **YouTube Music in neuem Tab öffnen:** Wechsle zu einem Tab, in dem du bei YouTube Music angemeldet bist.
3. **In die Konsole einfügen & Enter drücken:** Drücke F12 → Tab Console, füge mit Ctrl+V ein und drücke Enter. (Falls der Browser beim ersten Mal fragt, tippe allow pasting ein und drücke Enter.)

### 2. In Spotify speichern
1. **Spotify Song-Links kopieren:** Spotify unterstützt das direkte Einfügen kopierter Song-Links in jede Playlist.
2. **Leere Playlist in Spotify öffnen & Ctrl+V drücken:** Erstelle eine neue Playlist in Spotify, klicke hinein und drücke Ctrl+V.

---

## License

MIT
