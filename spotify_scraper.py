import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


class SpotifyScraper:
    """
    API anahtarı gerektirmeden Spotify Playlist, Album veya Track linklerinden
    şarkı listesini (isim, sanatçı, albüm, süre, spotify_id) çeker.
    - Herkese açık listelerde: Playwright headless + Spotify Pathfinder GraphQL pagination (offset=0,100,200...)
      ile 1000+ şarkılık listeleri bile saniyeler içinde eksiksiz çeker.
    - Gizli (Private / pt=... token'lı) listelerde: Otomatik olarak görünür tarayıcı (headed) açarak
      oturum üzerinden tüm şarkıları çeker.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or os.path.dirname(os.path.abspath(__file__)))
        self.profile_dir = self.base_dir / "ytm_browser_profile"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    @staticmethod
    def parse_spotify_url(url: str) -> Tuple[Optional[str], Optional[str]]:
        url = url.strip()
        uri_match = re.match(r"spotify:(playlist|album|track):([a-zA-Z0-9]+)", url)
        if uri_match:
            return uri_match.group(1), uri_match.group(2)

        parsed = urlparse(url)
        if "spotify.com" in parsed.netloc or "spotify.link" in parsed.netloc:
            if "spotify.link" in parsed.netloc:
                try:
                    resp = requests.head(url, allow_redirects=True, timeout=10)
                    url = resp.url
                    parsed = urlparse(url)
                except Exception:
                    pass
            parts = [p for p in parsed.path.split("/") if p]
            for i, part in enumerate(parts):
                if part in ("playlist", "album", "track") and i + 1 < len(parts):
                    item_id = parts[i + 1].split("?")[0]
                    return part, item_id
        return None, None

    def fetch_from_url(self, url: str, allow_visible_browser_for_private: bool = True) -> Dict:
        item_type, item_id = self.parse_spotify_url(url)
        if not item_type or not item_id:
            raise ValueError(f"Geçersiz Spotify linki: {url}")

        print(f"[Spotify] '{item_type}/{item_id}' okunuyor...")

        # 1. Önce Playwright Headless + GraphQL Pagination ile tam listeyi çekmeyi dene
        pw_result, needs_login = self._scrape_via_pathfinder(
            item_type=item_type,
            item_id=item_id,
            original_url=url,
            headless=True,
        )
        if pw_result and pw_result.get("tracks"):
            print(
                f"[Spotify] '{pw_result['title']}' listesinden "
                f"{len(pw_result['tracks'])}/{pw_result.get('total_count', len(pw_result['tracks']))} şarkı çekildi."
            )
            return pw_result

        # 2. Eğer gizli liste olduğu için login'e yönlendirdiyse (örn. &pt=... linkleri):
        if needs_login and allow_visible_browser_for_private:
            print(
                f"\n[Spotify Gizli Liste Algılandı] '{url}' gizli bir liste olduğu için Spotify girişi gerekiyor."
            )
            print("[Spotify] Görünür tarayıcı açılıyor, lütfen Spotify hesabınızla giriş yapın...")
            pw_vis_result, _ = self._scrape_via_pathfinder(
                item_type=item_type,
                item_id=item_id,
                original_url=url,
                headless=False,
                login_timeout_sec=180,
            )
            if pw_vis_result and pw_vis_result.get("tracks"):
                print(
                    f"[Spotify] Gizli liste '{pw_vis_result['title']}' başarıyla çekildi "
                    f"({len(pw_vis_result['tracks'])} şarkı)."
                )
                return pw_vis_result

        # 3. Yedek: Embed sayfası
        embed_result = self._try_embed_fallback(item_type, item_id, url)
        if embed_result and embed_result.get("tracks"):
            return embed_result

        raise RuntimeError(f"Spotify linkinden şarkılar çekilemedi: {url}")

    def _scrape_via_pathfinder(
        self,
        item_type: str,
        item_id: str,
        original_url: str,
        headless: bool = True,
        login_timeout_sec: int = 15,
    ) -> Tuple[Optional[Dict], bool]:
        """
        Playwright ile Spotify sayfasını açar, `fetchPlaylist` GraphQL isteğini yakalar
        ve `offset=0, 100, 200...` döngüsüyle tüm şarkıları eksiksiz çeker.
        Dönüş: (result_dict, needs_login_bool)
        """
        from playwright.sync_api import sync_playwright

        captured_req: Dict = {}
        first_page_data: Dict = {}
        redirected_to_login = False

        def on_request(req):
            if "pathfinder" in req.url and req.method == "POST" and req.post_data:
                try:
                    body = json.loads(req.post_data)
                    op = body.get("operationName", "")
                    uri = body.get("variables", {}).get("uri", "")
                    if op in ("fetchPlaylist", "fetchPlaylistContents", "getAlbum") and item_id in uri:
                        captured_req["url"] = req.url
                        captured_req["headers"] = dict(req.headers)
                        captured_req["post"] = body
                except Exception:
                    pass

        def on_response(resp):
            nonlocal redirected_to_login, first_page_data
            if "accounts.spotify.com" in resp.url and "/login" in resp.url:
                redirected_to_login = True
            if "pathfinder" in resp.url and resp.request.method == "POST":
                try:
                    body = json.loads(resp.request.post_data or "{}")
                    op = body.get("operationName", "")
                    uri = body.get("variables", {}).get("uri", "")
                    if op in ("fetchPlaylist", "fetchPlaylistContents", "getAlbum") and item_id in uri:
                        data = resp.json()
                        if data.get("data", {}).get("playlistV2", {}).get("content"):
                            first_page_data = data
                except Exception:
                    pass

        try:
            with sync_playwright() as p:
                if headless:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(user_agent=self.USER_AGENT)
                else:
                    self.profile_dir.mkdir(parents=True, exist_ok=True)
                    launch_kwargs = {
                        "user_data_dir": str(self.profile_dir),
                        "headless": False,
                        "args": ["--disable-blink-features=AutomationControlled", "--start-maximized"],
                        "ignore_default_args": ["--enable-automation"],
                    }
                    try:
                        context = p.chromium.launch_persistent_context(channel="chrome", **launch_kwargs)
                    except Exception:
                        try:
                            context = p.chromium.launch_persistent_context(channel="msedge", **launch_kwargs)
                        except Exception:
                            context = p.chromium.launch_persistent_context(**launch_kwargs)

                page = context.pages[0] if context.pages else context.new_page()
                context.on("request", on_request)
                context.on("response", on_response)

                page.goto(original_url, wait_until="domcontentloaded", timeout=45000)

                start_t = time.time()
                while time.time() - start_t < login_timeout_sec:
                    if captured_req and first_page_data:
                        break
                    if headless and redirected_to_login and (time.time() - start_t > 4):
                        break
                    page.wait_for_timeout(500)

                if not captured_req:
                    context.close()
                    return None, redirected_to_login

                # İlk sayfadan başlık, toplam sayı ve ilk şarkıları çıkar
                pl_v2 = first_page_data.get("data", {}).get("playlistV2", {})
                title = pl_v2.get("name") or f"Spotify {item_type.capitalize()}"
                content = pl_v2.get("content", {})
                total_count = content.get("totalCount") or 0

                all_tracks: List[Dict] = []
                self._extract_tracks_from_pathfinder(first_page_data, all_tracks)

                # Eğer listede ilk sayfadan (genelde 25 şarkı) daha fazlası varsa 100'er 100'er kalanları çek
                offset = len(content.get("items", []))
                while offset < total_count:
                    page_json = page.evaluate(
                        """async ({reqInfo, offset, limit}) => {
                            const headers = {
                                'authorization': reqInfo.headers['authorization'],
                                'client-token': reqInfo.headers['client-token'] || '',
                                'content-type': 'application/json',
                                'app-platform': 'WebPlayer'
                            };
                            const body = JSON.parse(JSON.stringify(reqInfo.post));
                            body.variables.offset = offset;
                            body.variables.limit = limit;
                            const r = await fetch(reqInfo.url, {
                                method: 'POST',
                                headers,
                                body: JSON.stringify(body)
                            });
                            return await r.json();
                        }""",
                        {"reqInfo": captured_req, "offset": offset, "limit": 100},
                    )
                    items = (
                        page_json.get("data", {})
                        .get("playlistV2", {})
                        .get("content", {})
                        .get("items", [])
                    )
                    if not items:
                        break
                    self._extract_tracks_from_pathfinder(page_json, all_tracks)
                    offset += len(items)

                context.close()

                # Tekrarlayanları temizle (sırayı koruyarak)
                unique_tracks = []
                seen = set()
                for idx, t in enumerate(all_tracks):
                    key = t.get("spotify_id") or f"{t['name']}_{t['artist_str']}_{idx}"
                    if key not in seen:
                        seen.add(key)
                        unique_tracks.append(t)

                return {
                    "title": title,
                    "type": item_type,
                    "id": item_id,
                    "url": original_url,
                    "total_count": total_count or len(unique_tracks),
                    "tracks": unique_tracks,
                }, False

        except Exception as e:
            print(f"[Spotify Pathfinder Uyarı] {e}")
            return None, redirected_to_login

    def _try_embed_fallback(self, item_type: str, item_id: str, original_url: str) -> Optional[Dict]:
        embed_url = f"https://open.spotify.com/embed/{item_type}/{item_id}"
        try:
            resp = self.session.get(embed_url, timeout=15)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, "html.parser")
            next_data_script = soup.find("script", {"id": "__NEXT_DATA__"})
            if not next_data_script or not next_data_script.string:
                return None
            data = json.loads(next_data_script.string)
            entity = (
                data.get("props", {})
                .get("pageProps", {})
                .get("state", {})
                .get("data", {})
                .get("entity", {})
            )
            if not entity:
                return None
            title = entity.get("name") or entity.get("title") or f"Spotify {item_type.capitalize()}"
            tracks = []
            for idx, item in enumerate(entity.get("trackList", [])):
                t_name = item.get("title", "").strip()
                subtitle = item.get("subtitle", "").replace("\xa0", " ").strip()
                artists = [a.strip() for a in subtitle.split(",") if a.strip()]
                duration_ms = item.get("duration", 0)
                uri = item.get("uri", "")
                sp_id = uri.split(":")[-1] if ":" in uri else f"{item_id}_{idx}"
                if t_name:
                    tracks.append({
                        "name": t_name,
                        "artists": artists,
                        "artist_str": subtitle,
                        "album": "",
                        "duration_ms": duration_ms,
                        "duration_sec": round(duration_ms / 1000) if duration_ms else 0,
                        "spotify_id": sp_id,
                    })
            return {
                "title": title,
                "type": item_type,
                "id": item_id,
                "url": original_url,
                "total_count": len(tracks),
                "tracks": tracks,
            }
        except Exception:
            return None

    def _extract_tracks_from_pathfinder(self, data: Dict, out_tracks: List[Dict]):
        if not isinstance(data, dict):
            return
        playlist_v2 = data.get("data", {}).get("playlistV2", {})
        content = playlist_v2.get("content", {})
        items = content.get("items", [])

        for item in items:
            item_v2 = item.get("itemV2", {}).get("data", {})
            if not item_v2:
                continue
            name = item_v2.get("name", "").strip()
            if not name:
                continue
            artists_items = item_v2.get("artists", {}).get("items", [])
            artists = [
                a.get("profile", {}).get("name", "")
                for a in artists_items
                if a.get("profile", {}).get("name")
            ]
            album_name = item_v2.get("albumOfTrack", {}).get("name", "")
            duration_ms = (
                item_v2.get("trackDuration", {}).get("totalMilliseconds", 0)
                or item_v2.get("duration", {}).get("totalMilliseconds", 0)
            )
            uri = item_v2.get("uri", "")
            sp_id = uri.split(":")[-1] if ":" in uri else ""

            out_tracks.append({
                "name": name,
                "artists": artists,
                "artist_str": ", ".join(artists),
                "album": album_name,
                "duration_ms": duration_ms,
                "duration_sec": round(duration_ms / 1000) if duration_ms else 0,
                "spotify_id": sp_id,
            })
