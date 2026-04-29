"""
Custom exceptions for CommonForms.

This module provides specific exception types for different error scenarios,
enabling better error handling and more informative error messages.
"""

from commonforms.config import IMAGE_SIZE_MIN, IMAGE_SIZE_MAX


class CommonFormsError(Exception):
    """Base exception for all CommonForms errors."""

    pass


class EncryptedPdfError(CommonFormsError):
    """Raised when attempting to process an encrypted PDF file.

    Encrypted PDFs require a password to be read and processed. CommonForms
    currently does not support password-protected PDFs.
    """

    def __init__(self, message: str = "Cannot process encrypted PDF file"):
        self.message = message
        super().__init__(self.message)


class InvalidInputError(CommonFormsError):
    """Raised when input validation fails.

    This exception is raised when the input parameters to a function
    are invalid, such as out-of-range confidence values or non-existent files.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class FileNotFoundError(InvalidInputError):
    """Raised when a required input file does not exist.

    This exception provides a more specific error than the built-in
    FileNotFoundError, with additional context about what file was expected.
    """

    def __init__(self, file_path: str, file_type: str = "file"):
        self.file_path = file_path
        self.file_type = file_type
        self.message = f"Input {file_type} not found: {file_path}"
        super().__init__(self.message)


class InvalidConfidenceError(InvalidInputError):
    """Raised when confidence threshold is outside the valid range [0.0, 1.0]."""

    def __init__(self, confidence: float):
        self.confidence = confidence
        self.message = (
            f"Confidence threshold must be between 0.0 and 1.0, got: {confidence}"
        )
        super().__init__(self.message)


class InvalidImageSizeError(InvalidInputError):
    """Raised when image size is invalid (outside allowed range)."""

    def __init__(self, image_size: int):
        self.image_size = image_size
        self.message = f"Image size must be between {IMAGE_SIZE_MIN} and {IMAGE_SIZE_MAX}, got: {image_size}"
        super().__init__(self.message)
