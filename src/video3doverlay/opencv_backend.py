"""OpenCV and ModernGL backend for textured video plus a 3D fallback."""

from .utils import validate_video_path


class OpenCVModernGLEngine:
    """Display OpenCV frames through a ModernGL textured OpenGL pipeline."""

    def __init__(self, video_path: str, width: int = 1280, height: int = 720) -> None:
        self.video_path = validate_video_path(video_path)
        self.width = width
        self.height = height

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
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.width, self.height))
                window_self.texture.write(frame.tobytes())
                window_self.texture.use(0)
                window_self.ctx.clear(0.02, 0.02, 0.02)
                window_self.vertex_buffer.bind_to(
                    window_self.program, "in_pos", "in_uv"
                )
                window_self.ctx.render(window_self.program, mode=moderngl.TRIANGLE_FAN, vertices=4)

        try:
            mglw.run_window_config(VideoWindow)
        finally:
            capture.release()


def play_video_with_opencv_moderngl(video_path: str) -> None:
    """Run the OpenCV + ModernGL backend."""
    OpenCVModernGLEngine(video_path).run()