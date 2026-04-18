import os
import tempfile
import json
import streamlit as st
import streamlit.components.v1 as components
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

# Custom CSS styling with a full dark neon theme and animated polish
st.markdown("""
    <style>
        /* Global theme */
        * {
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: radial-gradient(circle at top left, rgba(124, 58, 237, 0.16), transparent 18%),
                        radial-gradient(circle at top right, rgba(56, 189, 248, 0.14), transparent 16%),
                        linear-gradient(180deg, #020617 0%, #090b1f 100%);
            color: #e2e8f0;
        }

        .stApp {
            background: transparent !important;
        }

        .main {
            background: rgba(8, 12, 28, 0.94);
            padding: 2rem;
            border-radius: 28px;
            margin: 1rem;
            border: 1px solid rgba(99, 102, 241, 0.24);
            box-shadow: 0 24px 90px rgba(79, 70, 229, 0.16);
            position: relative;
            overflow: hidden;
        }

        .main::before {
            content: '';
            position: absolute;
            top: -20%;
            left: -10%;
            width: 40rem;
            height: 40rem;
            background: radial-gradient(circle, rgba(124, 58, 237, 0.14), transparent 45%);
            filter: blur(80px);
            opacity: 0.9;
            animation: slowDrift 18s ease-in-out infinite;
            pointer-events: none;
        }

        .header-container {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2.5rem;
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.18), rgba(168, 85, 247, 0.16));
            border-radius: 32px;
            border: 1px solid rgba(79, 70, 229, 0.35);
            box-shadow: 0 28px 100px rgba(79, 70, 229, 0.14);
            animation: float 10s ease-in-out infinite;
        }

        .header-title {
            font-size: 3.6rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.02;
            background: linear-gradient(90deg, #7c3aed 0%, #22d3ee 45%, #f472b6 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: textShift 8s ease infinite;
        }

        .header-subtitle {
            font-size: 1.15rem;
            color: #cbd5e1;
            margin-top: 1rem;
            font-weight: 400;
            max-width: 720px;
            margin-left: auto;
            margin-right: auto;
            line-height: 1.75;
        }

        .upload-section {
            background: rgba(15, 23, 42, 0.78);
            border: 1px dashed rgba(99, 102, 241, 0.35);
            border-radius: 26px;
            padding: 3rem;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
            margin-bottom: 2rem;
            position: relative;
            animation: float 12s ease-in-out infinite;
            color: #e2e8f0 !important;
        }

        .upload-section:hover {
            background: rgba(15, 23, 42, 0.92);
            box-shadow: 0 32px 110px rgba(79, 70, 229, 0.18);
            transform: translateY(-3px);
        }

        .upload-section.dragover {
            border-color: #22d3ee;
            background: rgba(14, 50, 80, 0.95);
        }

        .progress-container {
            background: rgba(15, 23, 42, 0.86);
            border-radius: 22px;
            padding: 1.75rem;
            margin: 2rem 0;
            border: 1px solid rgba(99, 102, 241, 0.3);
            box-shadow: 0 22px 70px rgba(79, 70, 229, 0.13);
            color: #e2e8f0 !important;
        }

        .progress-step {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.7);
            transition: transform 0.25s ease, background 0.25s ease;
        }

        .progress-step:hover {
            transform: translateY(-2px);
        }

        .progress-step.active {
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.25), rgba(59, 130, 246, 0.22));
            border-left: 4px solid #7c3aed;
            animation: pulse 2.5s infinite;
        }

        .progress-step.completed {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.24), rgba(56, 189, 248, 0.18));
            border-left: 4px solid #22c55e;
        }

        .step-icon {
            width: 44px;
            height: 44px;
            min-width: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-size: 1.2rem;
            font-weight: 700;
        }

        .step-icon.active {
            background: linear-gradient(135deg, #7c3aed 0%, #22d3ee 100%);
            color: #0f172a;
        }

        .step-icon.completed {
            background: linear-gradient(135deg, #22c55e 0%, #0ea5e9 100%);
            color: white;
        }

        .step-icon.pending {
            background: #1e293b;
            color: #cbd5e1;
        }

        .stButton > button {
            background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%);
            color: white;
            border: none;
            border-radius: 16px;
            padding: 1rem 2rem;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
            box-shadow: 0 20px 55px rgba(124, 58, 237, 0.32);
            min-height: 52px;
            letter-spacing: 0.03em;
            position: relative;
            overflow: hidden;
        }

        .stButton > button::after {
            content: '';
            position: absolute;
            top: 0;
            left: -120%;
            width: 80%;
            height: 100%;
            background: linear-gradient(120deg, transparent, rgba(255, 255, 255, 0.25), transparent);
            transform: skewX(-20deg);
            transition: none;
        }

        .stButton > button:hover::after {
            animation: shimmer 1.2s ease forwards;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            background: linear-gradient(135deg, #8b5cf6 0%, #4f46e5 100%);
            box-shadow: 0 24px 70px rgba(124, 58, 237, 0.4);
        }

        .stButton > button:active {
            transform: translateY(0);
            box-shadow: 0 12px 32px rgba(124, 58, 237, 0.28);
        }

        .stButton > button:disabled {
            background: rgba(148, 163, 184, 0.3);
            color: #cbd5e1;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }

        .secondary-btn {
            background: rgba(255, 255, 255, 0.08);
            color: #e2e8f0;
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 14px;
            padding: 0.85rem 1.6rem;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.25s ease, background 0.25s ease, border-color 0.25s ease;
        }

        .secondary-btn:hover {
            background: rgba(255, 255, 255, 0.14);
            border-color: rgba(148, 163, 184, 0.35);
            transform: translateY(-1px);
        }

        .feature-card {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(99, 102, 241, 0.24);
            border-radius: 20px;
            padding: 1.35rem;
            transition: transform 0.35s ease, box-shadow 0.35s ease, background 0.35s ease;
            box-shadow: 0 18px 45px rgba(79, 70, 229, 0.14);
            color: #e2e8f0 !important;
            animation: float 9s ease-in-out infinite;
        }

        .feature-card:hover {
            transform: translateY(-4px);
            background: rgba(15, 23, 42, 0.95);
            box-shadow: 0 26px 68px rgba(79, 70, 229, 0.28);
        }

        .feature-card:before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 20px;
            background: radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 35%);
            opacity: 0;
            transition: opacity 0.35s ease;
            pointer-events: none;
        }

        .feature-card:hover:before {
            opacity: 1;
        }

        .feature-card div {
            color: #e2e8f0 !important;
        }

        .clip-card::after {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top left, rgba(124, 58, 237, 0.12), transparent 30%),
                        radial-gradient(circle at bottom right, rgba(56, 189, 248, 0.12), transparent 30%);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }

        .clip-card:hover::after {
            opacity: 1;
        }

        .video-container {
            border-radius: 28px;
            overflow: hidden;
            box-shadow: 0 38px 120px rgba(79, 70, 229, 0.18);
            margin: 1.75rem 0;
            border: 1px solid rgba(99, 102, 241, 0.24);
            animation: slowFloat 18s ease-in-out infinite;
        }

        .feature-icon {
            font-size: 1.55rem;
            margin-bottom: 0.65rem;
        }

        .clip-card {
            background: linear-gradient(135deg, rgba(4, 7, 20, 0.96), rgba(14, 23, 41, 0.96));
            border: 1px solid rgba(79, 70, 229, 0.28);
            border-radius: 26px;
            padding: 2rem;
            margin-bottom: 1.75rem;
            box-shadow: 0 32px 110px rgba(79, 70, 229, 0.18);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease both;
        }

        .clip-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 42px 120px rgba(79, 70, 229, 0.22);
        }

        .clip-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #7c3aed, #22d3ee, #ec4899);
        }

        .clip-badge {
            background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 100%);
            color: #0f172a;
            padding: 0.35rem 0.85rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 0.5rem;
            border: 1px solid rgba(167, 139, 250, 0.34);
        }

        .clip-title {
            font-size: 1.55rem;
            font-weight: 800;
            color: #f8fafc;
            margin: 0.5rem 0;
            line-height: 1.25;
        }

        .clip-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 1.75rem;
            font-size: 0.95rem;
            color: #94a3b8;
            margin-top: 0.9rem;
        }

        .clip-meta-item {
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }

        .video-container {
            border-radius: 28px;
            overflow: hidden;
            box-shadow: 0 38px 120px rgba(79, 70, 229, 0.18);
            margin: 1.75rem 0;
            border: 1px solid rgba(99, 102, 241, 0.24);
        }

        .transcript-section {
            background: rgba(4, 7, 20, 0.94);
            border-left: 4px solid #7c3aed;
            border-radius: 22px;
            padding: 1.75rem;
            margin-top: 2rem;
            max-height: 330px;
            overflow-y: auto;
            color: #e2e8f0;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.95rem;
            line-height: 1.75;
        }

        .transcript-section::-webkit-scrollbar {
            width: 8px;
        }

        .transcript-section::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.84);
            border-radius: 999px;
        }

        .transcript-section::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            border-radius: 999px;
        }

        .transcript-section::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #8b5cf6, #60a5fa);
        }

        .analytics-card {
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(15, 23, 42, 0.96));
            border: 1px solid rgba(99, 102, 241, 0.28);
            border-radius: 22px;
            padding: 1.75rem;
            margin: 1rem 0;
            box-shadow: 0 24px 80px rgba(79, 70, 229, 0.15);
            animation: fadeInUp 0.55s ease both;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            color: #f8fafc;
            margin: 0.5rem 0;
        }

        .metric-label {
            font-size: 0.9rem;
            color: #94a3b8;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .error-message {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.18), rgba(220, 38, 38, 0.18));
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-radius: 14px;
            padding: 1rem;
            margin: 1rem 0;
            color: #fca5a5;
            font-weight: 500;
            box-shadow: 0 12px 32px rgba(239, 68, 68, 0.12);
        }

        .success-message {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.18), rgba(22, 163, 74, 0.18));
            border: 1px solid rgba(34, 197, 94, 0.45);
            border-radius: 14px;
            padding: 1rem;
            margin: 1rem 0;
            color: #d1fae5;
            font-weight: 500;
            box-shadow: 0 12px 32px rgba(34, 197, 94, 0.12);
        }

        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(99, 102, 241, 0.3);
            border-radius: 50%;
            border-top-color: #a855f7;
            animation: spin 1s ease-in-out infinite;
            margin-right: 0.5rem;
        }

        .help-tooltip {
            position: relative;
            display: inline-block;
            margin-left: 0.5rem;
            cursor: help;
        }

        .help-tooltip .tooltip-text {
            visibility: hidden;
            width: 220px;
            background-color: rgba(4, 7, 20, 0.96);
            color: #e2e8f0;
            text-align: center;
            border-radius: 14px;
            padding: 0.75rem;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -110px;
            opacity: 0;
            transform: translateY(10px);
            transition: opacity 0.3s ease, transform 0.3s ease;
            font-size: 0.82rem;
            line-height: 1.5;
        }

        .help-tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
            transform: translateY(0);
        }

        .stTextInput > div > div > input,
        .stTextInput > div > div > textarea,
        .stSelectbox > div > div > div,
        .stNumberInput > div > div > input,
        .stSlider > div > div {
            background: rgba(15, 23, 42, 0.82) !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(99, 102, 241, 0.26) !important;
        }

        .stTextInput > div > label,
        .stSelectbox > label,
        .stNumberInput > div > label,
        .stSlider > div > label {
            color: #cbd5e1 !important;
        }

        .stMarkdown {
            color: #e2e8f0 !important;
        }

        .stButton > button:focus,
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus {
            outline: 3px solid rgba(124, 58, 237, 0.8);
            outline-offset: 2px;
            box-shadow: 0 0 0 8px rgba(124, 58, 237, 0.18);
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }

        @keyframes slowDrift {
            0% { transform: translate(-10%, 0); }
            50% { transform: translate(-12%, -8%); }
            100% { transform: translate(-10%, 0); }
        }

        @keyframes shimmer {
            100% { left: 120%; }
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.15); }
            50% { box-shadow: 0 0 0 14px rgba(124, 58, 237, 0.03); }
            100% { box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.15); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes textShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @media (max-width: 768px) {
            .header-title { font-size: 2.6rem; }
            .main { padding: 1rem; margin: 0.5rem; }
            .upload-section { padding: 2rem 1.25rem; }
            .clip-card { padding: 1.5rem; }
            .feature-card { padding: 1rem; }
        }
    </style>
""", unsafe_allow_html=True)

