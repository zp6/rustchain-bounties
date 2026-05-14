"""
Generate 5 Original RustChain Videos for BoTTube (Bounty #446).

This script creates 5 educational slideshow-style videos about RustChain topics
and optionally uploads them to BoTTube.

Videos:
1. "RustChain Proof of Antiquity Explained"
2. "How Blockchain Mining Works Without GPUs"
3. "Building on RustChain: Developer Guide"
4. "Hardware Attestation for Security"
5. "RustChain vs Traditional Mining"

Usage:
    python generate_videos.py              # Generate video files only
    python generate_videos.py --upload     # Generate and upload to BoTTube
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

from video_generator import Slide, generate_video, create_slide_image
from uploader import BoTTubeUploader, VideoMetadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent / "output_videos"

# ──────────────────────────────────────────────────
# Video 1: Proof of Antiquity Explained
# ──────────────────────────────────────────────────
VIDEO_1 = {
    "title": "RustChain Proof of Antiquity Explained",
    "description": (
        "An educational overview of RustChain's Proof of Antiquity consensus mechanism. "
        "Learn how PoA leverages hardware attestation and time-based verification to "
        "create a secure, energy-efficient blockchain without traditional mining."
    ),
    "tags": ["RustChain", "Proof of Antiquity", "Blockchain", "Consensus", "PoA"],
    "slides": [
        Slide(
            title="Proof of Antiquity",
            subtitle="RustChain's Revolutionary Consensus",
            bg_color=(15, 23, 42),
            accent_color=(59, 130, 246),
        ),
        Slide(
            title="What is Proof of Antiquity?",
            subtitle="A New Approach to Consensus",
            body_lines=[
                "• Time-based proof system",
                "• Hardware attestation required",
                "• No GPU mining needed",
                "• Energy efficient by design",
            ],
            bg_color=(15, 23, 42),
            accent_color=(59, 130, 246),
        ),
        Slide(
            title="How PoA Works",
            subtitle="The Core Mechanism",
            body_lines=[
                "1. Nodes register with hardware attestation",
                "2. System verifies node authenticity",
                "3. Nodes accumulate antiquity over time",
                "4. Older, verified nodes get priority",
            ],
            bg_color=(15, 23, 42),
            accent_color=(59, 130, 246),
        ),
        Slide(
            title="Benefits of PoA",
            subtitle="Why It Matters",
            body_lines=[
                "✓ 99.9% less energy than PoW",
                "✓ Resistant to 51% attacks",
                "✓ Genuine hardware requirement",
                "✓ Long-term network stability",
            ],
            bg_color=(15, 23, 42),
            accent_color=(59, 130, 246),
        ),
        Slide(
            title="Get Started with RustChain",
            subtitle="Join the Network",
            body_lines=[
                "Visit: rustchain.io",
                "GitHub: github.com/rustchain",
                "Discord: rustchain community",
            ],
            bg_color=(15, 23, 42),
            accent_color=(59, 130, 246),
        ),
    ],
}

# ──────────────────────────────────────────────────
# Video 2: Mining Without GPUs
# ──────────────────────────────────────────────────
VIDEO_2 = {
    "title": "How Blockchain Mining Works Without GPUs",
    "description": (
        "Discover how RustChain eliminates the need for GPU mining. "
        "This video explains the innovative approach to block validation "
        "using CPU-based hardware attestation instead of computational puzzles."
    ),
    "tags": ["RustChain", "Mining", "GPU-free", "Blockchain", "Hardware"],
    "slides": [
        Slide(
            title="Mining Without GPUs",
            subtitle="RustChain's Innovative Approach",
            bg_color=(30, 10, 60),
            accent_color=(168, 85, 247),
        ),
        Slide(
            title="The Problem with GPU Mining",
            subtitle="Traditional Blockchain Issues",
            body_lines=[
                "• Massive energy consumption",
                "• E-waste from burned-out GPUs",
                "• Centralized mining pools",
                "• High barrier to entry",
            ],
            bg_color=(30, 10, 60),
            accent_color=(168, 85, 247),
        ),
        Slide(
            title="CPU-Based Verification",
            subtitle="RustChain's Solution",
            body_lines=[
                "• Uses standard CPU hardware",
                "• Hardware attestation (TPM/TEE)",
                "• No special equipment needed",
                "• Anyone with a PC can participate",
            ],
            bg_color=(30, 10, 60),
            accent_color=(168, 85, 247),
        ),
        Slide(
            title="Environmental Impact",
            subtitle="Sustainability Matters",
            body_lines=[
                "• 1000x less energy consumption",
                "• No e-waste from mining rigs",
                "• Carbon-neutral blockchain",
                "• Sustainable future for crypto",
            ],
            bg_color=(30, 10, 60),
            accent_color=(168, 85, 247),
        ),
        Slide(
            title="Start Mining on RustChain",
            subtitle="Your CPU is All You Need",
            body_lines=[
                "Download the RustChain node software",
                "Run hardware attestation",
                "Start contributing to the network",
                "Earn RTC tokens",
            ],
            bg_color=(30, 10, 60),
            accent_color=(168, 85, 247),
        ),
    ],
}

# ──────────────────────────────────────────────────
# Video 3: Developer Guide
# ──────────────────────────────────────────────────
VIDEO_3 = {
    "title": "Building on RustChain: Developer Guide",
    "description": (
        "A comprehensive developer guide for building on RustChain. "
        "Learn about the SDK, smart contracts in Rust, and how to deploy "
        "your first decentralized application on the RustChain network."
    ),
    "tags": ["RustChain", "Developer", "SDK", "Smart Contracts", "Rust"],
    "slides": [
        Slide(
            title="Building on RustChain",
            subtitle="Developer Guide",
            bg_color=(10, 40, 30),
            accent_color=(34, 197, 94),
        ),
        Slide(
            title="Getting Started",
            subtitle="Your First Steps",
            body_lines=[
                "• Install Rust toolchain (rustup)",
                "• Clone RustChain SDK template",
                "• Configure your development environment",
                "• Run local testnet",
            ],
            bg_color=(10, 40, 30),
            accent_color=(34, 197, 94),
        ),
        Slide(
            title="Smart Contracts in Rust",
            subtitle="Safe & Fast",
            body_lines=[
                "• Write contracts in Rust",
                "• Memory safety guaranteed",
                "• Compile to WASM for execution",
                "• Comprehensive testing framework",
            ],
            bg_color=(10, 40, 30),
            accent_color=(34, 197, 94),
        ),
        Slide(
            title="RustChain SDK Features",
            subtitle="Powerful Tools",
            body_lines=[
                "• Type-safe RPC client",
                "• Event subscription system",
                "• Wallet integration",
                "• Cross-contract calls",
            ],
            bg_color=(10, 40, 30),
            accent_color=(34, 197, 94),
        ),
        Slide(
            title="Deploy Your First dApp",
            subtitle="Ship It!",
            body_lines=[
                "1. Write your contract",
                "2. Test thoroughly",
                "3. Deploy to testnet",
                "4. Audit and go live!",
            ],
            bg_color=(10, 40, 30),
            accent_color=(34, 197, 94),
        ),
    ],
}

# ──────────────────────────────────────────────────
# Video 4: Hardware Attestation
# ──────────────────────────────────────────────────
VIDEO_4 = {
    "title": "Hardware Attestation for Security",
    "description": (
        "Deep dive into hardware attestation on RustChain. Understand how TPM, "
        "TEE, and secure enclaves provide trustless verification of node integrity "
        "and prevent Sybil attacks on the network."
    ),
    "tags": ["RustChain", "Hardware Attestation", "TPM", "TEE", "Security"],
    "slides": [
        Slide(
            title="Hardware Attestation",
            subtitle="Securing RustChain at the Hardware Level",
            bg_color=(40, 10, 10),
            accent_color=(239, 68, 68),
        ),
        Slide(
            title="What is Hardware Attestation?",
            subtitle="Trust Through Hardware",
            body_lines=[
                "• Cryptographic proof of hardware identity",
                "• TPM (Trusted Platform Module)",
                "• TEE (Trusted Execution Environment)",
                "• Remote verification capability",
            ],
            bg_color=(40, 10, 10),
            accent_color=(239, 68, 68),
        ),
        Slide(
            title="How It Works on RustChain",
            subtitle="The Verification Process",
            body_lines=[
                "1. Node generates attestation report",
                "2. Report includes hardware measurements",
                "3. Network verifies report signature",
                "4. Verified node joins consensus",
            ],
            bg_color=(40, 10, 10),
            accent_color=(239, 68, 68),
        ),
        Slide(
            title="Preventing Attacks",
            subtitle="Security Guarantees",
            body_lines=[
                "✓ Sybil attack resistance",
                "✓ No virtual node spoofing",
                "✓ Physical hardware requirement",
                "✓ tamper-evident verification",
            ],
            bg_color=(40, 10, 10),
            accent_color=(239, 68, 68),
        ),
        Slide(
            title="The Future of Blockchain Security",
            subtitle="Hardware-Backed Trust",
            body_lines=[
                "RustChain leads the way in",
                "hardware-verified blockchain security.",
                "Join us in building a safer Web3.",
            ],
            bg_color=(40, 10, 10),
            accent_color=(239, 68, 68),
        ),
    ],
}

# ──────────────────────────────────────────────────
# Video 5: RustChain vs Traditional Mining
# ──────────────────────────────────────────────────
VIDEO_5 = {
    "title": "RustChain vs Traditional Mining",
    "description": (
        "A detailed comparison between RustChain's Proof of Antiquity and "
        "traditional Proof of Work mining. See how RustChain achieves better "
        "security, efficiency, and decentralization without energy-intensive mining."
    ),
    "tags": ["RustChain", "PoW", "PoA", "Comparison", "Blockchain"],
    "slides": [
        Slide(
            title="RustChain vs Traditional Mining",
            subtitle="A New Paradigm",
            bg_color=(10, 20, 50),
            accent_color=(251, 191, 36),
        ),
        Slide(
            title="Traditional PoW Mining",
            subtitle="The Old Way",
            body_lines=[
                "• Requires expensive ASICs/GPUs",
                "• Massive electricity consumption",
                "• Concentrated in mining pools",
                "• Environmental concerns",
            ],
            bg_color=(10, 20, 50),
            accent_color=(251, 191, 36),
        ),
        Slide(
            title="RustChain's PoA",
            subtitle="The Better Way",
            body_lines=[
                "• Standard hardware sufficient",
                "• Minimal energy usage",
                "• True decentralization",
                "• Environmentally sustainable",
            ],
            bg_color=(10, 20, 50),
            accent_color=(251, 191, 36),
        ),
        Slide(
            title="Head to Head Comparison",
            subtitle="The Numbers Speak",
            body_lines=[
                "Energy:     PoW: 150 TWh/yr → PoA: ~0.15 TWh/yr",
                "Hardware:   PoW: $5000+     → PoA: $500",
                "Entry:      PoW: High       → PoA: Low",
                "Security:   PoW: Good       → PoA: Excellent",
            ],
            bg_color=(10, 20, 50),
            accent_color=(251, 191, 36),
        ),
        Slide(
            title="The Future is RustChain",
            subtitle="Join the Revolution",
            body_lines=[
                "Sustainable. Secure. Decentralized.",
                "",
                "Learn more at rustchain.io",
                "Start building today!",
            ],
            bg_color=(10, 20, 50),
            accent_color=(251, 191, 36),
        ),
    ],
}

ALL_VIDEOS = [VIDEO_1, VIDEO_2, VIDEO_3, VIDEO_4, VIDEO_5]


def generate_all_videos(output_dir: Path = OUTPUT_DIR) -> list[dict]:
    """Generate all 5 RustChain videos."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for i, video_config in enumerate(ALL_VIDEOS, 1):
        logger.info(f"Generating video {i}/5: {video_config['title']}")

        # Create a thumbnail from the first slide
        thumbnail = create_slide_image(video_config["slides"][0])
        thumb_path = output_dir / f"video_{i}_thumbnail.png"
        thumbnail.save(str(thumb_path))

        # Generate the video
        safe_title = video_config["title"].replace(" ", "_").replace(":", "").replace("'", "")
        video_path = output_dir / f"video_{i}_{safe_title}.mp4"

        actual_path = generate_video(
            slides=video_config["slides"],
            output_path=str(video_path),
            width=1280,
            height=720,
            fps=24,
            slide_duration=5.0,
        )

        result = {
            "index": i,
            "title": video_config["title"],
            "description": video_config["description"],
            "tags": video_config["tags"],
            "video_file": actual_path,
            "thumbnail": str(thumb_path),
        }
        results.append(result)
        logger.info(f"✅ Video {i} complete: {actual_path}")

    # Save metadata
    meta_path = output_dir / "videos_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Metadata saved to {meta_path}")

    return results


