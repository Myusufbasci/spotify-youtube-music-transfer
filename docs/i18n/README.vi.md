# spotify-youtube-music-transfer

[English](../../README.md) · [Türkçe](README.tr.md) · [Español](README.es.md) · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · [العربية](README.ar.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [日本語](README.ja.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · [Bahasa Indonesia](README.id.md) · **Tiếng Việt** · [Polski](README.pl.md) · [Українська](README.uk.md) · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

Chuyển đổi danh sách phát hai chiều & khớp lời bài hát không cần API key

Dán link Spotify để tìm trên YouTube Music, hoặc link YouTube Music để tìm trên Spotify.

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

## Hướng dẫn lưu vào tài khoản

### Lưu vào YouTube Music
1. **Sao chép mã chuyển YouTube Music** — Sao chép đoạn mã console giúp tạo toàn bộ danh sách phát trong tài khoản của bạn.
2. **Mở YouTube Music trong tab mới** — Chuyển sang tab trình duyệt đã đăng nhập YouTube Music.
3. **Dán vào Console & nhấn Enter** — Nhấn F12 → tab Console, dán bằng Ctrl+V và nhấn Enter. (Nếu trình duyệt hỏi quyền dán lần đầu, hãy gõ allow pasting rồi nhấn Enter.)

### Lưu vào Spotify
1. **Sao chép liên kết bài hát Spotify** — Ứng dụng Spotify hỗ trợ dán trực tiếp danh sách liên kết bài hát vào bất kỳ playlist nào.
2. **Mở playlist trống trên Spotify & nhấn Ctrl+V** — Tạo một playlist mới trên Spotify, nhấp vào bên trong và nhấn Ctrl+V.

## License

MIT
