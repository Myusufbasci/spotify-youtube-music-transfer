# spotify-youtube-music-transfer

[English](../../README.md) · [Türkçe](README.tr.md) · [Español](README.es.md) · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · [العربية](README.ar.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [日本語](README.ja.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · **Bahasa Indonesia** · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Українська](README.uk.md) · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

Transfer playlist dua arah & pencocokan lirik tanpa kunci API

Tempel tautan Spotify untuk dicocokkan di YouTube Music, atau tautan YouTube Music untuk dicocokkan di Spotify.

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

## Panduan Simpan ke Akun

### Simpan ke YouTube Music
1. **Salin Skrip Transfer YouTube Music** — Salin skrip konsol untuk membuat semua playlist di akun Anda sekaligus.
2. **Buka YouTube Music di Tab Baru** — Buka tab tempat Anda sudah login ke YouTube Music.
3. **Tempel di Console & Tekan Enter** — Tekan F12 → tab Console, tempel dengan Ctrl+V lalu tekan Enter. (Jika browser meminta izin saat pertama kali menempel, ketik allow pasting lalu tekan Enter.)

### Simpan ke Spotify
1. **Salin Tautan Lagu Spotify** — Aplikasi Spotify mendukung penempelan tautan lagu secara langsung ke dalam playlist.
2. **Buka Playlist Kosong di Spotify & Tekan Ctrl+V** — Buat playlist baru di Spotify, klik di dalamnya, dan tekan Ctrl+V.

## License

MIT
