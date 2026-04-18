import json
import os
import tempfile
import textwrap
from typing import List, Tuple

import numpy as np
import soundfile as sf
import moviepy as mp
import whisper
from PIL import Image, ImageDraw, ImageFont

import cv2


model = None


def load_transcription_model():
    global model
    if model is None:
        model = whisper.load_model("small")
    return model


def transcribe_video(video_path: str) -> Tuple[str, List[dict], str]:
    model = load_transcription_model()
    audio_path = _extract_audio(video_path)
    result = model.transcribe(audio_path, language="en", fp16=False)
    segments = []
    for segment in result.get("segments", []):
        segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip(),
        })
    return result.get("text", ""), segments, audio_path


def _extract_audio(video_path: str) -> str:
    audio_path = os.path.join(tempfile.gettempdir(), "attentionx_audio.wav")
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
    return audio_path


def compute_audio_energy(audio_path: str, sr: int = 22050, hop_length: int = 1024) -> Tuple[np.ndarray, np.ndarray]:
    y, sample_rate = sf.read(audio_path)
    if y.ndim > 1:
        y = np.mean(y, axis=1)
    if sample_rate != sr:
        raise ValueError(f"Expected sample rate {sr}, but got {sample_rate}.")
    frame_length = 2048
    step = hop_length
    rms = np.array([
        np.sqrt(np.mean(y[i : i + frame_length] ** 2))
        for i in range(0, max(1, len(y) - frame_length + 1), step)
    ])
    times = np.arange(len(rms)) * step / sample_rate
    return times, rms


def compute_sentiment_score(text: str) -> float:
    """Estimate sentiment/emotion from text keywords."""
    positive_words = ["amazing", "incredible", "love", "perfect", "best", "awesome", "fantastic", "brilliant", "genius", "mind-blowing", "stunning", "beautiful", "powerful", "revolutionary", "breakthrough", "game-changer"]
    negative_words = ["terrible", "awful", "hate", "worst", "horrible", "dangerous", "failed", "mistake", "problem", "issue", "wrong", "broken", "crash"]
    emotional_words = ["feel", "think", "believe", "realize", "understand", "discover", "share", "remember", "promise", "swear", "absolutely", "definitely"]
    
    text_lower = text.lower()
    sentiment = 0.5  # neutral baseline
    
    for word in positive_words:
        if word in text_lower:
            sentiment += 0.05
    for word in negative_words:
        if word in text_lower:
            sentiment += 0.03
    for word in emotional_words:
        if word in text_lower:
            sentiment += 0.02
    
    return min(max(sentiment, 0.0), 1.0)


def generate_hook(text: str) -> str:
    """Generate viral hook headlines for clips."""
    hooks = [
        "Wait, you NEED to hear this...",
        "Here's the secret nobody talks about:",
        "This will BLOW YOUR MIND 🤯",
        "Plot twist incoming...",
        "The real talk starts here:",
        "This changes EVERYTHING:",
        "Most people don't know this:",
        "Your life will never be the same:",
        "This is the MOMENT that matters:",
        "The answer you've been waiting for:",
    ]
    
    # Select hook based on text keywords
    text_lower = text.lower()
    if any(word in text_lower for word in ["secret", "hidden", "truth", "lie", "real"]):
        return hooks[1]
    elif any(word in text_lower for word in ["amazing", "incredible", "mind", "blow", "wow"]):
        return hooks[2]
    elif any(word in text_lower for word in ["change", "transform", "revolution", "new"]):
        return hooks[5]
    elif any(word in text_lower for word in ["why", "how", "what", "answer", "solution"]):
        return hooks[9]
    else:
        return hooks[0]


