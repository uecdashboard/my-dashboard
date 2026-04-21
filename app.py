"""
Streamlit Dashboard — Images & Comments from GitHub

Fetches dashboard_data.json from a GitHub repository, then renders
each image + comment as a styled HTML card.  Update the JSON or images
on GitHub and the dashboard refreshes automatically.
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import base64

# ──────────────────────────────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub Image Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────
# Premium CSS
# ──────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(160deg, #0a0a1a 0%, #1a1a3e 40%, #0f0c29 100%);
    color: #e0e0e0;
}

/* ── Header ──────────────────────────────────────────────────────── */
.dash-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    padding: 2.5rem 3rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
}
.dash-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    animation: shimmer 6s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(30px, -20px); }
}
.dash-header h1 {
    color: #fff;
    font-weight: 800;
    font-size: 2.4rem;
    position: relative;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.dash-header p {
    color: rgba(255,255,255,0.88);
    font-size: 1.1rem;
    margin-top: 0.5rem;
    position: relative;
    font-weight: 300;
}

/* ── Status bar ──────────────────────────────────────────────────── */
.status-bar {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.status-chip {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 50px;
    padding: 0.6rem 1.4rem;
    font-size: 0.85rem;
    color: #bbb;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.status-chip .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
}
.dot-green { background: #00e676; box-shadow: 0 0 8px #00e676; }
.dot-blue  { background: #448aff; box-shadow: 0 0 8px #448aff; }
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

/* ── Cards ────────────────────────────────────────────────────────── */
.card-grid {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}
.card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}
.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2);
    border-color: rgba(102, 126, 234, 0.3);
}
.card-image {
    flex: 0 0 50%;
    max-width: 50%;
    overflow: hidden;
}
.card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.5s ease;
}
.card:hover .card-image img {
    transform: scale(1.05);
}
.card-body {
    flex: 1;
    padding: 2rem 2.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.card-body .card-number {
    font-size: 0.75rem;
    font-weight: 600;
    color: #667eea;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.6rem;
}
.card-body h2 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 1rem;
    line-height: 1.3;
}
.card-body .comment {
    font-size: 1rem;
    line-height: 1.7;
    color: #aaa;
    font-weight: 300;
}
.card-body .divider {
    width: 50px;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 3px;
    margin: 1rem 0;
}

/* ── Reverse card (alternating layout) ───────────────────────────── */
.card.reverse {
    flex-direction: row-reverse;
}

/* ── Empty state ─────────────────────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #666;
}
.empty-state .icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}
.empty-state h3 {
    color: #999;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* ── Footer ──────────────────────────────────────────────────────── */
.footer {
    text-align: center;
    padding: 3rem 0 1.5rem;
    color: #555;
    font-size: 0.8rem;
}
.footer a { color: #667eea; text-decoration: none; }

/* ── Responsive ──────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .card, .card.reverse { flex-direction: column; }
    .card-image { flex: none; max-width: 100%; height: 250px; }
}
</style>
"""

