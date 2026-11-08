# spotify-youtube-music-transfer

[English](../../README.md) · [Türkçe](README.tr.md) · [Español](README.es.md) · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · [العربية](README.ar.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [日本語](README.ja.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · **Українська** · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

Двостороннє перенесення плейлистів та пошук за текстом пісень без API-ключів

Вставте посилання Spotify для пошуку в YouTube Music або посилання YouTube Music для пошуку в Spotify.

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

## Інструкція зі збереження

### Зберегти в YouTube Music
1. **Скопіюйте скрипт для YouTube Music** — Скопіюйте консольний скрипт, який створить плейлисти у вашому акаунті.
2. **Відкрийте YouTube Music у новій вкладці** — Перейдіть до вкладки з виконаним входом у YouTube Music.
3. **Вставте в консоль і натисніть Enter** — Натисніть F12 → вкладка Console, вставте через Ctrl+V і натисніть Enter. (Якщо браузер попросить дозвіл при першій вставці, введіть allow pasting і натисніть Enter.)

### Зберегти в Spotify
1. **Скопіюйте посилання на треки Spotify** — Додаток Spotify підтримує пряму вставку скопійованих посилань у будь-який плейлист.
2. **Відкрийте порожній плейлист у Spotify та натисніть Ctrl+V** — Створіть новий плейлист у Spotify, клікніть всередині та натисніть Ctrl+V.

## License

MIT