# Header section with psychological design
st.markdown("""
    <div class="header-container">
        <div class="header-title">✨ AttentionX</div>
        <div class="header-subtitle">Transform long-form content into viral short-form clips in seconds</div>
    </div>
""", unsafe_allow_html=True)

components.html("""
    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem; flex-wrap: wrap;">
        <div class="feature-card" style="text-align: center; padding: 1rem; border-radius: 12px; border: 1px solid rgba(34, 197, 94, 0.18);">
            <div class="feature-icon">🎯</div>
            <div style="font-weight: 700; color: #22d3ee;">Smart Detection</div>
            <div style="font-size: 0.92rem; color: #cbd5e1;">AI finds viral moments</div>
        </div>
        <div class="feature-card" style="text-align: center; padding: 1rem; border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.18);">
            <div class="feature-icon">⚡</div>
            <div style="font-weight: 700; color: #7c3aed;">Lightning Fast</div>
            <div style="font-size: 0.92rem; color: #cbd5e1;">Process in minutes</div>
        </div>
        <div class="feature-card" style="text-align: center; padding: 1rem; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.18);">
            <div class="feature-icon">📱</div>
            <div style="font-weight: 700; color: #38bdf8;">Multi-Platform</div>
            <div style="font-size: 0.92rem; color: #cbd5e1;">TikTok, Instagram, YouTube</div>
        </div>
        <div class="feature-card" style="text-align: center; padding: 1rem; border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.18);">
            <div class="feature-icon">🚀</div>
            <div style="font-weight: 700; color: #fb7185;">Viral Ready</div>
            <div style="font-size: 0.92rem; color: #cbd5e1;">Optimized for engagement</div>
        </div>
    </div>
""", height=240)

