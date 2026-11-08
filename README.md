# Spotify ↔ YouTube Music (Lyrics-Aware Bi-Directional Transfer)

**Languages:** **English** | [Türkçe](docs/i18n/README.tr.md) | [Español](docs/i18n/README.es.md) | [中文 (简体)](docs/i18n/README.zh.md) | [हिन्दी](docs/i18n/README.hi.md) | [العربية](docs/i18n/README.ar.md) | [Português](docs/i18n/README.pt.md) | [Русский](docs/i18n/README.ru.md) | [日本語](docs/i18n/README.ja.md) | [Deutsch](docs/i18n/README.de.md) | [Français](docs/i18n/README.fr.md) | [한국어](docs/i18n/README.ko.md) | [Italiano](docs/i18n/README.it.md) | [Bahasa Indonesia](docs/i18n/README.id.md) | [Tiếng Việt](docs/i18n/README.vi.md) | [Polski](docs/i18n/README.pl.md) | [Українська](docs/i18n/README.uk.md) | [Nederlands](docs/i18n/README.nl.md) | [ไทย](docs/i18n/README.th.md) | [Svenska](docs/i18n/README.sv.md)

---

An open-source, **zero-API-key**, bi-directional playlist transfer tool between **Spotify** and **YouTube Music**. When a track cannot be matched directly by title and artist—or when it has been re-uploaded under a pseudo-artist name, renamed, or added as a local file—the engine automatically fetches the track's **lyrics** (`LRCLIB`, embedded `YouTube Music` lyrics, `Lyrics.ovh`, and web search) and verifies the match using lyric snippets.

---

## Key Features

- **Bi-Directional Transfer (`Spotify ↔ YouTube Music`):**
  - Automatically detects whether the pasted URL is from Spotify or YouTube / YouTube Music and switches the matching direction accordingly.
- **Zero API Keys Required:**
  - No Spotify Developer client credentials or Google Cloud OAuth setup needed.
  - Bypasses the 100-track embed limit using Spotify Pathfinder GraphQL pagination to fetch 1,000+ track playlists in seconds.
- **Lyrics-Aware Fallback Matching:**
  - If direct title/artist matching yields low confidence, the engine fetches the song's full lyrics, extracts distinctive lyric lines, searches the target platform by lyrics, and verifies text similarity (`rapidfuzz`).
  - Handles local files (`Artist - Track` in title) and tracks re-uploaded under unofficial/pseudo-artist names.
- **20 Built-in UI Languages:**
  - English (default), Turkish, Spanish, Simplified Chinese, Hindi, Arabic (RTL), Portuguese, Russian, Japanese, German, French, Korean, Italian, Indonesian, Vietnamese, Polish, Ukrainian, Dutch, Thai, and Swedish.
- **One-Step Account Saving in Your Existing Browser:**
  - **Save to YouTube Music:** Copy a one-time console script that creates all matched playlists directly inside your signed-in `music.youtube.com` tab in seconds, or open instant YouTube playback queues without signing in.
  - **Save to Spotify:** Copy all matched Spotify track URLs with one click and press `Ctrl+V` directly inside any empty playlist in the Spotify desktop or web app.

---

## Installation

```bash
git clone https://github.com/Myusufbasci/spotify-to-ytmusic.git
cd spotify-to-ytmusic

pip install -r requirements.txt
playwright install chromium
```

---

## Usage

### 1. Web UI (Recommended)

```bash
python app.py --web --port 5050
```

Open `http://127.0.0.1:5050` in your browser:
1. Paste one or more **Spotify** or **YouTube Music** playlist URLs in the left panel and click **Scan & Match Tracks**.
2. Follow the **Account Save Guide** on the right panel to save your playlists to YouTube Music or Spotify in seconds.

### 2. Command-Line Interface (CLI)

```bash
python app.py "https://open.spotify.com/playlist/..." "https://music.youtube.com/playlist?list=..."
```

---

## Project Structure

| File | Description |
| :--- | :--- |
| `app.py` | Flask web application (with 20-language UI) and CLI entry point |
| `i18n.py` | Internationalization dictionary for 20 languages |
| `spotify_scraper.py` | Zero-API-key Spotify Playlist/Album/Track scraper (Pathfinder GraphQL & Embed) |
| `lyrics_matcher.py` | Spotify → YouTube Music direct & lyrics-aware matching engine |
| `ytm_to_spotify.py` | YouTube Music → Spotify scraper, Pathfinder search, and lyrics verification engine |
| `ytmusic_saver.py` | Instant YouTube playback queue generator and browser session helper |

---

## License

MIT
