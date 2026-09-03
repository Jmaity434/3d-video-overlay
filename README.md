# 3d-video-overlay

[![CI](https://github.com/Jmaity434/3d-video-overlay/actions/workflows/ci.yml/badge.svg)](https://github.com/Jmaity434/3d-video-overlay/actions/workflows/ci.yml)

`3d-video-overlay` is the GitHub repository for `video3doverlay`, a Python
library that displays a live 2D video background with an interactive Panda3D
3D overlay. The video is decoded at runtime and is not converted, re-encoded,
or exported to another video file.

The names have different roles:

- **Repository name:** `3d-video-overlay` (this GitHub project).
- **Python distribution name:** `video3doverlay` (the name used by packaging
  tools).
- **Python import name:** `video3doverlay` (the name used in `import`
  statements).

## Features

- Panda3D `MovieTexture` playback on a full-window 2D card.
- Optional model loading through Panda3D's model loader.
- Cyan procedural wireframe fallback when no model is supplied or a model
  cannot be loaded.
- Automatic frame-based overlay rotation.
- Keyboard translation on the X and Z axes.
- Mouse-drag heading and pitch control.
- Video path validation before Panda3D creates a graphics window.
- Logging and clear runtime errors for video-stream failures.
- Optional classical OpenCV motion tracking that aligns the overlay to the
  largest moving region in the video.

This repository includes three selectable rendering backends using seven
libraries: Panda3D, Pygame, PyOpenGL, OpenCV, ModernGL, PyTorch, and
torchvision. See the full
[five-library comparison](docs/LIBRARY-COMPARISON.md). No AI integration is
included.

## Library Documentation

Detailed product and engineering documentation is available in [`docs/`](docs/README.md):

- [PRD](docs/PRD.md): product requirements, users, goals, and acceptance criteria.
- [TRD](docs/TRD.md): technical requirements, runtime contracts, and constraints.
- [ADD](docs/ADD.md): architecture, scene graph, lifecycle, and design decisions.
- [API Reference](docs/API.md): public functions, engine behavior, helpers, and controls.
- [CI/CD and Distribution Plan](docs/CICD-DISTRIBUTION.md): CI, releases, and PyPI strategy.
- [Five-Library Comparison](docs/LIBRARY-COMPARISON.md): backend roles, trade-offs, and selection guide.

## Requirements

- Python 3.8 or newer.
- Panda3D 1.10.14 or newer for the primary 3D engine.
- Pygame 2.5.0 or newer and PyOpenGL 3.1.7 or newer for the custom OpenGL
  backend.
- OpenCV 4.8.0 or newer and ModernGL 5.8.0 or newer for the computer-vision
  backend.
- ModernGL Window 2.4.0 or newer for the ModernGL native window integration.
- PyTorch 2.0.0 or newer and torchvision 0.15.0 or newer for depth estimation.
- GPU is recommended for real-time depth inference; CPU fallback is supported.
- A display-capable environment supported by Panda3D. A normal desktop
  session is recommended; the library does not configure an off-screen or
  headless renderer.
- A video format supported by the installed Panda3D build. The library
  accepts `.mp4`, `.avi`, and `.mkv` file extensions.

## Installation

### Install from GitHub

Clone your repository and install the library in editable mode:

```bash
git clone https://github.com/Jmaity434/3d-video-overlay.git
cd 3d-video-overlay
python -m pip install -e .
```

The package declares Panda3D as a runtime dependency, so this command installs
Panda3D as well. The base install stays lightweight; install an optional extra
only for the backend you need:

```bash
python -m pip install -e ".[pygame]"   # Pygame + PyOpenGL + OpenCV
python -m pip install -e ".[vision]"   # OpenCV + ModernGL
python -m pip install -e ".[depth]"    # OpenCV + ModernGL + PyTorch
python -m pip install -e ".[all]"      # every backend and depth dependency
```

You can also install the base package directly without cloning it:

```bash
python -m pip install "git+https://github.com/Jmaity434/3d-video-overlay.git"
```

To install from an existing local checkout with the test tools:

```bash
python -m pip install -e . pytest
```

## Quick Start

```python
from video3doverlay import play_video_with_3d_overlay

play_video_with_3d_overlay(
    video_path="assets/demo.mp4",
    model_path="assets/marker.egg",
  tracking_enabled=True,
)
```

`model_path` is optional:

```python
from video3doverlay import play_video_with_3d_overlay

play_video_with_3d_overlay("assets/demo.mp4")
```

The call validates the video path, constructs `Video3DOverlayEngine`, and
blocks in Panda3D's `run()` loop. The video card fills the `render2d` frame and
the 3D object is placed at `(x=0, y=8, z=0)` in the 3D scene.

Set `tracking_enabled=True` to open a parallel OpenCV video stream. The
tracker uses background subtraction, selects the largest moving region, maps
its center to the overlay's X/Z position, and adjusts the overlay scale. This
is classical computer vision, not AI. It is a screen-space motion alignment,
not camera calibration or true 3D pose estimation.

### Runnable Copy-and-Paste Sample

After cloning the repository, create a file named `run_overlay.py` in the
repository root and paste this code into it:

```python
import logging

from video3doverlay import play_video_with_3d_overlay

logging.basicConfig(level=logging.INFO)

play_video_with_3d_overlay("assets/demo.mp4")
```

Put a supported video at `assets/demo.mp4`, install the package, and run:

```bash
mkdir -p assets
# Copy your own .mp4, .avi, or .mkv file to assets/demo.mp4.
python -m pip install -e .
python run_overlay.py
```

Expected result:

- A Panda3D window opens with the video filling the background.
- A cyan wireframe box appears in the center because this sample does not
  provide a model.
- The box rotates automatically while the video continues playing.
- Arrow keys or `WASD` move the box, `R` resets it, and primary-mouse dragging
  changes its heading and pitch.
- There is normally no success message in the terminal; the visible result is
  the Panda3D window. Invalid or unreadable video files produce a logged error
  and a `RuntimeError`.

Press `Ctrl+C` in the terminal or close the Panda3D window to stop the sample.

To use a model instead, pass its path as the second argument:

```python
play_video_with_3d_overlay("assets/demo.mp4", "assets/marker.egg")
```

### Alternative Backend Samples

The project also provides two selectable backends. Start only one backend per
process because each backend owns its native graphics window.

Pygame + PyOpenGL:

```python
from video3doverlay import play_video_with_pygame_opengl

play_video_with_pygame_opengl("assets/demo.mp4")
```

OpenCV + ModernGL:

```python
from video3doverlay import play_video_with_opencv_moderngl

play_video_with_opencv_moderngl("assets/demo.mp4")
```

OpenCV + PyTorch depth + ModernGL:

```python
from video3doverlay import play_video_with_opencv_moderngl

play_video_with_opencv_moderngl(
  "assets/demo.mp4",
  depth_enabled=True,
  depth_model="MiDaS_small",
  device="cuda",  # Use "cpu" when CUDA is unavailable.
)
```

On the first depth-enabled run, PyTorch Hub downloads and caches the MiDaS
model weights. A network connection is therefore required once unless the
weights are already cached. Omit `device` to select CUDA automatically when
available, otherwise CPU is used. The output is relative depth, not measured
distance in meters.

The Pygame backend uses OpenCV for frames, PyOpenGL for rendering, and draws
an interactive wireframe sphere. The ModernGL backend uses OpenCV for frames
and classical motion detection, then displays the processed frame through
ModernGL. No AI or model-file parser is included in either alternative.

For the advanced depth mode, use the dedicated convenience function:

```python
from video3doverlay import play_video_with_depth_overlay

play_video_with_depth_overlay("assets/demo.mp4", device="cuda")
```

Omit `device` for automatic CUDA-or-CPU selection, or pass `device="cpu"` on
machines without a compatible GPU.

### Live Camera and Recording

The OpenCV + ModernGL backend can use a webcam instead of a video file. The
camera index is usually `0` for the default camera:

```python
from video3doverlay import play_video_with_depth_overlay

play_video_with_depth_overlay(
  video_path="",          # ignored when camera_index is provided
  camera_index=0,
  device="cuda",
)
```

To record the processed camera frame stream while it is displayed:

```python
from video3doverlay import play_video_with_depth_overlay

play_video_with_depth_overlay(
  "",
  camera_index=0,
  output_path="recordings/camera-processed.mp4",
)
```

The recording contains the processed camera frames, motion annotations, and
optional depth visualization. It does not capture Panda3D geometry because
Panda3D, Pygame, and ModernGL use separate native rendering contexts. A
browser website cannot import this desktop Python GUI directly; use a
server-side process and stream its frames to the browser with WebRTC or a
similar lightweight transport.

### Headless Smoke Check

The following command checks a video path without opening a graphics window:

```bash
PYTHONPATH=src python -c "from video3doverlay.utils import is_valid_video_path; print(is_valid_video_path('assets/demo.mp4'))"
```

For an existing supported file, it prints:

```text
True
```

For a missing file, it prints `False`. This check does not prove that the
installed Panda3D build can decode the file; the full sample is the test for
actual playback.

## Runtime Controls

| Input | Behavior |
| --- | --- |
| Left arrow or `A` | Move overlay left on X |
| Right arrow or `D` | Move overlay right on X |
| Up arrow or `W` | Move overlay up on Z |
| Down arrow or `S` | Move overlay down on Z |
| `R` | Reset position to `(0, 8, 0)` and reset rotation |
| Hold primary mouse button and move | Change heading and pitch |

When the mouse is not being dragged, the overlay rotates at 30 degrees per
second. Mouse movement temporarily replaces that automatic heading and pitch
update; releasing the button resumes automatic heading rotation.

## Direct Engine Usage

Use the engine directly when Panda3D must be configured before the main loop:

```python
from video3doverlay import Video3DOverlayEngine

app = Video3DOverlayEngine("assets/demo.mkv")
# Configure other Panda3D state here.
app.run()
```

The engine inherits from `direct.showbase.ShowBase.ShowBase`. Its startup
sequence is:

1. Validate that the video exists and has an accepted extension.
2. Load the video as a `MovieTexture`, start looping playback, and synchronize
   its audio when Panda3D provides an audio stream.
3. Attach a textured full-screen card to `render2d` in the background bin.
4. Load the requested model or create a wireframe box fallback.
5. Attach the overlay to `render`, bind controls, and register the animation
   task.

## Validation Helpers

The dependency-light helpers in `video3doverlay.utils` can be used before
starting the graphics runtime:

```python
from video3doverlay.utils import is_valid_video_path, validate_video_path

if is_valid_video_path("assets/demo.mp4"):
    path = validate_video_path("assets/demo.mp4")
```

`validate_video_path()` returns a `pathlib.Path` and raises:

- `TypeError` for an empty or invalid path value.
- `FileNotFoundError` when the path is not an existing file.
- `ValueError` when the extension is not `.mp4`, `.avi`, or `.mkv`.

`is_valid_video_path()` catches those validation errors and returns `True` or
`False`.

## Project Layout

```text
.
├── src/
│   └── video3doverlay/
│       ├── __init__.py   # Public exports and version
│       ├── engine.py     # Panda3D engine and runtime controls
│       ├── pygame_backend.py  # Pygame + PyOpenGL backend
│       ├── opencv_backend.py  # OpenCV + ModernGL backend
│       ├── depth.py        # PyTorch MiDaS depth estimator
│       └── utils.py      # Video path validation
├── tests/
│   └── test_engine.py    # Headless validation and API tests
├── .github/
│   └── workflows/ci.yml  # GitHub Actions test matrix
├── LICENSE
├── README.md
└── pyproject.toml
```

The src layout prevents the test runner from accidentally importing the
checkout instead of the installed package. The package version is currently
`0.1.0`.

## Development and Testing

Run the checks from the repository root:

```bash
python -m pip install -e . pytest
python -m compileall -q src tests
python -m pytest -q
```

The tests validate paths and public metadata without opening a Panda3D window,
so they are suitable for headless CI. GitHub Actions runs the same checks on
Python 3.8 through 3.12 for pushes to `main` and pull requests.

## Limitations

- This library provides a simple overlay scene, not camera-pose estimation.
  OpenCV motion tracking can approximate alignment to the largest moving
  region when enabled.
- The overlay is positioned in Panda3D world coordinates; it is not projected
  from video metadata or detected features.
- A file extension check does not guarantee that the file's codec is supported
  by the installed Panda3D build.
- Video playback and audio depend on Panda3D's available movie and audio
  backends on the target platform.
- Depth estimation depends on PyTorch model weights and is substantially faster
  on a compatible CUDA GPU; CPU inference may not be real time.
- The current public API runs one Panda3D application loop per invocation.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).