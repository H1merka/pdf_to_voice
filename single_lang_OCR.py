from pdf2image import convert_from_path
import pytesseract
from gtts import gTTS
import sys
import os


def pdf_to_audio(pdf_path, audio_path='output.mp3', lang='ru'):
    """
    Converts a PDF file to an audio message using OCR and text-to-speech.

    Args:
        pdf_path (str): Path to the input PDF file.
        audio_path (str): Path to the output audio file (default: 'output.mp3').
        lang (str): Language code for speech synthesis (default: 'ru' for Russian).
    """
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path)

        # Extract text from each image using OCR
        total_text = ""
        for image in images:
            text = pytesseract.image_to_string(image, lang='rus')  # Use 'rus' for Russian OCR
            total_text += text + "\n"

        # Convert the extracted text to speech
        tts = gTTS(text=total_text, lang=lang)
        tts.save(audio_path)
        print(f"Audio saved to: {audio_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_audio.py <path_to_pdf> [path_to_audio_output]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    audio_path = sys.argv[2] if len(sys.argv) > 2 else 'output.mp3'

    # Check if the PDF file exists
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    pdf_to_audio(pdf_path, audio_path)
