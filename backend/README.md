# PDF Translator Backend

FastAPI backend for translating PDF files between Hindi and English.

## Features

- Extract text from PDF files
- Translate text between Hindi and English
- Generate new PDF with translated text
- Preserve basic formatting

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the FastAPI server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## API Endpoints

### POST /translate-pdf/

Translate a PDF file from source language to target language.

**Parameters:**
- `file`: PDF file to translate (form-data)
- `source_lang`: Source language ('en' or 'hi')
- `target_lang`: Target language ('en' or 'hi')

**Response:**
- Returns the translated PDF file

### GET /health

Health check endpoint.

## Notes

- The free googletrans library may have rate limits
- For production use, consider using Google Cloud Translation API
- Hindi text rendering in PDFs may require additional font support