st.markdown("---")

# Advanced Settings Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Advanced Settings")
    
    # Help section at top
    with st.expander("💡 How to Use AttentionX", expanded=False):
        st.markdown("""
        **Step 1:** Upload your long-form video (lecture, podcast, talk)
        **Step 2:** Adjust sensitivity for your content type
        **Step 3:** Choose export format and add branding
        **Step 4:** Generate clips and download for social media
        
        **Pro Tips:**
        - Educational content works best
        - Clear audio = better results
        - Try different sensitivity levels
        - Use watermarks for branding
        """)
    
    num_clips = st.slider(
        "Number of clips to generate",
        min_value=1,
        max_value=10,
        value=4,
        help="More clips = more options, but longer processing time"
    )
    
    min_clip_length = st.slider(
        "Minimum clip length (seconds)",
        min_value=3,
        max_value=15,
        value=5,
        help="Shorter clips for TikTok, longer for YouTube"
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
        help="Higher = more clips, Lower = only best moments"
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
    
    # Troubleshooting section
    with st.expander("🔧 Troubleshooting", expanded=False):
        st.markdown("""
        **No clips found?**
        - Increase sensitivity slider
        - Reduce minimum clip length
        - Check audio quality
        
        **Poor quality clips?**
        - Ensure good lighting in source video
        - Check original video resolution
        - Try different export format
        
        **Processing too slow?**
        - Reduce number of clips
        - Use shorter source video
        - Close other applications
        """)
    st.markdown("### 📊 About")
    st.info("🎯 **AttentionX** helps creators turn long videos into viral clips. Perfect for TikTok, Instagram Reels, and YouTube Shorts!")
    st.markdown("[View on GitHub](https://github.com) • [Report Issue](https://github.com/issues)")

# Upload section with improved UX
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("## 📹 Upload Your Long-Form Video")
st.markdown("Transform lectures, podcasts, or talks into viral short clips in minutes.")

# File upload with validation
video_file = st.file_uploader(
    "Choose a video file (MP4, MOV, MKV, WebM)",
    type=["mp4", "mov", "mkv", "webm"],
    help="Maximum file size: 500MB. Best results with clear audio and dynamic content."
)

# File validation feedback
if video_file is not None:
    file_size = len(video_file.read()) / (1024 * 1024)  # MB
    video_file.seek(0)  # Reset file pointer
    
    if file_size > 500:
        st.markdown('<div class="error-message">⚠️ File size too large (%.1f MB). Please upload a video under 500MB.</div>' % file_size, unsafe_allow_html=True)
        video_file = None
    elif file_size < 10:
        st.markdown('<div class="success-message">✅ File uploaded successfully (%.1f MB)</div>' % file_size, unsafe_allow_html=True)
    else:
        st.info(f"📁 File uploaded: {video_file.name} ({file_size:.1f} MB)")

st.markdown("""
**🎯 Best Practices for Great Results:**
- **Content Type:** Educational talks, interviews, or storytelling work best
- **Audio Quality:** Clear speech with minimal background noise
- **Length:** 10-60 minutes for optimal highlight detection
- **Energy:** Videos with dynamic speaking patterns and emotional content
""")

st.markdown('</div>', unsafe_allow_html=True)

if video_file is not None:
    with st.spinner("Processing your video..."):
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, video_file.name)
        with open(video_path, "wb") as f:
            f.write(video_file.read())

    # Progress tracking system - Visibility of system status
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.markdown("### 📊 Processing Progress")
    
    progress_steps = [
        {"icon": "📹", "title": "Video Uploaded", "description": "File received and validated", "status": "completed"},
        {"icon": "🎯", "title": "AI Analysis", "description": "Transcribing audio with Whisper", "status": "pending"},
        {"icon": "📊", "title": "Content Analysis", "description": "Analyzing energy and sentiment", "status": "pending"},
        {"icon": "✂️", "title": "Clip Generation", "description": "Creating viral short clips", "status": "pending"},
    ]
    
    for i, step in enumerate(progress_steps):
        status_class = "completed" if step["status"] == "completed" else "active" if i == 0 else "pending"
        icon_class = "completed" if step["status"] == "completed" else "active" if i == 0 else "pending"
        
        st.markdown(f'''
            <div class="progress-step {status_class}">
                <div class="step-icon {icon_class}">{step["icon"]}</div>
                <div>
                    <div style="font-weight: 600; color: #1e293b;">{step["title"]}</div>
                    <div style="font-size: 0.9rem; color: #64748b;">{step["description"]}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    st.video(video_path)
    st.markdown('</div>', unsafe_allow_html=True)

    col_analyze, col_spacer = st.columns([1, 4])
    with col_analyze:
        analyze_button = st.button("🚀 Start AI Analysis", use_container_width=True, help="Begin the intelligent clip generation process")

    if analyze_button:
        # Update progress - Step 2 active
        progress_steps[1]["status"] = "active"
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.markdown('<div class="success-message">🎯 Starting AI analysis...</div>', unsafe_allow_html=True)

        with st.spinner("🎯 Transcribing audio with AI..."):
            status_text.markdown('<div class="success-message">🎯 Step 1/3: Transcribing audio with Whisper AI...</div>', unsafe_allow_html=True)
            transcript_text, segments, audio_path = transcribe_video(video_path)
            progress_bar.progress(33)
            time.sleep(0.5)  # Brief pause for visual feedback

        # Update progress - Step 3 active
        progress_steps[2]["status"] = "active"
        
        with st.spinner("📊 Analyzing content patterns..."):
            status_text.markdown('<div class="success-message">📊 Step 2/3: Analyzing audio energy and emotional patterns...</div>', unsafe_allow_html=True)
            energy_times, energy = compute_audio_energy(audio_path)
            progress_bar.progress(66)
            time.sleep(0.5)

        # Update progress - Step 4 active
        progress_steps[3]["status"] = "active"
        
        with st.spinner("✂️ Generating viral clips..."):
            status_text.markdown('<div class="success-message">✂️ Step 3/3: Generating high-impact short clips...</div>', unsafe_allow_html=True)
            
            # Select highlights with improved algorithm
            highlights = select_highlights(segments, energy_times, energy, num_clips)
            progress_bar.progress(100)
            time.sleep(0.5)

        # Success message
        status_text.markdown('<div class="success-message">✅ Analysis complete! Found {} viral moments in your video.</div>'.format(len(highlights)), unsafe_allow_html=True)
        
        # Clear progress bar
        progress_bar.empty()
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

        # Display results with improved UX
        if highlights:
            st.markdown("---")
            st.markdown("## 🎬 Your Viral Clips")
            st.markdown("Found **{} high-impact moments** ready for social media! Each clip is optimized for engagement.".format(len(highlights)))
            
            for idx, highlight in enumerate(highlights, start=1):
                st.markdown(f'<div class="clip-card">', unsafe_allow_html=True)
                
                # Header with rank and sentiment
                col_badge, col_title, col_score = st.columns([0.15, 0.6, 0.25])
                with col_badge:
                    rank_emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "⭐"
                    st.markdown(f'<span class="clip-badge">{rank_emoji}</span>', unsafe_allow_html=True)
                
                with col_title:
                    hook_text = highlight.get("hook", "Engaging moment")
                    st.markdown(f'<div class="clip-title">{hook_text[:50]}...</div>', unsafe_allow_html=True)
                
                with col_score:
                    sentiment_emoji = "🔥" if highlight.get("sentiment", 0) > 0.7 else "⭐"
                    score = highlight["score"]
                    st.markdown(f'<div style="text-align: right;"><div class="metric-value" style="font-size: 1.2rem;">{score:.2f}</div><div class="metric-label">{sentiment_emoji} SCORE</div></div>', unsafe_allow_html=True)

                # Time information
                col_time1, col_time2, col_duration = st.columns(3)
                with col_time1:
                    st.markdown(f'**⏱️ Start:** {highlight["start"]:.1f}s')
                with col_time2:
                    st.markdown(f'**⏹️ End:** {highlight["end"]:.1f}s')
                with col_duration:
                    duration = highlight["end"] - highlight["start"]
                    st.markdown(f'**📏 Length:** {duration:.1f}s')

                # Content preview
                st.markdown(f'**💬 Content:** _{highlight["text"][:100]}..._')

                # Advanced editing section
                with st.expander(f"⚙️ Advanced Editing (Clip {idx})"):
                    st.markdown("**Fine-tune your clip for maximum impact:**")
                    
                    col_edit1, col_edit2 = st.columns(2)
                    with col_edit1:
                        trim_start = st.slider(
                            "Trim start time",
                            min_value=max(0.0, highlight["start"] - 2.0),
                            max_value=min(highlight["end"] - 1.0, highlight["start"] + 2.0),
                            value=float(highlight["start"]),
                            step=0.5,
                            key=f"trim_start_{idx}",
                            help="Adjust where the clip begins"
                        )
                    
                    with col_edit2:
                        trim_end = st.slider(
                            "Trim end time", 
                            min_value=max(highlight["start"] + 1.0, highlight["end"] - 2.0),
                            max_value=highlight["end"] + 2.0,
                            value=float(highlight["end"]),
                            step=0.5,
                            key=f"trim_end_{idx}",
                            help="Adjust where the clip ends"
                        )
                    
                    speed_options = {"Normal (1x)": 1.0, "Slower (0.8x)": 0.8, "Faster (1.2x)": 1.2, "Very Fast (1.5x)": 1.5}
                    selected_speed = st.selectbox(
                        "Playback speed",
                        list(speed_options.keys()),
                        index=0,
                        key=f"speed_{idx}",
                        help="Adjust speed for different platforms"
                    )
                    speed_factor = speed_options[selected_speed]

                # Generate clip with user settings
                clip_path = os.path.join(temp_dir, f"clip_{idx}.mp4")
                with st.spinner(f"🎬 Rendering clip {idx}..."):
                    try:
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
                        
                        # Display video
                        st.video(clip_path)
                        
                        # Download options
                        st.markdown("### 💾 Download Options")
                        col_download1, col_download2, col_download3 = st.columns(3)
                        
                        with col_download1:
                            with open(clip_path, "rb") as clip_file:
                                st.download_button(
                                    label=f"⬇️ {export_format}",
                                    data=clip_file,
                                    file_name=f"attentionx_clip_{idx}_{export_format.replace(' ', '_')}.mp4",
                                    mime="video/mp4",
                                    use_container_width=True,
                                    key=f"download_{idx}_main"
                                )
                        
                        # Alternative formats
                        alt_formats = [f for f in EXPORT_FORMATS.keys() if f != export_format][:2]
                        for i, alt_fmt in enumerate(alt_formats):
                            with col_download2 if i == 0 else col_download3:
                                clip_path_alt = os.path.join(temp_dir, f"clip_{idx}_alt_{i}.mp4")
                                if st.button(f"Generate {alt_fmt}", key=f"gen_alt_{idx}_{i}"):
                                    with st.spinner(f"Creating {alt_fmt} version..."):
                                        generate_clip_with_format(
                                            video_path,
                                            {**highlight, "start": trim_start, "end": trim_end},
                                            clip_path_alt,
                                            format_name=alt_fmt,
                                            watermark_text=watermark_text if watermark_text else None
                                        )
                                        with open(clip_path_alt, "rb") as cf:
                                            st.download_button(
                                                label=f"⬇️ {alt_fmt}",
                                                data=cf,
                                                file_name=f"attentionx_clip_{idx}_{alt_fmt.replace(' ', '_')}.mp4",
                                                mime="video/mp4",
                                                use_container_width=True,
                                                key=f"download_{idx}_alt_{i}"
                                            )
                        
                    except Exception as e:
                        st.markdown(f'<div class="error-message">❌ Error generating clip {idx}: {str(e)}</div>', unsafe_allow_html=True)
                        st.button("🔄 Retry", key=f"retry_{idx}")

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
            
            # Enhanced Analytics Dashboard
            st.markdown("## 📈 Performance Analytics")
            st.markdown("Track your content's viral potential and optimization metrics.")
            
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                video_duration = highlights[-1]["end"] if highlights else 0
                st.markdown(f'<div class="metric-value">{video_duration:.0f}s</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">VIDEO LENGTH</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_b:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{len(highlights)}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">CLIPS GENERATED</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_c:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                avg_score = sum(h["score"] for h in highlights) / len(highlights) if highlights else 0
                st.markdown(f'<div class="metric-value">{avg_score:.2f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">AVG VIRAL SCORE</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_d:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                total_clip_time = sum(h["end"] - h["start"] for h in highlights)
                st.markdown(f'<div class="metric-value">{total_clip_time:.0f}s</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">TOTAL CLIP TIME</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Help and tips section
            st.markdown("---")
            st.markdown("## 💡 Pro Tips for Maximum Engagement")
            
            tips_col1, tips_col2 = st.columns(2)
            with tips_col1:
                st.markdown("""
                **🎯 Content Strategy:**
                - Post during peak hours (6-9 PM local time)
                - Use trending hashtags in your caption
                - Engage with comments within first hour
                - Cross-post to multiple platforms
                
                **📱 Platform Optimization:**
                - TikTok: 15-60 seconds, vertical format
                - Instagram: 15-90 seconds, square or vertical
                - YouTube: 15-60 seconds, horizontal preferred
                """)
                
            with tips_col2:
                st.markdown("""
                **🚀 Viral Hooks:**
                - Start with questions or surprising facts
                - Use emotional language (amazing, shocking, incredible)
                - Keep first 3 seconds attention-grabbing
                - End with call-to-action
                
                **📊 Analytics Tracking:**
                - Monitor views, likes, shares, and comments
                - A/B test different hooks and thumbnails
                - Track which clips perform best
                - Adjust future content based on data
                """)

            st.markdown("---")
            st.success("🎉 **Ready to go viral!** Download your clips and share them across social media platforms.")
            
        else:
            st.markdown('<div class="error-message">⚠️ No highlights detected in this video. Try adjusting the sensitivity settings or upload a different video with more dynamic content.</div>', unsafe_allow_html=True)
            
            with st.expander("🔧 Troubleshooting Tips"):
                st.markdown("""
                **If no clips were found:**
                - **Increase sensitivity** in the sidebar (try 0.8+)
                - **Reduce minimum clip length** (try 3-5 seconds)
                - **Check audio quality** - ensure clear speech
                - **Try different content** - videos with conversations work best
                
                **For better results:**
                - Videos with emotional content (excitement, surprise)
                - Clear speech and good audio quality
                - Dynamic energy changes (pauses, emphasis)
                - Educational or storytelling content
                """)
            st.success("🚀 **Share your results** — Tag @AttentionX to be featured!")

