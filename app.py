import argparse
import concurrent.futures
import json
import os
import threading
from pathlib import Path
from typing import Dict, List
from flask import Flask, jsonify, render_template_string, request

from spotify_scraper import SpotifyScraper
from lyrics_matcher import YTMusicLyricsMatcher
from ytmusic_saver import YTMusicSaver
from ytm_to_spotify import YTMToSpotifyMatcher

app = Flask(__name__)

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
RESULTS_FILE = BASE_DIR / "last_transfer_results.json"

scraper = SpotifyScraper()
matcher = YTMusicLyricsMatcher(language="en")
saver = YTMusicSaver(base_dir=str(BASE_DIR))
ytm_to_sp = YTMToSpotifyMatcher()

STATE = {
    "running": False,
    "phase": "idle",
    "message": "Hazır",
    "current": 0,
    "total": 0,
    "playlists": [],
}
STATE_LOCK = threading.Lock()


def load_saved_playlists() -> List[Dict]:
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for pl in data:
                        if "direction" not in pl:
                            pl["direction"] = "sp_to_ytm"
                    return data
        except Exception:
            pass
    return []


def save_playlists_to_disk(playlists: List[Dict]):
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)


def recompute_playlist_stats(pl: Dict):
    items = pl.get("items", [])
    direction = pl.get("direction", "sp_to_ytm")
    pl["total_tracks"] = len(items)
    pl["stats"] = {
        "direct_match": sum(1 for m in items if m and m.get("status") == "direct_match"),
        "lyrics_match": sum(1 for m in items if m and m.get("status") == "lyrics_match"),
        "low_confidence": sum(1 for m in items if m and m.get("status") == "low_confidence"),
        "not_found": sum(1 for m in items if m and m.get("status") == "not_found"),
    }
    if direction == "sp_to_ytm":
        video_ids = [
            m["yt_match"]["videoId"]
            for m in items
            if m and m.get("yt_match") and m["yt_match"].get("videoId")
        ]
        pl["instant_links"] = saver.generate_instant_playlist_urls(video_ids)
    else:
        pl["instant_links"] = []


def process_urls(urls: List[str], clear_existing: bool = False, max_workers: int = 8) -> List[Dict]:
    with STATE_LOCK:
        STATE["running"] = True
        STATE["phase"] = "scraping"
        STATE["message"] = "Bağlantılar okunuyor..."
        STATE["current"] = 0
        STATE["total"] = 0

    try:
        scraped_lists = []
        total_tracks = 0
        for u in urls:
            u = u.strip()
            if not u:
                continue
            is_yt = ytm_to_sp.is_youtube_url(u)
            direction = "ytm_to_sp" if is_yt else "sp_to_ytm"

            with STATE_LOCK:
                STATE["message"] = f"{'YouTube Music' if is_yt else 'Spotify'} okunuyor: {u}"

            if is_yt:
                src_data = ytm_to_sp.fetch_from_url(u)
            else:
                src_data = scraper.fetch_from_url(u)

            src_data["direction"] = direction
            scraped_lists.append(src_data)
            total_tracks += len(src_data.get("tracks", []))

        with STATE_LOCK:
            STATE["phase"] = "matching"
            STATE["total"] = total_tracks
            STATE["current"] = 0

        existing = [] if clear_existing else load_saved_playlists()

        for src_data in scraped_lists:
            direction = src_data.get("direction", "sp_to_ytm")
            tracks = src_data.get("tracks", [])
            matched_tracks = [None] * len(tracks)

            if direction == "ytm_to_sp":
                # Spotify arama oturumunu iş parçacıklarından önce hazırla
                with STATE_LOCK:
                    STATE["message"] = "Spotify arama oturumu hazırlanıyor..."
                ytm_to_sp._ensure_spotify_search_session()

            def _worker(idx_track):
                idx, tr = idx_track
                if direction == "ytm_to_sp":
                    res = ytm_to_sp.match_track(tr)
                else:
                    res = matcher.match_track(tr)
                    if res["confidence"] < 99.5:
                        lyrics_res = matcher.match_track(tr, force_lyrics=True)
                        if lyrics_res.get("yt_match") and lyrics_res["confidence"] >= res["confidence"] - 5:
                            res = lyrics_res

                with STATE_LOCK:
                    STATE["current"] += 1
                    STATE["message"] = (
                        f"{STATE['current']} / {STATE['total']} — "
                        f"{tr.get('name')} ({tr.get('artist_str') or 'Bilinmeyen Sanatçı'})"
                    )
                return idx, res

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(_worker, (i, t)) for i, t in enumerate(tracks)]
                for fut in concurrent.futures.as_completed(futures):
                    idx, res = fut.result()
                    matched_tracks[idx] = res

            pl_result = {
                "title": src_data.get("title", "Çalma Listesi"),
                "spotify_url": src_data.get("url", ""),
                "direction": direction,
                "total_tracks": len(tracks),
                "stats": {},
                "instant_links": [],
                "items": matched_tracks,
            }
            recompute_playlist_stats(pl_result)

            existing = [
                p for p in existing
                if not (p.get("title") == pl_result["title"] and p.get("direction") == direction)
            ]
            existing.append(pl_result)

        save_playlists_to_disk(existing)

        with STATE_LOCK:
            STATE["playlists"] = existing
            STATE["phase"] = "done"
            STATE["message"] = f"Tamamlandı ({total_tracks} şarkı eşleştirildi)."
            STATE["running"] = False

        return existing

    except Exception as e:
        with STATE_LOCK:
            STATE["phase"] = "error"
            STATE["message"] = f"Hata: {str(e)}"
            STATE["running"] = False
        raise


HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify ↔ YouTube Music — Bi-Directional Lyrics Transfer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #09090b;
            --surface: #111114;
            --surface-2: #18181c;
            --surface-3: #202026;
            --border: #26262c;
            --border-subtle: #1c1c21;
            --text: #f4f4f6;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            --accent: #10b981;
            --accent-hover: #059669;
            --accent-soft: rgba(16, 185, 129, 0.12);
            --yt-red: #f43f5e;
            --yt-soft: rgba(244, 63, 94, 0.12);
            --amber: #f59e0b;
            --amber-soft: rgba(245, 158, 11, 0.12);
            --sky: #38bdf8;
            --sky-soft: rgba(56, 189, 248, 0.12);
            --danger: #ef4444;
            --radius: 8px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }

        .mono {
            font-family: 'JetBrains Mono', monospace;
            font-variant-numeric: tabular-nums;
        }

        .layout {
            max-width: 1240px;
            margin: 0 auto;
            padding: 32px 24px 64px;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 28px;
            gap: 16px;
            flex-wrap: wrap;
        }

        .brand {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .brand-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: var(--text);
        }

        .brand-tag {
            font-size: 11px;
            font-weight: 500;
            padding: 2px 8px;
            border-radius: 4px;
            background: var(--surface-3);
            color: var(--text-secondary);
            border: 1px solid var(--border);
            letter-spacing: 0.02em;
        }

        .dir-tag-ytm {
            background: var(--yt-soft);
            color: #fb7185;
            border-color: rgba(244, 63, 94, 0.3);
        }

        .dir-tag-sp {
            background: var(--accent-soft);
            color: #34d399;
            border-color: rgba(16, 185, 129, 0.3);
        }

        .brand-sub {
            color: var(--text-secondary);
            font-size: 13px;
        }

        .topbar-actions {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text);
            text-decoration: none;
            white-space: nowrap;
        }

        .btn:hover:not(:disabled) {
            background: var(--surface-3);
            border-color: #383842;
        }

        .btn:disabled {
            opacity: 0.45;
            cursor: not-allowed;
        }

        .btn-primary {
            background: var(--text);
            color: #09090b;
            border-color: var(--text);
            font-weight: 600;
        }

        .btn-primary:hover:not(:disabled) {
            background: #e4e4e7;
            border-color: #e4e4e7;
        }

        .btn-accent {
            background: var(--accent);
            color: #052e16;
            border-color: var(--accent);
            font-weight: 600;
        }

        .btn-accent:hover:not(:disabled) {
            background: var(--accent-hover);
            border-color: var(--accent-hover);
            color: #ffffff;
        }

        .btn-ghost {
            background: transparent;
            border-color: transparent;
            color: var(--text-secondary);
        }

        .btn-ghost:hover:not(:disabled) {
            background: var(--surface-2);
            color: var(--text);
        }

        .btn-sm {
            padding: 5px 10px;
            font-size: 12px;
        }

        .icon {
            width: 15px;
            height: 15px;
            flex-shrink: 0;
        }

        .top-grid {
            display: grid;
            grid-template-columns: 1fr 1.18fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        @media (max-width: 960px) {
            .top-grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            gap: 12px;
            flex-wrap: wrap;
        }

        .card-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card-desc {
            font-size: 12.5px;
            color: var(--text-secondary);
            margin-bottom: 14px;
        }

        textarea.input-area {
            width: 100%;
            height: 98px;
            background: var(--bg);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 13px;
            resize: vertical;
            outline: none;
            transition: border-color 0.15s;
        }

        textarea.input-area:focus {
            border-color: #52525b;
        }

        .input-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            gap: 10px;
            flex-wrap: wrap;
        }

        .checkbox-label {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            font-size: 12.5px;
            color: var(--text-secondary);
            cursor: pointer;
            user-select: none;
        }

        .progress-container {
            margin-top: 14px;
            padding: 12px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            display: none;
        }

        .progress-meta {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }

        .progress-track {
            width: 100%;
            height: 6px;
            background: var(--surface-3);
            border-radius: 3px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: var(--accent);
            width: 0%;
            transition: width 0.25s ease;
        }

        /* Guide Tabs */
        .guide-switch {
            display: inline-flex;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 2px;
            gap: 2px;
        }

        .guide-tab {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11.5px;
            font-weight: 500;
            cursor: pointer;
        }

        .guide-tab.active {
            background: var(--surface-3);
            color: var(--text);
        }

        .steps-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .step-item {
            display: flex;
            gap: 12px;
            padding: 12px;
            background: var(--bg);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            align-items: flex-start;
        }

        .step-num {
            width: 22px;
            height: 22px;
            border-radius: 4px;
            background: var(--surface-3);
            border: 1px solid var(--border);
            color: var(--text);
            font-size: 11px;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: 1px;
        }

        .step-body {
            flex: 1;
            min-width: 0;
        }

        .step-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 3px;
        }

        .step-text {
            font-size: 12.5px;
            color: var(--text-secondary);
            line-height: 1.45;
        }

        .step-actions {
            margin-top: 10px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }

        kbd {
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 1px 6px;
            font-size: 11.5px;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text);
        }

        .code-drawer {
            margin-top: 10px;
            display: none;
        }

        .code-drawer.open {
            display: block;
        }

        .code-box-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            padding: 6px 10px;
            font-size: 11.5px;
            color: var(--text-secondary);
        }

        .code-pre {
            width: 100%;
            height: 105px;
            background: #050507;
            color: #d4d4d8;
            border: 1px solid var(--border);
            border-radius: 0 0 6px 6px;
            padding: 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11.5px;
            resize: vertical;
            outline: none;
        }

        .playlist-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            margin-bottom: 24px;
            overflow: hidden;
        }

        .playlist-top {
            padding: 18px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }

        .playlist-title-row {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .playlist-name {
            font-size: 17px;
            font-weight: 600;
            letter-spacing: -0.01em;
        }

        .stat-pills {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 8px;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 9px;
            border-radius: 4px;
            font-size: 11.5px;
            font-weight: 500;
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text-secondary);
        }

        .pill-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
        }

        .dot-green { background: var(--accent); }
        .dot-sky { background: var(--sky); }
        .dot-amber { background: var(--amber); }
        .dot-red { background: var(--danger); }

        .playlist-toolbar {
            padding: 10px 20px;
            background: var(--bg);
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }

        .filter-tabs {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }

        .tab-btn {
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-secondary);
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
        }

        .tab-btn:hover {
            color: var(--text);
            background: var(--surface-2);
        }

        .tab-btn.active {
            background: var(--surface-3);
            color: var(--text);
            border-color: var(--border);
        }

        .search-input {
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 6px 11px;
            border-radius: 5px;
            font-size: 12.5px;
            width: 240px;
            outline: none;
        }

        .search-input:focus {
            border-color: #52525b;
        }

        .queue-bar {
            padding: 10px 20px;
            background: var(--surface-2);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .table-wrap {
            max-height: 540px;
            overflow-y: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        thead th {
            position: sticky;
            top: 0;
            background: var(--surface);
            color: var(--text-muted);
            font-weight: 500;
            font-size: 11.5px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 10px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            z-index: 2;
        }

        tbody td {
            padding: 10px 16px;
            border-bottom: 1px solid var(--border-subtle);
            vertical-align: middle;
        }

        tbody tr:hover {
            background: rgba(255, 255, 255, 0.02);
        }

        .track-cell {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .thumb {
            width: 34px;
            height: 34px;
            border-radius: 4px;
            background: var(--surface-3);
            object-fit: cover;
            flex-shrink: 0;
        }

        .track-title {
            font-weight: 500;
            color: var(--text);
            display: block;
        }

        .track-artist {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .yt-link {
            color: var(--text);
            text-decoration: none;
            font-weight: 500;
        }

        .yt-link:hover {
            color: var(--accent);
            text-decoration: underline;
        }

        .lyric-quote {
            margin-top: 4px;
            display: inline-block;
            font-size: 11.5px;
            color: var(--sky);
            background: var(--sky-soft);
            border: 1px solid rgba(56, 189, 248, 0.25);
            padding: 2px 7px;
            border-radius: 4px;
        }

        .status-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11.5px;
            font-weight: 500;
            white-space: nowrap;
        }

        .st-direct {
            background: var(--accent-soft);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.25);
        }

        .st-lyrics {
            background: var(--sky-soft);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.25);
        }

        .st-low {
            background: var(--amber-soft);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.25);
        }

        .st-none {
            background: rgba(239, 68, 68, 0.12);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.25);
        }

        .empty-state {
            text-align: center;
            padding: 56px 20px;
            color: var(--text-secondary);
            background: var(--surface);
            border: 1px dashed var(--border);
            border-radius: var(--radius);
        }
    </style>
