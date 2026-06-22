"""Streamlit frontend for the Tax Talk domain-oracle API.

Redesigned: dark-mode developer aesthetic · Material Symbols · amber/gold accent
"""

from __future__ import annotations

import json
import os
from typing import Any, Generator

import httpx
from dotenv import load_dotenv

# Load a local .env file before Streamlit import so theme env vars are available at startup.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=False)

# Streamlit config in script (mirrors .streamlit/config.toml defaults)
os.environ["STREAMLIT_CLIENT_SHOW_ERROR_DETAILS"] = os.environ.get("STREAMLIT_CLIENT_SHOW_ERROR_DETAILS", "true")
os.environ["STREAMLIT_THEME_BASE"] = os.environ.get("STREAMLIT_THEME_BASE", "dark")
os.environ["STREAMLIT_THEME_PRIMARY_COLOR"] = os.environ.get("STREAMLIT_THEME_PRIMARY_COLOR", "#F59E0B")
os.environ["STREAMLIT_THEME_BACKGROUND_COLOR"] = os.environ.get("STREAMLIT_THEME_BACKGROUND_COLOR", "#0D0D0D")
os.environ["STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR"] = os.environ.get("STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR", "#141414")
os.environ["STREAMLIT_THEME_TEXT_COLOR"] = os.environ.get("STREAMLIT_THEME_TEXT_COLOR", "#E8E8E8")
os.environ["STREAMLIT_THEME_SIDEBAR_BACKGROUND_COLOR"] = os.environ.get("STREAMLIT_THEME_SIDEBAR_BACKGROUND_COLOR", "#0A0A0A")
os.environ["STREAMLIT_THEME_SIDEBAR_TEXT_COLOR"] = os.environ.get("STREAMLIT_THEME_SIDEBAR_TEXT_COLOR", "#E8E8E8")

import streamlit as st

# ---------------------------------------------------------------------------
# Profile — fill in your own links
# ---------------------------------------------------------------------------
LINKEDIN_URL = "https://linkedin.com/in/krishna-khandelwal-b86541250/"
GITHUB_URL = "https://github.com/KKhandelwal1733"
BLOG_URL = "https://kkhandelwal.me"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets[key]
    except KeyError:
        return os.getenv(key, default)


