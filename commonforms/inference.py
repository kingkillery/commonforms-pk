from __future__ import annotations
from ultralytics import YOLO
from pathlib import Path
from huggingface_hub import hf_hub_download

from commonforms.utils import BoundingBox, Page, Widget
from commonforms.form_creator import PyPdfFormCreator
from commonforms.exceptions import (
    EncryptedPdfError,
    InvalidConfidenceError,
    InvalidImageSizeError,
    FileNotFoundError as InputFileNotFoundError,
)
from commonforms.config import (
    DEFAULT_IMAGE_SIZE,
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_IOU_THRESHOLD,
    FAST_MODE_IOU_THRESHOLD,
    ONNX_IMAGE_SIZE,
    WIDGET_Y_ALIGNMENT_THRESHOLD,
    BOUNDING_BOX_ROUNDING_PRECISION,
    CONFIDENCE_MIN,
    CONFIDENCE_MAX,
    IMAGE_SIZE_MIN,
)

import formalpdf
import pypdfium2


# our mapping from (model_name, fast) to (repo_id, filename) for the huggingface hub
models = {
    ("FFDNET-S", True): ("jbarrow/FFDNet-S-cpu", "FFDNet-S.onnx"),
    ("FFDNET-S", False): ("jbarrow/FFDNet-S", "FFDNet-S.pt"),
    ("FFDNET-L", True): ("jbarrow/FFDNet-L-cpu", "FFDNet-L.onnx"),
    ("FFDNET-L", False): ("jbarrow/FFDNet-L", "FFDNet-L.pt"),
}


class FFDNetDetector:
    """Form field detection using YOLO-based FFDNet models.

    This class provides functionality to detect form fields (TextBox, ChoiceButton,
    Signature) in PDF page images using pre-trained FFDNet models.

    Attributes:
        device: The device to run inference on (e.g., "cpu", "cuda", or GPU index).
        fast: Whether to use ONNX model for faster CPU inference.
        model: The loaded YOLO model instance.
        id_to_cls: Mapping from class IDs to widget type names.

    Example:
        >>> detector = FFDNetDetector("FFDNet-L", device="cpu")
        >>> pages = render_pdf("input.pdf")
        >>> widgets = detector.extract_widgets(pages, confidence=0.3)
    """

    def __init__(
        self, model_or_path: str, device: int | str = "cpu", fast: bool = False
    ) -> None:
        """Initialize the FFDNet detector.

        Args:
            model_or_path: Model name ("FFDNet-S" or "FFDNet-L") or path to a
                custom model file (.pt or .onnx).
            device: Device for inference. Use "cpu", "cuda", or an integer GPU index.
            fast: If True, use ONNX model for ~50% faster CPU inference with
                a small accuracy trade-off.
        """
        self.device = device
        self.fast = fast

        model_path = self.get_model_path(model_or_path, device, fast)
        self.model = YOLO(model_path, task="detect")

        self.id_to_cls = {0: "TextBox", 1: "ChoiceButton", 2: "Signature"}

    def get_model_path(
        self, model_or_path: str, device: int | str = "cpu", fast: bool = False
    ) -> str:
        """
        Construct the path to the model weights based on:
         (a) the requested model (in the package or external path)
         (b) --fast (if enabled, use ONNX, otherwise use pt)
        """
        model_upper = model_or_path.upper()
        if model_upper in ["FFDNET-S", "FFDNET-L"]:
            # download the model, will just use the cached version if it already exists
            repo_id, filename = models[(model_upper, fast)] 
            model_path = hf_hub_download(repo_id=repo_id, filename=filename) 
        else:
            model_path = model_or_path

        return model_path

    def extract_widgets(
        self,
        pages: list[Page],
        confidence: float = DEFAULT_CONFIDENCE_THRESHOLD,
        image_size: int = DEFAULT_IMAGE_SIZE,
    ) -> dict[int, list[Widget]]:
        """Extract form field widgets from rendered PDF pages.

        Runs the detection model on each page image and returns detected widgets
        organized by page number, sorted in approximate reading order.

        Args:
            pages: List of Page objects containing rendered page images.
            confidence: Minimum confidence threshold for detections (0.0 to 1.0).
                Lower values detect more widgets but may include false positives.
            image_size: Image size for model inference. Ignored in fast mode
                where ONNX models use a fixed size.

        Returns:
            Dictionary mapping page indices to lists of detected Widget objects.
            Pages with no detections are omitted from the dictionary.
        """
        if self.fast:
            # ONNX models are compiled with a fixed input size
            results = [
                self.model.predict(
                    p.image,
                    iou=FAST_MODE_IOU_THRESHOLD,
                    conf=confidence,
                    augment=False,
                    imgsz=ONNX_IMAGE_SIZE,
                    # pass verbose=False to avoid synchronous stdout blocking overhead
                    verbose=False,
                )
                for p in pages
            ]
        else:
            results = self.model.predict(
                [p.image for p in pages],
                iou=DEFAULT_IOU_THRESHOLD,
                conf=confidence,
                augment=True,
                imgsz=image_size,
                device=self.device,
                # pass verbose=False to avoid synchronous stdout blocking overhead
                verbose=False,
            )

        widgets = {}
        for page_ix, result in enumerate(results):
            if isinstance(result, list):
                result = result[0]
            # no predictions, skip page
            if result is None or result.boxes is None:
                continue

            widgets[page_ix] = []
            for box in result.boxes.cpu().numpy():
                x, y, w, h = box.xywhn[0]
                cls_id = int(box.cls.item())
                widget_type = self.id_to_cls[cls_id]

                widgets[page_ix].append(
                    Widget(
                        widget_type=widget_type,
                        bounding_box=BoundingBox.from_yolo(cx=x, cy=y, w=w, h=h),
                        page=page_ix,
                    )
                )

            # do our best to sort the widgets into something resembling reading
            # order; this is important for being able to Tab/Shift-Tab back and
            # forth to navigate the page.
            widgets[page_ix] = sort_widgets(widgets[page_ix])

        return widgets


