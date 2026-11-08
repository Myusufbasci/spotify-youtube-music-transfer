# sp2ytm

[English](../../README.md) ? [Türkçe](README.tr.md) ? [Español](README.es.md) ? [中文 (简体)](README.zh.md) ? [हिन्दी](README.hi.md) ? [العربية](README.ar.md) ? [Português](README.pt.md) ? [Русский](README.ru.md) ? [日本語](README.ja.md) ? [Deutsch](README.de.md) ? [Français](README.fr.md) ? [한국어](README.ko.md) ? [Italiano](README.it.md) ? [Bahasa Indonesia](README.id.md) ? [Tiếng Việt](README.vi.md) ? [Polski](README.pl.md) ? [Українська](README.uk.md) ? **Nederlands** ? [ไทย](README.th.md) ? [Svenska](README.sv.md)

Bidirectionele afspeellijst-overdracht & songtekst-matching zonder API-sleutel.

Plak Spotify-links om te zoeken op YouTube Music, of YouTube Music-links om te zoeken op Spotify.

## Quick Start

```bash
git clone https://github.com/Myusufbasci/sp2ytm.git
cd sp2ytm

pip install -r requirements.txt
playwright install chromium
python app.py --web --port 5050
```

Open `http://127.0.0.1:5050`.

## Handleiding voor opslaan

### Opslaan in YouTube Music
1. **Kopieer het YouTube Music-script** ? Kopieer het consolescript dat alle afspeellijsten in je account aanmaakt.
2. **Open YouTube Music in een nieuw tabblad** ? Ga naar een tabblad waarin je bent ingelogd op YouTube Music.
3. **Plak in de Console en druk op Enter** ? Druk op F12 → tabblad Console, plak met Ctrl+V en druk op Enter. (Als de browser eerst om toestemming vraagt, typ dan allow pasting en druk op Enter.)

### Opslaan in Spotify
1. **Kopieer Spotify-nummerlinks** ? Spotify ondersteunt het direct plakken van gekopieerde nummerlinks in elke afspeellijst.
2. **Open een lege afspeellijst in Spotify en druk op Ctrl+V** ? Maak een nieuwe afspeellijst in Spotify, klik erin en druk op Ctrl+V.

## License

MIT
