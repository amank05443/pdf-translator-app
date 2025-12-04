import PyPDF2
import pdfplumber
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
import os
import textwrap
import re
import unicodedata
from weasyprint import HTML, CSS
import html as html_module
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def normalize_devanagari_text(text: str) -> str:
    """
    Normalize Devanagari text to use precomposed characters where possible.
    Uses Unicode NFC normalization which combines base characters with combining marks.

    Args:
        text: Unicode text to normalize

    Returns:
        Normalized text with combined characters where possible
    """
    if not text or not text.strip():
        return text

    # Apply NFC (Canonical Decomposition, followed by Canonical Composition)
    # This combines base characters with their diacritical marks
    normalized_text = unicodedata.normalize('NFC', text)

    return normalized_text

def extract_text_with_ocr(pdf_path: str) -> dict:
    """
    Extract text from a PDF using OCR (for image-based/scanned PDFs).
    Uses Tesseract OCR to extract text from PDF pages converted to images.

    Args:
        pdf_path: Path to the input PDF file

    Returns:
        Dictionary containing pages with text extracted via OCR
    """
    pages_data = []
    try:
        print("Using OCR to extract text from image-based PDF...")

        # Check if tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            raise Exception("Tesseract OCR is not installed. Please install Tesseract to process image-based PDFs. Visit: https://github.com/tesseract-ocr/tesseract")

        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=300)

        for page_num, image in enumerate(images):
            # Use Tesseract to extract text with layout information
            # Using --psm 1 for automatic page segmentation with OSD (Orientation and Script Detection)
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config='--psm 1')

            # Get page dimensions from the image
            page_width, page_height = image.size
            # Convert pixels to points (1 inch = 72 points, DPI=300)
            page_width_pt = (page_width / 300) * 72
            page_height_pt = (page_height / 300) * 72

            # Group words into lines based on their positions
            lines = []
            current_line = []
            current_line_num = -1

            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                if not text:
                    continue

                conf = int(ocr_data['conf'][i])
                if conf < 30:  # Skip low-confidence words
                    continue

                line_num = ocr_data['line_num'][i]

                # If we're on a new line, save the previous one
                if line_num != current_line_num and current_line:
                    lines.append(current_line)
                    current_line = []

                current_line_num = line_num

                # Convert pixel coordinates to points
                x = (ocr_data['left'][i] / 300) * 72
                y = (ocr_data['top'][i] / 300) * 72
                width = (ocr_data['width'][i] / 300) * 72
                height = (ocr_data['height'][i] / 300) * 72

                current_line.append({
                    'text': text,
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height
                })

            # Add the last line
            if current_line:
                lines.append(current_line)

            # Convert lines to structured format
            structured_lines = []
            all_text = []

            for line in lines:
                if not line:
                    continue

                # Combine words in the line
                line_text = ' '.join([w['text'] for w in line])
                line_x = min([w['x'] for w in line])
                line_y = line[0]['y']

                # Estimate font size from word heights
                avg_height = sum([w['height'] for w in line]) / len(line)

                structured_lines.append({
                    'text': line_text,
                    'x': line_x,
                    'y': line_y,
                    'font_size': avg_height * 0.75,  # Approximate font size
                    'words': line
                })
                all_text.append(line_text)

            pages_data.append({
                'page_num': page_num + 1,
                'text': '\n'.join(all_text),
                'lines': structured_lines,
                'width': page_width_pt,
                'height': page_height_pt
            })
            print(f"OCR extracted page {page_num + 1}: {len(structured_lines)} lines, {page_width_pt:.1f}x{page_height_pt:.1f}pt")

    except Exception as e:
        raise Exception(f"Error extracting text with OCR: {str(e)}")

    return {'pages': pages_data}

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text from a PDF file with detailed layout information.
    Uses pdfplumber to capture text positions, font sizes, and formatting.

    Args:
        pdf_path: Path to the input PDF file

    Returns:
        Dictionary containing pages with text elements and their positions
    """
    pages_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Get page dimensions
                page_width = page.width
                page_height = page.height

                # Extract words with detailed positioning information
                words = page.extract_words(
                    x_tolerance=3,
                    y_tolerance=3,
                    keep_blank_chars=True,
                    use_text_flow=True
                )

                # Group words into lines based on y-coordinate
                lines = []
                if words:
                    current_line = []
                    current_y = words[0]['top']
                    y_tolerance = 3  # pixels tolerance for same line

                    for word in words:
                        # If word is on roughly the same y-coordinate, add to current line
                        if abs(word['top'] - current_y) <= y_tolerance:
                            current_line.append(word)
                        else:
                            # Save current line and start new one
                            if current_line:
                                lines.append(current_line)
                            current_line = [word]
                            current_y = word['top']

                    # Add the last line
                    if current_line:
                        lines.append(current_line)

                # Convert lines to structured format
                structured_lines = []
                all_text = []

                for line in lines:
                    if not line:
                        continue

                    # Get line properties from first word
                    line_text = ' '.join([w['text'] for w in line])
                    line_x = min([w['x0'] for w in line])
                    line_y = line[0]['top']

                    # Estimate font size from word heights
                    avg_height = sum([w['bottom'] - w['top'] for w in line]) / len(line)

                    structured_lines.append({
                        'text': line_text,
                        'x': line_x,
                        'y': line_y,
                        'font_size': avg_height * 0.75,  # Approximate font size from height
                        'words': line
                    })
                    all_text.append(line_text)

                pages_data.append({
                    'page_num': page_num + 1,
                    'text': '\n'.join(all_text),
                    'lines': structured_lines,
                    'width': page_width,
                    'height': page_height
                })
                print(f"Extracted page {page_num + 1}: {len(structured_lines)} lines, {page_width}x{page_height}")

    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

    # Check if any text was extracted
    total_lines = sum(len(page.get('lines', [])) for page in pages_data)

    # If no text was extracted, try OCR
    if total_lines == 0:
        print("No text extracted with pdfplumber, trying OCR...")
        try:
            ocr_result = extract_text_with_ocr(pdf_path)
            # Verify OCR actually found text
            ocr_total_lines = sum(len(page.get('lines', [])) for page in ocr_result.get('pages', []))
            if ocr_total_lines == 0:
                raise Exception("OCR found no text content in the PDF")
            return ocr_result
        except Exception as ocr_error:
            print(f"OCR extraction also failed: {str(ocr_error)}")
            raise Exception(f"Could not extract text from PDF using either pdfplumber or OCR. The PDF may be an image without text, encrypted, or corrupted. OCR error: {str(ocr_error)}")

    return {'pages': pages_data}

def create_translated_pdf(pages_data: dict, output_path: str, target_lang: str = "en"):
    """
    Create a new PDF with translated text placed at the same positions as the original.
    Preserves font sizes and positioning for accurate layout matching.

    Args:
        pages_data: Dictionary containing pages with translated text and positioning info
        output_path: Path where the output PDF will be saved
        target_lang: Target language code ('en' or 'hi')
    """
    try:
        # Register font based on target language
        base_font_name = "Helvetica"
        if target_lang == "hi":
            base_font_name = register_hindi_font()

        # Process each page separately to maintain structure
        pages = pages_data.get('pages', [])

        if not pages:
            raise Exception("No pages data provided")

        c = None

        # Process each page
        for page_idx, page_data in enumerate(pages):
            # Get page-specific dimensions
            page_width = page_data.get('width', 612)  # default letter width
            page_height = page_data.get('height', 792)  # default letter height

            # Create canvas on first page
            if c is None:
                c = canvas.Canvas(output_path, pagesize=(page_width, page_height))

            # Get translated lines with position information
            translated_lines = page_data.get('lines', [])

            # Process each line with its positioning
            for line_data in translated_lines:
                # Get line properties
                if isinstance(line_data, dict):
                    line_text = line_data.get('text', '')
                    x_pos = line_data.get('x', 50)
                    y_pos = line_data.get('y', 100)
                    font_size = line_data.get('font_size', 12)
                else:
                    # Fallback for string lines
                    line_text = str(line_data)
                    x_pos = 50
                    y_pos = page_height - 100
                    font_size = 12

                if not line_text.strip():
                    continue

                # Normalize the text for better Devanagari rendering
                if target_lang == "hi":
                    line_text = normalize_devanagari_text(line_text)

                # Convert y coordinate (PDFPlumber uses top-left origin, ReportLab uses bottom-left)
                reportlab_y = page_height - y_pos

                # Set font size for this line
                try:
                    c.setFont(base_font_name, font_size)
                except:
                    c.setFont(base_font_name, 12)

                # Handle text that might be too long for the position
                # Calculate available width from x position to right margin
                available_width = page_width - x_pos - 50

                if available_width > 0:
                    # Try to fit text in available space
                    text_width = c.stringWidth(line_text, base_font_name, font_size)

                    if text_width > available_width:
                        # Text is too long, need to wrap or truncate
                        # For now, we'll try to fit as much as possible
                        chars_per_width = len(line_text) / text_width
                        estimated_chars = int(available_width * chars_per_width * 0.95)

                        if estimated_chars > 0 and estimated_chars < len(line_text):
                            # Try to break at word boundary
                            words = line_text.split()
                            fitted_text = ""
                            for word in words:
                                test_text = fitted_text + " " + word if fitted_text else word
                                if c.stringWidth(test_text, base_font_name, font_size) <= available_width:
                                    fitted_text = test_text
                                else:
                                    break
                            line_text = fitted_text if fitted_text else line_text[:estimated_chars]

                    # Draw the text at the original position
                    try:
                        c.drawString(x_pos, reportlab_y, line_text)
                    except Exception as e:
                        print(f"Warning: Could not render line at ({x_pos}, {reportlab_y}): {e}")
                        # Try with default font as fallback
                        try:
                            c.setFont("Helvetica", font_size)
                            c.drawString(x_pos, reportlab_y, line_text)
                        except:
                            pass

            # Show page (except after the last page, handled by save())
            if page_idx < len(pages) - 1:
                c.showPage()

        # Save the PDF
        if c:
            c.save()
            print(f"Successfully created PDF: {output_path} with {len(pages)} pages")
        else:
            raise Exception("Failed to create PDF canvas")

    except Exception as e:
        raise Exception(f"Error creating PDF: {str(e)}")

def register_hindi_font():
    """
    Register a Hindi font for use in PDFs.
    This function registers the Noto Sans Devanagari font for proper Hindi text rendering.
    """
    font_path = "fonts/NotoSansDevanagari-Regular.ttf"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('HindiFont', font_path))
            return 'HindiFont'
        except Exception as e:
            print(f"Error registering Hindi font: {e}")
            return 'Helvetica'
    else:
        print(f"Hindi font not found at {font_path}")
        return 'Helvetica'

def create_translated_pdf_weasyprint(pages_data: dict, output_path: str, target_lang: str = "en"):
    """
    Create a PDF using weasyprint for better Devanagari/Hindi text rendering.
    Uses HTML/CSS for layout which provides proper complex text layout support.

    Args:
        pages_data: Dictionary containing pages with translated text and positioning info
        output_path: Path where the output PDF will be saved
        target_lang: Target language code ('en' or 'hi')
    """
    try:
        pages = pages_data.get('pages', [])
        if not pages:
            raise Exception("No pages data provided")

        # Set font based on language
        font_family = "'Noto Sans Devanagari', sans-serif" if target_lang == "hi" else "Arial, sans-serif"
        font_path = os.path.abspath("fonts/NotoSansDevanagari-Regular.ttf") if target_lang == "hi" else None

        # Build HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    margin: 0;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: {font_family};
                }}
                .page {{
                    position: relative;
                    page-break-after: always;
                }}
                .line {{
                    position: absolute;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
            </style>
        </head>
        <body>
        """

        # Add each page
        for page_idx, page_data in enumerate(pages):
            page_width = page_data.get('width', 612)
            page_height = page_data.get('height', 792)
            lines = page_data.get('lines', [])

            # Convert points to pixels (1pt = 1.333px approximately)
            width_px = page_width * 1.333
            height_px = page_height * 1.333

            html_content += f"""
            <div class="page" style="width: {page_width}pt; height: {page_height}pt;">
            """

            # Add each line
            for line_data in lines:
                if isinstance(line_data, dict):
                    line_text = html_module.escape(line_data.get('text', ''))
                    x_pos = line_data.get('x', 50)
                    y_pos = line_data.get('y', 100)
                    font_size = line_data.get('font_size', 12)
                else:
                    continue

                if not line_text.strip():
                    continue

                html_content += f"""
                <div class="line" style="left: {x_pos}pt; top: {y_pos}pt; font-size: {font_size}pt;">
                    {line_text}
                </div>
                """

            html_content += "</div>\n"

        html_content += """
        </body>
        </html>
        """

        # Create CSS for font embedding if Hindi
        css_content = ""
        if target_lang == "hi" and font_path and os.path.exists(font_path):
            css_content = f"""
            @font-face {{
                font-family: 'Noto Sans Devanagari';
                src: url('file://{font_path}') format('truetype');
            }}
            """

        # Generate PDF using weasyprint
        if css_content:
            HTML(string=html_content).write_pdf(output_path, stylesheets=[CSS(string=css_content)])
        else:
            HTML(string=html_content).write_pdf(output_path)

        print(f"Successfully created PDF with weasyprint: {output_path} with {len(pages)} pages")

    except Exception as e:
        raise Exception(f"Error creating PDF with weasyprint: {str(e)}")