# ──────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_dashboard_data(owner: str, repo: str, branch: str, token: str = "") -> dict | None:
    """Fetch dashboard_data.json from the GitHub repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/dashboard_data.json?ref={branch}"
    headers = {"Accept": "application/vnd.github.v3.raw"}
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None


def get_raw_image_url(owner: str, repo: str, branch: str, image_path: str) -> str:
    """Build the raw.githubusercontent.com URL for an image."""
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{image_path}"


def build_dashboard_html(data: dict, owner: str, repo: str, branch: str) -> str:
    """Build the full HTML dashboard from the data dict."""
    title = data.get("title", "Dashboard")
    subtitle = data.get("subtitle", "")
    items = data.get("items", [])

    cards_html = ""
    for i, item in enumerate(items):
        image_url = get_raw_image_url(owner, repo, branch, item["image"])
        title_text = item.get("title", f"Item {i + 1}")
        comment = item.get("comment", "")
        reverse_class = " reverse" if i % 2 == 1 else ""

        cards_html += f"""
        <div class="card{reverse_class}">
            <div class="card-image">
                <img src="{image_url}" alt="{title_text}" loading="lazy" />
            </div>
            <div class="card-body">
                <div class="card-number">Item {i + 1:02d}</div>
                <h2>{title_text}</h2>
                <div class="divider"></div>
                <p class="comment">{comment}</p>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {CUSTOM_CSS}
    </head>
    <body>
        <div class="dash-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>

        <div class="status-bar">
            <div class="status-chip">
                <span class="dot dot-green"></span> Live from GitHub
            </div>
            <div class="status-chip">
                <span class="dot dot-blue"></span> {len(items)} items loaded
            </div>
            <div class="status-chip">
                🔗 {owner}/{repo} · {branch}
            </div>
        </div>

        <div class="card-grid">
            {cards_html}
        </div>

        <div class="footer">
            Powered by <a href="https://streamlit.io" target="_blank">Streamlit</a>
            · Data from <a href="https://github.com/{owner}/{repo}" target="_blank">GitHub</a>
            · Auto-refreshes every 5 min
        </div>
    </body>
    </html>
    """
    return html


def build_local_dashboard_html(data: dict) -> str:
    """Build dashboard HTML using local image paths (for demo / before GitHub push)."""
    title = data.get("title", "Dashboard")
    subtitle = data.get("subtitle", "")
    items = data.get("items", [])

    cards_html = ""
    for i, item in enumerate(items):
        title_text = item.get("title", f"Item {i + 1}")
        comment = item.get("comment", "")
        reverse_class = " reverse" if i % 2 == 1 else ""

        # We'll use a placeholder gradient for the image since local files
        # can't be shown inside components.html iframe
        cards_html += f"""
        <div class="card{reverse_class}">
            <div class="card-image" style="
                background: linear-gradient({120 + i*40}deg, #667eea, #764ba2, #f093fb);
                display: flex; align-items: center; justify-content: center;
                min-height: 280px;
            ">
                <div style="color:white; font-size:1.2rem; font-weight:600; text-align:center; padding:1rem;">
                    🖼️<br>{item.get('image', 'image')}<br>
                    <span style="font-size:0.75rem; opacity:0.7;">(Will load from GitHub)</span>
                </div>
            </div>
            <div class="card-body">
                <div class="card-number">Item {i + 1:02d}</div>
                <h2>{title_text}</h2>
                <div class="divider"></div>
                <p class="comment">{comment}</p>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {CUSTOM_CSS}
    </head>
    <body>
        <div class="dash-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>

        <div class="status-bar">
            <div class="status-chip">
                <span class="dot dot-green"></span> Local Preview Mode
            </div>
            <div class="status-chip">
                <span class="dot dot-blue"></span> {len(items)} items loaded
            </div>
        </div>

        <div class="card-grid">
            {cards_html}
        </div>

        <div class="footer">
            ⚡ Local preview — push to GitHub for live images
        </div>
    </body>
    </html>
    """
    return html


# ──────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ GitHub Connection")
    st.markdown("---")

    github_owner  = st.text_input("GitHub Owner / Org", value="", placeholder="e.g. radwakamal")
    github_repo   = st.text_input("Repository Name", value="", placeholder="e.g. my-dashboard")
    github_branch = st.text_input("Branch", value="main")
    github_token  = st.text_input("GitHub Token (optional)", type="password",
                                  help="Only needed for private repos")

    st.markdown("---")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        ### 📝 How to use
        1. Create a GitHub repo
        2. Add `dashboard_data.json` with your items
        3. Upload images to `images/` folder
        4. Enter repo details above
        5. Dashboard renders automatically!

        ### 📄 `dashboard_data.json` format
        ```json
        {
          "title": "My Dashboard",
          "subtitle": "Description",
          "items": [
            {
              "image": "images/pic.png",
              "title": "Title",
              "comment": "Your comment"
            }
          ]
        }
        ```
        """
    )

# ──────────────────────────────────────────────────────────────────────
# Main content
# ──────────────────────────────────────────────────────────────────────
tab_dashboard, tab_local, tab_guide = st.tabs(["🌐 Live Dashboard", "📁 Local Preview", "📖 Setup Guide"])

