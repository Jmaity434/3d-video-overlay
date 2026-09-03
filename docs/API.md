# API Reference

## 1. Public Package

```python
import video3doverlay
```

### `video3doverlay.__version__`

```python
__version__: str = "0.1.0"
```

The version identifies the package release, not the GitHub repository name.
The repository is `3d-video-overlay`; the distribution and import name is
`video3doverlay`.

## 2. Convenience Function

### `play_video_with_3d_overlay`

```python
def play_video_with_3d_overlay(
    video_path: str,
    model_path: Optional[str] = None,
    tracking_enabled: bool = False,
) -> None:
    ...
```

#### Parameters

- `video_path`: Local path to an existing `.mp4`, `.avi`, or `.mkv` file.
- `model_path`: Optional path accepted by Panda3D's `loader.loadModel()`.
  Invalid or missing models are replaced by the procedural wireframe.
- `tracking_enabled`: When `True`, use OpenCV background subtraction to align
    overlay position and scale to the largest moving region. Defaults to `False`.

#### Behavior

1. Validates `video_path`.
2. Creates `Video3DOverlayEngine`.
3. Calls Panda3D's blocking `run()` loop.

#### Raises

- `TypeError`: `video_path` is not a non-empty string.
- `FileNotFoundError`: `video_path` is not an existing file.
- `ValueError`: the extension is not supported.
- `RuntimeError`: Panda3D cannot create or configure the movie texture.

#### Example

```python
from video3doverlay import play_video_with_3d_overlay

play_video_with_3d_overlay("assets/demo.mp4")
```

Tracking example:

```python
play_video_with_3d_overlay("assets/demo.mp4", tracking_enabled=True)
```

## 3. Engine Class

### `Video3DOverlayEngine`

```python
class Video3DOverlayEngine(ShowBase):
    def __init__(
        self,
        video_path: str,
        model_path: Optional[str] = None,
        tracking_enabled: bool = False,
    ) -> None:
        ...
```

The class inherits from `direct.showbase.ShowBase.ShowBase` and performs
runtime setup during construction.

#### Publicly useful member

- `overlay: NodePath`: The loaded model or generated wireframe node. Host
  applications can use Panda3D's `NodePath` methods to inspect or adjust it
  before calling `run()`.

#### Construction behavior

- Disables Panda3D's default mouse camera controls.
- Creates a looping `MovieTexture` background.
- Synchronizes audio when the movie exposes a sound stream.
- Places the overlay at `(0.0, 8.0, 0.0)` and scale `1.5`.
- Registers keyboard, mouse, and animation-task behavior.
- When enabled, opens a second OpenCV stream and aligns the overlay to the
    largest moving region using classical background subtraction.

#### Direct-use example

```python
from video3doverlay import Video3DOverlayEngine

app = Video3DOverlayEngine("assets/demo.mp4")
app.overlay.setScale(2.0)
app.run()
```

## 4. Validation API

Import these helpers from `video3doverlay.utils`:

```python
from pathlib import Path
from typing import Union

VideoPath = Union[str, Path]
```

### `SUPPORTED_VIDEO_EXTENSIONS`

```python
SUPPORTED_VIDEO_EXTENSIONS = frozenset({".mp4", ".avi", ".mkv"})
```

### `validate_video_path`

```python
def validate_video_path(video_path: Union[str, Path]) -> Path:
    ...
```

Returns an expanded `Path` for an existing file with an accepted extension.
Raises `TypeError`, `FileNotFoundError`, or `ValueError` as described above.

### `is_valid_video_path`

```python
def is_valid_video_path(video_path: Union[str, Path]) -> bool:
    ...
```

Returns `True` only when `validate_video_path` succeeds. It catches validation
errors and returns `False`, making it suitable for preflight checks.

## 5. Runtime Controls

| Event | Action |
| --- | --- |
| `arrow_left`, `a` | X minus `0.25` |
| `arrow_right`, `d` | X plus `0.25` |
| `arrow_up`, `w` | Z plus `0.25` |
| `arrow_down`, `s` | Z minus `0.25` |
| `r` | Position `(0, 8, 0)`, HPR `(0, 0, 0)` |
| `mouse1` | Start drag tracking |
| `mouse1-up` | End drag tracking |

When not dragging, automatic heading is `task.time * 30.0` degrees. During a
drag, horizontal mouse movement changes heading and vertical movement changes
pitch.

## 6. Import Behavior

The package initializer exposes all backend classes and entry points through
module-level lazy attribute loading. This means importing
`video3doverlay.utils` does not require importing any graphics library first.
Requesting a backend export imports only that backend module: Panda3D exports
require Panda3D, Pygame exports require Pygame/PyOpenGL/OpenCV, and ModernGL
exports require OpenCV/ModernGL/ModernGL Window.

## 7. Alternative Backends

The package exposes two independent runtime backends. Select one entry point
per process; each backend owns its native window and render loop.

### `PygameOpenGLEngine`

```python
class PygameOpenGLEngine:
    def __init__(self, video_path: str, width: int = 1280, height: int = 720): ...
    def run(self) -> None: ...
```

This backend uses Pygame for window and events, PyOpenGL for rendering, and
OpenCV for video frame acquisition. It draws a wireframe sphere and supports
WASD/arrow movement, `R`, mouse dragging, and `Escape` to exit.

```python
from video3doverlay import play_video_with_pygame_opengl

play_video_with_pygame_opengl("assets/demo.mp4")
```

### `OpenCVModernGLEngine`

```python
class OpenCVModernGLEngine:
    def __init__(self, video_path: str, width: int = 1280, height: int = 720,
                 depth_enabled: bool = False, depth_model: str = "MiDaS_small",
                 device: Optional[str] = None): ...
    def run(self) -> None: ...
```

This backend uses OpenCV to read frames and detect large moving regions with
classical background subtraction. ModernGL uploads and displays the processed
frames. When `depth_enabled=True`, PyTorch runs the selected MiDaS model and a
colored relative-depth visualization is blended into each frame.

```python
from video3doverlay import play_video_with_opencv_moderngl

play_video_with_opencv_moderngl(
    "assets/demo.mp4", depth_enabled=True, device="cuda"
)
```

### `DepthEstimator`

```python
class DepthEstimator:
    def __init__(self, model_type: str = "MiDaS_small",
                 device: Optional[str] = None): ...
    def estimate(self, frame_bgr: Any) -> Any: ...
```

`DepthEstimator` lazily loads MiDaS through PyTorch Hub. `device=None` selects
CUDA when available and otherwise CPU. `estimate()` accepts an OpenCV BGR
frame and returns a normalized float depth array with matching height and
width. The values are relative depth scores, not metric distances.

`select_depth_device(device=None)` returns an explicit device unchanged, or
automatically selects `cuda`/`cpu`; it returns `unavailable` if PyTorch is not
installed.

Both alternatives raise `RuntimeError` when their dependencies are missing or
the video cannot be opened. Neither backend uses AI.

### `play_video_with_depth_overlay`

```python
def play_video_with_depth_overlay(
    video_path: str,
    depth_model: str = "MiDaS_small",
    device: Optional[str] = None,
) -> None: ...
```

This convenience function is equivalent to the OpenCV + ModernGL backend with
`depth_enabled=True`. It loads MiDaS through PyTorch Hub and uses CUDA when
available unless `device` is explicitly set.