API_BASE_URL: str = _get_secret("API_BASE_URL", "http://localhost:8000").rstrip("/")
SUPABASE_URL: str = _get_secret("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY: str = _get_secret("SUPABASE_ANON_KEY", "")


# ---------------------------------------------------------------------------
# IMPROVEMENT 1: Shared HTTP Client (Connection Pooling)
# ---------------------------------------------------------------------------
@st.cache_resource
def get_http_client() -> httpx.Client:
    """Returns a globally cached HTTP client to reuse TCP connections."""
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    return httpx.Client(timeout=120.0, limits=limits)


# ---------------------------------------------------------------------------
# Material Symbols helper
# ---------------------------------------------------------------------------

def micon(name: str, size: int = 20, color: str = "", weight: int = 400, grade: int = 0, fill: int = 0) -> str:
    """Return an inline HTML <span> for a Material Symbols Rounded icon."""
    style_parts = [
        f"font-size:{size}px",
        f"width:{size}px",
        f"height:{size}px",
        "overflow:hidden",
        "display:inline-block",
        f"font-variation-settings: 'FILL' {fill}, 'wght' {weight}, 'GRAD' {grade}, 'opsz' {size}",
        "vertical-align: middle",
        "line-height: 1",
    ]
    if color:
        style_parts.append(f"color:{color}")
    style = ";".join(style_parts)
    return f'<span class="material-symbols-rounded" style="{style}">{name}</span>'


# ---------------------------------------------------------------------------
# Theme injection — dark mode + amber accent + Material Symbols
# ---------------------------------------------------------------------------
# [CSS omitted for brevity in reading, but included exactly as you wrote it]
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

.material-symbols-rounded {
    font-family: 'Material Symbols Rounded' !important;
    font-weight: normal;
    font-style: normal;
    display: inline-block;
    line-height: 1;
    text-transform: none;
    letter-spacing: normal;
    word-wrap: normal;
    white-space: nowrap;
    direction: ltr;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
}

:root {
    --bg-primary:       #0D0D0D;
    --bg-surface:       #141414;
    --bg-elevated:      #1C1C1C;
    --bg-hover:         #242424;
    --border-subtle:    #2A2A2A;
    --border-default:   #333333;
    --text-primary:     #E8E8E8;
    --text-secondary:   #8A8A8A;
    --text-muted:       #555555;
    --accent:           #F59E0B;
    --accent-dim:       #B45309;
    --accent-glow:      rgba(245, 158, 11, 0.10);
    --accent-glow-strong: rgba(245, 158, 11, 0.25);
    --success:          #10B981;
    --warning:          #F59E0B;
    --error:            #EF4444;
    --font-sans:        'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono:        'JetBrains Mono', 'Fira Code', monospace;
    --radius-sm:        6px;
    --radius-md:        10px;
    --radius-lg:        16px;
}

/* ── Global Overrides ───────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
}

[data-testid="stHeader"] { background-color: transparent !important; }

/* ── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
[data-testid="stSidebar"] [data-testid="stMarkdown"] span:not(.material-symbols-rounded),
[data-testid="stSidebar"] label {
    color: var(--text-secondary) !important;
    font-family: var(--font-sans) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] span.material-symbols-rounded {
    font-family: 'Material Symbols Rounded' !important;
}
[data-testid="stSidebar"] h2 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border-subtle) !important; opacity: 0.5; }

/* ── Sidebar Expander ───────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary span {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
}

/* ── Buttons ────────────────────────────────────────────────── */
[data-testid="stSidebar"] button[kind="secondary"],
[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
    background-color: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover,
[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
    background-color: var(--bg-hover) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background-color: var(--accent) !important;
    color: #000 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
}

[data-testid="stForm"] button[type="submit"],
[data-testid="stForm"] button[kind="secondaryFormSubmit"] {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dim) 100%) !important;
    color: #000 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.25s ease !important;
}
[data-testid="stForm"] button[type="submit"]:hover,
[data-testid="stForm"] button[kind="secondaryFormSubmit"]:hover {
    filter: brightness(1.1) !important;
    box-shadow: 0 0 20px var(--accent-glow-strong) !important;
}

/* ── Input fields ───────────────────────────────────────────── */
input[type="text"], input[type="password"], input[type="email"],
[data-testid="stTextInput"] input {
    background-color: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-sans) !important;
    transition: border-color 0.2s ease !important;
}
input:focus, [data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}

/* ── Chat ───────────────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background-color: var(--bg-surface) !important;
    border-color: var(--border-default) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
}

[data-testid="stChatMessage"] {
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.75rem !important;
    transition: border-color 0.2s ease;
    align-items: flex-start !important;
    gap: 0.9rem !important;
}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] { margin-top: 0.1rem !important; }
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] svg,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] img { width: 1rem !important; height: 1rem !important; }
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] { min-width: 0 !important; flex: 1 1 auto !important; }
[data-testid="stChatMessage"]:hover { border-color: var(--border-default) !important; }
[data-testid="stChatMessage"]:has(.user-msg-marker) { border-left: 2px solid var(--accent) !important; }
.user-msg-marker { display: none; }

[data-testid="stChatMessage"] [data-testid="stExpander"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    margin-top: 0.5rem;
}
[data-testid="stChatMessage"] [data-testid="stExpander"] summary span {
    color: var(--accent) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}

/* ── Slider ─────────────────────────────────────────────────── */
[data-testid="stSlider"] { margin-bottom: 0.4rem !important; }
[data-testid="stSlider"] label { margin-bottom: 0.3rem !important; font-size: 0.9rem !important; }
[data-testid="stSlider"] [data-testid="stThumbValue"] { color: var(--accent) !important; font-size: 0.85rem !important; }
[data-testid="stSlider"] [role="slider"] { background-color: var(--accent) !important; border-color: var(--accent-dim) !important; }
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"],
[data-testid="stSlider"] div[role="progressbar"] { background-color: var(--accent) !important; }
[data-testid="stSlider"] [data-testid="stTickBarMax"] { background-color: var(--border-subtle) !important; }
[data-testid="stSlider"] [data-testid="stHelp"] { margin-top: 0.2rem !important; font-size: 0.75rem !important; }
[data-testid="stSlider"] input[type="range"]::-webkit-slider-thumb,
[data-testid="stSlider"] input[type="range"]::-moz-range-thumb {
    background: var(--accent) !important;
    border: 1px solid var(--accent-dim) !important;
}
[data-testid="stSlider"] input[type="range"]::-webkit-slider-runnable-track,
[data-testid="stSlider"] input[type="range"]::-moz-range-track {
    background: var(--accent) !important;
}