# ── Tab 1: Live from GitHub ──────────────────────────────────────────
with tab_dashboard:
    if github_owner and github_repo:
        with st.spinner("🔗 Fetching data from GitHub …"):
            data = fetch_dashboard_data(github_owner, github_repo, github_branch, github_token)

        if data:
            st.success(f"✅ Connected to **{github_owner}/{github_repo}** — "
                       f"loaded **{len(data.get('items', []))}** items")

            html = build_dashboard_html(data, github_owner, github_repo, github_branch)
            # Calculate height based on number of items
            n_items = len(data.get("items", []))
            height = 350 + (n_items * 380)
            components.html(html, height=height, scrolling=True)
        else:
            st.error("❌ Could not fetch `dashboard_data.json` from the repo. "
                     "Make sure the file exists and the repo is public (or provide a token).")
    else:
        st.markdown(
            """
            <div style="text-align:center; padding:4rem 2rem; color:#888;">
                <div style="font-size:4rem; margin-bottom:1rem;">🔗</div>
                <h3 style="color:#aaa; margin-bottom:0.5rem;">Connect to GitHub</h3>
                <p>Enter your <strong>GitHub Owner</strong> and <strong>Repository Name</strong>
                in the sidebar to load your dashboard.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Tab 2: Local preview (from local dashboard_data.json) ───────────
with tab_local:
    st.markdown("### 📁 Preview from local `dashboard_data.json`")
    st.info("This preview uses your local `dashboard_data.json` file. "
            "Images will show as placeholders — they'll load from GitHub once you push.")

    try:
        import os
        local_json = os.path.join(os.path.dirname(__file__), "dashboard_data.json")
        with open(local_json, "r", encoding="utf-8") as f:
            local_data = json.load(f)

        html = build_local_dashboard_html(local_data)
        n_items = len(local_data.get("items", []))
        height = 350 + (n_items * 380)
        components.html(html, height=height, scrolling=True)

        with st.expander("📝 Edit dashboard_data.json"):
            st.json(local_data)
    except FileNotFoundError:
        st.warning("No local `dashboard_data.json` found.")

# ── Tab 3: Setup Guide ──────────────────────────────────────────────
with tab_guide:
    st.markdown(
        """
        ## 🚀 Complete Setup Guide

        ### How This Works

        ```
        ┌─────────────────────────────┐
        │  GitHub Repository          │
        │  ├── dashboard_data.json    │──── Streamlit fetches this
        │  └── images/                │
        │      ├── photo1.png         │──── Images loaded via raw URLs
        │      └── photo2.png         │
        └─────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────┐
        │  Streamlit Dashboard        │
        │  ┌───────┬─────────────┐    │
        │  │ Image │ Comment     │    │
        │  └───────┴─────────────┘    │
        │  ┌─────────────┬───────┐    │
        │  │ Comment     │ Image │    │
        │  └─────────────┴───────┘    │
        └─────────────────────────────┘
        ```

        ---

        ### Step 1 — Create a GitHub Repository
        1. Go to [github.com/new](https://github.com/new)
        2. Name it (e.g. `my-dashboard`)
        3. Make it **Public**

        ### Step 2 — Add Your Data

        Create `dashboard_data.json` in the repo root:
        ```json
        {
            "title": "📊 My Dashboard",
            "subtitle": "Images & comments from GitHub",
            "items": [
                {
                    "image": "images/report1.png",
                    "title": "Monthly Report",
                    "comment": "Revenue grew by 25% this month."
                },
                {
                    "image": "images/chart2.png",
                    "title": "User Analytics",
                    "comment": "Active users increased to 5,000."
                }
            ]
        }
        ```

        ### Step 3 — Upload Images
        Create an `images/` folder in your repo and upload your images there.
        The `image` field in JSON must match the file path in the repo.

        ### Step 4 — Connect the Dashboard
        Enter your GitHub **owner** and **repo name** in the sidebar ← and click enter.

        ### Step 5 — Update Anytime!
        - Edit `dashboard_data.json` on GitHub to add/change comments
        - Upload new images to `images/`
        - Dashboard refreshes automatically (every 5 minutes)
        - Click 🔄 **Refresh** in the sidebar for instant updates

        ---

        ### Deploy on Streamlit Cloud (FREE)
        1. Push this `app.py` + `requirements.txt` to your GitHub repo
        2. Go to [share.streamlit.io](https://share.streamlit.io/)
        3. Sign in with GitHub
        4. Select your repo → Deploy
        5. Get a live URL: `https://your-app.streamlit.app`
        """
    )
