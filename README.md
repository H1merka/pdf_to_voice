# PDF to Speech Converter

A small project that converts text extracted from PDF files into voice messages in MP3 format.

---

## Features

- Extracts text from PDF documents, including complex layouts.
- Converts extracted text into speech using Google Text-to-Speech (gTTS).
- Generates MP3 audio files from PDF content.

---

## Installation

### System Dependencies

Before installing Python dependencies, make sure to install the following system packages:

- **Tesseract OCR** (required for text extraction from images inside PDFs):

  - **Ubuntu/Debian:**
    ```bash
    sudo apt-get update
    sudo apt-get install tesseract-ocr libtesseract-dev
    ```

  - **macOS (using Homebrew):**
    ```bash
    brew install tesseract
    ```

- **Poppler-utils** (required for PDF to image conversion):

  - **Ubuntu/Debian:**
    ```bash
    sudo apt-get install poppler-utils
    ```

  - **macOS (using Homebrew):**
    ```bash
    brew install poppler
    ```

---

### Python Dependencies

It is recommended to use a virtual environment.

1. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. Install Python packages:

    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

After installation, run the main script providing the PDF file path, and it will generate an MP3 audio file with the spoken content.

---

## Development Team

GitHub link: [link](https://github.com/H1merka)

---

## License

This project is licensed under the [MIT](https://opensource.org/licenses/MIT) License.
