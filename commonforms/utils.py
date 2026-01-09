"""
Data structures used throughout CommonForms.

This module provides the core data classes for representing bounding boxes,
detected widgets, and rendered PDF pages.
"""

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from dataclasses import dataclass
from PIL import Image


class BoundingBox(BaseModel):
    """Normalized bounding box with coordinates in range [0.0, 1.0].

    Coordinates are normalized relative to image/page dimensions, where
    (0, 0) is the top-left corner and (1, 1) is the bottom-right corner.

    Attributes:
        x0: Left edge x-coordinate (normalized).
        y0: Top edge y-coordinate (normalized).
        x1: Right edge x-coordinate (normalized).
        y1: Bottom edge y-coordinate (normalized).
    """

    x0: float
    y0: float
    x1: float
    y1: float

    @classmethod
    def from_yolo(cls, cx: float, cy: float, w: float, h: float) -> BoundingBox:
        """Create a BoundingBox from YOLO center-format coordinates.

        Args:
            cx: Center x-coordinate (normalized).
            cy: Center y-coordinate (normalized).
            w: Width (normalized).
            h: Height (normalized).

        Returns:
            BoundingBox with corner coordinates.
        """
        return cls(x0=cx - w / 2, y0=cy - h / 2, x1=cx + w / 2, y1=cy + h / 2)


class Widget(BaseModel):
    """A detected form field widget.

    Represents a single form field detected in a PDF page, including its
    type, location, and page number.

    Attributes:
        widget_type: Type of form field ("TextBox", "ChoiceButton", or "Signature").
        bounding_box: Location of the widget on the page (normalized coordinates).
        page: Zero-indexed page number where the widget was detected.
    """

    widget_type: Literal[
        "TextBox",
        "ChoiceButton",
        "Signature",
    ]
    bounding_box: BoundingBox
    page: int


@dataclass
class Page:
    """A rendered PDF page.

    Contains the rendered image of a PDF page along with its dimensions.

    Attributes:
        image: PIL Image object of the rendered page.
        width: Width of the rendered image in pixels.
        height: Height of the rendered image in pixels.
    """

    image: Image.Image
    width: float
    height: float
