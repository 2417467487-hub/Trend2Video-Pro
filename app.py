"""Streamlit execution UI for Trend2Video Pro."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.collectors.collector_manager import collect_all_topics
from src.database.db import list_topics, upsert_topics
from src.pipeline import GenerationRequest, run_generation


PLATFORMS = ["B站", "小红书", "YouTube Shorts", "TikTok"]
STYLES = ["科技资讯", "干货讲解", "爆款口播", "深度分析"]
DURATIONS = [30, 60, 90]


st.set_page_config(page_title="Trend2Video Pro", layout="wide")
st.title("Trend2Video Pro")
st.caption("One-click trend-to-video execution engine with quality control")

page = st.sidebar.radio("页面", ["一键生成视频", "热点池"])


def render_result(result: dict) -> None:
    """Render generated result assets."""
    files = result["files"]
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("视频预览")
        video_path = Path(files["video"])
        if video_path.exists():
            st.video(str(video_path))
        else:
            st.warning("视频未成功生成，请查看质量报告和 .error.txt。")
    with right:
        st.subheader("发布素材")
        st.write(f"**标题：** {result['script'].get('title', result['input']['title'])}")
        st.write(f"**简介：** {result['script'].get('description', '')}")
        st.write(f"**标签：** {', '.join(result['script'].get('tags', []))}")
        st.metric("选题机会分", result["topic_score"].get("final_opportunity_score"))
        st.metric("脚本质量分", result["script_score"].get("overall_script_score"))
        st.metric("视频质量分", result["video_score"].get("overall_video_score", result["video_score"].get("video_quality_score")))
        thumb_path = Path(files["thumbnail"])
        if thumb_path.exists():
            st.image(str(thumb_path), caption="封面图")

    report_md = Path(files["report_md"])
    if report_md.exists():
        with st.expander("质量评分报告", expanded=True):
            st.markdown(report_md.read_text(encoding="utf-8"))

    st.subheader("下载")
    buttons = [
        ("下载视频", files["video"]),
        ("下载脚本", files["script_md"]),
        ("下载字幕", files["subtitles"]),
        ("下载封面", files["thumbnail"]),
        ("下载质量报告", files["report_md"]),
    ]
    cols = st.columns(len(buttons))
    for col, (label, path) in zip(cols, buttons):
        p = Path(path)
        if p.exists():
            col.download_button(label, data=p.read_bytes(), file_name=p.name)


if page == "一键生成视频":
    st.subheader("一键生成视频")
    with st.form("generator"):
        title = st.text_input("热点标题", value="AI Agent 浏览器插件正在变成新趋势")
        url = st.text_input("热点链接（可选）", value="")
        platform = st.selectbox("目标平台", PLATFORMS)
        style = st.selectbox("视频风格", STYLES)
        duration = st.selectbox("视频时长", DURATIONS, index=1)
        submitted = st.form_submit_button("一键生成视频", type="primary")

    if submitted:
        progress = st.progress(0, text="启动生成流程")
        try:
            progress.progress(15, text="抓取网页与评分")
            request = GenerationRequest(title=title, url=url, platform=platform, duration=int(duration), style=style)
            progress.progress(35, text="生成脚本、质检和分镜")
            result = run_generation(request)
            progress.progress(85, text="合成视频、封面和报告")
            progress.progress(100, text="生成完成")
            render_result(result)
        except Exception as exc:
            st.error(f"生成失败：{exc}")

if page == "热点池":
    st.subheader("热点池")
    st.write("热点池只是入口：快速发现可制作选题，然后一键进入视频生产流程。")
    if st.button("更新今日热点", type="primary"):
        with st.spinner("正在抓取 GitHub Trending / Hacker News / Product Hunt..."):
            count = upsert_topics(collect_all_topics(limit=20))
        st.success(f"已更新 {count} 条热点")

    topics = list_topics(limit=20)
    if not topics:
        st.info("暂无热点。点击“更新今日热点”开始。")
    for topic in topics:
        with st.container(border=True):
            top_line = st.columns([4, 1])
            top_line[0].markdown(f"### #{topic['id']} {topic['title']}")
            top_line[1].metric("机会分", round(topic["final_opportunity_score"], 1))
            st.write(f"**来源：** {topic['source']}  \n**URL：** {topic['url']}")
            if topic.get("description"):
                st.write(topic["description"])
            st.write(f"**推荐理由：** {topic['recommendation_reason']}")
            st.write(f"**风险提示：** {topic['risk_note']}")
            with st.form(f"topic-generate-{topic['id']}"):
                cols = st.columns(4)
                platform = cols[0].selectbox("平台", PLATFORMS, key=f"platform-{topic['id']}")
                style = cols[1].selectbox("风格", STYLES, key=f"style-{topic['id']}")
                duration = cols[2].selectbox("时长", DURATIONS, index=1, key=f"duration-{topic['id']}")
                submitted = cols[3].form_submit_button("一键生成视频")
                if submitted:
                    result = run_generation(
                        GenerationRequest(
                            topic_id=topic["id"],
                            title=topic["title"],
                            url=topic["url"],
                            platform=platform,
                            style=style,
                            duration=duration,
                        )
                    )
                    render_result(result)