/* ── Segmented control overrides ───────────────────────────────── */
[data-testid="stSegmentedControl"] button,
[data-testid="stSegmentedControl"] [role="button"] {
    color: var(--text-primary) !important;
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-default) !important;
}
[data-testid="stSegmentedControl"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] [aria-selected="true"],
[data-testid="stSegmentedControl"] [data-state="on"] {
    background-color: var(--accent) !important;
    color: #000 !important;
    border-color: var(--accent) !important;
}

/* ── Scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-default); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── Custom Component Classes ───────────────────────────────── */
[data-testid="stForm"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    padding: 2rem 2rem 1.5rem !important;
    box-shadow: 0 0 40px var(--accent-glow), 0 0 80px rgba(245, 158, 11, 0.04), 0 4px 24px rgba(0, 0, 0, 0.5) !important;
    max-width: 420px;
    margin: 0 auto !important;
}
[data-testid="stForm"] [data-testid="InputInstructions"] { display: none !important; }
input[type="password"]::-ms-reveal, input[type="password"]::-ms-clear { display: none !important; }

.login-header { text-align: center; margin-bottom: 1.5rem; }
.login-header h1 { font-family: var(--font-sans); font-weight: 700; font-size: 1.8rem; color: var(--text-primary); margin: 0.5rem 0 0.25rem; letter-spacing: -0.02em; }
.login-header .subtitle { color: var(--text-muted); font-size: 0.88rem; line-height: 1.5; }
.login-header .icon-wrapper { display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: 14px; background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dim) 100%); margin-bottom: 0.3rem; }
.login-footer { text-align: center; color: var(--text-muted); font-size: 0.78rem; margin-top: 1rem; line-height: 1.5; }

.cite-card { background: var(--bg-elevated); border: 1px solid var(--border-subtle); border-left: 3px solid var(--accent-dim); border-radius: var(--radius-sm); padding: 0.7rem 0.9rem; margin-bottom: 0.5rem; }
.cite-card .cite-header { font-size: 0.82rem; font-weight: 600; color: var(--accent); margin-bottom: 0.25rem; display: flex; align-items: center; gap: 6px; }
.cite-card .cite-meta { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.3rem; }
.cite-card .cite-text { font-size: 0.8rem; color: var(--text-secondary); line-height: 1.55; }

.faith-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px 4px 8px; border-radius: 20px; font-size: 0.8rem; font-weight: 500; font-family: var(--font-sans); margin-top: 0.4rem; }
.faith-badge.supported { background: rgba(16, 185, 129, 0.12); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.25); }
.faith-badge.partially_supported { background: rgba(245, 158, 11, 0.12); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.25); }
.faith-badge.unsupported { background: rgba(239, 68, 68, 0.12); color: var(--error); border: 1px solid rgba(239, 68, 68, 0.25); }

.profile-links { display: flex; gap: 6px; flex-wrap: wrap; }
.profile-links a { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border-radius: 6px; background: var(--bg-elevated); border: 1px solid var(--border-subtle); color: var(--text-secondary) !important; text-decoration: none !important; font-size: 0.78rem; font-weight: 500; font-family: var(--font-sans); transition: all 0.2s ease; }
.profile-links a:hover { border-color: var(--accent); color: var(--accent) !important; background: var(--accent-glow); }

.status-pill { display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 500; }
.status-pill.online { background: rgba(16, 185, 129, 0.12); color: var(--success); }
.status-pill.offline { background: rgba(239, 68, 68, 0.12); color: var(--error); }

