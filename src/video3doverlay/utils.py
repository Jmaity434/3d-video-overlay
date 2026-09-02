"""Dependency-free validation helpers."""

from pathlib import Path
from typing import Union

VideoPath = Union[str, Path]
SUPPORTED_VIDEO_EXTENSIONS = frozenset({".mp4", ".avi", ".mkv"})


def validate_video_path(video_path: VideoPath) -> Path:
    """Return a usable video path or raise a descriptive validation error."""
    if not isinstance(video_path, (str, Path)) or not str(video_path).strip():
        raise TypeError("video_path must be a non-empty string or pathlib.Path")

    path = Path(video_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError("Video file does not exist: {}".format(path))
    if path.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
        accepted = ", ".join(sorted(SUPPORTED_VIDEO_EXTENSIONS))
        raise ValueError(
            "Unsupported video format '{}'; expected one of {}".format(
                path.suffix or "<no extension>", accepted
            )
        )
    return path


def is_valid_video_path(video_path: VideoPath) -> bool:
    """Return whether *video_path* exists and uses a supported extension."""
    try:
        validate_video_path(video_path)
    except (OSError, TypeError, ValueError):
        return False
    return True