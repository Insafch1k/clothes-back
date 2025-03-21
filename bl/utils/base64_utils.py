import base64

def decode_base64(base64_string, output_path):
    """
    Декодирует строку Base64 и сохраняет результат в файл.

    :param base64_string: Строка Base64 для декодирования.
    :param output_path: Путь, куда сохранить декодированный файл.
    :return: None
    """
    try:
        image_data = base64.b64decode(base64_string)
        with open(output_path, "wb") as img_file:
            img_file.write(image_data)
    except Exception as e:
        raise ValueError(f"Ошибка декодирования Base64: {str(e)}")

def encode_to_base64(file_path):
    """
    Кодирует файл в строку Base64.

    :param file_path: Путь к файлу для кодирования.
    :return: Строка Base64.
    """
    try:
        with open(file_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
        return encoded_image
    except Exception as e:
        raise ValueError(f"Ошибка кодирования Base64: {str(e)}")