def upload_all_videos(results: list[dict], api_key: str = None) -> None:
    """Upload generated videos to BoTTube."""
    uploader = BoTTubeUploader(api_key=api_key)

    uploads = []
    for r in results:
        meta = VideoMetadata(
            title=r["title"],
            description=r["description"],
            tags=r["tags"],
        )
        uploads.append((r["video_file"], meta))

    upload_results = uploader.batch_upload(uploads)
    uploader.save_results(upload_results, str(OUTPUT_DIR / "upload_results.json"))

    succeeded = sum(1 for r in upload_results if r.success)
    logger.info(f"Upload complete: {succeeded}/{len(upload_results)} successful")


def main():
    do_upload = "--upload" in sys.argv

    logger.info("=" * 60)
    logger.info("RustChain Video Generator — Bounty #446")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    results = generate_all_videos()

    print(f"\n{'='*60}")
    print(f"Generated {len(results)} videos in {OUTPUT_DIR}")
    for r in results:
        print(f"  {r['index']}. {r['title']}")
        print(f"     File: {r['video_file']}")
    print(f"{'='*60}\n")

    if do_upload:
        api_key = os.getenv("BOTTUBE_API_KEY")
        upload_all_videos(results, api_key)
    else:
        print("To upload to BoTTube, run: python generate_videos.py --upload")
        print("Set BOTTUBE_API_KEY environment variable for authentication.")


if __name__ == "__main__":
    main()
