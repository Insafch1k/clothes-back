from rembg import remove
from PIL import Image
import os
import uuid

# Определяем пути для загрузки и обработанных файлов внутри директории photo_clothes
BASE_PHOTO_DIR = os.path.join(os.getcwd(), "photo_clothes")  # Корневая директория photo_clothes
UPLOAD_FOLDER = os.path.join(BASE_PHOTO_DIR, "uploads_clothes")  # Путь для оригинальных изображений
PROCESSED_FOLDER = os.path.join(BASE_PHOTO_DIR, "processed_images_clothes")  # Путь для обработанных изображений

# Создаем папки, если их нет
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

def remove_background_clothes(input_path):
    """
    Удаляет фон из изображения и сохраняет результат.
    """
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)

        output_filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)

        output_image.save(output_path)
        return output_filename
    except Exception as error:
        print(f"Ошибка обработки изображения: {error}")
        return None