# spotify-youtube-music-transfer

[English](../../README.md) · [Türkçe](README.tr.md) · [Español](README.es.md) · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · **العربية** · [Português](README.pt.md) · [Русский](README.ru.md) · [日本語](README.ja.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Українська](README.uk.md) · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

أداة نقل قوائم التشغيل ثنائية الاتجاه والمطابقة عبر كلمات الأغاني بدون مفتاح API

الصق روابط Spotify للمطابقة على YouTube Music، أو روابط YouTube Music للمطابقة على Spotify.

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

## دليل الحفظ في الحساب

### الحفظ في YouTube Music
1. **انسخ كود النقل إلى YouTube Music** — انسخ كود وحدة التحكم الذي سينشئ قوائم التشغيل في حسابك دفعة واحدة.
2. **افتح YouTube Music في علامة تبويب جديدة** — انتقل إلى علامة التبويب المسجل دخولك فيها إلى YouTube Music.
3. **الصق في Console واضغط Enter** — اضغط F12 ← اختر Console، ثم الصق عبر Ctrl+V واضغط Enter. (إذا طلب المتصفح إذن اللصق لأول مرة، اكتب allow pasting واضغط Enter.)

### الحفظ في Spotify
1. **انسخ روابط أغاني Spotify** — يدعم تطبيق Spotify لصق روابط الأغاني المنسوخة مباشرة داخل أي قائمة تشغيل.
2. **افتح قائمة فارغة في Spotify واضغط Ctrl+V** — أنشئ قائمة تشغيل جديدة في Spotify واضغط بداخلها ثم Ctrl+V لإضافة جميع الأغاني.

## License

MIT
