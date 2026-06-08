"""Streamlit execution UI for Trend2Video Pro."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.pipeline import GenerationRequest, run_generation


st.set_page_config(page_title="Trend2Video Pro", layout="centered")
st.title("Trend2Video Pro")
st.caption("From Emerging Trend to Publish-Ready Short Video in One Click")

with st.form("generator"):
    title = st.text_input("热点标题", value="OpenAI 发布新的 AI 视频工作流趋势")
    url = st.text_input("热点链接", value="")
    platform = st.selectbox("目标平台", ["B站", "小红书", "YouTube Shorts", "TikTok"])
    duration = st.selectbox("视频时长", [30, 60, 90], index=1)
    style = st.selectbox("风格", ["科技资讯", "干货讲解", "爆款口播", "深度分析"])
    voice = st.selectbox("配音声音", ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "en-US-AriaNeural"])
    rate = st.select_slider("语速", options=["-20%", "-10%", "+0%", "+10%", "+20%"], value="+0%")
    submitted = st.form_submit_button("一键生成视频", type="primary")

if submitted:
    progress = st.progress(0, text="启动生成流程")
    try:
        progress.progress(10, text="抓取网页与选题评分")
        request = GenerationRequest(title=title, url=url, platform=platform, duration=int(duration), style=style, voice=voice, rate=rate)
        progress.progress(25, text="生成脚本、质检与分镜")
        result = run_generation(request)
        progress.progress(80, text="合成视频、封面与质量报告")
        progress.progress(100, text="生成完成")

        files = result["files"]
        st.subheader("最终结果")
        st.write(f"**标题：** {result['script'].get('title', title)}")
        st.write(f"**简介：** {result['script'].get('description', '')}")
        st.write(f"**标签：** {', '.join(result['script'].get('tags', []))}")

        video_path = Path(files["video"])
        if video_path.exists():
            st.video(str(video_path))
        else:
            st.warning("视频未成功生成，请查看质量报告和 .error.txt。")

        thumb_path = Path(files["thumbnail"])
        if thumb_path.exists():
            st.image(str(thumb_path), caption="封面")

        report_md = Path(files["report_md"])
        if report_md.exists():
            st.markdown(report_md.read_text(encoding="utf-8"))

        for label, path in [
            ("下载视频", files["video"]),
            ("下载脚本", files["script_md"]),
            ("下载字幕", files["subtitles"]),
            ("下载封面", files["thumbnail"]),
            ("下载质量报告", files["report_md"]),
        ]:
            p = Path(path)
            if p.exists():
                st.download_button(label, data=p.read_bytes(), file_name=p.name)
    except Exception as exc:
        st.error(f"生成失败：{exc}")
