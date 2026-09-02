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
) -> None:
    ...
```

#### Parameters

- `video_path`: Local path to an existing `.mp4`, `.avi`, or `.mkv` file.
- `model_path`: Optional path accepted by Panda3D's `loader.loadModel()`.
  Invalid or missing models are replaced by the procedural wireframe.

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

## 3. Engine Class

### `Video3DOverlayEngine`

```python
class Video3DOverlayEngine(ShowBase):
    def __init__(
        self,
        video_path: str,
        model_path: Optional[str] = None,
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

The package initializer exposes `Video3DOverlayEngine` and
`play_video_with_3d_overlay` through module-level lazy attribute loading. This
means importing `video3doverlay.utils` does not require importing Panda3D first.
Requesting either engine export does require the declared Panda3D dependency.
