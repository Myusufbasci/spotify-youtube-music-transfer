# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | [Türkçe](README.tr.md) | [Español](README.es.md) | [中文 (简体)](README.zh.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | [Polski](README.pl.md) | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | **Svenska**

---

> Dubbelriktad spellistöverföring och låttextmatchning utan API-nyckel

Klistra in Spotify-länkar för att matcha på YouTube Music, eller YouTube Music-länkar för att matcha på Spotify.

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

## Guide för att spara till konto

### 1. Spara till YouTube Music
1. **Kopiera överföringsskript för YouTube Music:** Kopiera konsolskriptet som skapar spellistorna på ditt konto.
2. **Öppna YouTube Music i en ny flik:** Byt till en flik där du är inloggad på YouTube Music.
3. **Klistra in i Console & tryck Enter:** Tryck F12 → fliken Console, klistra in med Ctrl+V och tryck Enter. (Om webbläsaren ber om tillåtelse första gången, skriv allow pasting och tryck Enter.)

### 2. Spara till Spotify
1. **Kopiera Spotify-låtlänkar:** Spotify stöder att du klistrar in kopierade låtlänkar direkt i valfri spellista.
2. **Öppna en tom spellista i Spotify & tryck Ctrl+V:** Skapa en ny spellista i Spotify, klicka i listan och tryck Ctrl+V.

---

## License

MIT
