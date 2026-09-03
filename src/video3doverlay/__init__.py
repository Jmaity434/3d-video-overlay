"""Public API for video3doverlay."""

from typing import Any

__version__ = "0.1.0"

__all__ = [
    "Video3DOverlayEngine",
    "PygameOpenGLEngine",
    "OpenCVModernGLEngine",
    "DepthEstimator",
    "select_depth_device",
    "play_video_with_3d_overlay",
    "play_video_with_pygame_opengl",
    "play_video_with_opencv_moderngl",
    "play_video_with_depth_overlay",
    "__version__",
]


def __getattr__(name: str) -> Any:
    """Load graphics-backed exports only when an application requests them."""
    if name in {"Video3DOverlayEngine", "play_video_with_3d_overlay"}:
        from .engine import Video3DOverlayEngine, play_video_with_3d_overlay

        return {
            "Video3DOverlayEngine": Video3DOverlayEngine,
            "play_video_with_3d_overlay": play_video_with_3d_overlay,
        }[name]
    if name in {"PygameOpenGLEngine", "play_video_with_pygame_opengl"}:
        from .pygame_backend import PygameOpenGLEngine, play_video_with_pygame_opengl

        return {
            "PygameOpenGLEngine": PygameOpenGLEngine,
            "play_video_with_pygame_opengl": play_video_with_pygame_opengl,
        }[name]
    if name in {"OpenCVModernGLEngine", "play_video_with_opencv_moderngl"}:
        from .opencv_backend import (
            OpenCVModernGLEngine,
            play_video_with_opencv_moderngl,
        )

        return {
            "OpenCVModernGLEngine": OpenCVModernGLEngine,
            "play_video_with_opencv_moderngl": play_video_with_opencv_moderngl,
        }[name]
    if name == "play_video_with_depth_overlay":
        from .opencv_backend import play_video_with_depth_overlay

        return play_video_with_depth_overlay
    if name in {"DepthEstimator", "select_depth_device"}:
        from .depth import DepthEstimator, select_depth_device

        return {
            "DepthEstimator": DepthEstimator,
            "select_depth_device": select_depth_device,
        }[name]
    raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))