</head>
<body>
<div class="layout">
    <header class="topbar">
        <div class="brand">
            <div class="brand-title">
                <svg class="icon" style="width:20px;height:20px;color:var(--accent)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 2.1l4 4-4 4"></path>
                    <path d="M3 12.2v-2a4 4 0 0 1 4-4h14"></path>
                    <path d="M7 21.9l-4-4 4-4"></path>
                    <path d="M21 11.8v2a4 4 0 0 1-4 4H3"></path>
                </svg>
                <span>Spotify &harr; YouTube Music</span>
                <span class="brand-tag mono">Bi-Directional</span>
            </div>
            <div class="brand-sub">API anahtarsız, çift yönlü çalma listesi ve şarkı sözü (lyrics) eşleştirme aracı</div>
        </div>
        <div class="topbar-actions">
            <button type="button" class="btn btn-sm" onclick="exportJSON()">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                JSON İndir
            </button>
            <button type="button" class="btn btn-sm btn-ghost" onclick="clearAllPlaylists()">
                Listeleri Temizle
            </button>
        </div>
    </header>

    <div class="top-grid">
        <!-- Left: Universal Input Panel -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Kaynak Bağlantılar (Spotify veya YouTube Music)
                </div>
                <span class="mono" style="font-size:11.5px; color:var(--text-muted)">Otomatik Yön Algılama</span>
            </div>
            <div class="card-desc">
                <strong>Spotify</strong> bağlantısı yapıştırırsanız YouTube Music'te; <strong>YouTube / YouTube Music</strong> bağlantısı yapıştırırsanız Spotify'da (bire bir + şarkı sözleriyle) eşleştirir.
            </div>
            <textarea id="urlsInput" class="input-area mono" placeholder="https://open.spotify.com/playlist/...&#10;veya&#10;https://music.youtube.com/playlist?list=..."></textarea>
            <div class="input-footer">
                <label class="checkbox-label">
                    <input type="checkbox" id="replaceCheck">
                    <span>Mevcut listeleri temizleyip sıfırdan tara</span>
                </label>
                <button type="button" id="startBtn" class="btn btn-primary" onclick="startProcess()">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Şarkıları Tara ve Eşleştir
                </button>
            </div>

            <div id="progressBox" class="progress-container">
                <div class="progress-meta">
                    <span id="progressText">Hazırlanıyor...</span>
                    <span id="progressPct" class="mono">0%</span>
                </div>
                <div class="progress-track">
                    <div id="progressFill" class="progress-fill"></div>
                </div>
            </div>
        </div>

        <!-- Right: Bi-Directional Transfer Guide -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <svg class="icon" style="color:var(--accent)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                    Hesaba Kayıt Rehberi
                </div>
                <div class="guide-switch">
                    <button type="button" id="guideTabYTM" class="guide-tab active" onclick="switchGuideMode('sp_to_ytm')">YouTube Music'e Kayıt</button>
                    <button type="button" id="guideTabSP" class="guide-tab" onclick="switchGuideMode('ytm_to_sp')">Spotify'a Kayıt</button>
                </div>
            </div>

            <!-- Guide Mode 1: Save to YouTube Music -->
            <div id="guidePanelYTM" class="steps-list">
                <div class="step-item">
                    <div class="step-num mono">1</div>
                    <div class="step-body">
                        <div class="step-title">YouTube Music Aktarım Kodunu Kopyalayın</div>
                        <div class="step-text">
                            Spotify'dan eşleştirilen çalma listelerini tek seferde oluşturacak konsol betiğini panoya kopyalayın.
                        </div>
                        <div class="step-actions">
                            <button type="button" id="copyAllYTMBtn" class="btn btn-accent btn-sm" onclick="copyYTMConsoleScript(-1, this)">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                </svg>
                                <span>Aktarım Kodunu Kopyala</span>
                            </button>
                            <button type="button" class="btn btn-sm" onclick="toggleCodeDrawer()">
                                <span id="toggleCodeLabel">Kodu Göster</span>
                            </button>
                        </div>
                        <div id="codeDrawer" class="code-drawer">
                            <div class="code-box-header">
                                <span class="mono">ytmusic_create_playlists.js</span>
                                <button type="button" class="btn btn-sm" style="padding:2px 8px; font-size:11px;" onclick="copyFromCodeBox(this)">Kopyala</button>
                            </div>
                            <textarea id="manualCodeBox" class="code-pre" readonly onclick="this.select()"></textarea>
                        </div>
                    </div>
                </div>

                <div class="step-item">
                    <div class="step-num mono">2</div>
                    <div class="step-body">
                        <div class="step-title">YouTube Music'i Yeni Sekmede Açın</div>
                        <div class="step-text">Oturumunuzun açık olduğu YouTube Music sekmesine geçin.</div>
                        <div class="step-actions">
                            <a href="https://music.youtube.com" target="_blank" rel="noopener" class="btn btn-sm">
                                <span>music.youtube.com'u Aç</span>
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                    <polyline points="15 3 21 3 21 9"></polyline>
                                    <line x1="10" y1="14" x2="21" y2="3"></line>
                                </svg>
                            </a>
                        </div>
                    </div>
                </div>

                <div class="step-item">
                    <div class="step-num mono">3</div>
                    <div class="step-body">
                        <div class="step-title">Konsola Yapıştırıp Çalıştırın</div>
                        <div class="step-text">
                            <kbd>F12</kbd> &rarr; <strong>Console</strong> sekmesine tıklayın, <kbd>Ctrl</kbd>+<kbd>V</kbd> yapıp <kbd>Enter</kbd>'a basın.
                            <span style="display:block; margin-top:4px; color:var(--text-muted); font-size:11.5px;">
                                İlk kez yapıştırıyorsanız tarayıcı güvenlik uyarısı sonrası konsola <kbd>allow pasting</kbd> (veya <kbd>yapıştırmaya izin ver</kbd>) yazıp Enter'a basın.
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Guide Mode 2: Save to Spotify -->
            <div id="guidePanelSP" class="steps-list" style="display:none;">
                <div class="step-item">
                    <div class="step-num mono">1</div>
                    <div class="step-body">
                        <div class="step-title">Spotify Şarkı Bağlantılarını Kopyalayın</div>
                        <div class="step-text">
                            Spotify masaüstü ve web uygulaması, kopyalanan şarkı bağlantılarını doğrudan çalma listesine yapıştırmayı destekler (konsol açmaya gerek yoktur).
                        </div>
                        <div class="step-actions">
                            <button type="button" id="copyAllSPBtn" class="btn btn-accent btn-sm" onclick="copySpotifyTrackLinks(-1, this)">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                </svg>
                                <span>Spotify Şarkı Linklerini Kopyala</span>
                            </button>
                            <a href="https://open.spotify.com" target="_blank" rel="noopener" class="btn btn-sm">
                                <span>open.spotify.com'u Aç ↗</span>
                            </a>
                        </div>
                    </div>
                </div>

                <div class="step-item">
                    <div class="step-num mono">2</div>
                    <div class="step-body">
                        <div class="step-title">Spotify'da Boş Bir Çalma Listesi Açıp Ctrl+V Yapın</div>
                        <div class="step-text">
                            Spotify uygulamasında veya web sayfasında yeni bir çalma listesi oluşturun, listenin içine bir kez tıklayıp <kbd>Ctrl</kbd>+<kbd>V</kbd> (Yapıştır) tuşlarına basın. Tüm şarkılar anında eklenecektir.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="resultsArea"></div>
