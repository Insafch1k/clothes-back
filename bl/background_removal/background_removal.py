from rembg import remove
from PIL import Image
import os
import uuid


UPLOAD_FOLDER = "processed_images"

# Создаём папку для обработанных изображений (если её нет)
if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


def remove_background(input_path):
    """
    Удаляет фон с изображения и сохраняет результат
    """
    try:
        # Открываем изображение
        input_image = Image.open(input_path)
        # Удаляем фон
        output_image = remove(input_image)

        # Генерируем уникальное имя для файла
        output_filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)

        # Сохраняем обработанное изображение
        output_image.save(output_path)

        return output_filename
    except Exception as error:
        print(f"Ошибка обработки изображения: {error}")
    return None