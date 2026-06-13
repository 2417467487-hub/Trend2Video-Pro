"""Streamlit UI for Trend2Video Pro."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.agents.orchestrator import run_trend_to_video
from src.collectors.collector_manager import collect_all_topics
from src.creator.creator_profile import load_creator_profile, save_creator_profile
from src.database.db import list_topics, upsert_topics

PLATFORMS = ["Bilibili", "Xiaohongshu", "YouTube Shorts", "TikTok"]
STYLES = ["Tech News", "Educational", "Viral Talking Head", "Deep Analysis"]
DURATIONS = [30, 60, 90]

st.set_page_config(page_title="Trend2Video Pro", layout="wide")
st.title("Trend2Video Pro")
st.caption("Trend Intelligence + Content Execution System")

page = st.sidebar.radio("Page", ["One-Click Generate", "Trend Pool", "Creator Profile", "Generated Packages"])


def render_result(result: dict) -> None:
    """Render generated result assets."""
    files = result["files"]
    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Video Preview")
        video_path = Path(files["video"])
        if video_path.exists():
            st.video(str(video_path))
        else:
            st.warning("Video was not created. Check the quality report and .error.txt file.")
    with right:
        st.subheader("Publish Package")
        st.write(f"**Title:** {result['script'].get('title', result['input']['title'])}")
        st.write(f"**Description:** {result['script'].get('description', '')}")
        st.write(f"**Tags:** {', '.join(result['script'].get('tags', []))}")
        st.metric("Topic Score", result["topic_score"].get("final_opportunity_score"))
        st.metric("Creator Fit", result.get("creator_fit", {}).get("creator_fit_score", "n/a"))
        st.metric("Viral Probability", result.get("viral_prediction", {}).get("viral_probability", "n/a"))
        st.metric("Video Quality", result["video_score"].get("overall_video_score", result["video_score"].get("video_quality_score")))
        thumb_path = Path(files["thumbnail"])
        if thumb_path.exists():
            st.image(str(thumb_path), caption="Thumbnail")

    report_md = Path(files["report_md"])
    if report_md.exists():
        with st.expander("Quality Report", expanded=True):
            st.markdown(report_md.read_text(encoding="utf-8"))

    package_dir = result.get("publish_package", {}).get("package_dir")
    if package_dir:
        st.success(f"Publish package exported: {package_dir}")

    st.subheader("Downloads")
    buttons = [
        ("Video", files["video"]),
        ("Script", files["script_md"]),
        ("Subtitles", files["subtitles"]),
        ("Thumbnail", files["thumbnail"]),
        ("Quality Report", files["report_md"]),
    ]
    cols = st.columns(len(buttons))
    for col, (label, path) in zip(cols, buttons):
        p = Path(path)
        if p.exists():
            col.download_button(label, data=p.read_bytes(), file_name=p.name)


if page == "One-Click Generate":
    st.subheader("One-Click Generate")
    with st.form("generator"):
        title = st.text_input("Trend title", value="AI Agent Browser Tool Trend")
        url = st.text_input("Trend URL (optional)", value="")
        platform = st.selectbox("Target platform", PLATFORMS)
        style = st.selectbox("Video style", STYLES)
        duration = st.selectbox("Duration", DURATIONS, index=1)
        submitted = st.form_submit_button("Generate publish package", type="primary")
    if submitted:
        with st.spinner("Running trend-to-video agent pipeline..."):
            result = run_trend_to_video(
                {"title": title, "url": url, "description": ""},
                creator_profile=load_creator_profile(),
                platform=platform,
                style=style,
                duration=int(duration),
            )
        render_result(result)

elif page == "Trend Pool":
    st.subheader("Trend Pool")
    st.write("A lightweight entry point for finding what to make next. This is not a dashboard.")
    if st.button("Update topics", type="primary"):
        with st.spinner("Collecting GitHub Trending, Hacker News, and Product Hunt topics..."):
            count = upsert_topics(collect_all_topics(limit=20))
        st.success(f"Updated {count} topics")

    topics = list_topics(limit=20)
    if not topics:
        st.info("No topics yet. Click Update topics first.")
    for topic in topics:
        with st.container(border=True):
            cols = st.columns([4, 1])
            cols[0].markdown(f"### #{topic['id']} {topic['title']}")
            cols[1].metric("Score", round(topic["final_opportunity_score"], 1))
            st.write(f"**Source:** {topic['source']}  \n**URL:** {topic['url']}")
            if topic.get("description"):
                st.write(topic["description"])
            st.write(f"**Reason:** {topic['recommendation_reason']}")
            st.write(f"**Risk:** {topic['risk_note']}")
            with st.form(f"topic-generate-{topic['id']}"):
                form_cols = st.columns(4)
                platform = form_cols[0].selectbox("Platform", PLATFORMS, key=f"platform-{topic['id']}")
                style = form_cols[1].selectbox("Style", STYLES, key=f"style-{topic['id']}")
                duration = form_cols[2].selectbox("Duration", DURATIONS, index=1, key=f"duration-{topic['id']}")
                submitted = form_cols[3].form_submit_button("Generate")
                if submitted:
                    result = run_trend_to_video(topic, load_creator_profile(), platform, style, duration)
                    render_result(result)

elif page == "Creator Profile":
    st.subheader("Creator Profile")
    profile = load_creator_profile()
    with st.form("creator-profile"):
        niche = st.text_area("Creator niche", value=profile.get("niche", ""))
        tone = st.text_input("Tone", value=profile.get("tone", ""))
        audience = st.text_input("Audience", value=profile.get("audience", ""))
        keywords = st.text_input("Keywords", value=", ".join(profile.get("keywords", [])))
        platforms = st.multiselect("Target platforms", PLATFORMS, default=[p for p in profile.get("target_platforms", []) if p in PLATFORMS])
        saved = st.form_submit_button("Save profile", type="primary")
    if saved:
        profile.update(
            {
                "niche": niche,
                "tone": tone,
                "audience": audience,
                "keywords": [item.strip() for item in keywords.split(",") if item.strip()],
                "target_platforms": platforms,
            }
        )
        save_creator_profile(profile)
        st.success("Creator profile saved")
    st.json(profile)

else:
    st.subheader("Generated Packages")
    package_root = Path("outputs/publish_packages")
    packages = sorted(package_root.glob("*"), reverse=True) if package_root.exists() else []
    if not packages:
        st.info("No publish packages yet. Generate a video first.")
    for package in packages[:20]:
        with st.container(border=True):
            st.markdown(f"### {package.name}")
            st.write(str(package))
            files = sorted([p.name for p in package.iterdir() if p.is_file()])
            st.write(", ".join(files))