.user-card { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: var(--bg-elevated); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); margin-bottom: 0.5rem; }
.user-card .user-email { font-size: 0.82rem; color: var(--text-secondary); font-family: var(--font-mono); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.sidebar-section { display: flex; align-items: center; gap: 6px; margin-bottom: 0.5rem; }
.sidebar-section h3 { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin: 0; }
</style>
"""

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_DEFAULTS: dict[str, Any] = {
    "access_token": None,
    "user_email": None,
    "messages": [],
    "chat_mode": "Stream",
    "api_health_status": None,
    "api_health_checked": False,
    "retry_request": None,
}


def _init_session() -> None:
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Auth — Supabase REST
# ---------------------------------------------------------------------------

def supabase_login(email: str, password: str) -> dict[str, Any] | None:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        st.error("SUPABASE_URL and SUPABASE_ANON_KEY must be configured.")
        return None

    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    client = get_http_client()
    try:
        resp = client.post(url, headers=headers, json={"email": email, "password": password})
        if resp.status_code == 200:
            return resp.json()
        body = resp.json()
        detail = body.get("error_description") or body.get("msg") or resp.text
        st.error(f"Login failed: {detail}")
        return None
    except httpx.RequestError as exc:
        st.error(f"Could not reach Supabase auth endpoint: {exc}")
        return None


def supabase_signup(email: str, password: str) -> dict[str, Any] | None:
    """Register a new user with Supabase."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        st.error("SUPABASE_URL and SUPABASE_ANON_KEY must be configured.")
        return None

    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    client = get_http_client()
    try:
        resp = client.post(url, headers=headers, json={"email": email, "password": password})
        if resp.status_code in (200, 201):
            return resp.json()
        body = resp.json()
        detail = body.get("error_description") or body.get("msg") or resp.text
        st.error(f"Signup failed: {detail}")
        return None
    except httpx.RequestError as exc:
        st.error(f"Could not reach Supabase auth endpoint: {exc}")
        return None


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def call_chat(
    query: str, top_k: int, dense_top_k: int, bm25_top_k: int, token: str,
) -> dict[str, Any] | None:
    payload = {"query": query, "top_k": top_k, "dense_top_k": dense_top_k, "bm25_top_k": bm25_top_k}
    client = get_http_client()
    try:
        resp = client.post(f"{API_BASE_URL}/chat", headers=_auth_headers(token), json=payload)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        # IMPROVEMENT 2: Graceful JWT Expiration
        if exc.response.status_code == 401:
            st.error("Session expired. Please sign in again.")
            st.session_state.access_token = None
            st.rerun()
        else:
            st.error(f"API error {exc.response.status_code}: {exc.response.text[:300]}")
        return None
    except httpx.RequestError as exc:
        st.error(f"Could not reach API: {exc}")
        return None


def stream_chat(
    query: str, top_k: int, dense_top_k: int, bm25_top_k: int, token: str,
) -> Generator[tuple[str, dict[str, Any]], None, None]:
    payload = {"query": query, "top_k": top_k, "dense_top_k": dense_top_k, "bm25_top_k": bm25_top_k}
    client = get_http_client()
    try:
        with client.stream("POST", f"{API_BASE_URL}/chat/stream", headers=_auth_headers(token), json=payload) as resp:
            resp.raise_for_status()
            
            # IMPROVEMENT 4: Robust SSE Chunk Parsing
            current_event = "message"
            current_data = []

            for raw_line in resp.iter_lines():
                line = raw_line.strip()
                
                # An empty line denotes the end of an SSE block
                if not line:
                    if current_data:
                        data_str = "\n".join(current_data)
                        try:
                            parsed_data = json.loads(data_str)
                        except json.JSONDecodeError:
                            parsed_data = {"raw": data_str}
                        yield current_event, parsed_data
                    # Reset state for next block
                    current_event = "message"
                    current_data = []
                elif line.startswith("event:"):
                    current_event = line[len("event:"):].strip()
                elif line.startswith("data:"):
                    current_data.append(line[len("data:"):].strip())
                    
    except httpx.HTTPStatusError as exc:
        # IMPROVEMENT 2: Graceful JWT Expiration
        if exc.response.status_code == 401:
            st.error("Session expired. Please sign in again.")
            st.session_state.access_token = None
            st.rerun()
        else:
            st.error(f"API error {exc.response.status_code}: {exc.response.text[:300]}")
    except httpx.RequestError as exc:
        st.error(f"Could not reach API: {exc}")


def check_api_health() -> bool:
    client = get_http_client()
    try:
        resp = client.get(f"{API_BASE_URL}/health/live")
        return resp.status_code == 200
    except httpx.RequestError:
        return False


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

_FAITHFULNESS_MAP: dict[str, dict[str, str]] = {
    "supported": {
        "icon": "verified",
        "label": "Supported",
        "css": "supported",
    },
    "partially_supported": {
        "icon": "help",
        "label": "Partially Supported",
        "css": "partially_supported",
    },
    "unsupported": {
        "icon": "dangerous",
        "label": "Unsupported",
        "css": "unsupported",
    },
}


def _render_citations(citations: list[dict[str, Any]]) -> None:
    if not citations:
        return
    with st.expander(f":material/menu_book: Citations {len(citations)} citation(s)", expanded=False):
        for i, c in enumerate(citations, 1):
            source = c.get("source_key", "unknown")
            section = c.get("section_title", "")
            period = c.get("applicable_period", "")
            text = c.get("text", c.get("page_content", ""))

            meta_parts = []
            if section:
                meta_parts.append(section)
            if period:
                meta_parts.append(period)
            meta_str = " · ".join(meta_parts)

            card_html = f"""<div class="cite-card">
    <div class="cite-header">{micon('description', 16, '#F59E0B')} [{i}] {source}</div>"""
            if meta_str:
                card_html += f'\n    <div class="cite-meta">{meta_str}</div>'
            if text:
                preview = text[:400] + ("…" if len(text) > 400 else "")
                card_html += f'\n    <div class="cite-text">{preview}</div>'
            card_html += "\n</div>"
            st.markdown(card_html, unsafe_allow_html=True)


def _render_faithfulness(faithfulness: dict[str, Any] | None) -> None:
    if not faithfulness:
        return
    verdict: str = faithfulness.get("verdict", "")
    score: float | None = faithfulness.get("score")
    rationale: str = faithfulness.get("rationale", "")

    info = _FAITHFULNESS_MAP.get(verdict, {"icon": "radio_button_unchecked", "label": verdict.replace("_", " ").title(), "css": ""})
    score_str = f" · {score:.2f}" if score is not None else ""

    badge_html = (
        f'<div class="faith-badge {info["css"]}">'
        f'{micon(info["icon"], 18, "", 500, 0, 1)} '
        f'{info["label"]}{score_str}'
        f'</div>'
    )
    st.markdown(badge_html, unsafe_allow_html=True)

    if rationale:
        with st.expander("Rationale", expanded=False):
            st.write(rationale)


# ---------------------------------------------------------------------------
# Login page
# ---------------------------------------------------------------------------

def render_login_page() -> None:
    st.markdown("<div style='padding-top:8vh'></div>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        auth_mode = st.session_state.get("auth_mode", "Sign in")
        tab1, tab2 = st.columns(2, gap="small")
        
        with tab1:
            if st.button(
                ":material/login: Sign in",
                use_container_width=True,
                type="primary" if auth_mode == "Sign in" else "secondary",
                key="auth_signin",
            ):
                st.session_state.auth_mode = "Sign in"
                st.rerun()
        
        with tab2:
            if st.button(
                ":material/person_add: Sign up",
                use_container_width=True,
                type="primary" if auth_mode == "Sign up" else "secondary",
                key="auth_signup",
            ):
                st.session_state.auth_mode = "Sign up"
                st.rerun()
        
        st.markdown("<div style='margin-bottom:0.5rem'></div>", unsafe_allow_html=True)

        with st.form("auth_form"):
            auth_mode = st.session_state.get("auth_mode", "Sign in")

            st.markdown(
                f"""
                <div class="login-header">
                    <div class="icon-wrapper">
                        {micon('gavel', 28, '#000', 600, 0, 1)}
                    </div>
                    <h1>Tax Talk</h1>
                    <p class="subtitle">
                        Grounded answers on Indian GST &amp; Income Tax law.<br>
                        Every claim cites its source clause.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            email = st.text_input("Email", placeholder="you@example.com", label_visibility="collapsed")
            password = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")

            if auth_mode == "Sign up":
                password_confirm = st.text_input(
                    "Confirm Password", type="password", placeholder="Confirm password", label_visibility="collapsed"
                )
            else:
                password_confirm = None

            submitted = st.form_submit_button(
                "Sign in" if auth_mode == "Sign in" else "Create account",
                use_container_width=True,
            )

            st.markdown(
                f"""<div class="login-footer">
                    {micon('lock', 14, '#555')} Secured with Supabase Auth ·
                    Contact the project admin for access.
                </div>""",
                unsafe_allow_html=True,
            )

        if submitted:
            auth_mode = st.session_state.get("auth_mode", "Sign in")
            if not email or not password:
                st.warning("Please enter both email and password.")
            elif auth_mode == "Sign up" and password != password_confirm:
                st.warning("Passwords do not match.")
            elif auth_mode == "Sign up" and len(password) < 6:
                st.warning("Password must be at least 6 characters.")
            else:
                spinner_text = "Signing in..." if auth_mode == "Sign in" else "Creating account..."
                with st.spinner(spinner_text):
                    if auth_mode == "Sign in":
                        result = supabase_login(email, password)
                    else:
                        result = supabase_signup(email, password)

                if result:
                    st.session_state.access_token = result.get("access_token") or result.get("session", {}).get("access_token")
                    st.session_state.user_email = result.get("user", {}).get("email") or email
                    if auth_mode == "Sign up":
                        st.success("Account created successfully! Please sign in.")
                        st.rerun()
                    else:
                        st.rerun()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _sidebar_section(icon_name: str, title: str) -> None:
    st.markdown(
        f'<div class="sidebar-section">{micon(icon_name, 18, "#F59E0B", 500, 0, 1)} '
        f'<h3>{title}</h3></div>',
        unsafe_allow_html=True,
    )

def _chat_avatar(role: str) -> str:
    return ":material/person:" if role == "user" else ":material/gavel:"


def _make_retry_payload(query: str, top_k: int, dense_top_k: int, bm25_top_k: int, mode: str) -> dict[str, Any]:
    return {
        "query": query, "top_k": top_k, "dense_top_k": dense_top_k, "bm25_top_k": bm25_top_k, "mode": mode,
    }


def _render_retry_button(retry_payload: dict[str, Any], key_suffix: str) -> None:
    col1, col2, col3 = st.columns([1, 0.2, 1])
    with col2:
        if st.button(":material/refresh: Retry", key=f"retry_{key_suffix}", use_container_width=True, type="secondary"):
            st.session_state.retry_request = retry_payload
            st.rerun()


def render_sidebar() -> tuple[int, int, int]:
    with st.sidebar:
        if any([LINKEDIN_URL, GITHUB_URL, BLOG_URL]):
            _sidebar_section("person", "Profile")
            links_html = '<div class="profile-links">'
            if LINKEDIN_URL: links_html += f'<a href="{LINKEDIN_URL}" target="_blank">{micon("link", 14)} LinkedIn</a>'
            if GITHUB_URL: links_html += f'<a href="{GITHUB_URL}" target="_blank">{micon("code", 14)} GitHub</a>'
            if BLOG_URL: links_html += f'<a href="{BLOG_URL}" target="_blank">{micon("rss_feed", 14)} Blog</a>'
            links_html += '</div>'
            st.markdown(links_html, unsafe_allow_html=True)

        st.markdown("---")

        _sidebar_section("tune", "Settings")

        current_mode = st.session_state.get("chat_mode", "Streaming")
        st.session_state.chat_mode = st.segmented_control(
            "Response mode", ["Streaming", "Non-Streaming"],
            default=current_mode if current_mode in {"Streaming", "Non-Streaming"} else "Streaming",
            selection_mode="single", label_visibility="collapsed",
        )

        top_k = st.slider("Citations (top-k)", min_value=1, max_value=15, value=5)

        with st.expander("Advanced retrieval", expanded=False):
            dense_top_k = st.slider("Dense candidates", min_value=7, max_value=100, value=10)
            bm25_top_k = st.slider("BM25 candidates", min_value=7, max_value=100, value=10)

        st.markdown("---")

        _sidebar_section("monitor_heart", "API Status")

        if st.button("Check health", use_container_width=True, type="secondary"):
            with st.spinner("Checking…"):
                healthy = check_api_health()
            st.session_state.api_health_status = healthy
            st.session_state.api_health_checked = True

        if st.session_state.get("api_health_checked"):
            if st.session_state.get("api_health_status"):
                st.markdown(f'<span class="status-pill online">{micon("check_circle", 14, "#10B981", 500, 0, 1)} Online</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="status-pill offline">{micon("error", 14, "#EF4444", 500, 0, 1)} Unreachable</span>', unsafe_allow_html=True)

        st.markdown("---")

        _sidebar_section("badge", "Session")
        st.markdown(
            f"""<div class="user-card">
    {micon('account_circle', 22, '#F59E0B', 400, 0, 1)}
    <span class="user-email">{st.session_state.user_email}</span>
</div>""",
            unsafe_allow_html=True,
        )

        if st.button("Sign out", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    return top_k, dense_top_k, bm25_top_k


# ---------------------------------------------------------------------------
# Chat UI
# ---------------------------------------------------------------------------

def render_chat(top_k: int, dense_top_k: int, bm25_top_k: int) -> None:
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:10px;margin-bottom:-0.5rem;">
    {micon('gavel', 30, '#F59E0B', 600, 0, 1)}
    <span style="font-size:1.6rem;font-weight:700;letter-spacing:-0.02em;:var(--text-primary);">
        Tax Talk
    </span>
</div>""",
        unsafe_allow_html=True,
    )
    st.caption("Grounded answers on Indian GST & Income Tax law — every claim cites its source clause.")

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar=_chat_avatar(msg["role"])):
            if msg["role"] == "user":
                st.markdown('<div class="user-msg-marker"></div>', unsafe_allow_html=True)
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                _render_citations(msg.get("citations", []))
                _render_faithfulness(msg.get("faithfulness"))
                retry_payload = msg.get("retry_payload")
                if msg.get("failed") and isinstance(retry_payload, dict):
                    st.caption("AI response failed. You can retry this prompt.")
                    _render_retry_button(retry_payload, f"history_{idx}")

    retry_request = st.session_state.pop("retry_request", None)
    if isinstance(retry_request, dict):
        query = str(retry_request.get("query", "")).strip()
        if not query:
            st.warning("Could not retry because the original query is missing.")
            return

        retry_top_k = int(retry_request.get("top_k", top_k))
        retry_dense_top_k = int(retry_request.get("dense_top_k", dense_top_k))
        retry_bm25_top_k = int(retry_request.get("bm25_top_k", bm25_top_k))
        retry_mode = str(retry_request.get("mode", st.session_state.chat_mode))

        token: str = st.session_state.access_token
        if retry_mode == "Stream":
            _handle_stream(query, retry_top_k, retry_dense_top_k, retry_bm25_top_k, token)
        else:
            _handle_sync(query, retry_top_k, retry_dense_top_k, retry_bm25_top_k, token)
        return

    user_input: str | None = st.chat_input("Ask a tax question…")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=_chat_avatar("user")):
        st.markdown('<div class="user-msg-marker"></div>', unsafe_allow_html=True)
        st.markdown(user_input)

    token: str = st.session_state.access_token
    if st.session_state.chat_mode == "Stream":
        _handle_stream(user_input, top_k, dense_top_k, bm25_top_k, token)
    else:
        _handle_sync(user_input, top_k, dense_top_k, bm25_top_k, token)


