"""OpenCV, PyTorch, and ModernGL backend for depth-aware video output."""

from typing import Optional

from .utils import validate_video_path
from .depth import DepthEstimator, select_depth_device


class OpenCVModernGLEngine:
    """Display OpenCV frames through a ModernGL textured OpenGL pipeline."""

    def __init__(
        self,
        video_path: str,
        width: int = 1280,
        height: int = 720,
        depth_enabled: bool = False,
        depth_model: str = "MiDaS_small",
        device: Optional[str] = None,
    ) -> None:
        self.video_path = validate_video_path(video_path)
        self.width = width
        self.height = height
        self.depth_enabled = depth_enabled
        self.depth_model = depth_model
        self.device = select_depth_device(device)

    def run(self) -> None:
        """Run the ModernGL backend using a GLFW window supplied by moderngl-window."""
        try:
            import cv2
            import moderngl
            import moderngl_window as mglw
        except ImportError as error:
            raise RuntimeError(
                "The ModernGL backend requires opencv-python, moderngl, and "
                "moderngl-window"
            ) from error

        capture = cv2.VideoCapture(str(self.video_path))
        if not capture.isOpened():
            raise RuntimeError("OpenCV could not open video: {}".format(self.video_path))
        motion_detector = cv2.createBackgroundSubtractorMOG2()
        depth_estimator = (
            DepthEstimator(self.depth_model, self.device)
            if self.depth_enabled
            else None
        )

        class VideoWindow(mglw.WindowConfig):
            gl_version = (3, 3)
            window_size = (self.width, self.height)
            title = "3d-video-overlay - OpenCV + ModernGL"
            aspect_ratio = self.width / float(self.height)

            def __init__(window_self, **kwargs):
                super().__init__(**kwargs)
                window_self.program = window_self.ctx.program(
                    vertex_shader=(
                        "#version 330\n"
                        "in vec2 in_pos; in vec2 in_uv; out vec2 uv;\n"
                        "void main() { uv = in_uv; gl_Position = vec4(in_pos, 0.0, 1.0); }"
                    ),
                    fragment_shader=(
                        "#version 330\n"
                        "uniform sampler2D video; in vec2 uv; out vec4 color;\n"
                        "void main() { color = texture(video, uv); }"
                    ),
                )
                window_self.texture = window_self.ctx.texture(
                    (self.width, self.height), 3
                )
                import struct

                vertices = (
                    -1.0, -1.0, 0.0, 1.0,
                    1.0, -1.0, 1.0, 1.0,
                    1.0, 1.0, 1.0, 0.0,
                    -1.0, 1.0, 0.0, 0.0,
                )
                window_self.vertex_buffer = window_self.ctx.buffer(
                    data=struct.pack("16f", *vertices)
                )
                window_self.vertex_array = window_self.ctx.vertex_array(
                    window_self.program,
                    [(window_self.vertex_buffer, "2f 2f", "in_pos", "in_uv")],
                )

            def render(window_self, current_time: float, frame_time: float) -> None:
                success, frame = capture.read()
                if not success:
                    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    return
                motion_mask = motion_detector.apply(frame)
                contours, _ = cv2.findContours(
                    motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                for contour in contours:
                    if cv2.contourArea(contour) < 500.0:
                        continue
                    x, y, box_width, box_height = cv2.boundingRect(contour)
                    cv2.rectangle(
                        frame, (x, y), (x + box_width, y + box_height),
                        (0, 255, 255), 2,
                    )
                if depth_estimator is not None:
                    depth = depth_estimator.estimate(frame)
                    depth_image = cv2.applyColorMap(
                        (depth * 255.0).astype("uint8"), cv2.COLORMAP_MAGMA
                    )
                    frame = cv2.addWeighted(frame, 0.72, depth_image, 0.28, 0.0)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.width, self.height))
                window_self.texture.write(frame.tobytes())
                window_self.texture.use(0)
                window_self.ctx.clear(0.02, 0.02, 0.02)
                window_self.vertex_array.render(mode=moderngl.TRIANGLE_FAN, vertices=4)

        try:
            mglw.run_window_config(VideoWindow)
        finally:
            capture.release()


def play_video_with_opencv_moderngl(
    video_path: str,
    depth_enabled: bool = False,
    depth_model: str = "MiDaS_small",
    device: Optional[str] = None,
) -> None:
    """Run the OpenCV + ModernGL backend."""
    OpenCVModernGLEngine(
        video_path, depth_enabled=depth_enabled, depth_model=depth_model, device=device
    ).run()


def play_video_with_depth_overlay(
    video_path: str,
    depth_model: str = "MiDaS_small",
    device: Optional[str] = None,
) -> None:
    """Run the OpenCV + ModernGL backend with PyTorch depth enabled."""
    play_video_with_opencv_moderngl(
        video_path, depth_enabled=True, depth_model=depth_model, device=device
    )