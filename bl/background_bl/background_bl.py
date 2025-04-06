from rembg import remove
from PIL import Image
import os
import uuid
import config
from bl.utils.create_folders import create_folders_for_background

create_folders_for_background()


def remove_background(input_path):
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)

        output_filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(config.PROCESSED_FOLDER_BACKGROUND, output_filename)

        output_image.save(output_path)
        return output_filename
    except Exception as error:
        print(f"Ошибка обработки изображения: {error}")
        return None
