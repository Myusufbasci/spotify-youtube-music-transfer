# Spotify ? YouTube Music

**Languages:** [English](../../README.md) | [Türkçe](README.tr.md) | [Español](README.es.md) | [中文 (简体)](README.zh.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | **한국어** | [Italiano](README.it.md) | [Bahasa Indonesia](README.id.md) | [Tiếng Việt](README.vi.md) | [Polski](README.pl.md) | [Українська](README.uk.md) | [Nederlands](README.nl.md) | [ไทย](README.th.md) | [Svenska](README.sv.md)

---

> API 키가 필요 없는 양방향 플레이리스트 변환 및 가사 기반 매칭 엔진

Spotify 링크를 붙여넣으면 YouTube Music에서, YouTube Music 링크를 붙여넣으면 Spotify에서 매칭합니다.

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

## 계정 저장 가이드

### 1. YouTube Music에 저장
1. **YouTube Music 전송 스크립트 복사:** 계정에 플레이리스트를 일괄 생성하는 콘솔 스크립트를 복사하세요.
2. **새 탭에서 YouTube Music 열기:** YouTube Music에 로그인된 탭으로 이동하세요.
3. **콘솔에 붙여넣고 Enter 누르기:** F12 → Console 탭을 열고 Ctrl+V로 붙여넣은 뒤 Enter를 누르세요. (브라우저에서 최초 붙여넣기 허용을 요청하면 allow pasting을 입력하고 Enter를 누르세요.)

### 2. Spotify에 저장
1. **Spotify 트랙 링크 복사:** Spotify 앱이나 웹에서는 복사한 트랙 링크를 플레이리스트에 직접 붙여넣을 수 있습니다.
2. **Spotify에서 빈 플레이리스트를 열고 Ctrl+V:** Spotify에서 새 플레이리스트를 만들고 목록 안을 클릭한 뒤 Ctrl+V를 누르세요.

---

## License

MIT
