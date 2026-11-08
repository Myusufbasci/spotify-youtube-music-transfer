# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | [Türkçe](README.tr.md) | [Español](README.es.md) | [中文 (简体)](README.zh.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [Português](README.pt.md) | **Русский** | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | [Polski](README.pl.md) | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | [Svenska](README.sv.md)

---

> Двунаправленный перенос плейлистов и поиск по тексту песен без API-ключей

Вставьте ссылки Spotify для поиска в YouTube Music или ссылки YouTube Music для поиска в Spotify.

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

## Инструкция по сохранению

### 1. Сохранить в YouTube Music
1. **Скопируйте скрипт для YouTube Music:** Скопируйте консольный скрипт для автоматического создания плейлистов в вашем аккаунте.
2. **Откройте YouTube Music в новой вкладке:** Перейдите во вкладку с выполненным входом в YouTube Music.
3. **Вставьте в консоль и нажмите Enter:** Нажмите F12 → вкладка Console, вставьте через Ctrl+V и нажмите Enter. (Если браузер запросит разрешение при первой вставке, введите allow pasting и нажмите Enter.)

### 2. Сохранить в Spotify
1. **Скопируйте ссылки на треки Spotify:** Приложение и веб-плеер Spotify поддерживают прямую вставку ссылок на треки в любой плейлист.
2. **Откройте пустой плейлист в Spotify и нажмите Ctrl+V:** Создайте новый плейлист в Spotify, кликните внутри списка и нажмите Ctrl+V.

---

## License

MIT
