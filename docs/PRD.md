# Product Requirements Document

## 1. Document Control

| Field | Value |
| --- | --- |
| Product | 3D Video Overlay |
| Repository | `3d-video-overlay` |
| Python package | `video3doverlay` |
| Version baseline | `0.1.0` |
| Status | Alpha / developer preview |
| Owner | Jmaity434 |

## 2. Product Summary

`video3doverlay` lets a Python developer play a normal 2D video and render a
live, interactive 3D object over the video in the same Panda3D application.
The video remains a runtime media asset. The library does not transcode,
modify, or export the source video.

The initial product is intentionally small: one blocking convenience function,
one configurable `ShowBase` subclass, an optional Panda3D model, and a
procedural wireframe fallback that guarantees a visible overlay during setup.

## 3. Problem Statement

Developers who need a quick visual prototype for video annotation, education,
previsualization, or interactive demonstrations should not have to build the
video texture, scene graph, input bindings, and animation loop themselves.
They need a reliable starting point that keeps video playback and 3D rendering
in one real-time process.

## 4. Goals

### 4.1 Version 0.1 goals

- Accept a local video path and validate it before opening a graphics window.
- Support `.mp4`, `.avi`, and `.mkv` filename extensions.
- Render the video on a full-window 2D card behind the 3D scene.
- Start looping video playback and synchronize audio when available.
- Load an optional model with Panda3D's loader.
- Render a cyan wireframe fallback when a model is absent or fails to load.
- Provide automatic rotation and simple keyboard/mouse interaction.
- Provide opt-in classical motion tracking that aligns the overlay to moving
  video content without AI.
- Support a live OpenCV camera source and optional processed-frame recording.
- Expose a small top-level API that is easy to discover.
- Provide headless validation tests and GitHub Actions verification.

### 4.2 Future goals

- Explicit window, camera, playback, and overlay configuration objects.
- Pause, resume, seek, volume, and playback-state controls.
- Model transform, scale, material, and animation configuration.
- Camera calibration or video-to-world coordinate mapping.
- Optional off-screen rendering and embedding into an existing application.
- Broader media backend and codec diagnostics.
- Published versioned wheels on PyPI.

## 5. Non-goals

- Editing, transcoding, exporting, or permanently compositing video.
- Semantic recognition of people or markers, and calibrated camera-pose
  estimation.
- Exact recording of a Panda3D 3D framebuffer from the alternative backend.
- A complete media player UI.
- A guarantee that every codec accepted by a file extension is supported by
  the installed Panda3D build.

## 6. Target Users and Use Cases

### Developers

A developer can install the package, provide a local video, and display an
interactive model with minimal code.

### Technical artists and educators

A user can demonstrate spatial concepts by moving and rotating a model while
video continues in the background.

### Prototype teams

A team can validate a real-time overlay concept without creating an exported
intermediate video or designing a complete rendering loop.

## 7. User Experience Requirements

- Invalid paths must fail before Panda3D creates a window.
- A missing or unreadable model must not prevent the video window from opening;
  the wireframe fallback should be used.
- The background must remain behind all 3D overlay content.
- Keyboard interaction must not stop video playback.
- Mouse interaction must provide immediate visible rotation feedback.
- Runtime failures must be logged with the relevant asset path.
- The README must provide a copy-and-paste example and expected result.

## 8. Functional Requirements

| ID | Requirement | Baseline acceptance |
| --- | --- | --- |
| FR-01 | Validate video path | Existing file and accepted extension required |
| FR-02 | Load video | Use Panda3D `MovieTexture` |
| FR-03 | Render background | Attach a textured card to `render2d` in background bin |
| FR-04 | Audio | Start and synchronize the movie audio when provided |
| FR-05 | Model | Load optional model using `loader.loadModel()` |
| FR-06 | Fallback | Render procedural wireframe when model is absent or fails |
| FR-07 | Animation | Rotate overlay every frame while not dragging |
| FR-08 | Keyboard | Arrow keys and `WASD` translate on X/Z |
| FR-09 | Mouse | Primary-button drag changes heading and pitch |
| FR-10 | Reset | `R` restores position and rotation |
| FR-11 | Tracking | Optional OpenCV motion alignment updates overlay X/Z and scale |
| FR-12 | Camera | OpenCV camera index can replace a video file |
| FR-13 | Recording | Optional MP4 recording of processed OpenCV frames |

## 9. Quality Requirements

- Python `>=3.8` support.
- Type hints on public and internal function signatures.
- No generated media or build artifacts committed to Git.
- Source-layout packaging through Hatchling.
- Tests that do not require a display server for validation behavior.
- Clear exceptions for invalid input and video startup failure.

## 10. Success Metrics

For the alpha release:

- A new developer can install and launch the documented sample in under five
  minutes after providing a supported local video.
- Invalid paths produce actionable exceptions rather than a blank window.
- CI passes on every push to `main` and every pull request.
- The public import surface remains limited to documented entry points.

## 11. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Codec support varies by platform | Document backend limitation; preserve original loader error |
| No display in CI | Keep CI tests headless and separate runtime smoke testing |
| Model format differs by Panda3D build | Use fallback wireframe and log load failure |
| World coordinates do not match video pixels | Document as non-goal; plan calibration API |
| Window lifecycle is controlled by `ShowBase` | Keep convenience API explicit and document blocking behavior |

## 12. Release Acceptance

Version `0.1.0` is acceptable as an alpha when the package builds from the
src layout, the validation tests pass, the README sample is accurate, and the
GitHub Actions workflow is green. A future stable release should add runtime
integration tests with real media and a supported display configuration.
