"""
Configuration constants for CommonForms.

This module centralizes all magic numbers and default values used throughout
the codebase, making them easier to maintain and document.
"""

# =============================================================================
# Model Inference Configuration
# =============================================================================

# Default image size (in pixels) for model inference.
# Higher values may improve detection accuracy but increase memory usage.
DEFAULT_IMAGE_SIZE: int = 1600

# Fixed image size for ONNX models (fast mode).
# ONNX models are compiled with a specific input size and cannot be changed.
ONNX_IMAGE_SIZE: int = 1216

# Default confidence threshold for detections.
# Values range from 0.0 to 1.0. Lower values detect more widgets but may
# include false positives. Higher values are more conservative.
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.3

# Intersection over Union (IoU) threshold for non-maximum suppression.
# Used to filter overlapping bounding boxes.
DEFAULT_IOU_THRESHOLD: float = 0.1

# IoU threshold for fast mode (ONNX).
# Set to 1.0 to effectively disable NMS in fast mode.
FAST_MODE_IOU_THRESHOLD: float = 1.0


# =============================================================================
# Widget Sorting Configuration
# =============================================================================

# Threshold for considering widgets on the same line when sorting.
# Widgets with y-coordinates within this threshold are grouped together.
# Value is in normalized coordinates (0.0 to 1.0).
WIDGET_Y_ALIGNMENT_THRESHOLD: float = 0.01

# Number of decimal places for rounding y-coordinates when sorting widgets.
# Helps handle minor vertical alignment differences.
BOUNDING_BOX_ROUNDING_PRECISION: int = 3


# =============================================================================
# PDF Form Field Configuration
# =============================================================================

# Bit flag for multiline text fields in PDF form fields.
# This is the 13th bit (0-indexed as 12) in the field flags.
# Reference: PDF specification, Table 226 - Field flags for text fields.
PDF_MULTILINE_FLAG: int = 1 << 12


# =============================================================================
# Validation Limits
# =============================================================================

# Valid range for confidence threshold
CONFIDENCE_MIN: float = 0.0
CONFIDENCE_MAX: float = 1.0

# Minimum valid image size
IMAGE_SIZE_MIN: int = 32
