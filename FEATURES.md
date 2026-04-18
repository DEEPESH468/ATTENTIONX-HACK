# AttentionX — Complete Feature List

## Core Features (MVP)

### 1. **Automated Highlight Detection**
- Speech-to-text transcription via OpenAI Whisper
- Audio energy analysis (RMS-based peak detection)
- Sentiment scoring using keyword analysis
- Multi-factor scoring algorithm:
  - Audio energy: 50%
  - Keyword relevance: 30%
  - Emotional sentiment: 15%
  - Ideal length: 5%

### 2. **Smart Vertical Cropping**
- OpenCV Haar cascade face detection
- Automatic speaker centering for 9:16 aspect ratio
- Perfect for TikTok/Instagram Reels/YouTube Shorts

### 3. **Automatic Hook Generation**
- Context-aware viral captions
- Patterns: "Wait, you NEED to hear this...", "This will BLOW YOUR MIND 🤯", etc.
- Fallback for moment descriptions

### 4. **Dynamic Caption Overlay**
- Auto-wrapped text with optimal line breaks
- High-contrast white text on semi-transparent black background
- Positioned at bottom of video for viewer comfort

### 5. **Batch Clip Generation**
- Generate 1-10 clips in single processing pass
- Rank clips by virality score (🥇🥈🥉⭐)
- Configurable minimum/maximum clip length

---

## Advanced Features (NEW)

### 6. **Multi-Format Export Presets**
**Supported platforms:**
- 🎬 **TikTok**: 1080×1920 @ 30fps (ultrafast preset)
- 📱 **Instagram Reels**: 1080×1920 @ 30fps (ultrafast preset)
- ▶️ **YouTube Shorts**: 1080×1920 @ 30fps (fast preset)
- 🖥️ **Landscape**: 1920×1080 @ 24fps (fast preset)

**Implementation:**
- Format-specific resolution and FPS optimization
- One-click export to any platform
- Alternative format generation with same clip

### 7. **Custom Watermarks/Branding**
- Text watermark overlay (top-left positioned)
- Add creator name, brand, or social handle
- Applied to all generated clips
- Non-intrusive design with transparency

**Usage:**
- Sidebar input: "@YourName" or "YourBrand"
- Automatically applied to all exports
- Customizable per session

### 8. **Interactive Clip Editor**
- **Trim Control**: Adjust clip start/end times
- **Speed Adjustment**: Playback speed 0.5x to 2.0x
  - 0.5x = slow motion
  - 1.0x = normal
  - 2.0x = fast forward
- **Expandable UI**: Edit panel under each clip

**Workflow:**
1. Generate initial clips
2. Expand "Edit Clip X"
3. Adjust trim start/end and speed
4. Re-render with changes
5. Download edited version

### 9. **A/B Testing Console**
- Compare two hook variants side-by-side
- Track engagement metrics:
  - Views per hook
  - Clicks per hook
  - CTR (Click-Through Rate)
- Winner determination based on CTR
- Input fields for real social media data

**Metrics Displayed:**
- **Winner**: Hook A 🏆 / Hook B 🏆 / Tie 🤝
- **Hook A CTR**: Percentage of clicks / views
- **Hook B CTR**: Percentage of clicks / views

### 10. **Performance Analytics Dashboard**
**Metrics tracked:**
- 📹 **Video Duration**: Total input video length
- ✂️ **Clips Generated**: Count of clips created
- ⭐ **Avg Viral Score**: Average highlight score
- 🎬 **Total Clip Time**: Sum of all clip durations

**Use cases:**
- Understand content quality
- Compare performance across videos
- Benchmark viral potential

### 11. **Sentiment Analysis**
**Keyword-based detection:**
- **Positive emotions** (boost scoring):
  - amazing, awesome, love, perfect, incredible, fantastic
  - good, great, wonderful, beautiful, excellent
- **Negative/dramatic** (also boost scoring):
  - shocking, surprising, unexpected, wow, unbelievable
  - mind-blowing, crazy, insane

**Scoring impact:**
- Sentiment keywords increase highlight score by 15%
- Displayed as emotion emoji (🔥 for high sentiment)
- Helps identify emotionally resonant moments

