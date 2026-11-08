# spotify-youtube-music-transfer

**English** · [Türkçe](docs/i18n/README.tr.md) · [Español](docs/i18n/README.es.md) · [中文 (简体)](docs/i18n/README.zh.md) · [हिन्दी](docs/i18n/README.hi.md) · [العربية](docs/i18n/README.ar.md) · [Português](docs/i18n/README.pt.md) · [Русский](docs/i18n/README.ru.md) · [日本語](docs/i18n/README.ja.md) · [Deutsch](docs/i18n/README.de.md) · [Français](docs/i18n/README.fr.md) · [한국어](docs/i18n/README.ko.md) · [Italiano](docs/i18n/README.it.md) · [Bahasa Indonesia](docs/i18n/README.id.md) · [Tiếng Việt](docs/i18n/README.vi.md) · [Polski](docs/i18n/README.pl.md) · [Українська](docs/i18n/README.uk.md) · [Nederlands](docs/i18n/README.nl.md) · [ไทย](docs/i18n/README.th.md) · [Svenska](docs/i18n/README.sv.md)

Bi-directional playlist transfer between **Spotify** and **YouTube Music** (`Spotify ↔ YouTube Music`) with lyrics-based fallback matching. No API keys, OAuth developer apps, or paid subscriptions required.

![Web UI Preview](docs/preview.png)

## Why?

Most playlist converters fail in two ways:
1. They require you to register developer applications on Spotify and Google Cloud just to move a few playlists.
2. They rely purely on `Title + Artist` string matching. When a song is uploaded under a different title, a pseudo-artist name (common for unreleased/removed tracks on Spotify), or as a local file, standard tools either skip it or match a random cover/backing track.

This tool reads full playlists directly (bypassing Spotify's 100-track embed limit via Pathfinder GraphQL pagination using your existing Edge/Chrome browser) and falls back to **lyrics matching** (`LRCLIB`, embedded YouTube Music lyrics, and web search) when metadata matching is uncertain.

| Feature | Standard Tools | `spotify-youtube-music-transfer` |
| :--- | :--- | :--- |
| Spotify / Google API Keys | Required | **None** |
| Playlists over 100 tracks | Truncated without OAuth | **Full pagination** |
| Direction | Often one-way | **Spotify ↔ YouTube Music** |
| Renamed / Pseudo-artist tracks | Skipped or wrong cover | **Lyrics fallback verification** |
| Setup for non-technical users | Terminal + `pip` + Chromium | **Single `.exe` or `Start-Windows.bat`** |

## Quick Start (No Python or Terminal Required)

### Option A: Standalone Windows `.exe`
Download **`Spotify-YouTube-Music-Transfer.exe`** from [**Releases**](https://github.com/Myusufbasci/spotify-youtube-music-transfer/releases/latest) and double-click it. Your browser will open `http://127.0.0.1:5050` automatically.

### Option B: One-Click Launcher (Windows / macOS / Linux)
1. Click **`Code` → `Download ZIP`** and extract the folder.
2. On Windows, double-click **`Start-Windows.bat`** (auto-installs Python via `winget` if missing, installs dependencies, and opens the Web UI).
3. On macOS / Linux, double-click **`start-mac-linux.command`**.

### Option C: Developer / CLI Setup

```bash
git clone https://github.com/Myusufbasci/spotify-youtube-music-transfer.git
cd spotify-youtube-music-transfer

pip install -r requirements.txt
python app.py --web --open --port 5050
```

CLI batch mode:

```bash
python app.py "https://open.spotify.com/playlist/..." "https://music.youtube.com/playlist?list=..."
```

## How It Works

1. **Direct Pass:** Queries the target catalog (`Official Songs` prioritized over user videos), scoring title similarity, channel/artist match, and track duration while penalizing unrequested covers, instrumentals, or karaoke tracks.
2. **Lyrics Pass (Fallback):** If a track scores below the confidence threshold, the matcher fetches its lyrics, extracts distinctive lines, queries the target platform by lyrics, and cross-checks lyric similarity using `rapidfuzz`.
3. **Browser-Native Saving:**
   - **To YouTube Music:** Generates a self-contained console snippet that calls YouTube Music's internal `playlist/create` endpoint directly from your signed-in browser tab, plus login-free playback queue links.
   - **To Spotify:** Copies matched `open.spotify.com/track/...` URLs to your clipboard so you can paste (`Ctrl+V`) them directly into any Spotify playlist.

## Project Structure

- `Start-Windows.bat` / `start-mac-linux.command` — Double-click launchers with automatic setup
- `app.py` — Flask web UI (20 languages, default English) and CLI runner
- `spotify_scraper.py` — Keyless Spotify playlist/album/track reader (Pathfinder GraphQL & Embed)
- `lyrics_matcher.py` — Spotify → YouTube Music matcher with LRCLIB / YTMusic lyrics verification
- `ytm_to_spotify.py` — YouTube Music → Spotify reader and Pathfinder search matcher
- `ytmusic_saver.py` — Queue link builder and optional Playwright session helper
- `i18n.py` — UI translations for 20 languages

## License

MIT
