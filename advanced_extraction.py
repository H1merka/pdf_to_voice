import sys
import argparse
import re
from pathlib import Path
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from gtts import gTTS


class PDFToAudioConverter:
    """
    Class to convert a PDF document into an audio file using gTTS.
    """

    def __init__(self, language='ru', slow=False):
        """
        Initialize the converter with speech settings.
        :param language: Speech language code (e.g., 'ru', 'en')
        :param slow: Slow speech if True
        """
        self.language = language
        self.slow = slow

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from a PDF file using pdfminer.
        :param pdf_path: Path to the PDF file
        :return: Extracted text as a string
        """
        output_string = StringIO()

        with open(pdf_path, 'rb') as file:
            laparams = LAParams(
                boxes_flow=0.5,
                word_margin=0.1,
                char_margin=2.0,
                line_margin=0.5
            )

            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output_string, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            for page in PDFPage.get_pages(file):
                interpreter.process_page(page)

        text = output_string.getvalue()
        device.close()
        output_string.close()

        return text

    def clean_text(self, text):
        """
        Cleans the extracted text from extra spaces and unwanted characters.
        :param text: Raw text extracted from PDF
        :return: Cleaned text
        """
        if not text:
            return ""

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:()\-—–«»""„"\']+', ' ', text)
        text = re.sub(r'([.!?])\1+', r'\1', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def text_to_speech(self, text, output_path):
        """
        Converts cleaned text to speech and saves it as an audio file.
        :param text: Text to convert
        :param output_path: Path to save the output MP3
        :return: True on success, False on failure
        """
        if not text.strip():
            print("The input text is empty.")
            return False

        try:
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            tts.save(output_path)
            print(f"Audio file successfully saved: {output_path}")
            return True

        except Exception as e:
            print(f"Error while generating audio: {e}")
            return False

    def convert_pdf_to_audio(self, pdf_path, output_dir=None):
        """
        Main method to extract text from a PDF and convert it to audio.
        :param pdf_path: Path to input PDF
        :param output_dir: Directory to save the audio file
        :return: True on success, False on failure
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            print(f"File not found: {pdf_path}")
            return False

        if output_dir is None:
            output_dir = pdf_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Extracting text from: {pdf_path}")
        text = self.extract_text_from_pdf(pdf_path)

        if not text:
            print("Failed to extract text from PDF.")
            return False

        print(f"Characters before cleaning: {len(text)}")

        cleaned_text = self.clean_text(text)

        print(f"Characters after cleaning: {len(cleaned_text)}")

        if not cleaned_text:
            print("Text is empty after cleaning.")
            return False

        audio_filename = f"{pdf_path.stem}.mp3"
        audio_path = output_dir / audio_filename

        print("Generating audio...")

        if self.text_to_speech(cleaned_text, str(audio_path)):
            print(f"Audio file created: {audio_path}")
            return True

        print("Failed to generate audio file.")
        return False


def main():
    """
    Entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(
        description='PDF to audio (MP3) converter using gTTS.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python pdf_to_audio.py document.pdf
  python pdf_to_audio.py document.pdf --output ./audio
  python pdf_to_audio.py document.pdf --language en --slow
        '''
    )

    parser.add_argument('pdf_file', help='Path to the PDF file')
    parser.add_argument('--output', '-o', help='Directory to save MP3')
    parser.add_argument('--language', '-l', default='ru',
                        help='Language for speech synthesis (default: ru)')
    parser.add_argument('--slow', '-s', action='store_true',
                        help='Use slow speech')

    args = parser.parse_args()

    converter = PDFToAudioConverter(
        language=args.language,
        slow=args.slow
    )

    success = converter.convert_pdf_to_audio(
        args.pdf_file,
        args.output
    )

    if success:
        print("\nConversion completed successfully.")
    else:
        print("\nAn error occurred during conversion.")
        sys.exit(1)


if __name__ == "__main__":
    main()
