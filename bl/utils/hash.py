import hashlib


def calculate_hash(file_bytes: bytes) -> str:
    """Вычисляет SHA-256 хэш файла"""
    return hashlib.sha256(file_bytes).hexdigest()
