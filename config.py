import os

# Определяем пути для загрузки и обработанных файлов внутри директории photo_clothes
BASE_PHOTO_DIR_CLOTHES = os.path.join(os.getcwd(), "photo_clothes")  # Корневая директория photo_clothes
UPLOAD_FOLDER_CLOTHES = os.path.join(BASE_PHOTO_DIR_CLOTHES, "uploads_clothes")  # Путь для оригинальных изображений
PROCESSED_FOLDER_CLOTHES = os.path.join(BASE_PHOTO_DIR_CLOTHES,
                                        "processed_images_clothes")  # Путь для обработанных изображений

UPLOAD_FOLDER_CATALOG = os.path.join(BASE_PHOTO_DIR_CLOTHES,
                                     "uploads_clothes_catalog")  # Путь для оригинальных изображений каталога
PROCESSED_FOLDER_CATALOG = os.path.join(BASE_PHOTO_DIR_CLOTHES,
                                        "processed_images_clothes_catalog")  # Путь для обработанных изображений

# Определяем пути для загрузки и обработанных файлов внутри директории photo_background
BASE_PHOTO_DIR_BACKGROUND = os.path.join(os.getcwd(), "photo_background")  # Корневая директория photo_background
UPLOAD_FOLDER_BACKGROUND = os.path.join(BASE_PHOTO_DIR_BACKGROUND, "uploads")  # Путь для оригинальных изображений
PROCESSED_FOLDER_BACKGROUND = os.path.join(BASE_PHOTO_DIR_BACKGROUND,
                                           "processed_images")  # Путь для обработанных изображений
