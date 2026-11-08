# sp2ytm

[English](../../README.md) ? [Türkçe](README.tr.md) ? [Español](README.es.md) ? [中文 (简体)](README.zh.md) ? **हिन्दी** ? [العربية](README.ar.md) ? [Português](README.pt.md) ? [Русский](README.ru.md) ? [日本語](README.ja.md) ? [Deutsch](README.de.md) ? [Français](README.fr.md) ? [한국어](README.ko.md) ? [Italiano](README.it.md) ? [Bahasa Indonesia](README.id.md) ? [Tiếng Việt](README.vi.md) ? [Polski](README.pl.md) ? [Українська](README.uk.md) ? [Nederlands](README.nl.md) ? [ไทย](README.th.md) ? [Svenska](README.sv.md)

बिना API कुंजी के द्वि-दिशात्मक प्लेलिस्ट और लिरिक्स मैचिंग इंजन.

YouTube Music पर मैच करने के लिए Spotify लिंक या Spotify पर मैच करने के लिए YouTube Music लिंक पेस्ट करें।

## Quick Start

```bash
git clone https://github.com/Myusufbasci/sp2ytm.git
cd sp2ytm

pip install -r requirements.txt
playwright install chromium
python app.py --web --port 5050
```

Open `http://127.0.0.1:5050`.

## खाते में सहेजने की गाइड

### YouTube Music में सहेजें
1. **YouTube Music ट्रांसफर स्क्रिप्ट कॉपी करें** ? वह कंसोल स्क्रिप्ट कॉपी करें जो आपके खाते में सभी प्लेलिस्ट बना देगी।
2. **नए टैब में YouTube Music खोलें** ? उस टैब पर जाएँ जहाँ आप YouTube Music में लॉग इन हैं।
3. **Console में पेस्ट करें और Enter दबाएँ** ? F12 दबाएँ → Console टैब चुनें, Ctrl+V से पेस्ट करें और Enter दबाएँ। (यदि ब्राउज़र पहली बार पेस्ट करने की अनुमति मांगे, तो allow pasting लिखकर Enter दबाएँ।)

### Spotify में सहेजें
1. **Spotify गाने के लिंक कॉपी करें** ? Spotify ऐप में कॉपी किए गए ट्रैक लिंक को सीधे किसी भी प्लेलिस्ट में पेस्ट किया जा सकता है।
2. **Spotify में खाली प्लेलिस्ट खोलें और Ctrl+V दबाएँ** ? Spotify में नई प्लेलिस्ट बनाएँ, अंदर क्लिक करें और Ctrl+V दबाएँ।

## License

MIT
