# video3doverlay

[![CI](https://github.com/Jmaity434/3d-video-overlay/actions/workflows/ci.yml/badge.svg)](https://github.com/Jmaity434/3d-video-overlay/actions/workflows/ci.yml)

`video3doverlay` is a Python library that displays a live 2D video background
with an interactive Panda3D 3D overlay. The video is decoded at runtime and
is not converted, re-encoded, or exported to another video file.

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

## Requirements

- Python 3.8 or newer.
- Panda3D 1.10.14 or newer.
- A display-capable environment supported by Panda3D. A normal desktop
  session is recommended; the library does not configure an off-screen or
  headless renderer.
- A video format supported by the installed Panda3D build. The library
  accepts `.mp4`, `.avi`, and `.mkv` file extensions.

## Installation

Install directly from this repository while developing:

```bash
python -m pip install -e .
```

The package declares Panda3D as a runtime dependency, so a regular install
will install it as well. If you are installing from a local checkout and want
to install test tools too:

```bash
python -m pip install -e . pytest
```

## Quick Start

```python
from video3doverlay import play_video_with_3d_overlay

play_video_with_3d_overlay(
    video_path="assets/demo.mp4",
    model_path="assets/marker.egg",
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

- This library provides a simple overlay scene, not camera tracking or
  automatic alignment between a model and objects in the video.
- The overlay is positioned in Panda3D world coordinates; it is not projected
  from video metadata or detected features.
- A file extension check does not guarantee that the file's codec is supported
  by the installed Panda3D build.
- Video playback and audio depend on Panda3D's available movie and audio
  backends on the target platform.
- The current public API runs one Panda3D application loop per invocation.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).