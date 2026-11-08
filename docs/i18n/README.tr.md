# spotify-youtube-music-transfer

[English](../../README.md) · **Türkçe** · [Español](README.es.md) · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · [العربية](README.ar.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [日本語](README.ja.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Українська](README.uk.md) · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

API anahtarsız, çift yönlü çalma listesi ve şarkı sözü (lyrics) eşleştirme aracı

Spotify bağlantısı yapıştırırsanız YouTube Music'te; YouTube Music bağlantısı yapıştırırsanız Spotify'da (bire bir + şarkı sözleriyle) eşleştirir.

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

## Hesaba Kayıt Rehberi

### YouTube Music'e Kayıt
1. **YouTube Music Aktarım Kodunu Kopyalayın** — Eşleştirilen çalma listelerini tek seferde oluşturacak konsol betiğini panoya kopyalayın.
2. **YouTube Music'i Yeni Sekmede Açın** — Oturumunuzun açık olduğu YouTube Music sekmesine geçin.
3. **Konsola Yapıştırıp Çalıştırın** — F12 → Console sekmesine tıklayın, Ctrl+V yapıp Enter'a basın. (İlk kez yapıştırıyorsanız tarayıcı uyarısı sonrası konsola allow pasting (veya yapıştırmaya izin ver) yazıp Enter'a basın.)

### Spotify'a Kayıt
1. **Spotify Şarkı Bağlantılarını Kopyalayın** — Spotify masaüstü ve web uygulaması, kopyalanan şarkı bağlantılarını doğrudan çalma listesine yapıştırmayı destekler.
2. **Spotify'da Boş Bir Çalma Listesi Açıp Ctrl+V Yapın** — Spotify'da yeni bir çalma listesi oluşturun, listenin içine bir kez tıklayıp Ctrl+V (Yapıştır) tuşlarına basın.

## License

MIT