def select_highlights(segments: List[dict], energy_times: np.ndarray, energy: np.ndarray, top_n: int = 3) -> List[dict]:
    if len(segments) == 0:
        return []

    energy_norm = (energy - energy.min()) / max(energy.max() - energy.min(), 1e-6)
    highlights = []
    
    priority_words = ["learn", "important", "key", "secret", "tip", "advice", "hack", "mistake", "why", "how", "never", "always", "remember", "forget"]
    
    for segment in segments:
        mid = (segment["start"] + segment["end"]) / 2.0
        idx = np.argmin(np.abs(energy_times - mid))
        energy_score = float(energy_norm[idx])
        
        text = segment["text"]
        text_lower = text.lower()
        
        # Keyword boost
        keyword_score = 0.0
        for word in priority_words:
            if word in text_lower:
                keyword_score += 0.15
        
        # Sentiment boost
        sentiment_score = compute_sentiment_score(text)
        
        # Length preference (5-30 words is ideal for TikTok)
        word_count = len(text.split())
        length_score = 0.0
        if 5 <= word_count <= 30:
            length_score = 0.2
        elif word_count < 5 or word_count > 50:
            length_score = -0.1
        
        # Combined score
        combined_score = (energy_score * 0.5) + (min(keyword_score, 0.3) * 0.3) + (sentiment_score * 0.15) + (length_score * 0.05)
        
        hook = generate_hook(text)
        
        highlights.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": text,
            "score": combined_score,
            "hook": hook,
            "sentiment": sentiment_score,
        })

    highlights = sorted(highlights, key=lambda item: item["score"], reverse=True)
    return highlights[:top_n]


