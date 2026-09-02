# Technical Requirements Document

## 1. Scope and Baseline

This document defines the technical contract for the `video3doverlay` Python
library at version `0.1.0`. The implementation uses Panda3D as the graphics
engine and Hatchling as the build backend.

## 2. Runtime Requirements

| Area | Requirement |
| --- | --- |
| Python | `>=3.8` |
| Graphics | `panda3d>=1.10.14` |
| Display | A Panda3D-supported display-capable environment |
| Input | Panda3D event messenger and mouse watcher |
| Media | Local file with `.mp4`, `.avi`, or `.mkv` extension |
| Build | PEP 517 build through Hatchling |

The extension allowlist is a fast preflight check, not a codec compatibility
guarantee. Actual decoding is delegated to the installed Panda3D runtime.

## 3. Package and Module Contracts

```text
src/video3doverlay/
├── __init__.py  Public exports and version
├── engine.py    ShowBase engine and runtime behavior
└── utils.py     Dependency-light path validation
```

`video3doverlay.__version__` and the project metadata must remain aligned at
`0.1.0` until a release process changes both deliberately.

## 4. Startup Sequence

1. `Video3DOverlayEngine.__init__` calls `validate_video_path` before
   initializing `ShowBase`, preventing an invalid path from opening a window.
2. `ShowBase` creates Panda3D's application services and scene roots.
3. The engine disables the default mouse camera controls.
4. The video is loaded with `loader.loadTexture()` and must be a
   `MovieTexture`.
5. Movie playback is looped. If `getSound()` returns an audio stream, the
   stream is looped, started, and used for texture synchronization.
6. A `CardMaker` card covering `(-1, 1, -1, 1)` is attached to `render2d`.
   Depth testing and depth writes are disabled and the card uses the
   `background` bin.
7. The requested model is loaded, or a `LineSegs` wireframe box is created.
8. The overlay is attached to `render`, positioned at `(0, 8, 0)`, and scaled
   to `1.5`.
9. Input events and the per-frame animation task are registered.
10. The convenience function calls `app.run()` and blocks until the window
    closes.

## 5. Scene Graph and Coordinate Model

The video card is a 2D scene-graph node under `render2d`; it does not occupy a
3D world position. The overlay is a 3D node under `render`. Its initial world
position is selected for visibility with Panda3D's default forward direction.

Keyboard movement changes only X and Z. The Y coordinate remains unchanged.
Mouse drag changes heading (`H`) and pitch (`P`). Automatic heading is derived
from Panda3D task time at 30 degrees per second when no drag is active.

## 6. Error Handling

### Input errors

`validate_video_path` raises:

- `TypeError` for a non-string/non-`Path` or empty value.
- `FileNotFoundError` for a path that is not an existing regular file.
- `ValueError` for an extension outside the supported set.

### Video errors

Any failure while creating or configuring the movie background is logged with
`LOGGER.exception` and wrapped in `RuntimeError` with the video path. The
original error is retained as the exception cause.

### Model errors

Any model loader failure is logged with `LOGGER.exception`; the engine then
uses the procedural wireframe. Model failure is intentionally non-fatal.

## 7. Input and Task Design

Events are registered with `ShowBase.accept`:

- `arrow_left`, `arrow_right`, `arrow_up`, `arrow_down`
- `a`, `d`, `w`, `s`
- `r`
- `mouse1`, `mouse1-up`

The animation task returns `Task.cont` on every frame. It samples the mouse
watcher while dragging and otherwise updates automatic heading using
`task.time`.

## 8. Packaging Requirements

`pyproject.toml` must:

- Use `hatchling.build` as the PEP 517 backend.
- Declare distribution name `video3doverlay`.
- Declare Python `>=3.8`.
- Declare `panda3d>=1.10.14` as a runtime dependency.
- Point Hatchling at `src/video3doverlay`.

The source layout must remain installable with:

```bash
python -m pip install -e .
```

## 9. Testability Requirements

Tests should avoid constructing `ShowBase` unless a display-enabled integration
environment is explicitly configured. The current suite tests path validation
and package metadata. Future runtime tests should use an isolated Panda3D
window configuration and a small known-good media fixture.

## 10. Compatibility and Security

- Treat all user-provided paths as local filesystem paths; do not execute them.
- Do not download media or models implicitly.
- Preserve platform path handling through `pathlib.Path`.
- Keep dependency versions bounded only when a verified incompatibility exists.
- Do not log media contents or credentials; logging asset paths is acceptable.

## 11. Known Technical Limitations

- No explicit public pause/seek/stop methods exist yet.
- No aspect-ratio fitting policy is exposed; the card is a normalized full
  frame.
- No camera calibration or pixel-space overlay projection exists.
- Panda3D backend availability determines actual media decoding and audio.
- The current convenience function owns a single blocking application loop.
