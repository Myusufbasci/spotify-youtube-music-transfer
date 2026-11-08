import json
import re
import threading
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse
import requests
from rapidfuzz import fuzz
from ytmusicapi import YTMusic
from lyrics_matcher import YTMusicLyricsMatcher


class YTMToSpotifyMatcher:
    """
    Reads YouTube / YouTube Music playlists or tracks without an API key,
    searches the Spotify catalog via Pathfinder GraphQL (searchDesktop),
    and falls back to lyrics matching (embedded YTMusic lyrics + LRCLIB + Web Lyrics)
    when direct title/artist matching is uncertain.
    """

    DIRECT_MATCH_THRESHOLD = 84.0

    def __init__(self):
        self.ytmusic = YTMusic(language="en")
        self.lyrics_helper = YTMusicLyricsMatcher(language="en")
        self.session = requests.Session()
        self._token_lock = threading.Lock()
        self._pathfinder_info: Optional[Dict] = None
        self._token_timestamp: float = 0.0

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        parsed = urlparse(url.strip())
        return any(d in parsed.netloc.lower() for d in ("youtube.com", "youtu.be"))

    @staticmethod
    def parse_youtube_url(url: str) -> Tuple[Optional[str], Optional[str]]:
        url = url.strip()
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        if "list" in qs and qs["list"][0]:
            list_id = qs["list"][0]
            if not list_id.startswith("RD"):
                return "playlist", list_id

        if "v" in qs and qs["v"][0]:
            return "track", qs["v"][0]

        if "youtu.be" in parsed.netloc:
            vid = parsed.path.strip("/").split("/")[0]
            if vid:
                return "track", vid

        return None, None

    def fetch_from_url(self, url: str) -> Dict:
        item_type, item_id = self.parse_youtube_url(url)
        if not item_type or not item_id:
            raise ValueError(f"Invalid YouTube / YouTube Music URL: {url}")

        print(f"[YouTube Music] Reading '{item_type}/{item_id}'...")

        if item_type == "track":
            watch = self.ytmusic.get_watch_playlist(videoId=item_id)
            t_list = watch.get("tracks", [])
            if not t_list:
                raise RuntimeError(f"Failed to read YouTube track: {url}")
            t = t_list[0]
            artists = [a.get("name", "") for a in t.get("artists", []) if a.get("name")]
            dur_sec = self.lyrics_helper._parse_duration(t.get("length", ""))
            return {
                "title": t.get("title", "YouTube Music Track"),
                "type": "track",
                "id": item_id,
                "url": url,
                "total_count": 1,
                "tracks": [
                    {
                        "name": t.get("title", ""),
                        "artists": artists,
                        "artist_str": ", ".join(artists),
                        "album": t.get("album", {}).get("name", "") if isinstance(t.get("album"), dict) else "",
                        "duration_sec": dur_sec,
                        "videoId": item_id,
                    }
                ],
            }

        try:
            pl = self.ytmusic.get_playlist(item_id, limit=None)
            title = pl.get("title", "YouTube Music Playlist")
            raw_tracks = pl.get("tracks", [])
            tracks = []
            for t in raw_tracks:
                vid = t.get("videoId")
                t_name = t.get("title", "").strip()
                if not t_name:
                    continue
                artists = [a.get("name", "") for a in t.get("artists", []) if a.get("name")]
                dur_sec = t.get("duration_seconds") or self.lyrics_helper._parse_duration(t.get("duration", ""))
                tracks.append({
                    "name": t_name,
                    "artists": artists,
                    "artist_str": ", ".join(artists),
                    "album": t.get("album", {}).get("name", "") if isinstance(t.get("album"), dict) else "",
                    "duration_sec": dur_sec,
                    "videoId": vid or "",
                })
            if tracks:
                print(f"[YouTube Music] Fetched {len(tracks)} tracks from '{title}'.")
                return {
                    "title": title,
                    "type": "playlist",
                    "id": item_id,
                    "url": url,
                    "total_count": len(tracks),
                    "tracks": tracks,
                }
        except Exception as e:
            print(f"[YTMusic Playlist Warning] {e}, trying standard YouTube page fallback...")

        fallback = self._scrape_youtube_web_playlist(item_id, url)
        if fallback and fallback.get("tracks"):
            return fallback

        raise RuntimeError(f"Could not read YouTube playlist (make sure it is public): {url}")

    def _scrape_youtube_web_playlist(self, list_id: str, original_url: str) -> Optional[Dict]:
        web_url = f"https://www.youtube.com/playlist?list={list_id}"
        try:
            r = self.session.get(
                web_url,
                headers={"User-Agent": self.lyrics_helper.session.headers["User-Agent"]},
                timeout=15,
            )
            if r.status_code != 200:
                return None
            m = re.search(r"var ytInitialData\s*=\s*(\{.*?\});</script>", r.text)
            if not m:
                return None
            data = json.loads(m.group(1))
            title = (
                data.get("metadata", {})
                .get("playlistMetadataRenderer", {})
                .get("title", "YouTube Playlist")
            )
            tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
            tracks = []
            for tab in tabs:
                sec_list = (
                    tab.get("tabRenderer", {})
                    .get("content", {})
                    .get("sectionListRenderer", {})
                    .get("contents", [])
                )
                for sec in sec_list:
                    items = (
                        sec.get("itemSectionRenderer", {})
                        .get("contents", [{}])[0]
                        .get("playlistVideoListRenderer", {})
                        .get("contents", [])
                    )
                    for it in items:
                        v = it.get("playlistVideoRenderer", {})
                        if not v:
                            continue
                        vid = v.get("videoId", "")
                        runs = v.get("title", {}).get("runs", [])
                        t_name = runs[0].get("text", "") if runs else ""
                        owner_runs = v.get("shortBylineText", {}).get("runs", [])
                        artist_name = owner_runs[0].get("text", "") if owner_runs else ""
                        dur_sec = int(v.get("lengthSeconds", 0) or 0)
                        if t_name:
                            tracks.append({
                                "name": t_name,
                                "artists": [artist_name] if artist_name else [],
                                "artist_str": artist_name,
                                "album": "",
                                "duration_sec": dur_sec,
                                "videoId": vid,
                            })
            return {
                "title": title,
                "type": "playlist",
                "id": list_id,
                "url": original_url,
                "total_count": len(tracks),
                "tracks": tracks,
            }
        except Exception:
            return None

    def _ensure_spotify_search_session(self):
        with self._token_lock:
            if self._pathfinder_info and (time.time() - self._token_timestamp < 1500):
                return self._pathfinder_info

            from playwright.sync_api import sync_playwright

            captured = {}

            def on_req(req):
                if "pathfinder" in req.url and req.method == "POST" and req.post_data:
                    try:
                        d = json.loads(req.post_data)
                        if "search" in d.get("operationName", "").lower():
                            captured["url"] = req.url
                            captured["headers"] = {
                                "authorization": req.headers.get("authorization", ""),
                                "client-token": req.headers.get("client-token", ""),
                                "content-type": "application/json",
                                "app-platform": "WebPlayer",
                                "user-agent": req.headers.get("user-agent", ""),
                            }
                            captured["post"] = d
                    except Exception:
                        pass

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.on("request", on_req)
                page.goto("https://open.spotify.com/search/music", wait_until="networkidle", timeout=30000)
                browser.close()

            if not captured.get("headers"):
                raise RuntimeError("Failed to initialize anonymous Spotify search session.")

            self._pathfinder_info = captured
            self._token_timestamp = time.time()
            return self._pathfinder_info

    def search_spotify_tracks(self, query: str, limit: int = 5) -> List[Dict]:
        if not query.strip():
            return []
        info = self._ensure_spotify_search_session()
        body = json.loads(json.dumps(info["post"]))
        body["variables"]["searchTerm"] = query.strip()
        body["variables"]["limit"] = limit

        try:
            r = self.session.post(info["url"], headers=info["headers"], json=body, timeout=10)
            if r.status_code in (401, 403):
                self._token_timestamp = 0
                info = self._ensure_spotify_search_session()
                r = self.session.post(info["url"], headers=info["headers"], json=body, timeout=10)
            if r.status_code != 200:
                return []
            items = (
                r.json()
                .get("data", {})
                .get("searchV2", {})
                .get("tracksV2", {})
                .get("items", [])
            )
            results = []
            for wrap in items:
                d = wrap.get("item", {}).get("data", {})
                if not d or d.get("__typename") != "Track":
                    continue
                sp_id = d.get("id", "")
                name = d.get("name", "")
                artists = [
                    a.get("profile", {}).get("name", "")
                    for a in d.get("artists", {}).get("items", [])
                    if a.get("profile", {}).get("name")
                ]
                album = d.get("albumOfTrack", {}).get("name", "")
                sources = d.get("albumOfTrack", {}).get("coverArt", {}).get("sources", [])
                thumb = sources[0].get("url", "") if sources else ""
                dur_ms = d.get("duration", {}).get("totalMilliseconds", 0)
                results.append({
                    "videoId": sp_id,
                    "spotify_id": sp_id,
                    "uri": d.get("uri", f"spotify:track:{sp_id}"),
                    "title": name,
                    "artists": ", ".join(artists),
                    "album": album,
                    "duration_sec": round(dur_ms / 1000) if dur_ms else 0,
                    "resultType": "Spotify Track",
                    "url": f"https://open.spotify.com/track/{sp_id}",
                    "thumbnail": thumb,
                })
            return results
        except Exception:
            return []

    @staticmethod
    def clean_youtube_title_and_artist(raw_title: str, raw_channel: str) -> Tuple[str, str]:
        channel = re.sub(r"\s*-\s*Topic$", "", raw_channel, flags=re.IGNORECASE).strip()
        label_channels = (
            "netd müzik", "poll production", "avrupa müzik", "dmc", "seyhan müzik",
            "dokuz sekiz müzik", "kalan müzik", "sony music", "mahzen media", "beşiktaş kültür merkezi",
        )
        is_label = any(lbl in channel.lower() for lbl in label_channels)

        title = re.sub(
            r"\s*[\(\[][^)\]]*(official|video|audio|klip|lyrics|sözleri|hd|4k|hq|remaster|live|konser|visualizer)[^)\]]*[\)\]]",
            "",
            raw_title,
            flags=re.IGNORECASE,
        )
        title = re.sub(r"\s*\|.*$", "", title).strip()

        if " - " in title:
            parts = [p.strip() for p in title.split(" - ", 1) if p.strip()]
            if len(parts) == 2:
                left, right = parts[0], parts[1]
                if is_label or not channel or fuzz.token_set_ratio(left.lower(), channel.lower()) >= 70:
                    return right, left
                if fuzz.token_set_ratio(right.lower(), channel.lower()) >= 75:
                    return left, right
                return right, left

        return title.strip() or raw_title.strip(), ("" if is_label else channel)

    def match_track(self, yt_track: Dict, force_lyrics: bool = False) -> Dict:
        raw_title = yt_track.get("name", "")
        raw_artist = yt_track.get("artist_str", "")
        duration_sec = yt_track.get("duration_sec", 0)
        video_id = yt_track.get("videoId", "")

        clean_name, parsed_artist = self.clean_youtube_title_and_artist(raw_title, raw_artist)
        clean_name = self.lyrics_helper.clean_track_name(clean_name)

        direct_candidates = []
        if not force_lyrics:
            queries = []
            if parsed_artist:
                queries.append(f"{clean_name} {parsed_artist}".strip())
            if raw_title != clean_name:
                queries.append(raw_title)
            if clean_name not in queries:
                queries.append(clean_name)

            seen = set()
            for q in queries[:3]:
                for item in self.search_spotify_tracks(q, limit=5):
                    sid = item["spotify_id"]
                    if sid in seen:
                        continue
                    seen.add(sid)
                    scored = self._score_spotify_candidate(item, raw_title, clean_name, parsed_artist, duration_sec)
                    direct_candidates.append(scored)
                if direct_candidates and max(c["score"] for c in direct_candidates) >= 90:
                    break

            direct_candidates.sort(key=lambda x: x["score"], reverse=True)

        best_direct = direct_candidates[0] if direct_candidates else None
        if best_direct and best_direct["score"] >= self.DIRECT_MATCH_THRESHOLD and not force_lyrics:
            return {
                "spotify": yt_track,
                "status": "direct_match",
                "match_method": "Direct Match",
                "confidence": round(best_direct["score"], 1),
                "yt_match": best_direct,
                "lyrics_info": None,
                "alternatives": direct_candidates[1:5],
            }

        lyrics_text = None
        lyrics_source = None

        if video_id:
            yt_embedded = self.lyrics_helper._get_ytmusic_lyrics(video_id)
            if yt_embedded and len(yt_embedded.strip()) > 40:
                lyrics_text = yt_embedded.strip()
                lyrics_source = "YTMusic Lyrics"

        if not lyrics_text:
            lyrics_text, lyrics_source = self.lyrics_helper.fetch_track_lyrics(
                raw_title, clean_name, parsed_artist, duration_sec
            )

        lyrics_candidates = []
        matched_snippet = ""
        best_lyrics_sim = 0.0

        if lyrics_text:
            snippets = self.lyrics_helper.extract_distinctive_snippets(lyrics_text, clean_name)
            lyrics_candidates, matched_snippet, best_lyrics_sim = self._verify_spotify_by_lyrics(
                snippets=snippets,
                full_lyrics=lyrics_text,
                clean_name=clean_name,
                parsed_artist=parsed_artist,
                duration_sec=duration_sec,
                existing_candidates=direct_candidates,
            )

        all_cands = self.lyrics_helper._merge_candidates(lyrics_candidates, direct_candidates)
        if all_cands:
            best = all_cands[0]
            is_lyrics = best.get("matched_by_lyrics", False) or (lyrics_text is not None and best_lyrics_sim >= 45)
            status = "lyrics_match" if is_lyrics else ("direct_match" if best["score"] >= 75 else "low_confidence")
            method_label = (
                f"Lyrics Match ({lyrics_source})"
                if is_lyrics
                else ("Close Match" if status == "low_confidence" else "Direct Match")
            )
            return {
                "spotify": yt_track,
                "status": status,
                "match_method": method_label,
                "confidence": round(best["score"], 1),
                "yt_match": best,
                "lyrics_info": {
                    "found_lyrics": bool(lyrics_text),
                    "source": lyrics_source or "",
                    "matched_snippet": best.get("matched_snippet") or matched_snippet,
                    "lyrics_similarity": round(best.get("lyrics_similarity", best_lyrics_sim), 1),
                    "excerpt": (lyrics_text[:280] + "...") if lyrics_text and len(lyrics_text) > 280 else (lyrics_text or ""),
                },
                "alternatives": all_cands[1:5],
            }

        return {
            "spotify": yt_track,
            "status": "not_found",
            "match_method": "Not Found",
            "confidence": 0.0,
            "yt_match": None,
            "lyrics_info": None,
            "alternatives": [],
        }

    def _score_spotify_candidate(
        self, sp_item: Dict, raw_yt_title: str, clean_yt_name: str, yt_artist: str, yt_duration: int
    ) -> Dict:
        norm_yt_raw = self.lyrics_helper.normalize_text(raw_yt_title)
        norm_yt_clean = self.lyrics_helper.normalize_text(clean_yt_name)
        norm_yt_artist = self.lyrics_helper.normalize_text(yt_artist)

        norm_sp_title = self.lyrics_helper.normalize_text(sp_item["title"])
        norm_sp_clean = self.lyrics_helper.normalize_text(self.lyrics_helper.clean_track_name(sp_item["title"]))
        norm_sp_artist = self.lyrics_helper.normalize_text(sp_item["artists"])

        title_sim = max(
            fuzz.ratio(norm_yt_clean, norm_sp_clean),
            fuzz.token_sort_ratio(norm_yt_clean, norm_sp_clean) * 0.96,
            fuzz.partial_ratio(norm_sp_clean, norm_yt_raw) * 0.90,
        )

        if norm_yt_artist:
            artist_sim = max(
                fuzz.token_set_ratio(norm_yt_artist, norm_sp_artist),
                fuzz.partial_ratio(norm_sp_artist, norm_yt_raw) * 0.85,
            )
        else:
            artist_sim = fuzz.partial_ratio(norm_sp_artist, norm_yt_raw) * 0.90

        sp_dur = sp_item.get("duration_sec", 0)
        dur_bonus = 0.0
        if yt_duration > 0 and sp_dur > 0:
            diff = abs(yt_duration - sp_dur)
            if diff <= 4:
                dur_bonus = 7.0
            elif diff <= 12:
                dur_bonus = 3.0
            elif diff > 45:
                dur_bonus = -15.0

        score = max(0.0, min(100.0, (title_sim * 0.55) + (artist_sim * 0.45) + dur_bonus + 5.0))
        out = dict(sp_item)
        out.update({
            "score": round(score, 1),
            "title_sim": round(title_sim, 1),
            "artist_sim": round(artist_sim, 1),
            "matched_by_lyrics": False,
            "matched_snippet": "",
            "lyrics_similarity": 0.0,
        })
        return out

    def _verify_spotify_by_lyrics(
        self,
        snippets: List[str],
        full_lyrics: str,
        clean_name: str,
        parsed_artist: str,
        duration_sec: int,
        existing_candidates: List[Dict],
    ) -> Tuple[List[Dict], str, float]:
        norm_full = self.lyrics_helper.normalize_text(full_lyrics)
        cand_map: Dict[str, Dict] = {c["videoId"]: dict(c) for c in existing_candidates}
        best_snippet = snippets[0] if snippets else ""
        best_sim = 0.0

        for snip in snippets:
            try:
                r = self.session.get("https://lrclib.net/api/search", params={"q": snip}, timeout=8)
                if r.status_code == 200:
                    for lrc_item in r.json()[:3]:
                        t_name = lrc_item.get("trackName", "")
                        a_name = lrc_item.get("artistName", "")
                        if t_name:
                            for sp_item in self.search_spotify_tracks(f"{t_name} {a_name}".strip(), limit=3):
                                sid = sp_item["spotify_id"]
                                if sid not in cand_map:
                                    sc = self._score_spotify_candidate(
                                        sp_item, t_name, t_name, a_name, duration_sec
                                    )
                                    sc["matched_snippet"] = snip
                                    sc["lyric_search_hits"] = 1
                                    cand_map[sid] = sc
                                else:
                                    cand_map[sid]["lyric_search_hits"] = cand_map[sid].get("lyric_search_hits", 0) + 1
            except Exception:
                pass

            for sp_item in self.search_spotify_tracks(snip, limit=3):
                sid = sp_item["spotify_id"]
                if sid not in cand_map:
                    sc = self._score_spotify_candidate(sp_item, clean_name, clean_name, parsed_artist, duration_sec)
                    sc["matched_snippet"] = snip
                    sc["lyric_search_hits"] = 1
                    cand_map[sid] = sc
                else:
                    cand_map[sid]["lyric_search_hits"] = cand_map[sid].get("lyric_search_hits", 0) + 1

        verified = []
        for cand in cand_map.values():
            hits = cand.get("lyric_search_hits", 0)
            sp_lyrics, _ = self.lyrics_helper.fetch_track_lyrics(
                cand["title"], cand["title"], cand["artists"].split(",")[0], cand["duration_sec"]
            )
            sim = 0.0
            if sp_lyrics and norm_full:
                norm_sp_lrc = self.lyrics_helper.normalize_text(sp_lyrics)
                sim = max(
                    fuzz.token_set_ratio(norm_full, norm_sp_lrc),
                    fuzz.partial_ratio(norm_full[:500], norm_sp_lrc[:500]),
                )
            elif hits > 0:
                sim = min(92.0, 60.0 + (hits * 15.0))

            cand["lyrics_similarity"] = round(sim, 1)
            if sim >= 55.0 or hits > 0:
                cand["score"] = round(min(99.0, max(cand["score"], (cand["score"] * 0.45) + (sim * 0.55) + (hits * 6))), 1)
                cand["matched_by_lyrics"] = True
                if sim > best_sim:
                    best_sim = sim
                    if cand.get("matched_snippet"):
                        best_snippet = cand["matched_snippet"]
            verified.append(cand)

        verified.sort(key=lambda x: x["score"], reverse=True)
        return verified, best_snippet, best_sim