def sort_widgets(widgets: list[Widget]) -> list[Widget]:
    """
    Sort widgets in approximate reading order (left-to-right/top-to-bottom)
    which makes the LLMs less likely to mess up.
    """
    # Sort first by y coordinate, then x coordinate for reading order
    sorted_widgets = sorted(
        widgets,
        key=lambda w: (
            round(w.bounding_box.y0, BOUNDING_BOX_ROUNDING_PRECISION),
            w.bounding_box.x0,
        ),
    )

    # Find rows of widgets by grouping those with similar y coordinates
    y_threshold = WIDGET_Y_ALIGNMENT_THRESHOLD
    lines = []
    current_line = []

    for widget in sorted_widgets:
        if (
            not current_line
            or abs(widget.bounding_box.y0 - current_line[0].bounding_box.y0)
            < y_threshold
        ):
            current_line.append(widget)
        else:
            # Sort widgets in line by x coordinate
            current_line.sort(key=lambda w: w.bounding_box.x0)
            lines.append(current_line)
            current_line = [widget]

    if current_line:
        current_line.sort(key=lambda w: w.bounding_box.x0)
        lines.append(current_line)

    # Flatten the lines back into single list
    return [widget for line in lines for widget in line]


def render_pdf(pdf_path: str) -> list[Page]:
    """Render all pages of a PDF document as images.

    Args:
        pdf_path: Path to the PDF file to render.

    Returns:
        List of Page objects, each containing a PIL Image and dimensions.

    Raises:
        pypdfium2.PdfiumError: If the PDF is encrypted or cannot be opened.
    """
    pages = []
    doc = formalpdf.open(pdf_path)
    try:
        for page in doc:
            image = page.render()
            pages.append(Page(image=image, width=image.width, height=image.height))
        return pages
    finally:
        doc.document.close()


