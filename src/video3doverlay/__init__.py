"""Public API for video3doverlay."""

from typing import Any

__version__ = "0.1.0"

__all__ = [
    "Video3DOverlayEngine",
    "play_video_with_3d_overlay",
    "__version__",
]


def __getattr__(name: str) -> Any:
    """Load Panda3D-backed exports only when an application requests them."""
    if name in {"Video3DOverlayEngine", "play_video_with_3d_overlay"}:
        from .engine import Video3DOverlayEngine, play_video_with_3d_overlay

        return {
            "Video3DOverlayEngine": Video3DOverlayEngine,
            "play_video_with_3d_overlay": play_video_with_3d_overlay,
        }[name]
    raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))