"""Pygame and PyOpenGL backend with OpenCV frame acquisition."""

import time
from typing import Optional

from .utils import validate_video_path


class PygameOpenGLEngine:
    """Render OpenCV video frames and a simple interactive sphere in OpenGL."""

    def __init__(self, video_path: str, width: int = 1280, height: int = 720) -> None:
        self.video_path = validate_video_path(video_path)
        self.width = width
        self.height = height
        self.x = 0.0
        self.z = 0.0
        self.heading = 0.0
        self.pitch = 0.0

    def run(self) -> None:
        """Open the Pygame window and run until the user closes it."""
        try:
            import cv2
            import pygame
            from OpenGL import GL, GLU
        except ImportError as error:
            raise RuntimeError(
                "The Pygame backend requires pygame, PyOpenGL, and opencv-python"
            ) from error

        capture = cv2.VideoCapture(str(self.video_path))
        if not capture.isOpened():
            raise RuntimeError("OpenCV could not open video: {}".format(self.video_path))

        pygame.init()
        window_flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        pygame.display.set_mode((self.width, self.height), window_flags)
        pygame.display.set_caption("3d-video-overlay - Pygame + PyOpenGL")
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_TEXTURE_2D)
        video_texture = GL.glGenTextures(1)
        quadric = GLU.gluNewQuadric()
        clock = pygame.time.Clock()
        dragging = False
        last_mouse: Optional[tuple] = None
        running = True

        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.x, self.z, self.heading, self.pitch = 0.0, 0.0, 0.0, 0.0
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        dragging = True
                        last_mouse = event.pos
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        dragging = False
                        last_mouse = None
                    elif event.type == pygame.MOUSEMOTION and dragging and last_mouse:
                        self.heading -= (event.pos[0] - last_mouse[0]) * 0.5
                        self.pitch += (event.pos[1] - last_mouse[1]) * 0.5
                        last_mouse = event.pos

                keys = pygame.key.get_pressed()
                self.x += (
                    keys[pygame.K_d] + keys[pygame.K_RIGHT]
                    - keys[pygame.K_a] - keys[pygame.K_LEFT]
                ) * 0.05
                self.z += (
                    keys[pygame.K_w] + keys[pygame.K_UP]
                    - keys[pygame.K_s] - keys[pygame.K_DOWN]
                ) * 0.05
                if not dragging:
                    self.heading = time.monotonic() * 30.0

                success, frame = capture.read()
                if not success:
                    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.width, self.height))
                GL.glBindTexture(GL.GL_TEXTURE_2D, video_texture)
                GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
                GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
                GL.glTexImage2D(
                    GL.GL_TEXTURE_2D, 0, GL.GL_RGB, self.width, self.height, 0,
                    GL.GL_RGB, GL.GL_UNSIGNED_BYTE, frame,
                )
                self._draw_background(GL)
                GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
                self._draw_sphere(GL, GLU, quadric)
                pygame.display.flip()
                clock.tick(60)
        finally:
            capture.release()
            GLU.gluDeleteQuadric(quadric)
            GL.glDeleteTextures([video_texture])
            pygame.quit()

    @staticmethod
    def _draw_background(gl) -> None:
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-1, 1, -1, 1, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glColor3f(1, 1, 1)
        gl.glBegin(gl.GL_QUADS)
        for vertex, tex_coord in (
            ((-1, -1), (0, 1)), ((1, -1), (1, 1)),
            ((1, 1), (1, 0)), ((-1, 1), (0, 0)),
        ):
            gl.glTexCoord2f(*tex_coord)
            gl.glVertex2f(*vertex)
        gl.glEnd()

    def _draw_sphere(self, gl, glu, quadric) -> None:
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45, self.width / float(self.height), 0.1, 100)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(self.x, self.z, -6.0)
        gl.glRotatef(self.heading, 0, 1, 0)
        gl.glRotatef(self.pitch, 1, 0, 0)
        gl.glColor3f(0.1, 0.9, 1.0)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        glu.gluSphere(quadric, 1.2, 12, 8)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)


def play_video_with_pygame_opengl(video_path: str) -> None:
    """Run the Pygame + PyOpenGL backend."""
    PygameOpenGLEngine(video_path).run()