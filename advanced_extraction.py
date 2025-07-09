import os
import sys
import base64
from pdf2image import convert_from_path
import openai
from dotenv import load_dotenv
import subprocess

# Загрузка переменных окружения
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Проверка аргументов командной строки
if len(sys.argv) != 2:
    print("❌ Использование: python script.py <путь_к_pdf>")
    sys.exit(1)

PDF_PATH = sys.argv[1]

if not os.path.isfile(PDF_PATH):
    print(f"❌ Файл не найден: {PDF_PATH}")
    sys.exit(1)

# Создание временной директории для изображений
TEMP_IMG_DIR = "pdf_pages"
os.makedirs(TEMP_IMG_DIR, exist_ok=True)

# Шаг 1. Конвертация PDF в изображения
print("📄 Конвертация PDF в изображения...")
images = convert_from_path(PDF_PATH, dpi=300, fmt='jpeg', output_folder=TEMP_IMG_DIR)


def extract_text_from_images(images):
    print("🔍 Распознавание текста с изображений...")
    all_text = ""

    for i, img in enumerate(images):
        temp_img_path = f"{TEMP_IMG_DIR}/temp_page_{i}.jpg"
        img.save(temp_img_path)

        with open(temp_img_path, "rb") as image_file:
            b64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Извлекаем текст без анализа, просто OCR
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Ты OCR-система. Распознай текст с изображения. Ничего не переводи и не комментируй."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                        {"type": "text", "text": "Распознай и верни весь текст с изображения."}
                    ]
                }
            ],
            max_tokens=4096
        )

        extracted = response.choices[0].message.content.strip()
        all_text += extracted + "\n\n"

    print("🧠 Генерация общей выжимки на русском языке...")

    # Запрос к модели для генерации общей выжимки
    summary_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты помощник-референт. Прочитай следующий текст и сделай краткое, связное содержание "
                    "на русском языке. Сохрани только основную суть, убери второстепенные детали."
                )
            },
            {
                "role": "user",
                "content": all_text[:16000]  # ограничим для безопасного количества токенов
            }
        ],
        max_tokens=2048
    )

    final_summary = summary_response.choices[0].message.content.strip()
    return final_summary


def split_text(text, max_size=4000):
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Если один абзац слишком большой - разбиваем его по max_size
            if len(para) > max_size:
                for i in range(0, len(para), max_size):
                    chunks.append(para[i:i + max_size])
                current_chunk = ""
            else:
                current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def text_to_speech_chunks(text, output_dir="audio_chunks"):
    os.makedirs(output_dir, exist_ok=True)
    chunks = split_text(text)
    audio_paths = []
    for i, chunk in enumerate(chunks):
        print(f"🎤 Генерация голосового сообщения: часть {i+1}/{len(chunks)}...")
        response = openai.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=chunk
        )
        audio_path = os.path.join(output_dir, f"part_{i+1}.mp3")
        with open(audio_path, "wb") as f:
            f.write(response.content)
        audio_paths.append(audio_path)
    return audio_paths


def merge_audio_chunks_ffmpeg(audio_paths, output_path="final_voice.mp3"):
    print("🔊 Склейка аудиочастей через ffmpeg...")

    list_file = "audio_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for path in audio_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy", output_path
    ], check=True)

    print(f"✅ Итоговый файл сохранён: {output_path}")


# Основной запуск
if __name__ == "__main__":
    text = extract_text_from_images(images)
    with open("output_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    audio_files = text_to_speech_chunks(text)
    merge_audio_chunks_ffmpeg(audio_files)
    print("✅ Готово! Сохранены файлы: output_text.txt и final_voice.mp3")
