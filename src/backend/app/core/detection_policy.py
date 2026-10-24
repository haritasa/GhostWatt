"""Compatibility module exposing the backend-owned detection policy."""

from app.core.config import DetectionPolicy, settings

policy: DetectionPolicy = settings.DETECTION_POLICY

__all__ = ["DetectionPolicy", "policy"]
