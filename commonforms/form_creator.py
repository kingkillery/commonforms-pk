"""
PDF form field creation utilities.

This module provides classes and functions for creating PDF form fields
(text boxes, checkboxes, signatures) and adding them to PDF documents.
"""

from pypdf import PdfWriter, PdfReader
from pypdf.annotations import AnnotationDictionary
from pypdf.generic import (
    NameObject,
    ArrayObject,
    NumberObject,
    TextStringObject,
    DictionaryObject,
)

from commonforms.utils import BoundingBox
from commonforms.config import PDF_MULTILINE_FLAG


def rect_for(bounding_box: BoundingBox, page) -> ArrayObject:
    """Convert a normalized BoundingBox to PDF rectangle coordinates.

    Transforms normalized coordinates (0.0-1.0) to absolute PDF page
    coordinates, accounting for the page's cropbox or mediabox dimensions.
    Handles coordinate system conversion from top-left origin to PDF's
    bottom-left origin.

    Args:
        bounding_box: Normalized bounding box with coordinates in [0.0, 1.0].
        page: pypdf Page object to get dimensions from.

    Returns:
        ArrayObject containing [x0, y0, x1, y1] in PDF coordinate space.
    """
    # because the PDFs are rendered to images with the CropBox, we need to use
    # that as the offset for where we insert the widgets
    page = page.cropbox if page.cropbox else page.mediabox
    # here I'm flipping the page.top/page.bottom to change from top-left origin
    # to bottom-right origin; this results in a negative height, but the math
    # works out in the end
    page_x0, page_y0, page_x1, page_y1 = (page.left, page.top, page.right, page.bottom)
    page_width = page_x1 - page_x0
    page_height = page_y1 - page_y0

    x0 = page_x0 + (bounding_box.x0 * page_width)
    y0 = page_y0 + (bounding_box.y1 * page_height)
    x1 = page_x0 + (bounding_box.x1 * page_width)
    y1 = page_y0 + (bounding_box.y0 * page_height)

    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0

    return ArrayObject(
        [
            NumberObject(x0),
            NumberObject(y0),
            NumberObject(x1),
            NumberObject(y1),
        ]
    )


class Textbox(AnnotationDictionary):
    """PDF text field annotation.

    Creates a text input form field that users can fill in.

    Args:
        name: Unique field name used for form data identification.
        rect: PDF rectangle coordinates [x0, y0, x1, y1] for field placement.
        multiline: If True, allows multi-line text input.
        value: Initial text value for the field.
        default_value: Default value restored when form is reset.
    """

    def __init__(
        self,
        name: str,
        rect: ArrayObject,
        *,
        multiline: bool = False,
        value: str | None = None,
        default_value: str | None = None,
    ):
        super().__init__()

        self.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Tx"),
                NameObject("/T"): TextStringObject(name or ""),
                NameObject("/V"): TextStringObject(value or ""),
                NameObject("/DV"): TextStringObject(default_value or ""),
                NameObject("/Ff"): NumberObject(0 if not multiline else PDF_MULTILINE_FLAG),
                NameObject("/Rect"): rect,
                NameObject("/DA"): TextStringObject("/Helv 0 Tf 0 0 0 rg"),
            }
        )


class Checkbox(AnnotationDictionary):
    """PDF checkbox button annotation.

    Creates a checkbox form field that users can toggle on/off.

    Args:
        name: Unique field name used for form data identification.
        rect: PDF rectangle coordinates [x0, y0, x1, y1] for field placement.
        multiline: Unused parameter (kept for API consistency).
        value: Initial checked state (True = checked, False = unchecked).
        default_value: Unused parameter (kept for API consistency).
    """

    def __init__(
        self,
        name: str,
        rect: ArrayObject,
        *,
        multiline: bool = False,
        value: bool | None = None,
        default_value: str | None = None,
    ):
        super().__init__()
        pdf_value = NameObject("/Off") if not value else NameObject("/Yes")

        self.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Btn"),
                NameObject("/Ff"): NumberObject(0),
                NameObject("/Rect"): rect,
                NameObject("/V"): pdf_value,
                NameObject("/AS"): pdf_value,
                NameObject("/T"): TextStringObject(name),
            }
        )


