# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | **Türkçe** | [Español](README.es.md) | [中文 (简体)](README.zh.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | [Polski](README.pl.md) | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | [Svenska](README.sv.md)

---

> API anahtarsız, çift yönlü çalma listesi ve şarkı sözü (lyrics) eşleştirme aracı

Spotify bağlantısı yapıştırırsanız YouTube Music'te; YouTube Music bağlantısı yapıştırırsanız Spotify'da (bire bir + şarkı sözleriyle) eşleştirir.

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

## Hesaba Kayıt Rehberi

### 1. YouTube Music'e Kayıt
1. **YouTube Music Aktarım Kodunu Kopyalayın:** Eşleştirilen çalma listelerini tek seferde oluşturacak konsol betiğini panoya kopyalayın.
2. **YouTube Music'i Yeni Sekmede Açın:** Oturumunuzun açık olduğu YouTube Music sekmesine geçin.
3. **Konsola Yapıştırıp Çalıştırın:** F12 → Console sekmesine tıklayın, Ctrl+V yapıp Enter'a basın. (İlk kez yapıştırıyorsanız tarayıcı uyarısı sonrası konsola allow pasting (veya yapıştırmaya izin ver) yazıp Enter'a basın.)

### 2. Spotify'a Kayıt
1. **Spotify Şarkı Bağlantılarını Kopyalayın:** Spotify masaüstü ve web uygulaması, kopyalanan şarkı bağlantılarını doğrudan çalma listesine yapıştırmayı destekler.
2. **Spotify'da Boş Bir Çalma Listesi Açıp Ctrl+V Yapın:** Spotify'da yeni bir çalma listesi oluşturun, listenin içine bir kez tıklayıp Ctrl+V (Yapıştır) tuşlarına basın.

---

## License

MIT