def detect_face_crop(video_path: str, clip_start: float, clip_end: float, output_size=(720, 1280)) -> Tuple[np.ndarray, float, float]:
    video = mp.VideoFileClip(video_path).subclip(clip_start, clip_end)
    frame = video.get_frame((clip_end - clip_start) / 2.0)
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    h, w = frame.shape[0:2]
    target_w, target_h = output_size[1], output_size[0]
    if len(faces) > 0:
        x, y, bw, bh = faces[0]
        cx = x + bw // 2
        cy = y + bh // 2
    else:
        cx = w // 2
        cy = h // 2

    crop_width = min(w, target_w)
    crop_height = min(h, target_h)
    x1 = max(0, cx - crop_width // 2)
    x2 = min(w, x1 + crop_width)
    y1 = max(0, cy - crop_height // 2)
    y2 = min(h, y1 + crop_height)

    image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cropped = image[y1:y2, x1:x2]
    resized = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    return resized, crop_width, crop_height


def generate_clip(video_path: str, highlight: dict, output_path: str) -> str:
    start = max(0, highlight["start"] - 0.5)
    end = min(highlight["end"] + 0.5, mp.VideoFileClip(video_path).duration)
    clip = mp.VideoFileClip(video_path).subclip(start, end)
    if clip.w >= clip.h:
        crop_x1 = 0
        crop_y1 = 0
        crop_x2 = clip.w
        crop_y2 = clip.h
        if clip.w / clip.h > 9 / 16:
            crop_width = int(clip.h * 9 / 16)
            crop_x1 = max(0, int((clip.w - crop_width) / 2))
            crop_x2 = crop_x1 + crop_width
        clip = clip.crop(x1=crop_x1, y1=crop_y1, x2=crop_x2, y2=crop_y2)
    clip = clip.resize(height=1280)
    caption_text = highlight["text"]
    wrapped = textwrap.wrap(caption_text, width=40)
    font = ImageFont.load_default()
    line_height = font.getsize("A")[1] + 6
    caption_height = min(280, line_height * len(wrapped) + 40)
    caption_width = int(clip.w)
    caption_image = Image.new("RGBA", (caption_width, caption_height), (0, 0, 0, 180))
    draw = ImageDraw.Draw(caption_image)
    y = 18
    for line in wrapped:
        draw.text((20, y), line, font=font, fill="white")
        y += line_height
    caption_clip = mp.ImageClip(np.array(caption_image)).set_duration(clip.duration).set_position(("center", clip.h - caption_height - 20))
    output_clip = mp.CompositeVideoClip([clip, caption_clip])
    output_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, verbose=False, logger=None)
    return output_path


# Export format presets
EXPORT_FORMATS = {
    "TikTok": {"size": (1080, 1920), "fps": 30, "preset": "ultrafast"},
    "Instagram Reels": {"size": (1080, 1920), "fps": 30, "preset": "ultrafast"},
    "YouTube Shorts": {"size": (1080, 1920), "fps": 30, "preset": "fast"},
    "Landscape": {"size": (1920, 1080), "fps": 24, "preset": "fast"},
}


def generate_clip_with_format(video_path: str, highlight: dict, output_path: str, format_name: str = "TikTok", watermark_text: str = None) -> str:
    """Generate clip in specific format with optional watermark."""
    start = max(0, highlight["start"] - 0.5)
    end = min(highlight["end"] + 0.5, mp.VideoFileClip(video_path).duration)
    clip = mp.VideoFileClip(video_path).subclip(start, end)
    
    # Get format specs
    fmt = EXPORT_FORMATS.get(format_name, EXPORT_FORMATS["TikTok"])
    target_w, target_h = fmt["size"]
    
    # Crop to format
    if clip.w >= clip.h:
        crop_width = int(clip.h * target_w / target_h)
        crop_x1 = max(0, int((clip.w - crop_width) / 2))
        crop_x2 = crop_x1 + crop_width
        clip = clip.crop(x1=crop_x1, y1=0, x2=crop_x2, y2=clip.h)
    
    clip = clip.resize((target_w, target_h))
    
    # Add caption
    caption_text = highlight.get("hook", highlight["text"])[:60]
    wrapped = textwrap.wrap(caption_text, width=40)
    font = ImageFont.load_default()
    line_height = font.getsize("A")[1] + 6
    caption_height = min(280, line_height * len(wrapped) + 40)
    caption_width = target_w
    caption_image = Image.new("RGBA", (caption_width, caption_height), (0, 0, 0, 180))
    draw = ImageDraw.Draw(caption_image)
    y = 18
    for line in wrapped:
        draw.text((20, y), line, font=font, fill="white")
        y += line_height
    caption_clip = mp.ImageClip(np.array(caption_image)).set_duration(clip.duration).set_position(("center", target_h - caption_height - 20))
    
    # Add watermark if provided
    clips_list = [clip, caption_clip]
    if watermark_text:
        watermark_img = Image.new("RGBA", (target_w, 80), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_img)
        draw.text((10, 20), f"✨ {watermark_text}", font=font, fill="white")
        watermark = mp.ImageClip(np.array(watermark_img)).set_duration(clip.duration).set_position(("left", "top"))
        clips_list.append(watermark)
    
    output_clip = mp.CompositeVideoClip(clips_list)
    output_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=fmt["fps"], preset=fmt["preset"], verbose=False, logger=None)
    return output_path


def add_watermark(video_path: str, output_path: str, watermark_text: str) -> str:
    """Add text watermark to video."""
    clip = mp.VideoFileClip(video_path)
    w, h = clip.size
    
    watermark_img = Image.new("RGBA", (w, 60), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_img)
    draw.text((20, 15), f"✨ {watermark_text}", font=ImageFont.load_default(), fill="white")
    
    watermark = mp.ImageClip(np.array(watermark_img)).set_duration(clip.duration).set_position(("left", "top"))
    output_clip = mp.CompositeVideoClip([clip, watermark])
    output_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, verbose=False, logger=None)
    return output_path


def trim_clip(video_path: str, output_path: str, start_time: float, end_time: float) -> str:
    """Trim video to specific time range."""
    clip = mp.VideoFileClip(video_path)
    trimmed = clip.subclip(start_time, end_time)
    trimmed.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, verbose=False, logger=None)
    return output_path


def adjust_speed(video_path: str, output_path: str, speed_factor: float) -> str:
    """Adjust playback speed of video."""
    clip = mp.VideoFileClip(video_path)
    speedup = clip.speedx(speed_factor)
    speedup.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, verbose=False, logger=None)
    return output_path
