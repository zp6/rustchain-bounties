"""
BoTTube Video Uploader — Automated upload tool for BoTTube platform.
Connects to BoTTube API, uploads videos with metadata, and tracks progress.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BOTTUBE_API_BASE = os.getenv("BOTTUBE_API_BASE", "https://bottube.ai/api")


@dataclass
class VideoMetadata:
    """Metadata for a video upload."""
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    category: str = "Education"
    language: str = "en"
    license: str = "CC-BY"


@dataclass
class UploadResult:
    """Result of a single upload attempt."""
    file_path: str
    success: bool
    video_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class BoTTubeUploader:
    """Client for uploading videos to BoTTube."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("BOTTUBE_API_KEY", "")
        self.base_url = base_url or BOTTUBE_API_BASE
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"
        self.session.headers["User-Agent"] = "BoTTube-Uploader/1.0"

    def _api_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def check_health(self) -> bool:
        """Check if BoTTube API is reachable."""
        try:
            resp = self.session.get(self._api_url("/health"), timeout=10)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def upload_video(
        self,
        file_path: str,
        metadata: VideoMetadata,
        progress_callback=None,
    ) -> UploadResult:
        """
        Upload a single video file to BoTTube.

        Args:
            file_path: Path to the video file (MP4, WebM, etc.)
            metadata: Video metadata (title, description, tags)
            progress_callback: Optional callback(completed_bytes, total_bytes)

        Returns:
            UploadResult with success status and video details
        """
        path = Path(file_path)
        if not path.exists():
            return UploadResult(file_path=file_path, success=False, error="File not found")

        file_size = path.stat().st_size
        logger.info(f"Uploading '{metadata.title}' ({file_size:,} bytes)")

        try:
            # Step 1: Request upload URL / initialize upload
            init_resp = self.session.post(
                self._api_url("/videos/init"),
                json={
                    "title": metadata.title,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "category": metadata.category,
                    "language": metadata.language,
                    "file_size": file_size,
                    "file_name": path.name,
                },
                timeout=30,
            )

            if init_resp.status_code == 404:
                # API endpoint not found — fall back to direct upload
                logger.warning("Init endpoint not found, trying direct upload")
                return self._direct_upload(path, metadata, progress_callback)

            if init_resp.status_code != 200:
                error_msg = init_resp.text[:500]
                return UploadResult(
                    file_path=file_path, success=False,
                    error=f"Init failed ({init_resp.status_code}): {error_msg}"
                )

            init_data = init_resp.json()
            upload_url = init_data.get("upload_url", "")
            video_id = init_data.get("video_id", "")

            # Step 2: Upload file content
            with open(path, "rb") as f:
                file_data = f.read()

            if upload_url:
                # Resumable/chunked upload
                upload_resp = self.session.put(
                    upload_url,
                    data=self._progress_reader(file_data, file_size, progress_callback),
                    headers={"Content-Type": "video/mp4"},
                    timeout=600,
                )
            else:
                # Direct multipart upload
                upload_resp = self.session.post(
                    self._api_url("/videos/upload"),
                    files={"file": (path.name, file_data, "video/mp4")},
                    data={"video_id": video_id},
                    timeout=600,
                )

            if upload_resp.status_code not in (200, 201, 202):
                return UploadResult(
                    file_path=file_path, success=False,
                    error=f"Upload failed ({upload_resp.status_code}): {upload_resp.text[:500]}"
                )

            result_data = upload_resp.json()
            vid = result_data.get("video_id", video_id)
            url = result_data.get("url", f"https://bottube.ai/video/{vid}")

            logger.info(f"✅ Uploaded: {metadata.title} → {url}")
            return UploadResult(
                file_path=file_path, success=True,
                video_id=vid, url=url,
            )

        except requests.RequestException as e:
            return UploadResult(
                file_path=file_path, success=False,
                error=f"Network error: {e}"
            )

    def _direct_upload(self, path: Path, metadata: VideoMetadata, progress_callback) -> UploadResult:
        """Fallback: direct multipart upload in a single request."""
        file_size = path.stat().st_size
        with open(path, "rb") as f:
            file_data = f.read()

        try:
            resp = self.session.post(
                self._api_url("/videos"),
                files={"file": (path.name, file_data, "video/mp4")},
                data={
                    "title": metadata.title,
                    "description": metadata.description,
                    "tags": ",".join(metadata.tags),
                    "category": metadata.category,
                    "language": metadata.language,
                },
                timeout=600,
            )

            if resp.status_code in (200, 201):
                data = resp.json()
                vid = data.get("video_id", data.get("id", "unknown"))
                url = data.get("url", f"https://bottube.ai/video/{vid}")
                logger.info(f"✅ Uploaded (direct): {metadata.title} → {url}")
                return UploadResult(
                    file_path=str(path), success=True,
                    video_id=vid, url=url,
                )
            else:
                return UploadResult(
                    file_path=str(path), success=False,
                    error=f"Direct upload failed ({resp.status_code}): {resp.text[:500]}"
                )
        except requests.RequestException as e:
            return UploadResult(
                file_path=str(path), success=False,
                error=f"Network error: {e}"
            )

    @staticmethod
    def _progress_reader(data: bytes, total: int, callback):
        """Wrap bytes for progress tracking."""
        if callback:
            callback(len(data), total)
        return data

    def batch_upload(
        self,
        uploads: list[tuple[str, VideoMetadata]],
        max_retries: int = 2,
    ) -> list[UploadResult]:
        """
        Upload multiple videos with retry logic and progress tracking.

        Args:
            uploads: List of (file_path, metadata) tuples
            max_retries: Max retries per video on failure

        Returns:
            List of UploadResult for each video
        """
        results = []
        total = len(uploads)
        logger.info(f"Starting batch upload of {total} video(s)")

        for i, (file_path, metadata) in enumerate(uploads, 1):
            logger.info(f"[{i}/{total}] Processing: {metadata.title}")

            result = self.upload_video(file_path, metadata)

            # Retry on failure
            retries = 0
            while not result.success and retries < max_retries:
                retries += 1
                logger.warning(f"Retry {retries}/{max_retries} for {metadata.title}")
                time.sleep(2 ** retries)
                result = self.upload_video(file_path, metadata)

            results.append(result)

            # Progress summary
            succeeded = sum(1 for r in results if r.success)
            logger.info(f"Progress: {succeeded}/{total} successful")

        # Final summary
        succeeded = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        logger.info(f"\n{'='*50}")
        logger.info(f"Batch upload complete: {len(succeeded)}/{total} successful")
        if failed:
            logger.warning(f"Failed uploads:")
            for r in failed:
                logger.warning(f"  - {r.file_path}: {r.error}")

        return results

    def save_results(self, results: list[UploadResult], output_path: str = "upload_results.json"):
        """Save upload results to JSON for tracking."""
        data = [asdict(r) for r in results]
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Results saved to {output_path}")