</div>

<script>
let CURRENT_PLAYLISTS = [];
let FILTER_STATE = {};

function formatDuration(sec) {
    if (!sec || sec <= 0) return "--:--";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return m + ":" + String(s).padStart(2, "0");
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function switchGuideMode(mode) {
    const isYTM = mode === "sp_to_ytm";
    document.getElementById("guideTabYTM").classList.toggle("active", isYTM);
    document.getElementById("guideTabSP").classList.toggle("active", !isYTM);
    document.getElementById("guidePanelYTM").style.display = isYTM ? "flex" : "none";
    document.getElementById("guidePanelSP").style.display = isYTM ? "none" : "flex";
}

function buildYTMConsoleScript(targetIndex) {
    if (!CURRENT_PLAYLISTS || CURRENT_PLAYLISTS.length === 0) return "";
    const selected = targetIndex === -1
        ? CURRENT_PLAYLISTS.filter(p => (p.direction || "sp_to_ytm") === "sp_to_ytm")
        : [CURRENT_PLAYLISTS[targetIndex]];
    const payload = selected.filter(Boolean).map(pl => ({
        title: pl.title,
        videoIds: (pl.items || []).map(it => it.yt_match && it.yt_match.videoId).filter(Boolean)
    }));
    if (!payload.length) return "";

    const lines = [
        "(async () => {",
        "  const playlists = " + JSON.stringify(payload) + ";",
        "  const m = document.cookie.match(/(?:^|; )(?:__Secure-3PAPISID|SAPISID)=([^;]+)/);",
        "  const sapisid = m ? m[1] : null;",
        "  if (!sapisid) { alert('Lütfen önce YouTube Music hesabınıza giriş yapın.'); return; }",
        "  const origin = 'https://music.youtube.com';",
        "  async function getAuth() {",
        "    const ts = Math.floor(Date.now() / 1000);",
        "    const msg = new TextEncoder().encode(ts + ' ' + sapisid + ' ' + origin);",
        "    const buf = await crypto.subtle.digest('SHA-1', msg);",
        "    const hex = Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');",
        "    return 'SAPISIDHASH ' + ts + '_' + hex;",
        "  }",
        "  const cfg = window.ytcfg;",
        "  const apiKey = cfg.get('INNERTUBE_API_KEY');",
        "  const context = cfg.get('INNERTUBE_CONTEXT');",
        "  const authUser = String(cfg.get('SESSION_INDEX') || '0');",
        "  const created = [];",
        "  for (const pl of playlists) {",
        "    console.log('[Aktarım] Oluşturuluyor:', pl.title, '(' + pl.videoIds.length + ' şarkı)...');",
        "    const res = await fetch('/youtubei/v1/playlist/create?key=' + apiKey + '&prettyPrint=false', {",
        "      method: 'POST',",
        "      credentials: 'include',",
        "      headers: {",
        "        'Content-Type': 'application/json',",
        "        'Authorization': await getAuth(),",
        "        'X-Origin': origin,",
        "        'X-Goog-AuthUser': authUser",
        "      },",
        "      body: JSON.stringify({",
        "        context,",
        "        title: pl.title,",
        "        description: 'Spotify <-> YouTube Music aracı ile aktarıldı.',",
        "        privacyStatus: 'PRIVATE',",
        "        videoIds: pl.videoIds",
        "      })",
        "    }).then(r => r.json());",
        "    if (res.playlistId) {",
        "      const url = 'https://music.youtube.com/playlist?list=' + res.playlistId;",
        "      console.log('[Tamamlandı]', pl.title, '->', url);",
        "      created.push({title: pl.title, url, count: pl.videoIds.length});",
        "    } else {",
        "      console.error('[Hata]', pl.title, res);",
        "    }",
        "  }",
        "  if (created.length > 0) {",
        "    alert('Çalma listeleri oluşturuldu:\\n\\n' + created.map(c => '• ' + c.title + ' (' + c.count + ' şarkı)').join('\\n'));",
        "    window.location.href = created[0].url;",
        "  }",
        "})();"
    ];
    return lines.join("\n");
}

function buildSpotifyTrackLinks(targetIndex) {
    if (!CURRENT_PLAYLISTS || CURRENT_PLAYLISTS.length === 0) return "";
    const selected = targetIndex === -1
        ? CURRENT_PLAYLISTS.filter(p => p.direction === "ytm_to_sp")
        : [CURRENT_PLAYLISTS[targetIndex]];
    const urls = [];
    selected.filter(Boolean).forEach(pl => {
        (pl.items || []).forEach(it => {
            if (it && it.yt_match && it.yt_match.url) {
                urls.push(it.yt_match.url);
            }
        });
    });
    return urls.join("\n");
}

function writeToClipboard(text) {
    const codeBox = document.getElementById("manualCodeBox");
    if (codeBox) codeBox.value = text;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(() => {});
    }
    const temp = document.createElement("textarea");
    temp.value = text;
    temp.style.position = "fixed";
    temp.style.opacity = "0";
    document.body.appendChild(temp);
    temp.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(temp);
}

