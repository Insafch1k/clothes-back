import os
from config import UPLOAD_FOLDER_CLOTHES, PROCESSED_FOLDER_CLOTHES, UPLOAD_FOLDER_CATALOG, PROCESSED_FOLDER_CATALOG, \
    UPLOAD_FOLDER_BACKGROUND, PROCESSED_FOLDER_BACKGROUND


def create_folders_for_clothes():
    # Создаем папки, если их нет
    if not os.path.exists(UPLOAD_FOLDER_CLOTHES):
        os.makedirs(UPLOAD_FOLDER_CLOTHES)
    if not os.path.exists(PROCESSED_FOLDER_CLOTHES):
        os.makedirs(PROCESSED_FOLDER_CLOTHES)

    if not os.path.exists(UPLOAD_FOLDER_CATALOG):
        os.makedirs(UPLOAD_FOLDER_CATALOG)
    if not os.path.exists(PROCESSED_FOLDER_CATALOG):
        os.makedirs(PROCESSED_FOLDER_CATALOG)


def create_folders_for_background():
    # Создаем папки, если их нет
    if not os.path.exists(UPLOAD_FOLDER_BACKGROUND):
        os.makedirs(UPLOAD_FOLDER_BACKGROUND)
    if not os.path.exists(PROCESSED_FOLDER_BACKGROUND):
        os.makedirs(PROCESSED_FOLDER_BACKGROUND)