### 12. **Session Settings Panel**
**Configurable parameters:**
- **Num Clips** (1-10): How many clips to generate
- **Min Clip Length** (3-15 sec): Shorter is better for shorts
- **Max Clip Length** (10-60 sec): Platform-dependent
- **Sensitivity** (0.3-1.0): How selective about highlights
  - 0.3 = aggressive (more clips)
  - 1.0 = strict (only top moments)
- **Export Format**: TikTok / Reels / YouTube Shorts / Landscape
- **Watermark Text**: Custom branding
- **A/B Testing**: Toggle on/off

---

## Technical Implementation

### New Functions in `video_processor.py`

```python
# Multi-format export
generate_clip_with_format(video_path, highlight, output_path, format_name, watermark_text)

# Watermarking
add_watermark(video_path, output_path, watermark_text)

# Clip editing
trim_clip(video_path, output_path, start_time, end_time)
adjust_speed(video_path, output_path, speed_factor)

# Format presets dictionary
EXPORT_FORMATS = {
    "TikTok": {"size": (1080, 1920), "fps": 30, "preset": "ultrafast"},
    "Instagram Reels": {"size": (1080, 1920), "fps": 30, "preset": "ultrafast"},
    "YouTube Shorts": {"size": (1080, 1920), "fps": 30, "preset": "fast"},
    "Landscape": {"size": (1920, 1080), "fps": 24, "preset": "fast"},
}
```

### Enhanced UI Components in `app.py`

1. **Sidebar Advanced Settings**
   - Sliders for all numeric parameters
   - Selectbox for format presets
   - Text input for watermark
   - Checkbox for A/B testing

2. **Clip Editor Expanders**
   - Trim start/end inputs per clip
   - Speed adjustment slider
   - Re-render button

3. **A/B Testing Console**
   - Side-by-side hook comparison
   - Metrics input fields
   - Winner calculation and display

4. **Analytics Metrics**
   - 4-column metric display
   - Real-time calculations
   - User-friendly formatting

---

## Dependencies & Versions

```
streamlit==1.26.0
moviepy==2.2.1
soundfile==0.12.1
opencv-python==4.9.0.80
numpy==1.26.4
scipy==1.11.3
torch==2.2.0
whisper==1.1.10
Pillow==9.5.0
```

---

## Usage Flow

### Basic Workflow
1. Upload long-form video (MP4/MOV/MKV)
2. Adjust settings in sidebar (optional)
3. Click "🚀 Analyze & Generate Clips"
4. Review generated clips with scores
5. Download in desired format

### Advanced Workflow
1. Generate clips with default settings
2. Expand clip editor to trim or adjust speed
3. Re-render with new parameters
4. Enable A/B testing for hook comparison
5. Export multiple formats for A/B test
6. Track metrics in analytics dashboard

---

## Hackathon Scoring Impact

### Innovation (20%)
- ✅ Multi-format export for all platforms
- ✅ Interactive clip editor (trim + speed)
- ✅ A/B testing console for data-driven decisions
- ✅ Custom watermarking system

### Technical Execution (20%)
- ✅ Modular functions for each feature
- ✅ Error handling and fallbacks
- ✅ Optimized for Python 3.12
- ✅ Comprehensive feature set

### UX (25%)
- ✅ Professional gradient-based UI
- ✅ Intuitive sidebar settings
- ✅ Clear progress indicators
- ✅ Expandable edit panels
- ✅ Real-time analytics

### Impact (20%)
- ✅ Solves real creator workflow problem
- ✅ Supports all major short-form platforms
- ✅ Enables data-driven content decisions
- ✅ Accelerates content repurposing

---

## Future Enhancement Ideas

- 🎵 Background music integration (royalty-free library)
- 🤖 ML model fine-tuning on user feedback
- 🔗 Direct social media API integration (TikTok/Instagram upload)
- 📈 Trending keyword database for better hook generation
- 🎨 Effect library (transitions, filters, animations)
- 👥 Multi-user collaboration and team workspaces
- 💾 Project save/load functionality
- 🌐 Cloud storage integration (Google Drive, Dropbox)

