# sp2ytm

[English](../../README.md) ? [Türkçe](README.tr.md) ? [Español](README.es.md) ? [中文 (简体)](README.zh.md) ? [हिन्दी](README.hi.md) ? [العربية](README.ar.md) ? [Português](README.pt.md) ? [Русский](README.ru.md) ? [日本語](README.ja.md) ? [Deutsch](README.de.md) ? [Français](README.fr.md) ? [한국어](README.ko.md) ? **Italiano** ? [Bahasa Indonesia](README.id.md) ? [Tiếng Việt](README.vi.md) ? [Polski](README.pl.md) ? [Українська](README.uk.md) ? [Nederlands](README.nl.md) ? [ไทย](README.th.md) ? [Svenska](README.sv.md)

Trasferimento bidirezionale di playlist e corrispondenza tramite testi senza chiave API.

Incolla link Spotify per cercare su YouTube Music, o link YouTube Music per cercare su Spotify.

## Quick Start

```bash
git clone https://github.com/Myusufbasci/sp2ytm.git
cd sp2ytm

pip install -r requirements.txt
playwright install chromium
python app.py --web --port 5050
```

Open `http://127.0.0.1:5050`.

## Guida al salvataggio

### Salva su YouTube Music
1. **Copia lo script per YouTube Music** ? Copia lo script console che creerà le playlist nel tuo account.
2. **Apri YouTube Music in una nuova scheda** ? Passa a una scheda in cui hai effettuato l'accesso a YouTube Music.
3. **Incolla nella Console e premi Invio** ? Premi F12 → scheda Console, incolla con Ctrl+V e premi Invio. (Se il browser chiede conferma al primo incolla, digita allow pasting e premi Invio.)

### Salva su Spotify
1. **Copia i link dei brani Spotify** ? Spotify consente di incollare i link dei brani direttamente dentro qualsiasi playlist.
2. **Apri una playlist vuota su Spotify e premi Ctrl+V** ? Crea una nuova playlist su Spotify, fai clic all'interno e premi Ctrl+V.

## License

MIT
