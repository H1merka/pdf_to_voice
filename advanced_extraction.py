import os
import sys
import base64
from io import BytesIO
from typing import List
from PIL import Image
from pdf2image import convert_from_path
import openai
from dotenv import load_dotenv


load_dotenv()

openai_api_key: str | None
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

if len(sys.argv) != 2:
    print("Usage: python script.py <pdf_path>")
    sys.exit(1)

PDF_PATH: str = sys.argv[1]

if not os.path.isfile(PDF_PATH):
    print(f"File is not found: {PDF_PATH}")
    sys.exit(1)

# Convert PDF pages to a list of PIL images in memory
images: List[Image.Image] = convert_from_path(PDF_PATH, dpi=300, fmt='jpeg')


def extract_func(images: List[Image.Image]) -> str:
    """
    Extract text from a list of images by sending each image to the OpenAI GPT-4o model as a base64-encoded
    image embedded in the chat message. The model acts as an OCR system and returns recognized text.

    After extracting text from all pages, it sends the combined text back to the model for compression and summarization,
    preserving style and key facts, with the output fully in Russian.

    Args:
        images (list): List of PIL Image objects representing PDF pages.

    Returns:
        str: The compressed and summarized Russian text extracted from the PDF.
    """
    all_text: str = ""

    for _, img in enumerate(images):
        # Save image to bytes buffer in JPEG format without writing to disk
        img_bytes: BytesIO = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        # Encode image bytes to base64 string for embedding in OpenAI message
        b64_image: str = base64.b64encode(img_bytes.read()).decode("utf-8")

        # Send image and instruction to GPT-4o model acting as OCR
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Ты OCR-система. Распознай и верни весь текст с изображения без перевода и комментариев."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                        {"type": "text", "text": "Распознай текст и верни его полностью."}
                    ]
                }
            ],
            max_tokens=4096
        )

        extracted: str = response.choices[0].message.content.strip()
        all_text += extracted + "\n\n"

    # Prompt to compress and summarize the full extracted text, preserving style and meaning
    compression_prompt: str = (
        "Прочитай текст ниже и сократи его до 7000 символов. "
        "Сохрани структуру, стиль и все ключевые факты. "
        "Тон должен остаться таким же, как в оригинале, "
        "а содержание — полным и логичным. "
        "Получившийся текст должен быть полностью на русском языке. "
        "Получившийся текст должен выглядеть так, как будто это мысли автора, "
        "писавшего текст из запроса."
    )

    summary_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": compression_prompt},
            {"role": "user", "content": all_text}
        ],
        max_tokens=4096
    )

    final_summary: str = summary_response.choices[0].message.content.strip()

    return final_summary


def tts_func(text: str, filename: str = "final_voice.mp3") -> None:
    """
    Convert given text into speech audio using OpenAI's TTS model and save to a file.

    Args:
        text (str): Text to be converted to speech.
        filename (str): Output filename for the generated audio (default: "final_voice.mp3").

    Exits with error if text is too long to process in one request.
    """
    if len(text) > 12000:
        print("Text is too long.")
        sys.exit(1)

    # Request TTS audio generation from OpenAI
    response = openai.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input=text
    )

    # Write audio bytes to output file
    with open(filename, "wb") as f:
        f.write(response.content)


if __name__ == "__main__":
    # Extract and compress text from PDF images
    final_text: str = extract_func(images)

    # Save extracted and compressed text to output file
    with open("output_text.txt", "w", encoding="utf-8") as f:
        f.write(final_text)

    # Generate speech audio from the extracted text
    tts_func(final_text)
