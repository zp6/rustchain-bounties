# RustChain Bounty #446 — Upload 5 Original Videos to BoTTube

**Bounty:** #446 — Upload 5 Original Videos to BoTTube (25 RTC)  
**Submitter:** zp6  
**Wallet:** zp6  
**Date:** 2025-05-15

## Overview

This submission provides a complete Python toolkit for generating and uploading 5 original educational videos about RustChain to BoTTube.

## 📁 Files

| File | Description |
|------|-------------|
| `uploader.py` | BoTTube API client with batch upload, retry logic, and progress tracking |
| `video_generator.py` | PIL/Pillow-based slideshow video generator with crossfade transitions |
| `generate_videos.py` | Main script that generates all 5 RustChain videos and optionally uploads them |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## 🎬 The 5 Videos

1. **RustChain Proof of Antiquity Explained** — Overview of the PoA consensus mechanism
2. **How Blockchain Mining Works Without GPUs** — CPU-based verification explained
3. **Building on RustChain: Developer Guide** — SDK, smart contracts, and deployment
4. **Hardware Attestation for Security** — TPM/TEE and node verification
5. **RustChain vs Traditional Mining** — Side-by-side comparison with PoW

Each video features:
- Custom color themes per topic
- Animated crossfade transitions between slides
- Educational content with key bullet points
- 1280×720 HD resolution at 24fps
- ~25 seconds per video (5 slides × 5 seconds)

## 🚀 Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Generate Videos Only

```bash
python generate_videos.py
```

Videos will be saved to `output_videos/`.

### Generate & Upload to BoTTube

```bash
export BOTTUBE_API_KEY="your-api-key"
python generate_videos.py --upload
```

### Upload Pre-existing Videos

```bash
# Single video
python uploader.py video.mp4 --title "My Video" --description "Desc" --tags tag1 tag2

# Batch upload from JSON config
python uploader.py --json batch_config.json
```

## 🛠 Architecture

### uploader.py — BoTTube API Client

- **Two-step upload**: Init → Upload (with fallback to direct multipart)
- **Batch upload** with configurable retry logic (exponential backoff)
- **Progress tracking** via tqdm and JSON result files
- **Health check** endpoint verification
- **Configurable**: API key via env var, constructor, or CLI arg

### video_generator.py — Video Generation Engine

- **Slide-based**: Define slides with title, subtitle, body text, colors
- **Crossfade transitions**: Smooth blending between slides
- **Multi-format output**: MP4 (via ffmpeg), GIF fallback, raw RGB
- **Customizable**: Resolution, FPS, slide duration, fonts, colors
- **No GPU required**: Pure PIL/Pillow rendering

### generate_videos.py — Orchestration

- Defines all 5 videos with carefully crafted educational content
- Generates thumbnails from first slide of each video
- Saves structured metadata (JSON) for each video
- Optional upload step via `--upload` flag

## 📋 Requirements

- Python 3.10+
- Pillow (PIL) — image rendering
- requests — API communication
- tqdm — progress bars
- Optional: ffmpeg — for MP4 encoding (falls back to GIF)

## 📝 License

All code is original. Videos are educational content about RustChain, created for bounty #446.

## 🔗 Links

- BoTTube: https://bottube.ai
- RustChain: https://rustchain.io
