"""Streamlit execution console for Trend2Video Pro."""

from __future__ import annotations

from pathlib import Path
from time import sleep

import streamlit as st

from src.agents.orchestrator import run_trend_to_video
from src.creator.creator_profile import load_creator_profile


PLATFORMS = ["Bilibili", "YouTube", "TikTok"]
PIPELINE_PLATFORMS = {"Bilibili": "Bilibili", "YouTube": "YouTube Shorts", "TikTok": "TikTok"}
STYLES = ["Tech", "Viral", "Educational"]
PIPELINE_STYLES = {"Tech": "Tech News", "Viral": "Viral Talking Head", "Educational": "Educational"}
DURATIONS = [30, 60, 90]
AGENT_STEPS = [
    "Trend Scanning",
    "Opportunity Scoring",
    "Creator Fit Analysis",
    "Script Writing",
    "Fact Checking",
    "Storyboard Generation",
    "Video Generation",
    "Quality Review",
]


st.set_page_config(page_title="Trend2Video Pro", page_icon="T2V", layout="wide")
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1160px;}
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #ecfeff 0%, #f8fafc 100%);
        border: 1px solid #dbeafe;
        padding: 14px 16px;
        border-radius: 14px;
    }
    .hero {
        padding: 28px 32px;
        border-radius: 22px;
        color: white;
        background: linear-gradient(135deg, #0f172a 0%, #075985 52%, #0891b2 100%);
        margin-bottom: 22px;
    }
    .hero h1 {font-size: 44px; margin: 0 0 8px 0;}
    .hero p {font-size: 18px; opacity: .92; margin: 0;}
    .section-title {font-size: 23px; font-weight: 800; margin: 16px 0 8px 0;}
    .package-path {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 12px;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Trend2Video Pro</h1>
      <p>Execution Console for Content Creators. Input a trend, run the agents, export a publish-ready package.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def _read_text(path: str | Path, max_chars: int = 1200) -> str:
    file_path = Path(path)
    if not file_path.is_file():
        return ""
    return file_path.read_text(encoding="utf-8", errors="ignore")[:max_chars]


def _quality_summary(result: dict) -> list[str]:
    report = result.get("report", {})
    risks = report.get("risks", [])[:2]
    suggestions = report.get("suggestions", [])[:2]
    items = [f"Risk: {item}" for item in risks] + [f"Improve: {item}" for item in suggestions]
    return items or ["No blocking publishing risk detected in the MVP quality checks."]


def render_output(result: dict) -> None:
    """Render the finished creator package without raw logs or technical tables."""
    files = result.get("files", {})
    script = result.get("script", {})
    viral = result.get("viral_prediction", {})
    package = result.get("publish_package", {})
    viral_score = round(float(viral.get("viral_probability", 0)) * 100)

    st.markdown('<div class="section-title">3. Output: Publish-Ready Package</div>', unsafe_allow_html=True)
    top_left, top_right = st.columns([1.25, 1], gap="large")

    with top_left:
        with st.container(border=True):
            st.subheader("Video Preview")
            video_path = Path(files.get("video", ""))
            if video_path.is_file():
                st.video(str(video_path))
            else:
                st.info("Video preview will appear here after generation.")

    with top_right:
        with st.container(border=True):
            st.subheader("Creator Assets")
            st.metric("Viral Score", f"{viral_score}/100")
            st.markdown(f"**Title**  \n{script.get('title', result.get('input', {}).get('title', 'Untitled'))}")
            tags = " ".join("#" + str(tag).replace(" ", "") for tag in script.get("tags", []))
            st.markdown(f"**Hashtags**  \n{tags or '#Trend #Creator #Video'}")
            st.markdown(f"**Description**  \n{script.get('description', 'A concise trend breakdown for creators.')}")
            thumbnail_path = Path(files.get("thumbnail", ""))
            if thumbnail_path.is_file():
                st.image(str(thumbnail_path), caption="Thumbnail preview", use_container_width=True)

    lower_left, lower_right = st.columns([1, 1], gap="large")
    with lower_left:
        with st.container(border=True):
            st.subheader("Subtitles")
            subtitles = _read_text(files.get("subtitles", ""), max_chars=900)
            st.text_area("Ready-to-use SRT preview", value=subtitles, height=210, label_visibility="collapsed")

    with lower_right:
        with st.container(border=True):
            st.subheader("Quality Report Summary")
            for item in _quality_summary(result):
                st.write(f"- {item}")
            if package.get("package_dir"):
                st.markdown("**Publish package**")
                st.markdown(f"<div class='package-path'>{package['package_dir']}</div>", unsafe_allow_html=True)

    st.markdown("#### Download Package Assets")
    download_items = [
        ("MP4 Video", files.get("video")),
        ("Thumbnail", files.get("thumbnail")),
        ("Subtitles", files.get("subtitles")),
        ("Quality Report", files.get("report_md")),
    ]
    cols = st.columns(4)
    for col, (label, path) in zip(cols, download_items):
        file_path = Path(path or "")
        if file_path.is_file():
            col.download_button(label, data=file_path.read_bytes(), file_name=file_path.name, use_container_width=True)


st.markdown('<div class="section-title">1. Input: Trend Brief</div>', unsafe_allow_html=True)
with st.container(border=True):
    left, right = st.columns([1.35, 1], gap="large")
    with left:
        title = st.text_input("Trend title", value="AI Agent Trend", placeholder="Paste a product, GitHub repo, news headline, or creator trend")
        url = st.text_input("Trend URL", value="", placeholder="Optional: GitHub, Product Hunt, Hacker News, news page...")
    with right:
        platform = st.selectbox("Platform", PLATFORMS, index=0)
        style = st.selectbox("Style", STYLES, index=0)
        duration = st.selectbox("Duration", DURATIONS, index=1, format_func=lambda value: f"{value} seconds")

    generate = st.button("Generate Video Package", type="primary", use_container_width=True)

st.markdown('<div class="section-title">2. Execute: Agent Pipeline</div>', unsafe_allow_html=True)
progress_box = st.container(border=True)

if generate:
    with progress_box:
        progress = st.progress(0)
        status = st.empty()
        for index, step in enumerate(AGENT_STEPS, start=1):
            status.markdown(f"**Running:** {step}")
            progress.progress(index / len(AGENT_STEPS))
            sleep(0.15)
        status.markdown("**Finalizing:** Exporting publish-ready package")

    with st.spinner("Building your creator-ready package..."):
        result = run_trend_to_video(
            {"title": title, "url": url, "description": ""},
            creator_profile=load_creator_profile(),
            platform=PIPELINE_PLATFORMS[platform],
            style=PIPELINE_STYLES[style],
            duration=int(duration),
        )
    st.session_state["last_result"] = result
    with progress_box:
        st.success("Package ready. Review the final assets below.")
else:
    with progress_box:
        first_row = st.columns(4)
        for index, step in enumerate(AGENT_STEPS[:4]):
            first_row[index].write(f"- {step}")
        second_row = st.columns(4)
        for index, step in enumerate(AGENT_STEPS[4:]):
            second_row[index].write(f"- {step}")

if "last_result" in st.session_state:
    render_output(st.session_state["last_result"])
else:
    st.markdown('<div class="section-title">3. Output: Publish-Ready Package</div>', unsafe_allow_html=True)
    with st.container(border=True):
        preview, assets = st.columns([1.2, 1], gap="large")
        with preview:
            st.subheader("Video preview will appear here")
            st.info("Run the pipeline to generate MP4, thumbnail, subtitles, description, hashtags, and quality report.")
        with assets:
            st.subheader("Package Assets")
            st.write("- MP4 video")
            st.write("- Thumbnail")
            st.write("- Hashtags and description")
            st.write("- Subtitles")
            st.write("- Quality report summary")
