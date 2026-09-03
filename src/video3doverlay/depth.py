"""PyTorch depth estimation with automatic CPU/GPU device selection."""

from typing import Any, Optional


class DepthEstimator:
    """Estimate relative scene depth with the MiDaS PyTorch model.

    The model is loaded lazily because it may download weights on first use.
    MiDaS produces relative depth, not metric distance in physical units.
    """

    def __init__(
        self,
        model_type: str = "MiDaS_small",
        device: Optional[str] = None,
    ) -> None:
        self.model_type = model_type
        self.device_name = device
        self._torch: Any = None
        self._model: Any = None
        self._transform: Any = None

    @property
    def device(self) -> str:
        """Return the selected torch device name."""
        if self.device_name is not None:
            return self.device_name
        self._load_runtime()
        return str(self.device_name)

    def _load_runtime(self) -> None:
        if self._torch is not None:
            return
        try:
            import torch

            self._torch = torch
            if self.device_name is None:
                self.device_name = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = torch.hub.load(
                "intel-isl/MiDaS", self.model_type, trust_repo=True
            )
            transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
            self._transform = (
                transforms.small_transform
                if self.model_type == "MiDaS_small"
                else transforms.dpt_transform
            )
            self._model.to(self.device_name)
            self._model.eval()
        except Exception as error:
            raise RuntimeError(
                "Unable to load the PyTorch depth model '{}'. "
                "The first run needs network access to download MiDaS weights."
                .format(self.model_type)
            ) from error

    def estimate(self, frame_bgr: Any) -> Any:
        """Return a float32 relative-depth image matching the input dimensions."""
        self._load_runtime()
        import cv2

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        input_batch = self._transform(frame_rgb).to(self.device_name)
        with self._torch.inference_mode():
            prediction = self._model(input_batch)
            prediction = self._torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=frame_rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
        depth = prediction.cpu().numpy()
        minimum, maximum = float(depth.min()), float(depth.max())
        return (depth - minimum) / (maximum - minimum + 1e-6)


def select_depth_device(device: Optional[str] = None) -> str:
    """Select an explicit device or prefer CUDA when it is available."""
    if device is not None:
        return device
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "unavailable"