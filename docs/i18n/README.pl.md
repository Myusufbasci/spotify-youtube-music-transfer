# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | [Türkçe](README.tr.md) | [Español](README.es.md) | [中文 (简体)](README.zh.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | **Polski** | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | [Svenska](README.sv.md)

---

> Dwukierunkowy transfer playlist i dopasowywanie po tekstach bez klucza API

Wklej linki Spotify, aby dopasować w YouTube Music, lub linki YouTube Music, aby dopasować w Spotify.

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

## Instrukcja zapisu na koncie

### 1. Zapisz w YouTube Music
1. **Skopiuj skrypt dla YouTube Music:** Skopiuj skrypt konsoli, który utworzy playlisty na Twoim koncie.
2. **Otwórz YouTube Music w nowej karcie:** Przejdź do karty, w której jesteś zalogowany do YouTube Music.
3. **Wklej w konsoli i naciśnij Enter:** Naciśnij F12 → karta Console, wklej przez Ctrl+V i naciśnij Enter. (Jeśli przeglądarka poprosi o zgodę przy pierwszym wklejeniu, wpisz allow pasting i naciśnij Enter.)

### 2. Zapisz w Spotify
1. **Skopiuj linki do utworów Spotify:** Aplikacja Spotify obsługuje bezpośrednie wklejanie skopiowanych linków do dowolnej playlisty.
2. **Otwórz pustą playlistę w Spotify i naciśnij Ctrl+V:** Utwórz nową playlistę w Spotify, kliknij wewnątrz niej i naciśnij Ctrl+V.

---

## License

MIT
