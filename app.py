import os
import tempfile
import json
import streamlit as st
from video_processor import (
    compute_audio_energy, generate_clip, select_highlights, transcribe_video,
    generate_clip_with_format, add_watermark, trim_clip, adjust_speed, EXPORT_FORMATS
)

st.set_page_config(
    page_title="AttentionX",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Custom CSS styling
st.markdown("""
    <style>
        /* Global styles */
        * {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
            color: #e0e0e0;
        }
        
        /* Main container */
        .main {
            background: linear-gradient(135deg, rgba(15, 15, 30, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%);
            padding: 2rem;
        }
        
        /* Header styling */
        .header-container {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem 0;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-radius: 20px;
            border: 1px solid rgba(139, 92, 246, 0.2);
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
        }
        
        .header-title {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            letter-spacing: -1px;
        }
        
        .header-subtitle {
            font-size: 1.1rem;
            color: #a0a0c0;
            margin-top: 0.5rem;
            font-weight: 300;
        }
        
        /* Upload section */
        .upload-section {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            border: 2px dashed rgba(139, 92, 246, 0.3);
            border-radius: 15px;
            padding: 2.5rem;
            text-align: center;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
        }
        
        .upload-section:hover {
            border-color: rgba(139, 92, 246, 0.6);
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Clip card styling */
        .clip-card {
            background: linear-gradient(135deg, rgba(30, 30, 60, 0.8) 0%, rgba(40, 40, 80, 0.8) 100%);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
            transition: all 0.3s ease;
        }
        
        .clip-card:hover {
            border-color: rgba(139, 92, 246, 0.4);
            box-shadow: 0 12px 48px rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }
        
        .clip-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .clip-badge {
            display: inline-block;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .clip-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #e0e0ff;
            margin: 0.5rem 0;
        }
        
        .clip-meta {
            display: flex;
            gap: 2rem;
            font-size: 0.95rem;
            color: #a0a0c0;
            margin-top: 0.5rem;
        }
        
        .clip-meta-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Status messages */
        .stSuccess {
            background: rgba(34, 197, 94, 0.1) !important;
            border-color: rgba(34, 197, 94, 0.3) !important;
            color: #86efac !important;
            border-radius: 10px !important;
            padding: 1rem !important;
        }
        
        .stWarning {
            background: rgba(234, 179, 8, 0.1) !important;
            border-color: rgba(234, 179, 8, 0.3) !important;
            color: #fde047 !important;
            border-radius: 10px !important;
            padding: 1rem !important;
        }
        
        /* Spinner styling */
        .stSpinner {
            color: #6366f1 !important;
        }
        
        /* Transcript section */
        .transcript-section {
            background: rgba(30, 30, 60, 0.5);
            border-left: 4px solid #6366f1;
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 2rem;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .transcript-section::-webkit-scrollbar {
            width: 8px;
        }
        
        .transcript-section::-webkit-scrollbar-track {
            background: rgba(99, 102, 241, 0.1);
            border-radius: 10px;
        }
        
        .transcript-section::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.4);
            border-radius: 10px;
        }
        
        .transcript-section::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.6);
        }
        
        /* Video container */
        .video-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
            margin: 1rem 0;
        }
        
        h3 {
            color: #e0e0ff;
            font-weight: 700;
        }
        
        hr {
            border-color: rgba(139, 92, 246, 0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
    <div class="header-container">
        <div class="header-title">✨ AttentionX</div>
        <div class="header-subtitle">Transform long-form content into viral short-form clips in seconds</div>
    </div>
""", unsafe_allow_html=True)

# Info section
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⚡ Processing", "AI-Powered", "Real-time")
with col2:
    st.metric("🎬 Format", "Vertical 9:16", "TikTok/Reels")
with col3:
    st.metric("🔤 Captions", "Auto-Generated", "Smart")

st.markdown("---")

# Advanced Settings Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Advanced Settings")
    
    num_clips = st.slider(
        "Number of clips to generate",
        min_value=1,
        max_value=10,
        value=4,
        help="More clips = more social media content"
    )
    
    min_clip_length = st.slider(
        "Minimum clip length (seconds)",
        min_value=3,
        max_value=15,
        value=5,
        help="Shorter is better for TikTok (5-15 sec ideal)"
    )
    
    max_clip_length = st.slider(
        "Maximum clip length (seconds)",
        min_value=10,
        max_value=60,
        value=30,
        help="Maximum duration for generated clips"
    )
    
    sensitivity = st.slider(
        "Highlight sensitivity",
        min_value=0.3,
        max_value=1.0,
        value=0.6,
        step=0.1,
        help="Lower = more clips detected, Higher = only top moments"
    )
    
    st.divider()
    
    # Export settings
    st.markdown("### 📱 Export Settings")
    export_format = st.selectbox(
        "Export format preset",
        list(EXPORT_FORMATS.keys()),
        help="Choose platform-specific dimensions & fps"
    )
    
    watermark_text = st.text_input(
        "Watermark/Branding",
        placeholder="e.g., @YourName or YourBrand",
        help="Add text watermark to clips"
    )
    
    st.divider()
    
    # A/B Testing
    st.markdown("### 🎯 A/B Testing")
    ab_test_enabled = st.checkbox(
        "Enable A/B testing",
        help="Compare different hook styles"
    )
    
    st.divider()
    st.markdown("### 📊 About")
    st.info("🎯 **AttentionX** helps creators turn long videos into viral clips. Perfect for TikTok, Instagram Reels, and YouTube Shorts!")
    st.markdown("[View on GitHub](https://github.com) • [Report Issue](https://github.com/issues)")

# Upload section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("## 📹 Upload Your Video")
video_file = st.file_uploader("Drag and drop your long-form video or click to select", type=["mp4", "mov", "mkv", "webm"])
st.markdown('</div>', unsafe_allow_html=True)

if video_file is not None:
    with st.spinner("Saving video..."):
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, video_file.name)
        with open(video_path, "wb") as f:
            f.write(video_file.read())

    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    st.video(video_path)
    st.markdown('</div>', unsafe_allow_html=True)

    col_analyze, col_spacer = st.columns([1, 4])
    with col_analyze:
        analyze_button = st.button("🚀 Analyze & Generate Clips", use_container_width=True)

    if analyze_button:
        progress_bar = st.progress(0)
        status_text = st.empty()

        with st.spinner("🎯 Transcribing audio..."):
            status_text.text("Step 1/3: Transcribing audio with AI...")
            transcript_text, segments, audio_path = transcribe_video(video_path)
            progress_bar.progress(33)

        with st.spinner("📊 Analyzing audio energy..."):
            status_text.text("Step 2/3: Analyzing audio energy and emotions...")
            energy_times, energy = compute_audio_energy(audio_path)
            progress_bar.progress(66)

        with st.spinner("✂️ Identifying highlights..."):
            status_text.text("Step 3/3: Identifying highlight moments...")
            highlights = select_highlights(segments, energy_times, energy, top_n=num_clips)
            progress_bar.progress(100)

        status_text.empty()
        progress_bar.empty()

        if not highlights:
            st.warning("❌ No strong highlights found. Try a different video or increase the recording volume.")
        else:
            st.success(f"✅ Found {len(highlights)} viral moments! Download your clips below.")

            st.markdown("---")
            st.markdown("## 🎬 Your Generated Clips")

            for idx, highlight in enumerate(highlights, start=1):
                st.markdown(f'<div class="clip-card">', unsafe_allow_html=True)
                
                col_badge, col_title = st.columns([0.2, 0.8])
                with col_badge:
                    rank_emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "⭐"
                    st.markdown(f'<span class="clip-badge">{rank_emoji} CLIP {idx}</span>', unsafe_allow_html=True)
                with col_title:
                    st.markdown(f'<div class="clip-title">{highlight.get("hook", "Great Moment")}</div>', unsafe_allow_html=True)

                col_time1, col_time2, col_score = st.columns([0.25, 0.25, 0.5])
                with col_time1:
                    st.markdown(f'**⏱️ Start:** {highlight["start"]:.1f}s')
                with col_time2:
                    st.markdown(f'**⏹️ End:** {highlight["end"]:.1f}s')
                with col_score:
                    sentiment_emoji = "🔥" if highlight.get("sentiment", 0) > 0.7 else "⭐"
                    st.markdown(f'**{sentiment_emoji} Viral Score:** {highlight["score"]:.2f}')
                
                st.markdown(f'**Hook:** _{highlight.get("hook", "Check this moment...")}_')
                st.markdown(f'📝 {highlight["text"]}')

                # Clip editor
                with st.expander(f"✏️ Edit Clip {idx}"):
                    col_trim1, col_trim2 = st.columns(2)
                    with col_trim1:
                        trim_start = st.number_input(
                            f"Trim start (sec)",
                            min_value=0.0,
                            max_value=float(highlight["end"]),
                            value=float(highlight["start"]),
                            step=0.5,
                            key=f"trim_start_{idx}"
                        )
                    with col_trim2:
                        trim_end = st.number_input(
                            f"Trim end (sec)",
                            min_value=float(highlight["start"]),
                            max_value=100.0,
                            value=float(highlight["end"]),
                            step=0.5,
                            key=f"trim_end_{idx}"
                        )
                    
                    speed = st.slider(
                        f"Playback speed",
                        min_value=0.5,
                        max_value=2.0,
                        value=1.0,
                        step=0.25,
                        key=f"speed_{idx}",
                        help="0.5x = half speed, 2.0x = double speed"
                    )

                clip_path = os.path.join(temp_dir, f"clip_{idx}.mp4")
                with st.spinner(f"🎥 Rendering clip {idx} as {export_format}..."):
                    # Generate with selected format and watermark
                    generate_clip_with_format(
                        video_path,
                        {
                            **highlight,
                            "start": trim_start,
                            "end": trim_end,
                        },
                        clip_path,
                        format_name=export_format,
                        watermark_text=watermark_text if watermark_text else None
                    )

                st.video(clip_path)

                # Download options
                col_download1, col_download2 = st.columns(2)
                with col_download1:
                    with open(clip_path, "rb") as clip_file:
                        st.download_button(
                            label=f"⬇️ Download {export_format}",
                            data=clip_file,
                            file_name=f"attentionx_clip_{idx}_{export_format.replace(' ', '_')}.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                        )
                
                with col_download2:
                    # Alternative format download
                    alt_format = [f for f in EXPORT_FORMATS.keys() if f != export_format][0]
                    clip_path_alt = os.path.join(temp_dir, f"clip_{idx}_alt.mp4")
                    if st.button(f"Generate {alt_format}", key=f"alt_fmt_{idx}"):
                        with st.spinner(f"Rendering as {alt_format}..."):
                            generate_clip_with_format(
                                video_path,
                                {**highlight, "start": trim_start, "end": trim_end},
                                clip_path_alt,
                                format_name=alt_format,
                                watermark_text=watermark_text if watermark_text else None
                            )
                            with open(clip_path_alt, "rb") as cf:
                                st.download_button(
                                    label=f"⬇️ {alt_format}",
                                    data=cf,
                                    file_name=f"attentionx_clip_{idx}_{alt_format.replace(' ', '_')}.mp4",
                                    mime="video/mp4",
                                    use_container_width=True,
                                )

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("")

            # A/B Testing Section
            if ab_test_enabled and highlights:
                st.markdown("---")
                st.markdown("## 🎯 A/B Testing Console")
                
                ab_col1, ab_col2 = st.columns(2)
                with ab_col1:
                    st.markdown("### Hook A (Original)")
                    hook_a = highlights[0].get("hook", "Default")
                    st.info(f"📝 {hook_a}")
                    views_a = st.number_input("Views (Hook A)", value=0, key="views_a", min_value=0)
                    clicks_a = st.number_input("Clicks (Hook A)", value=0, key="clicks_a", min_value=0)
                
                with ab_col2:
                    st.markdown("### Hook B (Alternative)")
                    hook_b_options = [
                        "Wait, you NEED to hear this...",
                        "This will BLOW YOUR MIND 🤯",
                        "Plot twist incoming...",
                        "Here's the secret nobody talks about:",
                    ]
                    hook_b = st.selectbox("Choose Hook B", hook_b_options)
                    st.info(f"📝 {hook_b}")
                    views_b = st.number_input("Views (Hook B)", value=0, key="views_b", min_value=0)
                    clicks_b = st.number_input("Clicks (Hook B)", value=0, key="clicks_b", min_value=0)
                
                if views_a > 0 or views_b > 0:
                    ctr_a = (clicks_a / views_a * 100) if views_a > 0 else 0
                    ctr_b = (clicks_b / views_b * 100) if views_b > 0 else 0
                    
                    st.markdown("### 📊 Results")
                    result_col1, result_col2, result_col3 = st.columns(3)
                    with result_col1:
                        if views_a == 0 and views_b == 0:
                            winner = "No data yet"
                        else:
                            winner = "Hook A 🏆" if ctr_a > ctr_b else "Hook B 🏆" if ctr_b > ctr_a else "Tie 🤝"
                        st.metric("Winner", winner)
                    with result_col2:
                        st.metric("Hook A CTR", f"{ctr_a:.1f}%")
                    with result_col3:
                        st.metric("Hook B CTR", f"{ctr_b:.1f}%")

            st.markdown("---")
            st.markdown("## 📝 Full Transcript")
            st.markdown('<div class="transcript-section">', unsafe_allow_html=True)
            st.text(transcript_text[:8000] + ("..." if len(transcript_text) > 8000 else ""))
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")
            
            # Analytics Summary
            st.markdown("## 📈 Session Analytics")
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("📹 Video Duration", f"{highlights[-1]['end']:.0f}s" if highlights else "0s")
            with col_b:
                st.metric("✂️ Clips Generated", len(highlights))
            with col_c:
                avg_score = sum(h["score"] for h in highlights) / len(highlights) if highlights else 0
                st.metric("⭐ Avg Viral Score", f"{avg_score:.2f}")
            with col_d:
                total_clip_time = sum(h["end"] - h["start"] for h in highlights)
                st.metric("🎬 Total Clip Time", f"{total_clip_time:.0f}s")
            
            st.markdown("---")
            st.info("💡 **Pro tip:** Download these clips and post on TikTok, Instagram Reels, or YouTube Shorts for maximum engagement!")
            st.success("🚀 **Share your results** — Tag @AttentionX to be featured!")

