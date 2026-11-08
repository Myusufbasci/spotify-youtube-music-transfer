# spotify-youtube-music-transfer

[English](../../README.md) · [Türkçe](README.tr.md) · [Español](README.es.md) · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · [العربية](README.ar.md) · [Português](README.pt.md) · **Русский** · [日本語](README.ja.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Українська](README.uk.md) · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

Двунаправленный перенос плейлистов и поиск по тексту песен без API-ключей

Вставьте ссылки Spotify для поиска в YouTube Music или ссылки YouTube Music для поиска в Spotify.

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

## Инструкция по сохранению

### Сохранить в YouTube Music
1. **Скопируйте скрипт для YouTube Music** — Скопируйте консольный скрипт для автоматического создания плейлистов в вашем аккаунте.
2. **Откройте YouTube Music в новой вкладке** — Перейдите во вкладку с выполненным входом в YouTube Music.
3. **Вставьте в консоль и нажмите Enter** — Нажмите F12 → вкладка Console, вставьте через Ctrl+V и нажмите Enter. (Если браузер запросит разрешение при первой вставке, введите allow pasting и нажмите Enter.)

### Сохранить в Spotify
1. **Скопируйте ссылки на треки Spotify** — Приложение и веб-плеер Spotify поддерживают прямую вставку ссылок на треки в любой плейлист.
2. **Откройте пустой плейлист в Spotify и нажмите Ctrl+V** — Создайте новый плейлист в Spotify, кликните внутри списка и нажмите Ctrl+V.

## License

MIT
