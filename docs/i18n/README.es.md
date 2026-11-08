# spotify-youtube-music-transfer

[English](../../README.md) · [Türkçe](README.tr.md) · **Español** · [中文 (简体)](README.zh.md) · [हिन्दी](README.hi.md) · [العربية](README.ar.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [日本語](README.ja.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [Italiano](README.it.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Українська](README.uk.md) · [Nederlands](README.nl.md) · [ไทย](README.th.md) · [Svenska](README.sv.md)

Motor bidireccional de transferencia de listas y coincidencia por letras sin clave API

Pega enlaces públicos de Spotify para buscar en YouTube Music, o enlaces de YouTube Music para buscar en Spotify.

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

## Guía para guardar en tu cuenta

### Guardar en YouTube Music
1. **Copia el script de transferencia de YouTube Music** — Copia el script de consola que creará todas las listas en tu cuenta.
2. **Abre YouTube Music en una nueva pestaña** — Ve a una pestaña donde hayas iniciado sesión en YouTube Music.
3. **Pega en la consola y pulsa Enter** — Pulsa F12 → pestaña Console, pega con Ctrl+V y pulsa Enter. (Si el navegador pide permiso al pegar por primera vez, escribe allow pasting y pulsa Enter.)

### Guardar en Spotify
1. **Copia los enlaces de canciones de Spotify** — Spotify permite pegar enlaces de canciones directamente dentro de cualquier lista.
2. **Abre una lista vacía en Spotify y pulsa Ctrl+V** — Crea una nueva lista en Spotify, haz clic dentro y pulsa Ctrl+V para añadir todas las canciones.

## License

MIT
