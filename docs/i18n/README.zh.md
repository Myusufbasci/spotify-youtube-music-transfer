# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | [Türkçe](README.tr.md) | [Español](README.es.md) | **中文 (简体)** | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | [Polski](README.pl.md) | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | [Svenska](README.sv.md)

---

> 无需 API 密钥的双向歌单迁移与歌词智能匹配引擎

粘贴 Spotify 链接以匹配到 YouTube Music，或粘贴 YouTube Music 链接以匹配到 Spotify（支持歌词兜底匹配）。

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

## 保存到账户指南

### 1. 保存到 YouTube Music
1. **复制 YouTube Music 迁移脚本:** 复制一次性控制台脚本，用于在您的账户中自动创建歌单。
2. **在新标签页打开 YouTube Music:** 切换到已登录 YouTube Music 的浏览器标签页。
3. **粘贴到控制台并按回车:** 按 F12 → 选择 Console（控制台），按 Ctrl+V 粘贴并按 Enter。 (如果浏览器首次粘贴提示安全警告，请先输入 allow pasting 并按回车。)

### 2. 保存到 Spotify
1. **复制 Spotify 歌曲链接:** Spotify 桌面端和网页端支持将歌曲链接直接粘贴到任意歌单中。
2. **在 Spotify 打开空歌单并按 Ctrl+V:** 在 Spotify 新建一个歌单，点击列表区域并按 Ctrl+V 即可一次性添加所有歌曲。

---

## License

MIT
