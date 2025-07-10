import os
import sys
import base64
from pdf2image import convert_from_path
import openai
from dotenv import load_dotenv

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

        # Извлекаем текст — просто OCR
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

        extracted = response.choices[0].message.content.strip()
        all_text += extracted + "\n\n"

    print("🧠 Сжатие текста до ~50% длины с сохранением деталей...")

    # Шаг 2: Сжать текст до ~⅔ длины, сохранив смысл и детали
    compression_prompt = (
        "Прочитай текст ниже и сократи его до 7000 символов. Сохрани структуру, стиль и все ключевые факты. "
        "Тон должен остаться таким же, как в оригинале, а содержание — полным и логичным. "
        "Получившийся текст должен быть полностью на русском языке."
    )

    summary_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": compression_prompt},
            {"role": "user", "content": all_text}  # безопасный лимит
        ],
        max_tokens=4096  # ~2/3 от 4096 токенов — ориентировочно
    )

    final_summary = summary_response.choices[0].message.content.strip()

    return final_summary


def text_to_speech_single(text, filename="final_voice.mp3"):
    if len(text) > 12000:
        print("❌ Текст слишком длинный для озвучивания одним куском. Сократите его.")
        sys.exit(1)

    print("🎤 Генерация голосового сообщения из всего текста...")

    response = openai.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input=text
    )

    with open(filename, "wb") as f:
        f.write(response.content)

    print(f"✅ Итоговый аудиофайл сохранён: {os.path.abspath(filename)}")


# Основной запуск
if __name__ == "__main__":
    final_text = extract_text_from_images(images)

    with open("output_text.txt", "w", encoding="utf-8") as f:
        f.write(final_text)

    text_to_speech_single(final_text)
    print("✅ Готово! Сохранены файлы: output_text.txt и final_voice.mp3")
