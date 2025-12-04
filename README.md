# PDF Translator App

A full-stack web application that translates PDF files between Hindi and English while preserving the document formatting.

## Features

- 📄 Upload PDF files via drag-and-drop or file selection
- 🔄 Translate between Hindi and English (bidirectional)
- 💾 Download translated PDFs with preserved formatting
- 🎨 Modern, responsive UI built with Next.js and Tailwind CSS
- ⚡ Fast translation using Google Translate (via googletrans)
- 🌓 Dark mode support

## Tech Stack

### Frontend
- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **React Hooks** - Modern state management

### Backend
- **FastAPI** - High-performance Python web framework
- **PyPDF2** - PDF text extraction
- **ReportLab** - PDF generation
- **googletrans** - Free translation library
- **uvicorn** - ASGI server

## Project Structure

```
pdf-translator-app/
├── frontend/              # Next.js frontend application
│   ├── app/              # App router pages
│   ├── components/       # React components
│   └── package.json
├── backend/              # FastAPI backend application
│   ├── main.py          # API endpoints
│   ├── pdf_processor.py # PDF handling logic
│   ├── translator.py    # Translation logic
│   └── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **pip** (Python package manager)

### Installation

#### 1. Clone or navigate to the project directory

```bash
cd pdf-translator-app
```

#### 2. Set up the Backend

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Set up the Frontend

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### Running the Application

You need to run both the backend and frontend servers.

#### Terminal 1: Start the Backend Server

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python main.py
```

The backend will run on `http://localhost:8000`

#### Terminal 2: Start the Frontend Server

```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:3000`

### Using the Application

1. Open your browser and navigate to `http://localhost:3000`
2. Upload a PDF file by clicking or dragging and dropping
3. Select the source language (the current language of the PDF)
4. Select the target language (the language you want to translate to)
5. Click "Translate PDF"
6. Wait for the translation to complete (this may take a few moments)
7. The translated PDF will automatically download

## API Documentation

Once the backend is running, you can access the interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### `POST /translate-pdf/`

Translate a PDF file from source language to target language.

**Parameters:**
- `file` (form-data): PDF file to translate
- `source_lang` (form-data): Source language ('en' or 'hi')
- `target_lang` (form-data): Target language ('en' or 'hi')

**Response:**
- Returns the translated PDF file for download

### `GET /health`

Health check endpoint to verify the backend is running.

## Limitations & Notes

- **Translation Service**: Uses the free `googletrans` library, which may have rate limits. For production use, consider using the official Google Cloud Translation API.
- **Hindi Font Support**: Hindi text in generated PDFs may not render perfectly due to font limitations. For production use, you should include a proper Devanagari font (like Noto Sans Devanagari).
- **Format Preservation**: The app extracts text and recreates the PDF. Complex layouts, images, and special formatting may not be perfectly preserved.
- **File Size**: Very large PDFs may take longer to process or hit translation limits.

## Future Enhancements

- [ ] Add support for more languages
- [ ] Implement proper Hindi font support for better rendering
- [ ] Add progress bar for translation status
- [ ] Support for batch translation of multiple files
- [ ] Better formatting preservation (images, tables, etc.)
- [ ] Option to use paid translation APIs for better quality
- [ ] User authentication and translation history
- [ ] PDF preview before download

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError` when starting the backend

**Solution:** Make sure you've activated the virtual environment and installed all dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** Translation fails with rate limit errors

**Solution:** The free `googletrans` library has rate limits. Wait a few moments and try again. For production, use the official Google Cloud Translation API.

### Frontend Issues

**Problem:** Cannot connect to backend

**Solution:** Ensure the backend is running on `http://localhost:8000` and CORS is properly configured.

**Problem:** PDF not downloading after translation

**Solution:** Check the browser console for errors. Ensure the backend successfully generated the translated PDF.

## License

This project is open source and available for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
