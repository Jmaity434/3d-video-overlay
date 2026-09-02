"""Panda3D runtime for a video-backed 3D overlay."""

import logging
from typing import Any, Optional, Tuple

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import CardMaker, LineSegs, MovieTexture, NodePath

from .utils import validate_video_path

LOGGER = logging.getLogger(__name__)


class Video3DOverlayEngine(ShowBase):
    """Display a video on a 2D card while rendering an interactive 3D object."""

    def __init__(
        self,
        video_path: str,
        model_path: Optional[str] = None,
        tracking_enabled: bool = False,
    ) -> None:
        validated_video_path = validate_video_path(video_path)
        super().__init__()
        self.disableMouse()
        self._video_path = validated_video_path
        self._model_path = model_path
        self._tracking_enabled = tracking_enabled
        self._tracker: Optional[Any] = None
        self.overlay: NodePath = NodePath()
        self._last_mouse: Optional[Tuple[float, float]] = None
        self._video_texture: Optional[MovieTexture] = None
        self._setup_video_background()
        self._setup_overlay()
        if tracking_enabled:
            self._setup_tracker()
        self._bind_controls()
        self.taskMgr.add(self._animate_overlay, "video3doverlay-animation")

    def _setup_video_background(self) -> None:
        """Load and play the movie, keeping its card behind the 3D scene."""
        try:
            texture = self.loader.loadTexture(str(self._video_path))
            if texture is None or not isinstance(texture, MovieTexture):
                raise RuntimeError("Panda3D did not create a MovieTexture")
            self._video_texture = texture
            texture.setLoop(True)
            texture.play()

            sound = texture.getSound()
            if sound is not None:
                sound.setLoop(True)
                sound.play()
                texture.synchronizeTo(sound)

            card_maker = CardMaker("video-background")
            card_maker.setFrame(-1.0, 1.0, -1.0, 1.0)
            background = self.render2d.attachNewNode(card_maker.generate())
            background.setTexture(texture)
            background.setBin("background", 0)
            background.setDepthWrite(False)
            background.setDepthTest(False)
        except Exception as error:
            LOGGER.exception("Unable to stream video '%s'", self._video_path)
            raise RuntimeError(
                "Unable to load video with Panda3D: {}".format(self._video_path)
            ) from error

    def _setup_overlay(self) -> None:
        """Load the requested model, or create a visible wireframe fallback."""
        if self._model_path:
            try:
                loaded = self.loader.loadModel(self._model_path)
                if not loaded or loaded.isEmpty():
                    raise RuntimeError("loader returned an empty model")
                self.overlay = loaded
            except Exception:
                LOGGER.exception(
                    "Unable to load model '%s'; using wireframe", self._model_path
                )

        if self.overlay.isEmpty():
            self.overlay = self._create_wireframe_box()

        self.overlay.reparentTo(self.render)
        self.overlay.setPos(0.0, 8.0, 0.0)
        self.overlay.setScale(1.5)

    def _setup_tracker(self) -> None:
        """Create the optional classical OpenCV motion tracker."""
        try:
            import cv2

            tracker = cv2.VideoCapture(str(self._video_path))
            if not tracker.isOpened():
                raise RuntimeError("OpenCV could not open the tracking stream")
            self._tracker = {
                "capture": tracker,
                "detector": cv2.createBackgroundSubtractorMOG2(
                    history=120, varThreshold=32, detectShadows=False
                ),
                "cv2": cv2,
            }
        except Exception as error:
            LOGGER.exception("Unable to enable tracking for '%s'", self._video_path)
            raise RuntimeError(
                "Tracking requires a working OpenCV installation and video stream"
            ) from error

    def _create_wireframe_box(self) -> NodePath:
        lines = LineSegs("overlay-fallback")
        lines.setThickness(3.0)
        lines.setColor(0.1, 0.9, 1.0, 1.0)
        corners = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
        ]
        edges = (
            (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6),
            (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7),
        )
        for start, end in edges:
            lines.moveTo(*corners[start])
            lines.drawTo(*corners[end])
        return self.render.attachNewNode(lines.create())

    def _bind_controls(self) -> None:
        for event, x_delta, z_delta in (
            ("arrow_left", -0.25, 0.0), ("arrow_right", 0.25, 0.0),
            ("arrow_up", 0.0, 0.25), ("arrow_down", 0.0, -0.25),
            ("a", -0.25, 0.0), ("d", 0.25, 0.0),
            ("w", 0.0, 0.25), ("s", 0.0, -0.25),
        ):
            self.accept(event, self._translate, [x_delta, z_delta])
        self.accept("r", self._reset_overlay)
        self.accept("mouse1", self._start_drag)
        self.accept("mouse1-up", self._end_drag)

    def _translate(self, x_delta: float, z_delta: float) -> None:
        position = self.overlay.getPos()
        self.overlay.setPos(position.x + x_delta, position.y, position.z + z_delta)

    def _reset_overlay(self) -> None:
        self.overlay.setPos(0.0, 8.0, 0.0)
        self.overlay.setHpr(0.0, 0.0, 0.0)

    def _start_drag(self) -> None:
        self._last_mouse = self._read_mouse()

    def _end_drag(self) -> None:
        self._last_mouse = None

    def _read_mouse(self) -> Optional[Tuple[float, float]]:
        if not self.mouseWatcherNode.hasMouse():
            return None
        mouse = self.mouseWatcherNode.getMouse()
        return float(mouse.x), float(mouse.y)

    def _animate_overlay(self, task: Task) -> str:
        if self._tracker is not None:
            self._update_tracking()
        current = self._read_mouse()
        if self._last_mouse is not None and current is not None:
            delta_x = current[0] - self._last_mouse[0]
            delta_y = current[1] - self._last_mouse[1]
            self.overlay.setH(self.overlay.getH() - delta_x * 180.0)
            self.overlay.setP(self.overlay.getP() + delta_y * 180.0)
            self._last_mouse = current
        elif self._last_mouse is None:
            self.overlay.setH(task.time * 30.0)
        return Task.cont

    def _update_tracking(self) -> None:
        """Map the largest moving region from video pixels to world coordinates."""
        tracker = self._tracker
        if tracker is None:
            return
        capture = tracker["capture"]
        cv2 = tracker["cv2"]
        success, frame = capture.read()
        if not success:
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        mask = tracker["detector"].apply(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = [contour for contour in contours if cv2.contourArea(contour) >= 500.0]
        if not candidates:
            return
        x, y, width, height = cv2.boundingRect(max(candidates, key=cv2.contourArea))
        frame_height, frame_width = frame.shape[:2]
        center_x = (x + width / 2.0) / frame_width
        center_y = (y + height / 2.0) / frame_height
        self.overlay.setX((center_x - 0.5) * 8.0)
        self.overlay.setZ((0.5 - center_y) * 6.0)
        self.overlay.setScale(max(0.25, min(3.0, width / float(frame_width) * 4.0)))

    def destroy(self) -> None:
        """Release the optional tracking stream before closing Panda3D."""
        if self._tracker is not None:
            self._tracker["capture"].release()
            self._tracker = None
        super().destroy()


def play_video_with_3d_overlay(
    video_path: str,
    model_path: Optional[str] = None,
    tracking_enabled: bool = False,
) -> None:
    """Validate assets, create the engine, and enter Panda3D's main loop."""
    validate_video_path(video_path)
    app = Video3DOverlayEngine(video_path, model_path, tracking_enabled)
    app.run()