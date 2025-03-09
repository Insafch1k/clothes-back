import cv2
import numpy as np
import mediapipe as mp


class ClothesFitting:
    def __init__(self, person_image_path, clothes_image_path):
        """
        Инициализация класса.
        :param person_image_path: Путь к изображению человека.
        :param clothes_image_path: Путь к изображению одежды.
        """
        # Загрузка изображений
        self.person_image = cv2.imread(person_image_path)
        self.clothes_image = cv2.imread(clothes_image_path, cv2.IMREAD_UNCHANGED)

        # Проверка загрузки изображений
        if self.person_image is None:
            raise ValueError(f"Не удалось загрузить изображение человека по пути: {person_image_path}")
        if self.clothes_image is None:
            raise ValueError(f"Не удалось загрузить изображение одежды по пути: {clothes_image_path}")

        # Инициализация MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=True)

        # Поле для хранения результата
        self.annotated_image = None

    def detect_pose(self):
        """
        Обнаружение позы человека на изображении.
        :return: Ключевые точки позы (landmarks).
        """
        # Преобразование изображения в RGB
        image_rgb = cv2.cvtColor(self.person_image, cv2.COLOR_BGR2RGB)

        # Обработка изображения с помощью MediaPipe Pose
        results = self.pose.process(image_rgb)

        if results.pose_landmarks:
            return results.pose_landmarks.landmark
        else:
            raise ValueError("Поза не обнаружена. Убедитесь, что на изображении видно тело человека.")

    def calculate_clothes_size(self, landmarks):
        """
        Расчет размеров одежды на основе ключевых точек.
        :param landmarks: Ключевые точки позы.
        :return: Ширина и высота одежды, начальные координаты.
        """
        # Координаты плеч и бедер
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]

        # Преобразование нормализованных координат в пиксели
        height, width, _ = self.person_image.shape
        left_shoulder_x = int(left_shoulder.x * width)
        left_shoulder_y = int(left_shoulder.y * height)
        right_shoulder_x = int(right_shoulder.x * width)
        left_hip_y = int(left_hip.y * height)

        # Расчет размеров одежды
        clothes_width = abs(right_shoulder_x - left_shoulder_x) * 21 / 10  # Увеличение ширины в 2 раза
        clothes_height = abs(left_hip_y - left_shoulder_y) * 17 / 10  # Увеличение высоты в 2 раза

        # Начальные координаты для наложения
        start_x = min(left_shoulder_x, right_shoulder_x) - int(clothes_width * 0.28)  # Смещение для центрирования
        start_y = left_shoulder_y - int(clothes_height * 0.26)  # Смещение для центрирования

        return clothes_width, clothes_height, start_x, start_y

    def resize_clothes(self, clothes_width, clothes_height):
        """
        Масштабирование изображения одежды.
        :param clothes_width: Ширина одежды.
        :param clothes_height: Высота одежды.
        :return: Масштабированное изображение одежды.
        """
        if clothes_width > 0 and clothes_height > 0:
            return cv2.resize(self.clothes_image, (int(clothes_width), int(clothes_height)))
        else:
            raise ValueError("Некорректные размеры одежды.")

    def overlay_clothes(self, clothes_resized, start_x, start_y):
        """
        Наложение одежды на изображение человека.
        :param clothes_resized: Масштабированное изображение одежды.
        :param start_x: Начальная координата X для наложения.
        :param start_y: Начальная координата Y для наложения.
        """
        # Создание копии изображения для наложения
        self.annotated_image = self.person_image.copy()

        # Наложение одежды
        for c in range(3):  # RGB-каналы
            self.annotated_image[start_y:start_y + clothes_resized.shape[0],
            start_x:start_x + clothes_resized.shape[1], c] = \
                clothes_resized[:, :, c] * (clothes_resized[:, :, 3] / 255.0) + \
                self.annotated_image[start_y:start_y + clothes_resized.shape[0],
                start_x:start_x + clothes_resized.shape[1], c] * (1.0 - clothes_resized[:, :, 3] / 255.0)

    def save_result(self, output_path):
        """
        Сохранение результата.
        :param output_path: Путь для сохранения результата.
        """
        if self.annotated_image is not None:
            cv2.imwrite(output_path, self.annotated_image)
        else:
            raise ValueError("Результат не найден. Сначала выполните наложение одежды.")

    def show_result(self):
        """
        Отображение результата.
        """
        if self.annotated_image is not None:
            cv2.imshow('Result', self.annotated_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            raise ValueError("Результат не найден. Сначала выполните наложение одежды.")


# Пример использования
if __name__ == "__main__":
    try:
        # Инициализация класса
        clothes_fitting = ClothesFitting('person3.png', 'tshirt.png')

        # Обнаружение позы
        landmarks = clothes_fitting.detect_pose()

        # Расчет размеров одежды
        clothes_width, clothes_height, start_x, start_y = clothes_fitting.calculate_clothes_size(landmarks)

        # Масштабирование одежды
        clothes_resized = clothes_fitting.resize_clothes(clothes_width, clothes_height)

        # Наложение одежды
        clothes_fitting.overlay_clothes(clothes_resized, start_x, start_y)

        # Сохранение результата
        clothes_fitting.save_result('output.png')

        # Отображение результата
        clothes_fitting.show_result()

    except Exception as e:
        print(f"Произошла ошибка: {e}")
