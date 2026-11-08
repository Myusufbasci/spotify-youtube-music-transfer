# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | [Türkçe](README.tr.md) | [Español](README.es.md) | [中文 (简体)](README.zh.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [Português](README.pt.md) | [Русский](README.ru.md) | **日本語** | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | [Polski](README.pl.md) | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | [Svenska](README.sv.md)

---

> APIキー不要・歌詞照合対応の双方向プレイリスト移行ツール

SpotifyのURLを貼るとYouTube Musicで、YouTube MusicのURLを貼るとSpotifyで曲名＋歌詞から照合します。

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

## アカウントへの保存手順

### 1. YouTube Musicに保存
1. **YouTube Music移行スクリプトをコピー:** プレイリストを一括作成するコンソールスクリプトをコピーします。
2. **新しいタブでYouTube Musicを開く:** ログイン済みのYouTube Musicタブに移動します。
3. **Consoleに貼り付けてEnterを押す:** F12 → Consoleタブを開き、Ctrl+Vで貼り付けてEnterを押します。 (初回貼り付け時に警告が出た場合は allow pasting と入力してEnterを押してください。)

### 2. Spotifyに保存
1. **Spotifyの曲リンクをコピー:** SpotifyアプリやWeb版では、曲のURLをプレイリストに直接貼り付けられます。
2. **Spotifyで空のプレイリストを開き Ctrl+V:** Spotifyで新規プレイリストを作成し、リスト内をクリックしてCtrl+Vを押すと全曲追加されます。

---

## License

MIT
