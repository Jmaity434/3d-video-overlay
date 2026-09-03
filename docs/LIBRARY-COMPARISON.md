# Five-Library Comparison

This project uses seven runtime packages across three rendering approaches.
The five core libraries are `Panda3D`, `Pygame`, `PyOpenGL`, `OpenCV`, and
`ModernGL`; `PyTorch` and `torchvision` provide the optional MiDaS depth model.
No generative AI or semantic AI service is used. Motion detection remains
classical OpenCV processing.

## Direct Comparison Table

| Feature / Goal | Panda3D | Pygame + PyOpenGL | OpenCV + ModernGL |
| --- | --- | --- | --- |
| Primary use case | Complex 3D models & characters | Custom spatial shapes & text | Object tracking & computer vision |
| Learning curve | Medium (game engine concepts) | High (requires graphics math) | Low to medium (Pythonic APIs) |
| 3D file support (`.gltf` / `.obj`) | Native and excellent | Requires manual parsing scripts | Requires manual parsing scripts |
| Performance | Ultra-high (GPU optimized) | Ultra-high (GPU optimized) | High (CPU/GPU hybrid) |

## Backend Mapping in This Repository

| Backend | Python entry point | Libraries used | Current behavior |
| --- | --- | --- | --- |
| Panda3D | `play_video_with_3d_overlay` | Panda3D | `MovieTexture`, 3D model loading, wireframe fallback, keyboard/mouse control |
| Pygame + PyOpenGL | `play_video_with_pygame_opengl` | Pygame, PyOpenGL, OpenCV | OpenCV video frames, OpenGL background, interactive wireframe sphere |
| OpenCV + ModernGL | `play_video_with_opencv_moderngl` | OpenCV, ModernGL, ModernGL Window | OpenCV video frames, classical motion rectangles, ModernGL textured output |
| OpenCV + PyTorch + ModernGL | `play_video_with_opencv_moderngl(..., depth_enabled=True)` | OpenCV, PyTorch, torchvision, ModernGL | MiDaS relative-depth visualization with CUDA/CPU device selection |

The backends are alternatives. An application selects one entry point rather
than creating three graphics contexts for the same video. This prevents
Panda3D, Pygame, and ModernGL from competing for one native window.

## What the Table Means

- **Panda3D** is the recommended backend for imported 3D assets and characters.
  Its loader handles supported model formats and it provides the complete
  scene graph, task loop, and input system.
- **Pygame + PyOpenGL** is the lower-level custom-drawing route. The current
  backend uses OpenCV for frame acquisition and PyOpenGL for the window and
  overlay drawing; imported 3D file parsing is intentionally not automatic.
- **OpenCV + ModernGL** is the computer-vision route. OpenCV reads frames and
  performs classical motion detection, while ModernGL uploads and displays
  the processed frame on the GPU. It does not claim semantic recognition.
- **PyTorch depth** is an opt-in enhancement to that route. MiDaS estimates
  relative depth per frame; a CUDA GPU is recommended, while CPU inference is
  supported as a slower fallback.

## Selection Guide

Choose Panda3D for a model-centric 3D application, Pygame + PyOpenGL for
custom low-level shapes or text, and OpenCV + ModernGL when frame processing or
motion detection is the primary requirement. All three remain runtime choices
and share the repository's path-validation policy.