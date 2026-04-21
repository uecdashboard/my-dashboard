"""
Streamlit Dashboard — Fetches and displays an HTML file from GitHub.

The HTML file (dashboard.html) is stored on GitHub with images & comments.
This Streamlit app fetches it and renders it live.
Any edits to dashboard.html on GitHub will automatically appear here.
"""

import streamlit as st
import streamlit.components.v1 as components
import requests

# ──────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub HTML Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ GitHub Settings")
    st.markdown("---")

    github_owner  = st.text_input("GitHub Owner", value="uecdashboard")
    github_repo   = st.text_input("Repository Name", value="my-dashboard")
    github_branch = st.text_input("Branch", value="main")
    html_filename = st.text_input("HTML File Name", value="dashboard.html")

    st.markdown("---")

    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        ### 📝 How it works
        1. Your **HTML file** (`dashboard.html`) lives on GitHub
        2. This Streamlit app **fetches** it using the raw URL
        3. The HTML is **rendered** live in this page
        4. **Edit the HTML on GitHub** → dashboard updates!
        """
    )

# ──────────────────────────────────────────────────────────────────────
# Fetch HTML from GitHub
# ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # cache 5 minutes
def fetch_html_from_github(owner, repo, branch, filename):
    """Fetch the raw HTML file from GitHub."""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filename}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return None

# ──────────────────────────────────────────────────────────────────────
# Main content
# ──────────────────────────────────────────────────────────────────────
if github_owner and github_repo and html_filename:
    with st.spinner("🔗 Fetching HTML from GitHub..."):
        html_content = fetch_html_from_github(
            github_owner, github_repo, github_branch, html_filename
        )

    if html_content:
        st.success(
            f"✅ Loaded **{html_filename}** from "
            f"[{github_owner}/{github_repo}](https://github.com/{github_owner}/{github_repo})"
        )

        # Render the HTML
        components.html(html_content, height=1200, scrolling=True)

    else:
        st.error(
            f"❌ Could not fetch `{html_filename}` from "
            f"`https://github.com/{github_owner}/{github_repo}`. "
            f"Make sure the file exists and the repo is public."
        )
else:
    st.warning("👈 Enter your GitHub details in the sidebar.")