def _handle_stream(query: str, top_k: int, dense_top_k: int, bm25_top_k: int, token: str) -> None:
    with st.chat_message("assistant", avatar=_chat_avatar("assistant")):
        text_placeholder = st.empty()
        accumulated = ""
        citations: list[dict[str, Any]] = []
        faithfulness: dict[str, Any] | None = None
        got_done = False
        got_any_event = False
        failure_text = ""

        retry_payload = _make_retry_payload(
            query=query, top_k=top_k, dense_top_k=dense_top_k, bm25_top_k=bm25_top_k, mode="Stream",
        )

        with st.spinner("Thinking…"):
            for event_type, data in stream_chat(query, top_k, dense_top_k, bm25_top_k, token):
                got_any_event = True
                if event_type == "token":
                    accumulated += data.get("text", "")
                    text_placeholder.markdown(accumulated + "▌")
                elif event_type == "done":
                    got_done = True
                    text_placeholder.markdown(accumulated)
                    citations = data.get("citations", [])
                    _render_citations(citations)
                elif event_type == "faithfulness":
                    faithfulness = data
                    _render_faithfulness(faithfulness)

        failed = (not got_any_event) or (not got_done)
        if not failed and not accumulated.strip() and not citations and not faithfulness:
            failed = True

        if failed:
            if accumulated.strip():
                text_placeholder.markdown(accumulated)
                failure_text = "Response was interrupted before completion. Please retry."
            else:
                failure_text = "I could not generate a response. Please retry."
                text_placeholder.markdown(failure_text)
            st.caption("AI response failed. You can retry this prompt.")
            _render_retry_button(retry_payload, f"live_stream_{len(st.session_state.messages)}")
        elif accumulated:
            text_placeholder.markdown(accumulated)

    st.session_state.messages.append({
        "role": "assistant",
        "content": accumulated if accumulated.strip() else failure_text,
        "citations": citations,
        "faithfulness": faithfulness,
        "failed": failed,
        "retry_payload": retry_payload if failed else None,
    })