def _validate_inputs(
    input_path: str | Path,
    confidence: float,
    image_size: int,
) -> None:
    """Validate input parameters for prepare_form.

    Args:
        input_path: Path to the input PDF file.
        confidence: Confidence threshold for detection.
        image_size: Image size for inference.

    Raises:
        InputFileNotFoundError: If input file does not exist.
        InvalidConfidenceError: If confidence is outside [0.0, 1.0].
        InvalidImageSizeError: If image_size is not positive.
    """
    # Validate input file exists
    input_path = Path(input_path)
    if not input_path.exists():
        raise InputFileNotFoundError(str(input_path), "PDF file")

    # Validate confidence threshold
    if not (CONFIDENCE_MIN <= confidence <= CONFIDENCE_MAX):
        raise InvalidConfidenceError(confidence)

    # Validate image size
    if image_size < IMAGE_SIZE_MIN:
        raise InvalidImageSizeError(image_size)


def prepare_form(
    input_path: str | Path,
    output_path: str | Path,
    *,
    model_or_path: str = "FFDNet-L",
    keep_existing_fields: bool = False,
    use_signature_fields: bool = False,
    device: int | str = "cpu",
    image_size: int = DEFAULT_IMAGE_SIZE,
    confidence: float = DEFAULT_CONFIDENCE_THRESHOLD,
    fast: bool = False,
    multiline: bool = False,
) -> None:
    """Automatically detect and add form fields to a PDF document.

    This is the main entry point for CommonForms. It processes an input PDF,
    detects form fields using a trained model, and creates a new PDF with
    the detected fields added as interactive form elements.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path where the output PDF with form fields will be saved.
        model_or_path: Model name ("FFDNet-S" or "FFDNet-L") or path to custom model.
        keep_existing_fields: If True, preserve existing form fields in the PDF.
        use_signature_fields: If True, create signature fields for detected
            signatures; otherwise, create text fields.
        device: Device for model inference ("cpu", "cuda", or GPU index).
        image_size: Image size for inference. Higher values may improve accuracy.
        confidence: Detection confidence threshold (0.0 to 1.0).
        fast: If True, use ONNX model for faster CPU inference.
        multiline: If True, create multiline text fields.

    Raises:
        InputFileNotFoundError: If input PDF file does not exist.
        InvalidConfidenceError: If confidence is not in range [0.0, 1.0].
        InvalidImageSizeError: If image_size is not positive.
        EncryptedPdfError: If the input PDF is encrypted.

    Example:
        >>> from commonforms import prepare_form
        >>> prepare_form("input.pdf", "output.pdf", confidence=0.4)
    """
    # Validate inputs before processing
    _validate_inputs(input_path, confidence, image_size)

    detector = FFDNetDetector(model_or_path, device=device, fast=fast)

    try:
        pages = render_pdf(input_path)
    except pypdfium2._helpers.misc.PdfiumError:
        raise EncryptedPdfError

    results = detector.extract_widgets(
        pages, confidence=confidence, image_size=image_size
    )

    writer = PyPdfFormCreator(input_path)
    if not keep_existing_fields:
        writer.clear_existing_fields()

    for page_ix, widgets in results.items():
        for i, widget in enumerate(widgets):
            name = f"{widget.widget_type.lower()}_{widget.page}_{i}"

            if widget.widget_type == "TextBox":
                writer.add_text_box(name, page_ix, widget.bounding_box, multiline=multiline)
            elif widget.widget_type == "ChoiceButton":
                writer.add_checkbox(name, page_ix, widget.bounding_box)
            elif widget.widget_type == "Signature":
                if use_signature_fields:
                    writer.add_signature(name, page_ix, widget.bounding_box)
                else:
                    writer.add_text_box(name, page_ix, widget.bounding_box)

    writer.save(output_path)
    writer.close()