function flashButtonCopied(btn, originalText) {
    if (!btn) return;
    const span = btn.querySelector("span") || btn;
    const prev = originalText || span.innerText;
    span.innerText = "Kopyalandı ✓";
    setTimeout(() => {
        span.innerText = prev;
    }, 2200);
}

function copyYTMConsoleScript(targetIndex, btnEl) {
    const scriptText = buildYTMConsoleScript(targetIndex);
    if (!scriptText) {
        alert("Kopyalanacak Spotify -> YouTube Music listesi bulunamadı.");
        return;
    }
    switchGuideMode("sp_to_ytm");
    writeToClipboard(scriptText);
    const span = btnEl ? (btnEl.querySelector("span") || btnEl) : null;
    flashButtonCopied(btnEl, span ? span.innerText : "Kopyala");
}

function copySpotifyTrackLinks(targetIndex, btnEl) {
    const linksText = buildSpotifyTrackLinks(targetIndex);
    if (!linksText) {
        alert("Kopyalanacak YouTube Music -> Spotify listesi bulunamadı.");
        return;
    }
    switchGuideMode("ytm_to_sp");
    writeToClipboard(linksText);
    const span = btnEl ? (btnEl.querySelector("span") || btnEl) : null;
    flashButtonCopied(btnEl, span ? span.innerText : "Linkleri Kopyala");
}

