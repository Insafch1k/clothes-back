import cv2


class ClothesOverlay:
    def __init__(self, person_image, clothes_image):
        """
        Инициализация класса для наложения одежды.
        :param person_image: Изображение человека (в формате numpy array).
        :param clothes_image: Изображение футболки (в формате numpy array).
        """
        self.person_image = person_image
        self.clothes_image = clothes_image
        self.annotated_image = None

    def resize_clothes(self, clothes_width, clothes_height):
        """
        Масштабирование изображения футболки.
        :param clothes_width: Ширина футболки.
        :param clothes_height: Высота футболки.
        :return: Масштабированное изображение футболки.
        """
        if clothes_width > 0 and clothes_height > 0:
            return cv2.resize(self.clothes_image, (int(clothes_width), int(clothes_height)))
        else:
            raise ValueError("Некорректные размеры футболки.")

    def overlay_clothes(self, clothes_resized, start_x, start_y):
        """
        Наложение футболки на изображение человека.
        :param clothes_resized: Масштабированное изображение футболки.
        :param start_x: Начальная координата X для наложения.
        :param start_y: Начальная координата Y для наложения.
        """
        # Создание копии изображения для наложения
        self.annotated_image = self.person_image.copy()

        # Наложение футболки
        for c in range(3):  # RGB-каналы
            self.annotated_image[start_y:start_y + clothes_resized.shape[0],
            start_x:start_x + clothes_resized.shape[1], c] = \
                clothes_resized[:, :, c] * (clothes_resized[:, :, 3] / 255.0) + \
                self.annotated_image[start_y:start_y + clothes_resized.shape[0],
                start_x:start_x + clothes_resized.shape[1], c] * (1.0 - clothes_resized[:, :, 3] / 255.0)