def _handle_sync(query: str, top_k: int, dense_top_k: int, bm25_top_k: int, token: str) -> None:
    with st.chat_message("assistant", avatar=_chat_avatar("assistant")):
        retry_payload = _make_retry_payload(
            query=query, top_k=top_k, dense_top_k=dense_top_k, bm25_top_k=bm25_top_k, mode="Sync",
        )

        failed = False
        answer = ""
        citations: list[dict[str, Any]] = []
        faithfulness: dict[str, Any] | None = None

        with st.spinner("Thinking…"):
            result = call_chat(query, top_k, dense_top_k, bm25_top_k, token)

        if result is None:
            failed = True
            answer = "I could not generate a response. Please retry."
            st.markdown(answer)
        else:
            answer = result.get("answer", "")
            citations = result.get("citations", [])
            faithfulness = result.get("faithfulness")

            if not answer.strip() and not citations and not faithfulness:
                failed = True
                answer = "I received an empty response. Please retry."
                st.markdown(answer)
            else:
                if answer.strip():
                    st.markdown(answer)
                _render_citations(citations)
                _render_faithfulness(faithfulness)

        if failed:
            st.caption("AI response failed. You can retry this prompt.")
            _render_retry_button(retry_payload, f"live_sync_{len(st.session_state.messages)}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "citations": citations,
        "faithfulness": faithfulness,
        "failed": failed,
        "retry_payload": retry_payload if failed else None,
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

st.set_page_config(
    page_title="Tax Talk",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(THEME_CSS, unsafe_allow_html=True)

_FONT_URLS = [
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap",
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap",
]
_font_js = "\n".join(
    f"""if(!parent.document.querySelector('link[href="{u}"])){{
    var l=parent.document.createElement('link');l.rel='stylesheet';l.href='{u}';
    parent.document.head.appendChild(l);}}"""
    for u in _FONT_URLS
)
_font_links_local = "".join(f'<link rel="stylesheet" href="{u}">' for u in _FONT_URLS)
st.markdown(
    f"{_font_links_local}<script>{_font_js}</script>"
    "<style>html,body{{margin:0;padding:0;height:0;overflow:hidden}}</style>",
    unsafe_allow_html=True,
)

_init_session()

if not st.session_state.access_token:
    render_login_page()
else:
    _top_k, _dense_top_k, _bm25_top_k = render_sidebar()
    render_chat(_top_k, _dense_top_k, _bm25_top_k)