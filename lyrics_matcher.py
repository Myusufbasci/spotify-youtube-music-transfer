import re
import urllib.parse
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from ytmusicapi import YTMusic


class YTMusicLyricsMatcher:
    """
    Spotify şarkılarını YouTube Music üzerinde arar ve eşleştirir:
    1. Aşama: Doğrudan İsim + Sanatçı + Süre ile bire bir eşleştirme (Official Songs & Videos).
       - Yerel dosyaları (sanatçısı boş olup başlığında 'Sanatçı - Şarkı' yazanları) otomatik ayrıştırır.
       - Spotify'a farklı/sahte sanatçı adıyla yüklenmiş (re-upload) parçaları yakalamak için
         sanatçı uyumu düşük kaldığında salt şarkı adı ve söz aramasına geçer.
    2. Aşama (Bire bir bulunamazsa veya güven skoru düşükse):
       - Şarkının sözlerini (LRCLIB, Lyrics.ovh, Web) çeker,
       - Ayırt edici söz dizeleriyle YouTube Music'te arama yapar,
       - Aday şarkıların YouTube Music gömülü sözleriyle karşılaştırarak doğrular.
    """

    DIRECT_MATCH_THRESHOLD = 85.0

    def __init__(self, language: str = "en"):
        # ytmusicapi filter="songs" ayrıştırıcısı language="en" ile resmi şarkı kataloğunu eksiksiz tarar
        self.ytmusic = YTMusic(language="en")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        })

    @staticmethod
    def clean_track_name(name: str) -> str:
        """Parantez içi Remastered, feat., Radio Edit vb. ekleri temizler."""
        cleaned = re.sub(
            r"\s*[\(\[][^)\]]*(remaster|feat|ft\.|version|edit|mix|live|mono|stereo|deluxe|bonus|from|original)[^)\]]*[\)\]]",
            "",
            name,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"\s*-\s*.*(remaster|version|edit|mix|live|mono|stereo|original).*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        return cleaned.strip() or name.strip()

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[^\w\sçğıöşüâîûə]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def parse_local_or_combined_title(name: str, artist_str: str) -> Tuple[str, str]:
        """
        Spotify yerel dosyalarında (Local Files) sanatçı alanı boş olup
        şarkı adında 'Sanatçı - Şarkı Adı' veya 'Şarkı Adı - Sanatçı' yazıyorsa ayrıştırır.
        """
        if artist_str.strip():
            return name.strip(), artist_str.strip()
        if " - " in name:
            parts = [p.strip() for p in name.split(" - ") if p.strip()]
            if len(parts) >= 2:
                return parts[1], parts[0]
        return name.strip(), ""

    def match_track(self, sp_track: Dict, force_lyrics: bool = False) -> Dict:
        raw_name = sp_track.get("name", "")
        raw_artist_str = sp_track.get("artist_str", "")
        duration_sec = sp_track.get("duration_sec", 0)

        parsed_name, parsed_artist = self.parse_local_or_combined_title(raw_name, raw_artist_str)
        primary_artist = (
            sp_track.get("artists", [""])[0]
            if sp_track.get("artists") and sp_track.get("artists")[0]
            else parsed_artist
        )
        artist_str = raw_artist_str or parsed_artist
        clean_name = self.clean_track_name(parsed_name)

        # 1. AŞAMA: Doğrudan YouTube Music Araması (Songs + Videos)
        direct_candidates = []
        if not force_lyrics:
            direct_candidates = self._search_direct_candidates(
                raw_name, clean_name, primary_artist, artist_str, duration_sec
            )

        best_direct = direct_candidates[0] if direct_candidates else None

        if best_direct and best_direct["score"] >= self.DIRECT_MATCH_THRESHOLD and not force_lyrics:
            return {
                "spotify": sp_track,
                "status": "direct_match",
                "match_method": "Bire Bir Eşleşme",
                "confidence": round(best_direct["score"], 1),
                "yt_match": best_direct,
                "lyrics_info": None,
                "alternatives": direct_candidates[1:5],
            }

        # 2. AŞAMA: Bire bir bulunamadıysa veya skor düşükse SÖZLERLE EŞLEŞTİRME (Lyrics Matching)
        lyrics_text, lyrics_source = self.fetch_track_lyrics(parsed_name, clean_name, primary_artist, duration_sec)

        lyrics_candidates = []
        matched_snippet = ""
        best_lyrics_sim = 0.0

        if lyrics_text:
            snippets = self.extract_distinctive_snippets(lyrics_text, clean_name)
            lyrics_candidates, matched_snippet, best_lyrics_sim = self._search_and_verify_by_lyrics(
                snippets=snippets,
                full_lyrics=lyrics_text,
                sp_name=clean_name,
                sp_artist=primary_artist,
                sp_duration=duration_sec,
                existing_candidates=direct_candidates,
            )

        all_candidates = self._merge_candidates(lyrics_candidates, direct_candidates)

        if all_candidates:
            best = all_candidates[0]
            is_lyrics_winner = best.get("matched_by_lyrics", False) or (
                lyrics_text is not None and best_lyrics_sim >= 45
            )
            status = (
                "lyrics_match"
                if is_lyrics_winner
                else ("direct_match" if best["score"] >= 75 else "low_confidence")
            )
            method_label = (
                f"Sözlerle Eşleşti ({lyrics_source})"
                if is_lyrics_winner
                else ("Yakın Eşleşme" if status == "low_confidence" else "Bire Bir Eşleşme")
            )
            return {
                "spotify": sp_track,
                "status": status,
                "match_method": method_label,
                "confidence": round(best["score"], 1),
                "yt_match": best,
                "lyrics_info": {
                    "found_lyrics": bool(lyrics_text),
                    "source": lyrics_source or "",
                    "matched_snippet": best.get("matched_snippet") or matched_snippet,
                    "lyrics_similarity": round(best.get("lyrics_similarity", best_lyrics_sim), 1),
                    "excerpt": (
                        (lyrics_text[:280] + "...")
                        if lyrics_text and len(lyrics_text) > 280
                        else (lyrics_text or "")
                    ),
                },
                "alternatives": all_candidates[1:5],
            }

        return {
            "spotify": sp_track,
            "status": "not_found",
            "match_method": "Bulunamadı",
            "confidence": 0.0,
            "yt_match": None,
            "lyrics_info": {
                "found_lyrics": bool(lyrics_text),
                "source": lyrics_source or "",
                "matched_snippet": "",
                "lyrics_similarity": 0.0,
                "excerpt": (lyrics_text[:280] + "...") if lyrics_text else "",
            },
            "alternatives": [],
        }

    def _search_direct_candidates(
        self, name: str, clean_name: str, primary_artist: str, artist_str: str, duration_sec: int
    ) -> List[Dict]:
        queries = []
        if primary_artist:
            queries.append(f"{name} {primary_artist}".strip())
            if clean_name.lower() != name.lower():
                queries.append(f"{clean_name} {primary_artist}".strip())
        else:
            queries.append(name.strip())

        # Sahte sanatçı adıyla yüklenmiş (re-upload) şarkılar için yedek olarak salt şarkı adı sorgusu
        if clean_name and clean_name not in queries:
            queries.append(clean_name)

        seen_ids = set()
        candidates = []

        for q_idx, q in enumerate(queries):
            is_title_only_fallback = q_idx == len(queries) - 1 and q == clean_name and bool(primary_artist)
            for search_filter in ("songs", "videos"):
                try:
                    results = self.ytmusic.search(q, filter=search_filter, limit=5)
                except Exception:
                    results = []

                for r in results:
                    vid = r.get("videoId")
                    if not vid or vid in seen_ids:
                        continue
                    seen_ids.add(vid)
                    cand = self._build_and_score_candidate(
                        r,
                        name,
                        clean_name,
                        primary_artist,
                        artist_str,
                        duration_sec,
                        search_filter,
                        allow_reupload_artist_override=is_title_only_fallback,
                    )
                    candidates.append(cand)

                if candidates and max(c["score"] for c in candidates) >= 90:
                    break

            if candidates and max(c["score"] for c in candidates) >= 90:
                break

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates

    def _build_and_score_candidate(
        self,
        yt_item: Dict,
        sp_name: str,
        sp_clean_name: str,
        sp_primary_artist: str,
        sp_artist_str: str,
        sp_duration: int,
        search_filter: str,
        allow_reupload_artist_override: bool = False,
    ) -> Dict:
        yt_title = yt_item.get("title", "")
        yt_clean_title = self.clean_track_name(yt_title)
        yt_artists_list = [a.get("name", "") for a in yt_item.get("artists", []) if a.get("name")]
        yt_artist_str = ", ".join(yt_artists_list)
        yt_duration = yt_item.get("duration_seconds") or self._parse_duration(yt_item.get("duration", ""))

        norm_sp_name = self.normalize_text(sp_name)
        norm_sp_clean = self.normalize_text(sp_clean_name)
        norm_yt_title = self.normalize_text(yt_title)
        norm_yt_clean = self.normalize_text(yt_clean_title)

        norm_sp_artist = self.normalize_text(sp_primary_artist)
        norm_sp_all_artists = self.normalize_text(sp_artist_str)
        norm_yt_artist = self.normalize_text(yt_artist_str)

        # 1. Başlık benzerliği (0-100)
        title_sim = max(
            fuzz.ratio(norm_sp_name, norm_yt_title),
            fuzz.ratio(norm_sp_clean, norm_yt_clean),
            fuzz.token_sort_ratio(norm_sp_clean, norm_yt_clean) * 0.96,
        )

        # Video başlığı "Sanatçı - Şarkı Adı" formatındaysa parçalayarak da kontrol et
        if "-" in yt_title:
            parts = [self.normalize_text(p) for p in yt_title.split("-", 1)]
            for p in parts:
                p_clean = self.normalize_text(self.clean_track_name(p))
                if p_clean and p_clean != norm_sp_artist:
                    title_sim = max(
                        title_sim,
                        fuzz.ratio(norm_sp_clean, p_clean),
                        fuzz.token_sort_ratio(norm_sp_clean, p_clean) * 0.95,
                    )

        # 2. Sanatçı benzerliği (0-100)
        if not norm_sp_artist:
            # Yerel dosya / sanatçısı belirtilmemiş şarkılarda başlık içinde eşleşme varsa
            artist_sim = 88.0 if title_sim >= 85 else 60.0
        else:
            channel_artist_sim = max(
                fuzz.token_set_ratio(norm_sp_artist, norm_yt_artist),
                fuzz.token_set_ratio(norm_sp_all_artists, norm_yt_artist),
            )
            title_artist_sim = min(72.0, fuzz.partial_ratio(norm_sp_artist, norm_yt_title) * 0.75)
            artist_sim = max(channel_artist_sim, title_artist_sim)

            # Eğer Spotify'a sahte sanatçı adıyla yüklenmiş bir şarkıysa ama başlık %95+ ve süre bire bir aynıysa:
            if (
                allow_reupload_artist_override
                and artist_sim < 50
                and title_sim >= 94
                and sp_duration > 0
                and yt_duration > 0
                and abs(sp_duration - yt_duration) <= 5
            ):
                artist_sim = 82.0

        # 3. Süre uyumu (-18 ile +6 puan arası)
        duration_bonus = 0.0
        if sp_duration > 0 and yt_duration > 0:
            diff = abs(sp_duration - yt_duration)
            if diff <= 3:
                duration_bonus = 6.0
            elif diff <= 10:
                duration_bonus = 3.0
            elif diff <= 25:
                duration_bonus = 0.0
            elif diff > 45:
                duration_bonus = -18.0

        # 4. Resmi şarkı (song) bonusu
        type_bonus = 9.0 if search_filter == "songs" else 0.0

        # İstenmeyen cover/karaoke/instrumental/backing track cezası
        penalty = 0.0
        bad_keywords = (
            "karaoke",
            "instrumental",
            "enstrumental",
            "enstrümantal",
            "backing track",
            "drumless",
            "drums",
            "cover",
            "8d audio",
            "nightcore",
            "slowed",
            "sped up",
            "reverb",
            "canlı performans",
            "amatör",
        )
        combined_yt_norm = f"{norm_yt_title} {norm_yt_artist}"
        for bad_word in bad_keywords:
            if bad_word in combined_yt_norm and bad_word not in norm_sp_name:
                penalty -= 32.0

        raw_score = (title_sim * 0.54) + (artist_sim * 0.46) + duration_bonus + type_bonus + penalty
        final_score = max(0.0, min(100.0, raw_score))

        thumbnails = yt_item.get("thumbnails", [])
        thumb_url = thumbnails[-1].get("url", "") if thumbnails else ""
        vid = yt_item.get("videoId", "")

        return {
            "videoId": vid,
            "title": yt_title,
            "artists": yt_artist_str,
            "album": yt_item.get("album", {}).get("name", "") if isinstance(yt_item.get("album"), dict) else "",
            "duration_sec": yt_duration,
            "resultType": "Resmi Şarkı" if search_filter == "songs" else "Video",
            "url": f"https://music.youtube.com/watch?v={vid}",
            "thumbnail": thumb_url,
            "score": round(final_score, 1),
            "title_sim": round(title_sim, 1),
            "artist_sim": round(artist_sim, 1),
            "matched_by_lyrics": False,
            "matched_snippet": "",
            "lyrics_similarity": 0.0,
        }

    def fetch_track_lyrics(
        self, name: str, clean_name: str, artist: str, duration_sec: int = 0
    ) -> Tuple[Optional[str], Optional[str]]:
        # 1. LRCLIB Doğrudan Get
        if artist:
            for track_query in (name, clean_name):
                try:
                    params = {"track_name": track_query, "artist_name": artist}
                    if duration_sec > 0:
                        params["duration"] = duration_sec
                    r = self.session.get("https://lrclib.net/api/get", params=params, timeout=8)
                    if r.status_code == 200:
                        data = r.json()
                        plain = data.get("plainLyrics") or self._strip_lrc_timestamps(data.get("syncedLyrics", ""))
                        if plain and len(plain.strip()) > 40:
                            return plain.strip(), "LRCLIB"
                except Exception:
                    pass

        # 2. LRCLIB Search (Hem sanatçılı hem de sahte sanatçılı yüklemeler için salt şarkı adıyla)
        search_queries = [f"{clean_name} {artist}".strip(), clean_name] if artist else [clean_name]
        for q_str in search_queries:
            if not q_str:
                continue
            try:
                r = self.session.get("https://lrclib.net/api/search", params={"q": q_str}, timeout=8)
                if r.status_code == 200:
                    items = r.json()
                    if isinstance(items, list):
                        for item in items[:6]:
                            item_artist = self.normalize_text(item.get("artistName", ""))
                            item_title = self.normalize_text(item.get("trackName", ""))
                            item_dur = item.get("duration") or 0
                            dur_match = (duration_sec > 0 and item_dur > 0 and abs(duration_sec - item_dur) <= 6)
                            if (
                                (artist and fuzz.token_set_ratio(self.normalize_text(artist), item_artist) >= 65)
                                or fuzz.ratio(self.normalize_text(clean_name), item_title) >= 82
                                or (dur_match and fuzz.token_set_ratio(self.normalize_text(clean_name), item_title) >= 75)
                            ):
                                plain = item.get("plainLyrics") or self._strip_lrc_timestamps(
                                    item.get("syncedLyrics", "")
                                )
                                if plain and len(plain.strip()) > 40:
                                    return plain.strip(), "LRCLIB"
            except Exception:
                pass

        # 3. Lyrics.ovh
        if artist and clean_name:
            try:
                ovh_url = (
                    f"https://api.lyrics.ovh/v1/{urllib.parse.quote(artist)}/{urllib.parse.quote(clean_name)}"
                )
                r = self.session.get(ovh_url, timeout=6)
                if r.status_code == 200:
                    lyrics = r.json().get("lyrics", "")
                    if lyrics and len(lyrics.strip()) > 40:
                        return lyrics.strip(), "Lyrics.ovh"
            except Exception:
                pass

        # 4. Web Araması
        web_lyrics = self._scrape_lyrics_from_web(clean_name, artist)
        if web_lyrics:
            return web_lyrics, "Web Lyrics"

        return None, None

    def _scrape_lyrics_from_web(self, clean_name: str, artist: str) -> Optional[str]:
        query = f"{clean_name} {artist} şarkı sözleri lyrics".strip()
        try:
            resp = self.session.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                timeout=10,
            )
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, "html.parser")
            snippets = []
            for a in soup.select(".result__snippet"):
                txt = a.get_text(" ", strip=True)
                if txt and len(txt) > 25:
                    snippets.append(txt)
            if snippets:
                combined = "\n".join(snippets[:4])
                if len(combined) > 50:
                    return combined
        except Exception:
            pass
        return None

    @staticmethod
    def _strip_lrc_timestamps(synced_lyrics: str) -> str:
        if not synced_lyrics:
            return ""
        cleaned = re.sub(r"\[\d{2}:\d{2}(?:\.\d{1,3})?\]", "", synced_lyrics)
        return cleaned.strip()

    def extract_distinctive_snippets(self, lyrics: str, track_name: str = "") -> List[str]:
        lines = []
        seen = set()

        for raw_line in lyrics.splitlines():
            line = re.sub(r"\[.*?\]|\(.*?\)", "", raw_line).strip()
            words = [w for w in re.findall(r"\w+", line) if len(w) > 1]
            if len(words) < 4 or len(line) < 18:
                continue
            norm = self.normalize_text(line)
            if norm in seen:
                continue
            seen.add(norm)
            lines.append(line)

        if not lines:
            words = lyrics.split()
            if len(words) >= 6:
                return [" ".join(words[:8]), " ".join(words[8:16])][:2]
            return []

        snippets = [lines[0]]
        mid_idx = len(lines) // 3
        if mid_idx < len(lines) and lines[mid_idx] not in snippets:
            snippets.append(lines[mid_idx])

        longest_line = max(lines, key=lambda x: len(set(self.normalize_text(x).split())))
        if longest_line not in snippets:
            snippets.append(longest_line)

        return snippets[:3]

    def _search_and_verify_by_lyrics(
        self,
        snippets: List[str],
        full_lyrics: str,
        sp_name: str,
        sp_artist: str,
        sp_duration: int,
        existing_candidates: List[Dict],
    ) -> Tuple[List[Dict], str, float]:
        norm_full_lyrics = self.normalize_text(full_lyrics)
        candidate_map: Dict[str, Dict] = {c["videoId"]: dict(c) for c in existing_candidates}
        best_snippet = snippets[0] if snippets else ""
        best_lyrics_sim = 0.0

        for snippet in snippets:
            search_queries = [f"{snippet} {sp_artist}".strip(), f'"{snippet}"'] if sp_artist else [f'"{snippet}"']
            for sq in search_queries:
                for search_filter in ("songs", "videos"):
                    try:
                        results = self.ytmusic.search(sq, filter=search_filter, limit=4)
                    except Exception:
                        results = []

                    for r in results:
                        vid = r.get("videoId")
                        if not vid:
                            continue
                        if vid not in candidate_map:
                            cand = self._build_and_score_candidate(
                                r, sp_name, sp_name, sp_artist, sp_artist, sp_duration, search_filter
                            )
                            cand["matched_snippet"] = snippet
                            cand["lyric_search_hits"] = 1
                            candidate_map[vid] = cand
                        else:
                            candidate_map[vid]["lyric_search_hits"] = (
                                candidate_map[vid].get("lyric_search_hits", 0) + 1
                            )
                            if not candidate_map[vid].get("matched_snippet"):
                                candidate_map[vid]["matched_snippet"] = snippet

        sorted_cands = sorted(
            candidate_map.values(),
            key=lambda c: c["score"] + (c.get("lyric_search_hits", 0) * 12),
            reverse=True,
        )

        verified_candidates = []
        for idx, cand in enumerate(sorted_cands[:6]):
            vid = cand["videoId"]
            lyric_hits = cand.get("lyric_search_hits", 0)
            yt_lyrics = None

            if idx < 4:
                yt_lyrics = self._get_ytmusic_lyrics(vid)

            lyrics_sim = 0.0
            if yt_lyrics and norm_full_lyrics:
                norm_yt_lyrics = self.normalize_text(yt_lyrics)
                lyrics_sim = max(
                    fuzz.token_set_ratio(norm_full_lyrics, norm_yt_lyrics),
                    fuzz.partial_ratio(norm_full_lyrics[:500], norm_yt_lyrics[:500]),
                )
            elif lyric_hits > 0:
                lyrics_sim = min(92.0, 55.0 + (lyric_hits * 15.0) + (cand["artist_sim"] * 0.2))

            cand["lyrics_similarity"] = round(lyrics_sim, 1)

            if lyrics_sim >= 55.0 or lyric_hits > 0:
                boosted_score = max(
                    cand["score"],
                    (cand["score"] * 0.45) + (lyrics_sim * 0.55) + (lyric_hits * 6.0),
                )
                cand["score"] = round(min(99.0, boosted_score), 1)
                cand["matched_by_lyrics"] = True
                if lyrics_sim > best_lyrics_sim:
                    best_lyrics_sim = lyrics_sim
                    if cand.get("matched_snippet"):
                        best_snippet = cand["matched_snippet"]

            verified_candidates.append(cand)

        verified_candidates.sort(key=lambda x: x["score"], reverse=True)
        return verified_candidates, best_snippet, best_lyrics_sim

    def _get_ytmusic_lyrics(self, video_id: str) -> Optional[str]:
        try:
            watch = self.ytmusic.get_watch_playlist(videoId=video_id)
            lyrics_browse_id = watch.get("lyrics")
            if lyrics_browse_id:
                lyrics_data = self.ytmusic.get_lyrics(lyrics_browse_id)
                if lyrics_data and lyrics_data.get("lyrics"):
                    return lyrics_data["lyrics"]
        except Exception:
            pass
        return None

    @staticmethod
    def _merge_candidates(list_a: List[Dict], list_b: List[Dict]) -> List[Dict]:
        merged = {}
        for c in list_a + list_b:
            vid = c["videoId"]
            if vid not in merged or c["score"] > merged[vid]["score"]:
                merged[vid] = c
        res = list(merged.values())
        res.sort(key=lambda x: x["score"], reverse=True)
        return res

    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        if not duration_str:
            return 0
        parts = [int(p) for p in re.findall(r"\d+", duration_str)]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return 0
