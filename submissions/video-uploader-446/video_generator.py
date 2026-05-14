"""
Video Generator — Generate simple animated videos using PIL/Pillow.
Creates slide-show style videos with text overlays and colored backgrounds.
Outputs raw frame data that can be encoded to MP4.
"""

import os
import math
import struct
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Default dimensions
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 24
DEFAULT_DURATION = 15  # seconds


@dataclass
class Slide:
    """A single slide in a video."""
    title: str
    subtitle: str = ""
    body_lines: list[str] = None
    bg_color: tuple = (20, 30, 48)       # Dark blue
    title_color: tuple = (255, 255, 255)
    subtitle_color: tuple = (100, 200, 255)
    body_color: tuple = (200, 210, 220)
    accent_color: tuple = (255, 165, 0)  # Orange accent

    def __post_init__(self):
        if self.body_lines is None:
            self.body_lines = []


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a font, falling back to default if needed."""
    font_names = [
        "arial.ttf",
        "Arial.ttf",
        "Arial Bold.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple,
    width: int = DEFAULT_WIDTH,
):
    """Draw horizontally centered text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = (width - text_w) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_accent_line(draw: ImageDraw.ImageDraw, y: int, width: int, color: tuple, thickness: int = 3):
    """Draw a centered accent line."""
    line_w = min(width // 3, 300)
    x1 = (width - line_w) // 2
    x2 = x1 + line_w
    draw.rectangle([x1, y, x2, y + thickness], fill=color)


def create_slide_image(
    slide: Slide,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> Image.Image:
    """Render a single slide as a PIL Image."""
    img = Image.new("RGB", (width, height), slide.bg_color)
    draw = ImageDraw.Draw(img)

    # Decorative top bar
    draw.rectangle([0, 0, width, 6], fill=slide.accent_color)

    # Title
    title_font = _get_font(52, bold=True)
    _draw_centered_text(draw, slide.title, 80, title_font, slide.title_color, width)

    # Accent line under title
    _draw_accent_line(draw, 150, width, slide.accent_color, 4)

    # Subtitle
    if slide.subtitle:
        sub_font = _get_font(30)
        _draw_centered_text(draw, slide.subtitle, 180, sub_font, slide.subtitle_color, width)

    # Body lines
    if slide.body_lines:
        body_font = _get_font(24)
        y_start = 260 if slide.subtitle else 200
        for i, line in enumerate(slide.body_lines):
            y = y_start + i * 45
            if y > height - 80:
                break
            _draw_centered_text(draw, line, y, body_font, slide.body_color, width)

    # Bottom bar
    draw.rectangle([0, height - 6, width, height], fill=slide.accent_color)

    return img


def generate_frames(
    slides: list[Slide],
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: int = DEFAULT_FPS,
    slide_duration: float = 5.0,
    transition_frames: int = 12,
) -> list[Image.Image]:
    """
    Generate all frames for a slideshow video with crossfade transitions.

    Returns:
        List of PIL Images (frames)
    """
    frames = []
    frames_per_slide = int(fps * slide_duration)

    for idx, slide in enumerate(slides):
        slide_img = create_slide_image(slide, width, height)

        # Static frames for the slide
        for _ in range(frames_per_slide - transition_frames):
            frames.append(slide_img.copy())

        # Crossfade transition to next slide
        if idx < len(slides) - 1:
            next_img = create_slide_image(slides[idx + 1], width, height)
            for t in range(transition_frames):
                alpha = t / transition_frames
                blended = Image.blend(slide_img, next_img, alpha)
                frames.append(blended)

    return frames


def frames_to_raw_video(frames: list[Image.Image], output_path: str, fps: int = DEFAULT_FPS):
    """
    Write frames as raw RGB data to a file.
    NOTE: This produces uncompressed raw video. For MP4, use frames_to_mp4 instead.
    """
    with open(output_path, "wb") as f:
        for frame in frames:
            f.write(frame.tobytes())
    logger.info(f"Raw video written to {output_path} ({len(frames)} frames)")


def frames_to_mp4(frames: list[Image.Image], output_path: str, fps: int = DEFAULT_FPS) -> bool:
    """
    Encode frames to MP4 using available system tools.
    Tries ffmpeg first, then falls back to raw output.
    """
    raw_path = output_path + ".raw"
    frames_to_raw_video(frames, raw_path, fps)

    w, h = frames[0].size if frames else (DEFAULT_WIDTH, DEFAULT_HEIGHT)

    # Try ffmpeg
    import subprocess
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{w}x{h}",
            "-r", str(fps),
            "-i", raw_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            os.remove(raw_path)
            logger.info(f"MP4 encoded: {output_path}")
            return True
        else:
            logger.warning(f"ffmpeg failed: {result.stderr[:200]}")
    except FileNotFoundError:
        logger.warning("ffmpeg not found, trying alternative encoding")
    except subprocess.TimeoutExpired:
        logger.warning("ffmpeg timed out")

    # Fallback: write as GIF (universal compatibility)
    gif_path = output_path.replace(".mp4", ".gif")
    try:
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=int(1000 / fps),
            loop=0,
            optimize=True,
        )
        logger.info(f"GIF saved as fallback: {gif_path}")
        os.remove(raw_path)
        return True
    except Exception as e:
        logger.error(f"GIF fallback failed: {e}")
        return False


def generate_video(
    slides: list[Slide],
    output_path: str = "output.mp4",
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: int = DEFAULT_FPS,
    slide_duration: float = 5.0,
) -> str:
    """
    High-level function: generate a slideshow video from slides.

    Args:
        slides: List of Slide objects
        output_path: Output file path
        width: Video width
        height: Video height
        fps: Frames per second
        slide_duration: Duration per slide in seconds

    Returns:
        Path to the generated video file
    """
    logger.info(f"Generating video with {len(slides)} slides...")
    frames = generate_frames(slides, width, height, fps, slide_duration)
    logger.info(f"Generated {len(frames)} frames")

    success = frames_to_mp4(frames, output_path, fps)
    if success:
        return output_path
    else:
        # Return raw file as last resort
        raw_path = output_path.replace(".mp4", ".raw")
        frames_to_raw_video(frames, raw_path, fps)
        return raw_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Demo: generate a sample video
    demo_slides = [
        Slide(title="Welcome", subtitle="Video Generator Demo"),
        Slide(title="Feature 1", subtitle="Easy to use", body_lines=["Just define slides", "Add text and colors"]),
        Slide(title="Feature 2", subtitle="Customizable", body_lines=["Choose your colors", "Set your fonts"]),
        Slide(title="Thanks!", subtitle="Generated with video_generator.py"),
    ]

    output = generate_video(demo_slides, "demo_output.mp4")
    print(f"Demo video saved to: {output}")
