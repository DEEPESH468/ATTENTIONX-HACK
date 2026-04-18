# AttentionX — Automated Content Repurposing Engine

AttentionX turns long-form mentorship videos into snackable, shareable short-form clips using multimodal analysis, smart cropping, and caption generation.

## What this prototype does

- Upload a long-form lecture or talk video
- Transcribe the audio using Whisper
- Detect audio energy peaks and speaker sentiment indicators
- Identify candidate short clips from the transcript and audio spikes
- Use face detection to crop to vertical (9:16) output for Reels/TikTok
- Render timed captions and hook headlines for each clip
- Preview clips and download repurposed videos

## Tech stack

- Python 3.11+
- Streamlit for the web UI
- MoviePy for video editing and export
- OpenAI Whisper for speech-to-text
- SoundFile for audio analysis
- OpenCV for face detection and smart crop
- NumPy + SciPy for signal processing
- PIL for image manipulation

## Features

✨ **AI-Powered Highlight Detection** — Audio energy + sentiment analysis + keyword scoring
🎯 **Auto-Generated Hooks** — Viral captions like "Wait, you NEED to hear this..."
🎬 **Vertical Smart Crop** — Automatically centers speaker for TikTok/Reels
📝 **Dynamic Captions** — Auto-wrapped, high-contrast overlays
⭐ **Viral Scoring** — Multi-factor scoring for clip virality
🚀 **Batch Processing** — Generate multiple clips in one go

### 🎥 Advanced Features

🎞️ **Multi-Format Export** — TikTok (1080x1920), Instagram Reels, YouTube Shorts presets
🏷️ **Custom Watermarks** — Add branding/watermark text to every clip
✂️ **Clip Editor** — Trim clips, adjust playback speed (0.5x - 2x)
🎯 **A/B Testing Console** — Compare hook variants and track CTR performance
📊 **Performance Analytics** — Track clips generated, viral scores, total processing time
🌟 **Sentiment Analysis** — Detects emotional keywords for better clip ranking

## Getting started

1. Clone this repository:

```bash
mkdir attentionx-ai-hack && cd attentionx-ai-hack
# copy repo files into this folder
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the app from the same activated environment:

```bash
streamlit run app.py
```

If you see `ModuleNotFoundError` for `soundfile` or another package, it means Streamlit is launching from a different Python environment. In that case run:

```bash
source .venv/bin/activate
.venv/bin/streamlit run app.py
```

Alternatively, use the helper script:

```bash
./run.sh
```

4. Open the browser link, upload a long-form video, and generate clips.

## Notes

- For faster transcription, install a Whisper model such as `base.en` or `small`.
- If you want API transcription instead, replace the local whisper call with OpenAI Speech-to-Text.
- Hosting this prototype on Streamlit Cloud or Hugging Face Spaces gives extra evaluation credit.

## Demo video

Add your YouTube or Google Drive recording link here after you record the project demo.

## Submission checklist

- [ ] Public GitHub repository
- [ ] README with setup and demo link
- [ ] Working Streamlit prototype
- [ ] Sample video upload and clip extraction