function toggleCodeDrawer() {
    const drawer = document.getElementById("codeDrawer");
    const label = document.getElementById("toggleCodeLabel");
    const isOpen = drawer.classList.toggle("open");
    label.innerText = isOpen ? "Kodu Gizle" : "Kodu Göster";
    if (isOpen) {
        document.getElementById("manualCodeBox").value = buildYTMConsoleScript(-1);
    }
}

function copyFromCodeBox(btnEl) {
    const box = document.getElementById("manualCodeBox");
    if (!box.value) {
        box.value = buildYTMConsoleScript(-1);
    }
    writeToClipboard(box.value);
    flashButtonCopied(btnEl, "Kopyala");
}

async function startProcess() {
    const raw = document.getElementById("urlsInput").value.trim();
    if (!raw) {
        alert("Lütfen en az bir Spotify veya YouTube Music bağlantısı girin.");
        return;
    }
    const urls = raw.split("\n").map(s => s.trim()).filter(Boolean);
    const clearExisting = document.getElementById("replaceCheck").checked;

    document.getElementById("startBtn").disabled = true;
    const pBox = document.getElementById("progressBox");
    pBox.style.display = "block";
    document.getElementById("progressText").innerText = "Bağlantılar okunuyor...";
    document.getElementById("progressPct").innerText = "0%";
    document.getElementById("progressFill").style.width = "0%";

    await fetch("/api/start", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({urls, clear_existing: clearExisting})
    });
    pollStatus();
}

async function pollStatus() {
    const r = await fetch("/api/status");
    const st = await r.json();

    const pBox = document.getElementById("progressBox");
    pBox.style.display = "block";
    document.getElementById("progressText").innerText = st.message || "İşleniyor...";

    const pct = st.total > 0 ? Math.min(100, Math.round((st.current / st.total) * 100)) : (st.running ? 15 : 100);
    document.getElementById("progressPct").innerText = pct + "%";
    document.getElementById("progressFill").style.width = pct + "%";

    if (st.running) {
        setTimeout(pollStatus, 800);
    } else {
        document.getElementById("startBtn").disabled = false;
        setTimeout(() => { pBox.style.display = "none"; }, 2500);
        CURRENT_PLAYLISTS = st.playlists || [];
        if (CURRENT_PLAYLISTS.length > 0) {
            const lastDir = CURRENT_PLAYLISTS[CURRENT_PLAYLISTS.length - 1].direction || "sp_to_ytm";
            switchGuideMode(lastDir);
        }
        renderPlaylists();
    }
}

async function removePlaylist(plIdx) {
    const r = await fetch("/api/remove_playlist", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({index: plIdx})
    });
    const st = await r.json();
    CURRENT_PLAYLISTS = st.playlists || [];
    renderPlaylists();
}

async function clearAllPlaylists() {
    if (!CURRENT_PLAYLISTS.length) return;
    if (!confirm("Yüklü tüm çalma listelerini ekrandan temizlemek istiyor musunuz?")) return;
    const r = await fetch("/api/clear", {method: "POST"});
    const st = await r.json();
    CURRENT_PLAYLISTS = st.playlists || [];
    renderPlaylists();
}

