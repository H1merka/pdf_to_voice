import sys
import os
from pdfminer.high_level import extract_text
from gtts import gTTS


def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text.
    """
    return extract_text(pdf_path)


def generate_audio_from_text(text, output_audio_path, lang='ru'):
    """
    Generates an audio file from the provided text using gTTS.

    Args:
        text (str): Text to be converted into speech.
        output_audio_path (str): Path to save the output audio file.
        lang (str): Language code for the text-to-speech conversion (default: 'ru').
    """
    tts = gTTS(text=text, lang=lang)
    tts.save(output_audio_path)
    print(f"Audio file saved as: {output_audio_path}")


def main():
    """
    Main function to process a PDF file and generate an audio file from its text content.
    The path to the PDF file should be provided as a command-line argument.
    """
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_pdf>")
        return

    pdf_path = sys.argv[1]
    audio_output_path = "output_voice.mp3"

    if not os.path.isfile(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)

    if not text.strip():
        print("Failed to extract text from the PDF.")
        return

    print("Generating audio file...")
    generate_audio_from_text(text, audio_output_path)


if __name__ == "__main__":
    main()
