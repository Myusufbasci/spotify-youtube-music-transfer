# Spotify ↔ YouTube Music (Lyrics-Aware Bi-Directional Transfer)

API anahtarı, geliştirici hesabı veya ücretli abonelik gerektirmeden **Spotify** ve **YouTube Music** arasında çift yönlü çalma listesi aktarımı yapan; bire bir bulunamayan, adı değişmiş veya farklı/sahte sanatçı adıyla yüklenmiş şarkıları **şarkı sözleriyle (lyrics)** yakalayıp doğrulayan açık kaynaklı bir araçtır.

---

## Özellikler

- **Çift Yönlü Aktarım (`Spotify ↔ YouTube Music`):**
  - Yapıştırılan bağlantının Spotify mı yoksa YouTube / YouTube Music mi olduğunu otomatik algılar.
- **Sıfır API Anahtarı (Zero-API-Key):**
  - Spotify Developer veya Google Cloud API anahtarı istemez.
  - 100 şarkı sınırına takılmadan büyük listelerin tamamını (GraphQL sayfalama ile) saniyeler içinde çeker.
- **Şarkı Sözü Tabanlı Eşleştirme (Lyrics Fallback Matcher):**
  - İsim/sanatçı aramasıyla bire bir eşleşmeyen veya düşük güven puanı alan parçalar için **LRCLIB**, **YouTube Music gömülü sözleri**, **Lyrics.ovh** ve **Web araması** üzerinden şarkının sözlerini çeker.
  - Şarkının en ayırt edici dizelerini çıkararak hedef platformda aratır ve aday şarkıların sözleriyle metin benzerliğini (`rapidfuzz`) karşılaştırarak doğru parçayı yakalar.
  - Platformlara sahte/farklı sanatçı isimleriyle yeniden yüklenmiş (re-upload) veya yerel dosya (*Local File*) olarak eklenmiş şarkıları otomatik tespit eder.
- **Mevcut Tarayıcıda Tek Adımda Kayıt:**
  - **YouTube Music'e Kayıt:** Tek tıkla kopyalanan konsol betiği ile kendi açık tarayıcı sekmenizde (`music.youtube.com`) saniyeler içinde tüm çalma listelerini oluşturur veya giriş gerektirmeyen doğrudan çalma kuyruğu bağlantıları üretir.
  - **Spotify'a Kayıt:** Eşleşen tüm Spotify şarkı bağlantılarını panoya kopyalar; Spotify masaüstü veya web uygulamasında boş bir çalma listesine `Ctrl+V` yaparak tüm şarkıları tek seferde ekleyebilirsiniz.

---

## Kurulum

```bash
git clone https://github.com/KULLANICI_ADINIZ/spotify-to-ytmusic.git
cd spotify-to-ytmusic

pip install -r requirements.txt
playwright install chromium
```

---

## Kullanım

### 1. Web Arayüzü (Önerilen)

```bash
python app.py --web --port 5050
```

Tarayıcınızda `http://127.0.0.1:5050` adresini açın:
1. Sol paneldeki kutuya **Spotify** veya **YouTube Music** çalma listesi bağlantılarını yapıştırıp **Şarkıları Tara ve Eşleştir** butonuna basın.
2. Sağ paneldeki **Hesaba Kayıt Rehberi** adımlarını izleyerek tek tıkla kopyaladığınız kod veya bağlantılarla listelerinizi hesabınıza kaydedin.

### 2. Komut Satırı (CLI)

```bash
python app.py "https://open.spotify.com/playlist/..." "https://music.youtube.com/playlist?list=..."
```

---

## Mimari

| Dosya | Açıklama |
| :--- | :--- |
| `app.py` | Flask tabanlı yerel web arayüzü ve CLI giriş noktası |
| `spotify_scraper.py` | API anahtarsız Spotify Playlist/Album/Track okuyucu (Pathfinder GraphQL & Embed) |
| `lyrics_matcher.py` | Spotify → YouTube Music doğrudan ve şarkı sözü (lyrics) tabanlı eşleştirme motoru |
| `ytm_to_spotify.py` | YouTube Music → Spotify okuyucu, Pathfinder arama ve söz doğrulama motoru |
| `ytmusic_saver.py` | Doğrudan çalma kuyruğu üretici ve tarayıcı oturum yardımcı sınıfı |

---

## Lisans

MIT
