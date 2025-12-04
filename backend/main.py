from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from typing import Literal
import shutil
from pdf_processor import extract_text_from_pdf, create_translated_pdf_weasyprint
from translator import translate_text

app = FastAPI(title="PDF Translator API")

# Get allowed origins from environment variable or use defaults
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "PDF Translator API is running"}

@app.post("/translate-pdf/")
async def translate_pdf(
    file: UploadFile = File(...),
    source_lang: Literal["en", "hi"] = Form(...),
    target_lang: Literal["en", "hi"] = Form(...)
):
    """
    Translate a PDF file from source language to target language.
    Supported languages: 'en' (English), 'hi' (Hindi)
    """

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Validate language selection
    if source_lang == target_lang:
        raise HTTPException(status_code=400, detail="Source and target languages must be different")

    # Create temporary file for uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=UPLOAD_DIR) as temp_input:
        shutil.copyfileobj(file.file, temp_input)
        input_pdf_path = temp_input.name

    try:
        # Extract text from PDF with page structure
        print(f"Extracting text from PDF: {input_pdf_path}")
        pages_data = extract_text_from_pdf(input_pdf_path)

        if not pages_data.get('pages'):
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. The PDF might be empty, encrypted, or corrupted.")

        # Get all text for translation
        all_text = "\n\n".join([page.get('text', '') for page in pages_data['pages']])

        if not all_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in PDF. The PDF may contain only images without embedded text. Please ensure the PDF contains extractable text.")

        print(f"Extracted text length: {len(all_text)} characters")

        # Translate text
        print(f"Translating from {source_lang} to {target_lang}")
        translated_text = translate_text(all_text, source_lang=source_lang, target_lang=target_lang)

        print(f"Translated text length: {len(translated_text)} characters")

        # Split translated text back to lines matching original structure
        pages = pages_data['pages']

        # Split translated text by pages first
        original_page_texts = [page['text'] for page in pages]
        original_lengths = [len(text) for text in original_page_texts]
        total_original = sum(original_lengths)

        # Split translated text proportionally by pages
        translated_page_texts = []
        current_pos = 0

        for i in range(len(pages)):
            if i < len(pages) - 1:
                proportion = original_lengths[i] / total_original
                page_length = int(len(translated_text) * proportion)
                page_text = translated_text[current_pos:current_pos + page_length]
                current_pos += page_length
            else:
                page_text = translated_text[current_pos:]

            translated_page_texts.append(page_text)

        # Now match translated text to original line structure
        translated_pages = []

        for page_idx, page in enumerate(pages):
            page_translated_text = translated_page_texts[page_idx]
            original_lines = page['lines']

            # Split translated text for this page into lines matching original structure
            if not original_lines:
                translated_pages.append(page)
                continue

            # Calculate how much translated text each line should get (proportional)
            original_line_lengths = [len(line.get('text', '')) if isinstance(line, dict) else len(str(line)) for line in original_lines]
            total_page_length = sum(original_line_lengths) or 1

            translated_lines = []
            text_pos = 0

            for line_idx, original_line in enumerate(original_lines):
                # Get original line properties
                if isinstance(original_line, dict):
                    line_proportion = original_line_lengths[line_idx] / total_page_length
                    line_text_length = int(len(page_translated_text) * line_proportion)

                    # Get translated text for this line
                    if line_idx < len(original_lines) - 1:
                        line_translated_text = page_translated_text[text_pos:text_pos + line_text_length]
                        text_pos += line_text_length
                    else:
                        line_translated_text = page_translated_text[text_pos:]

                    # Create new line with same position but translated text
                    translated_lines.append({
                        'text': line_translated_text.strip(),
                        'x': original_line.get('x', 50),
                        'y': original_line.get('y', 100),
                        'font_size': original_line.get('font_size', 12),
                        'words': []
                    })
                else:
                    # Fallback for non-dict lines
                    translated_lines.append({
                        'text': page_translated_text,
                        'x': 50,
                        'y': 100,
                        'font_size': 12,
                        'words': []
                    })
                    break

            translated_pages.append({
                'page_num': page['page_num'],
                'text': page_translated_text,
                'lines': translated_lines,
                'width': page['width'],
                'height': page['height']
            })

        # Create new pages data structure
        translated_pages_data = {'pages': translated_pages}

        # Create output PDF with translated text using weasyprint
        output_pdf_path = os.path.join(UPLOAD_DIR, f"translated_{os.path.basename(input_pdf_path)}")
        print(f"Creating translated PDF: {output_pdf_path}")

        create_translated_pdf_weasyprint(translated_pages_data, output_pdf_path, target_lang=target_lang)

        # Return the translated PDF
        return FileResponse(
            output_pdf_path,
            media_type="application/pdf",
            filename=f"translated_{file.filename}",
            headers={
                "Content-Disposition": f'attachment; filename="translated_{file.filename}"'
            }
        )

    except Exception as e:
        print(f"Error during translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

    finally:
        # Cleanup input file
        if os.path.exists(input_pdf_path):
            try:
                os.remove(input_pdf_path)
            except Exception as e:
                print(f"Error cleaning up input file: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
