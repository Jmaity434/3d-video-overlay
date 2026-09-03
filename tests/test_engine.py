"""Tests for validation and the public package contract."""

from pathlib import Path

import pytest

from video3doverlay.utils import is_valid_video_path, validate_video_path
from video3doverlay.depth import select_depth_device
from video3doverlay.opencv_backend import OpenCVModernGLEngine


def test_validate_video_path_accepts_supported_existing_file(tmp_path: Path) -> None:
    video = tmp_path / "clip.MP4"
    video.touch()
    assert validate_video_path(video) == video
    assert is_valid_video_path(video)


def test_validate_video_path_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        validate_video_path(tmp_path / "missing.mp4")


def test_validate_video_path_rejects_unsupported_extension(tmp_path: Path) -> None:
    video = tmp_path / "clip.mov"
    video.touch()
    with pytest.raises(ValueError):
        validate_video_path(video)
    assert not is_valid_video_path(video)


def test_public_version() -> None:
    import video3doverlay

    assert video3doverlay.__version__ == "0.1.0"


def test_depth_device_honors_explicit_selection() -> None:
    assert select_depth_device("cpu") == "cpu"


def test_camera_backend_accepts_camera_index_without_video_file() -> None:
    engine = OpenCVModernGLEngine("", camera_index=0, device="cpu")
    assert engine.camera_index == 0
    assert engine.device == "cpu"


def test_camera_index_must_be_non_negative() -> None:
    with pytest.raises(ValueError):
        OpenCVModernGLEngine("", camera_index=-1)