function exportJSON() {
    if (!CURRENT_PLAYLISTS.length) {
        alert("İndirilecek veri bulunmuyor.");
        return;
    }
    const blob = new Blob([JSON.stringify(CURRENT_PLAYLISTS, null, 2)], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "playlist_transfer_export.json";
    a.click();
    URL.revokeObjectURL(url);
}

function setFilterTab(plIdx, tab) {
    if (!FILTER_STATE[plIdx]) FILTER_STATE[plIdx] = {tab: "all", q: ""};
    FILTER_STATE[plIdx].tab = tab;
    renderPlaylistRows(plIdx);
}

function setFilterQuery(plIdx, val) {
    if (!FILTER_STATE[plIdx]) FILTER_STATE[plIdx] = {tab: "all", q: ""};
    FILTER_STATE[plIdx].q = val.toLowerCase().trim();
    renderPlaylistRows(plIdx);
}

function updateGuideButtons() {
    const ytmLists = CURRENT_PLAYLISTS.filter(p => (p.direction || "sp_to_ytm") === "sp_to_ytm");
    const spLists = CURRENT_PLAYLISTS.filter(p => p.direction === "ytm_to_sp");

    const ytmCount = ytmLists.reduce((a, p) => a + (p.total_tracks || 0), 0);
    const spCount = spLists.reduce((a, p) => a + (p.total_tracks || 0), 0);

    const ytmBtn = document.getElementById("copyAllYTMBtn");
    if (ytmBtn) {
        const sp = ytmBtn.querySelector("span");
        if (sp) sp.innerText = ytmCount > 0 ? `YouTube Music Kodunu Kopyala (${ytmCount} Şarkı)` : "YouTube Music Kodunu Kopyala";
    }
    const spBtn = document.getElementById("copyAllSPBtn");
    if (spBtn) {
        const sp = spBtn.querySelector("span");
        if (sp) sp.innerText = spCount > 0 ? `Spotify Şarkı Linklerini Kopyala (${spCount} Şarkı)` : "Spotify Şarkı Linklerini Kopyala";
    }
    const codeBox = document.getElementById("manualCodeBox");
    if (codeBox) codeBox.value = buildYTMConsoleScript(-1);
}

function renderPlaylists() {
    updateGuideButtons();
    const area = document.getElementById("resultsArea");

    if (!CURRENT_PLAYLISTS || CURRENT_PLAYLISTS.length === 0) {
        area.innerHTML = `
            <div class="empty-state">
                <div style="font-size:15px; font-weight:600; color:var(--text); margin-bottom:6px;">Henüz Çalma Listesi Eklenmedi</div>
                <div>Sol üstteki kutuya bir <strong>Spotify</strong> veya <strong>YouTube Music</strong> çalma listesi bağlantısı yapıştırıp <strong>Şarkıları Tara ve Eşleştir</strong> butonuna basın.</div>
            </div>
        `;
        return;
    }

    area.innerHTML = "";
    CURRENT_PLAYLISTS.forEach((pl, idx) => {
        if (!FILTER_STATE[idx]) FILTER_STATE[idx] = {tab: "all", q: ""};
        const isYTMToSP = pl.direction === "ytm_to_sp";
        const dirBadge = isYTMToSP
            ? `<span class="brand-tag dir-tag-sp">YouTube Music &rarr; Spotify</span>`
            : `<span class="brand-tag dir-tag-ytm">Spotify &rarr; YouTube Music</span>`;

        const srcColTitle = isYTMToSP ? "YouTube Music Parçası" : "Spotify Parçası";
        const dstColTitle = isYTMToSP ? "Spotify Eşleşmesi" : "YouTube Music Eşleşmesi";

        const actionBtn = isYTMToSP
            ? `<button type="button" class="btn btn-accent btn-sm" onclick="copySpotifyTrackLinks(${idx}, this)">
                   <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                       <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                       <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                   </svg>
                   <span>Spotify Şarkı Linklerini Kopyala</span>
               </button>`
            : `<button type="button" class="btn btn-accent btn-sm" onclick="copyYTMConsoleScript(${idx}, this)">
                   <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                       <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                       <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                   </svg>
                   <span>YouTube Music Kodunu Kopyala</span>
               </button>`;

        const queueLinks = (pl.instant_links || []).map(l =>
            `<a class="btn btn-sm mono" href="${l.youtube_queue_url}" target="_blank" rel="noopener">${escapeHtml(l.label)} ↗</a>`
        ).join("");

        const queueSection = (!isYTMToSP && queueLinks)
            ? `<div class="queue-bar">
                   <span>Giriş yapmadan direkt YouTube çalma kuyruğu olarak aç:</span>
                   <div style="display:flex; gap:6px; flex-wrap:wrap;">${queueLinks}</div>
               </div>`
            : "";

        const card = document.createElement("div");
        card.className = "playlist-card";
        card.innerHTML = `
            <div class="playlist-top">
                <div>
                    <div class="playlist-title-row">
                        <span class="playlist-name">${escapeHtml(pl.title)}</span>
                        ${dirBadge}
                        <span class="brand-tag mono">${pl.total_tracks} şarkı</span>
                    </div>
                    <div class="stat-pills">
                        <span class="pill"><span class="pill-dot dot-green"></span>Bire Bir: <strong class="mono">${pl.stats.direct_match}</strong></span>
                        <span class="pill"><span class="pill-dot dot-sky"></span>Sözlerle Eşleşen: <strong class="mono">${pl.stats.lyrics_match}</strong></span>
                        <span class="pill"><span class="pill-dot dot-amber"></span>Yakın Eşleşme: <strong class="mono">${pl.stats.low_confidence}</strong></span>
                        <span class="pill"><span class="pill-dot dot-red"></span>Bulunamayan: <strong class="mono">${pl.stats.not_found}</strong></span>
                    </div>
                </div>
                <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                    ${actionBtn}
                    <button type="button" class="btn btn-sm btn-ghost" onclick="removePlaylist(${idx})" title="Listeyi Kaldır">
                        Kaldır
                    </button>
                </div>
            </div>

            ${queueSection}

            <div class="playlist-toolbar">
                <div class="filter-tabs" id="tabs_${idx}">
                    <button type="button" class="tab-btn active" data-tab="all" onclick="setFilterTab(${idx}, 'all')">Tümü (${pl.total_tracks})</button>
                    <button type="button" class="tab-btn" data-tab="direct_match" onclick="setFilterTab(${idx}, 'direct_match')">Bire Bir (${pl.stats.direct_match})</button>
                    <button type="button" class="tab-btn" data-tab="lyrics_match" onclick="setFilterTab(${idx}, 'lyrics_match')">Sözlerle Bulunanlar (${pl.stats.lyrics_match})</button>
                    <button type="button" class="tab-btn" data-tab="review" onclick="setFilterTab(${idx}, 'review')">İnceleme (${pl.stats.low_confidence + pl.stats.not_found})</button>
                </div>
                <input type="text" class="search-input" placeholder="Şarkı, sanatçı veya söz ara..." oninput="setFilterQuery(${idx}, this.value)">
            </div>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th style="width:48px;">#</th>
                            <th>${srcColTitle}</th>
                            <th style="width:68px;">Süre</th>
                            <th>${dstColTitle}</th>
                            <th style="width:170px;">Eşleşme Yöntemi</th>
                        </tr>
                    </thead>
                    <tbody id="tbody_${idx}"></tbody>
                </table>
            </div>
        `;
        area.appendChild(card);
        renderPlaylistRows(idx);
    });
}

function renderPlaylistRows(plIdx) {
    const pl = CURRENT_PLAYLISTS[plIdx];
    if (!pl) return;
    const st = FILTER_STATE[plIdx] || {tab: "all", q: ""};

    const tabsContainer = document.getElementById("tabs_" + plIdx);
    if (tabsContainer) {
        tabsContainer.querySelectorAll(".tab-btn").forEach(btn => {
            btn.classList.toggle("active", btn.getAttribute("data-tab") === st.tab);
        });
    }

    const tbody = document.getElementById("tbody_" + plIdx);
    if (!tbody) return;

    let html = "";
    (pl.items || []).forEach((item, i) => {
        if (!item) return;
        const sp = item.spotify || {};
        const yt = item.yt_match;
        const li = item.lyrics_info;

        if (st.tab === "direct_match" && item.status !== "direct_match") return;
        if (st.tab === "lyrics_match" && item.status !== "lyrics_match") return;
        if (st.tab === "review" && item.status !== "low_confidence" && item.status !== "not_found") return;

        if (st.q) {
            const hay = [
                sp.name,
                sp.artist_str,
                yt && yt.title,
                yt && yt.artists,
                li && li.matched_snippet
            ].filter(Boolean).join(" ").toLowerCase();
            if (!hay.includes(st.q)) return;
        }

        let stClass = "st-none";
        if (item.status === "direct_match") stClass = "st-direct";
        else if (item.status === "lyrics_match") stClass = "st-lyrics";
        else if (item.status === "low_confidence") stClass = "st-low";

        const lyricLine = (li && li.matched_snippet)
            ? `<div><span class="lyric-quote">Söz: "${escapeHtml(li.matched_snippet)}" (${li.lyrics_similarity}%)</span></div>`
            : "";

        const thumbImg = (yt && yt.thumbnail)
            ? `<img class="thumb" src="${escapeHtml(yt.thumbnail)}" loading="lazy" alt="">`
            : `<div class="thumb"></div>`;

        html += `
            <tr>
                <td class="mono" style="color:var(--text-muted);">${i + 1}</td>
                <td>
                    <span class="track-title">${escapeHtml(sp.name)}</span>
                    <span class="track-artist">${escapeHtml(sp.artist_str || "Bilinmeyen Sanatçı")}</span>
                </td>
                <td class="mono" style="color:var(--text-secondary);">${formatDuration(sp.duration_sec)}</td>
                <td>
                    ${yt ? `
                        <div class="track-cell">
                            ${thumbImg}
                            <div>
                                <a class="yt-link" href="${escapeHtml(yt.url)}" target="_blank" rel="noopener">${escapeHtml(yt.title)}</a>
                                <div class="track-artist">${escapeHtml(yt.artists)} · <span class="mono">${formatDuration(yt.duration_sec)}</span> · ${escapeHtml(yt.resultType)}</div>
                                ${lyricLine}
                            </div>
                        </div>
                    ` : `<span style="color:var(--danger);">Eşleşme bulunamadı</span>`}
                </td>
                <td>
                    <span class="status-tag ${stClass}">
                        <span>${escapeHtml(item.match_method)}</span>
                        <span class="mono">${item.confidence}%</span>
                    </span>
                </td>
            </tr>
        `;
    });

    if (!html) {
        html = `<tr><td colspan="5" style="text-align:center; padding:28px; color:var(--text-muted);">Bu filtreye uygun şarkı bulunamadı.</td></tr>`;
    }
    tbody.innerHTML = html;
}

fetch("/api/status").then(r => r.json()).then(st => {
    CURRENT_PLAYLISTS = st.playlists || [];
    renderPlaylists();
    if (st.running) pollStatus();
});
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/start", methods=["POST"])
def api_start():
    data = request.get_json(force=True)
    urls = data.get("urls", [])
    clear_existing = bool(data.get("clear_existing", False))
    if STATE["running"]:
        return jsonify({"ok": False, "error": "Şu anda bir tarama işlemi devam ediyor."})

    t = threading.Thread(target=process_urls, args=(urls, clear_existing), daemon=True)
    t.start()
    return jsonify({"ok": True})


@app.route("/api/status")
def api_status():
    with STATE_LOCK:
        if not STATE["running"]:
            STATE["playlists"] = load_saved_playlists()
        return jsonify(STATE)


@app.route("/api/remove_playlist", methods=["POST"])
def api_remove_playlist():
    data = request.get_json(force=True)
    idx = data.get("index", -1)
    with STATE_LOCK:
        playlists = load_saved_playlists()
        if 0 <= idx < len(playlists):
            playlists.pop(idx)
            save_playlists_to_disk(playlists)
        STATE["playlists"] = playlists
        return jsonify(STATE)


@app.route("/api/clear", methods=["POST"])
def api_clear():
    with STATE_LOCK:
        save_playlists_to_disk([])
        STATE["playlists"] = []
        return jsonify(STATE)


def main():
    parser = argparse.ArgumentParser(description="Spotify <-> YouTube Music Çift Yönlü Söz Eşleştirmeli Aktarım Aracı")
    parser.add_argument("urls", nargs="*", help="Aktarılacak Spotify veya YouTube Music linkleri")
    parser.add_argument("--web", action="store_true", help="Web arayüzünü başlat (http://127.0.0.1:5050)")
    parser.add_argument("--port", type=int, default=5050, help="Web arayüzü portu")
    args = parser.parse_args()

    if args.urls:
        process_urls(args.urls)

    if args.web or not args.urls:
        print(f"\n[Web Arayüzü] http://127.0.0.1:{args.port} adresinde çalışıyor...")
        app.run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()