def main():
    """CLI entry point for uploading videos."""
    import argparse

    parser = argparse.ArgumentParser(description="BoTTube Video Uploader")
    parser.add_argument("files", nargs="+", help="Video files to upload")
    parser.add_argument("--title", help="Video title (for single upload)")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--tags", nargs="*", default=[], help="Tags")
    parser.add_argument("--api-key", help="BoTTube API key")
    parser.add_argument("--json", help="JSON file with batch upload config")
    parser.add_argument("--output", default="upload_results.json", help="Results output file")

    args = parser.parse_args()

    uploader = BoTTubeUploader(api_key=args.api_key)

    if args.json:
        with open(args.json) as f:
            config = json.load(f)
        uploads = []
        for item in config.get("videos", []):
            meta = VideoMetadata(
                title=item["title"],
                description=item.get("description", ""),
                tags=item.get("tags", []),
            )
            uploads.append((item["file"], meta))
    else:
        if not args.title:
            print("Error: --title is required for single file upload")
            sys.exit(1)
        meta = VideoMetadata(title=args.title, description=args.description, tags=args.tags)
        uploads = [(f, meta) for f in args.files]

    results = uploader.batch_upload(uploads)
    uploader.save_results(results, args.output)

    sys.exit(0 if all(r.success for r in results) else 1)


if __name__ == "__main__":
    main()
