import os
import time
from pathlib import Path
from typing import Dict, List, Optional
import ytmusicapi
from ytmusicapi import YTMusic


class YTMusicSaver:
    """
    Utility class for generating instant YouTube playback queue URLs (no login required)
    and optionally saving playlists via a visible Playwright browser session.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or os.path.dirname(os.path.abspath(__file__)))
        self.auth_file = self.base_dir / "browser_auth.json"
        self.profile_dir = self.base_dir / "ytm_browser_profile"

    @staticmethod
    def generate_instant_playlist_urls(video_ids: List[str]) -> List[Dict[str, str]]:
        """
        Generates instant YouTube watch_videos queue URLs in batches of 50 tracks.
        """
        chunks = [video_ids[i : i + 50] for i in range(0, len(video_ids), 50)]
        links = []
        for idx, chunk in enumerate(chunks, start=1):
            ids_str = ",".join(chunk)
            yt_url = f"https://www.youtube.com/watch_videos?video_ids={ids_str}"
            ytm_url = f"https://music.youtube.com/watch?v={chunk[0]}&list=RDAMVM{chunk[0]}"
            label = f"Part {idx} ({len(chunk)})" if len(chunks) > 1 else f"Full Queue ({len(chunk)})"
            links.append({
                "label": label,
                "youtube_queue_url": yt_url,
                "first_song_ytm_url": ytm_url,
                "count": len(chunk),
            })
        return links

    def has_saved_session(self) -> bool:
        return self.auth_file.exists()

    def save_playlist_with_visible_browser(
        self,
        title: str,
        description: str,
        video_ids: List[str],
        privacy_status: str = "PRIVATE",
        timeout_sec: int = 240,
    ) -> Dict:
        clean_ids = [vid for vid in dict.fromkeys(video_ids) if vid]
        if not clean_ids:
            return {"success": False, "error": "No valid videoId items to save."}

        if self.auth_file.exists():
            try:
                ytm = YTMusic(str(self.auth_file))
                playlist_id = ytm.create_playlist(
                    title=title,
                    description=description,
                    privacy_status=privacy_status,
                    video_ids=clean_ids,
                )
                if playlist_id and not isinstance(playlist_id, dict):
                    pl_url = f"https://music.youtube.com/playlist?list={playlist_id}"
                    return {
                        "success": True,
                        "playlist_id": playlist_id,
                        "playlist_url": pl_url,
                        "added_count": len(clean_ids),
                        "method": "Saved Browser Session",
                    }
            except Exception:
                pass

        return self._launch_browser_and_create_playlist(
            title=title,
            description=description,
            video_ids=clean_ids,
            privacy_status=privacy_status,
            timeout_sec=timeout_sec,
        )

    def _launch_browser_and_create_playlist(
        self,
        title: str,
        description: str,
        video_ids: List[str],
        privacy_status: str,
        timeout_sec: int,
    ) -> Dict:
        from playwright.sync_api import sync_playwright

        captured_headers: Dict[str, str] = {}

        def on_request(request):
            nonlocal captured_headers
            if "music.youtube.com/youtubei/v1/" in request.url and request.method == "POST":
                headers = request.headers
                auth = headers.get("authorization", "")
                cookie = headers.get("cookie", "")
                if "SAPISIDHASH" in auth and ("SAPISID" in cookie or "__Secure-3PAPISID" in cookie):
                    captured_headers = dict(headers)

        self.profile_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            launch_kwargs = {
                "user_data_dir": str(self.profile_dir),
                "headless": False,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                ],
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

            page.goto("https://music.youtube.com", wait_until="domcontentloaded", timeout=60000)

            start_time = time.time()
            while time.time() - start_time < timeout_sec:
                if captured_headers:
                    break
                cookies = context.cookies("https://music.youtube.com")
                cookie_names = {c["name"] for c in cookies}
                if ("SAPISID" in cookie_names or "__Secure-3PAPISID" in cookie_names) and "music.youtube.com" in page.url:
                    try:
                        page.evaluate("window.scrollBy(0, 100)")
                    except Exception:
                        pass
                page.wait_for_timeout(1000)

            if not captured_headers:
                context.close()
                return {
                    "success": False,
                    "error": "Timed out waiting for YouTube Music sign-in.",
                }

            raw_header_lines = [f"{k}: {v}" for k, v in captured_headers.items() if not k.startswith(":")]
            ytmusicapi.setup(filepath=str(self.auth_file), headers_raw="\n".join(raw_header_lines))

            ytm = YTMusic(str(self.auth_file))
            playlist_id = ytm.create_playlist(
                title=title,
                description=description,
                privacy_status=privacy_status,
                video_ids=video_ids,
            )

            if not playlist_id or isinstance(playlist_id, dict):
                context.close()
                return {
                    "success": False,
                    "error": f"Failed to create playlist: {playlist_id}",
                }

            pl_url = f"https://music.youtube.com/playlist?list={playlist_id}"
            try:
                page.goto(pl_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(4000)
            except Exception:
                pass

            context.close()
            return {
                "success": True,
                "playlist_id": playlist_id,
                "playlist_url": pl_url,
                "added_count": len(video_ids),
                "method": "Visible Browser Automation",
            }
