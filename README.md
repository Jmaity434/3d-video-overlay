# video3doverlay

[![CI](https://github.com/Jmaity434/3d-video-overlay/actions/workflows/ci.yml/badge.svg)](https://github.com/Jmaity434/3d-video-overlay/actions/workflows/ci.yml)

`video3doverlay` is a small Panda3D library for displaying interactive 3D
content over a normal video stream. The video is decoded and displayed at
runtime, so this library does not transcode or export a new video file.

## Installation

```bash
python -m pip install video3doverlay
```

The package supports Python 3.8 and newer and depends on Panda3D 1.10.14 or
newer.

## Usage

```python
from video3doverlay import play_video_with_3d_overlay
play_video_with_3d_overlay("assets/demo.mp4", "assets/marker.egg")
```

The model argument is optional. When the model cannot be loaded, the engine
renders a cyan wireframe box so the overlay and its controls remain visible.
Supported video extensions are `.mp4`, `.avi`, and `.mkv`.

The runtime controls are:

- Arrow keys or `WASD`: translate the overlay on the X/Z axes.
- `R`: reset position and rotation.
- Hold the primary mouse button and drag: adjust heading and pitch.

For applications that need to configure Panda3D before entering its loop,
instantiate `Video3DOverlayEngine` directly and call `run()` after setup.

## Development

```bash
python -m pip install -e .
python -m pytest
```

The validation tests do not open a graphics window, which keeps them suitable
for headless continuous integration environments. GitHub Actions runs these
checks on Python 3.8 through 3.12 for pushes to `main` and pull requests.