class Signature(AnnotationDictionary):
    """PDF signature field annotation.

    Creates a digital signature field where users can add their signature.

    Args:
        name: Unique field name used for form data identification.
        rect: PDF rectangle coordinates [x0, y0, x1, y1] for field placement.
    """

    def __init__(self, name: str, rect: ArrayObject):
        super().__init__()
        self.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Widget"),
                NameObject("/FT"): NameObject("/Sig"),
                NameObject("/T"): TextStringObject(name),
                NameObject("/Rect"): rect,
                NameObject("/F"): NumberObject(4),
            }
        )


class PyPdfFormCreator:
    """PDF form field manager using pypdf.

    Provides methods to add form fields (text boxes, checkboxes, signatures)
    to an existing PDF document and save the result.

    Example:
        >>> creator = PyPdfFormCreator("input.pdf")
        >>> creator.add_text_box("name_field", 0, bounding_box)
        >>> creator.add_checkbox("agree_terms", 0, bounding_box)
        >>> creator.save("output.pdf")
        >>> creator.close()

    Attributes:
        reader: PdfReader for the source document.
        writer: PdfWriter for creating the output document.
    """

    def __init__(self, input_path: str):
        """Initialize the form creator with a PDF file.

        Args:
            input_path: Path to the input PDF file.
        """
        self.reader = PdfReader(input_path)
        # NOTE: Commenting out add_form_topname as it causes lazy loading issues with pages
        # self.reader.add_form_topname("original")
        self.writer = PdfWriter(clone_from=self.reader)
        # Cache the pages list because accessing self.writer.pages is expensive
        self.pages = self.writer.pages
        # Keep reader open until we're done - pypdf uses lazy loading

        zapf_font = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/ZapfDingbats"),
                NameObject("/Name"): NameObject("/ZaDb"),
            }
        )
        self.zapf_font = self.writer._add_object(zapf_font)

    def clear_existing_fields(self):
        """Clear all existing form fields from the PDF."""
        # Get the root form object if it exists
        if hasattr(self.writer, "_root_object"):
            root = self.writer._root_object
            if NameObject("/AcroForm") in root:
                acroform = root[NameObject("/AcroForm")]
                if NameObject("/Fields") in acroform:
                    # Replace with empty array to clear all fields
                    acroform[NameObject("/Fields")] = ArrayObject()

        # Also clear widget annotations from each page
        for page in self.pages:
            if NameObject("/Annots") in page:
                page[NameObject("/Annots")] = ArrayObject()

    def add_text_box(
        self,
        name: str,
        page: int,
        bounding_box: BoundingBox,
        multiline: bool = False,
    ) -> None:
        """Add a text input field to the PDF.

        Args:
            name: Unique field name for form data identification.
            page: Zero-indexed page number to add the field to.
            bounding_box: Normalized coordinates for field placement.
            multiline: If True, allows multi-line text input.
        """
        rect = rect_for(bounding_box, self.pages[page])
        textbox = Textbox(name=name, rect=rect, multiline=multiline)
        self.writer.add_annotation(page_number=page, annotation=textbox)

    def add_checkbox(self, name: str, page: int, bounding_box: BoundingBox) -> None:
        """Add a checkbox field to the PDF.

        Args:
            name: Unique field name for form data identification.
            page: Zero-indexed page number to add the field to.
            bounding_box: Normalized coordinates for field placement.
        """
        rect = rect_for(bounding_box, self.pages[page])
        checkbox = Checkbox(name=name, rect=rect)
        self.writer.add_annotation(page_number=page, annotation=checkbox)

    def add_signature(self, name: str, page: int, bounding_box: BoundingBox) -> None:
        """Add a signature field to the PDF.

        Args:
            name: Unique field name for form data identification.
            page: Zero-indexed page number to add the field to.
            bounding_box: Normalized coordinates for field placement.
        """
        rect = rect_for(bounding_box, self.pages[page])
        signature = Signature(name=name, rect=rect)
        self.writer.add_annotation(page_number=page, annotation=signature)

    def save(self, output_path: str) -> None:
        """Save the PDF with all added form fields.

        Args:
            output_path: Path where the output PDF will be saved.
        """
        self.writer.reattach_fields()
        with open(output_path, "wb") as fp:
            self.writer.write(fp)

    def close(self) -> None:
        """Close the PDF reader and writer, releasing resources."""
        self.writer.close()
        self.reader.close()
