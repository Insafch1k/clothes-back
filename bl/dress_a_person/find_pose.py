import cv2
import mediapipe as mp


class TShirtFitting:
    def __init__(self, person_image, clothes_image):
        """
        Инициализация класса для надевания футболки.
        :param person_image: Изображение человека (в формате numpy array).
        :param clothes_image: Изображение футболки (в формате numpy array).
        """
        self.person_image = person_image
        self.clothes_image = clothes_image
        self.annotated_image = None

    def calculate_clothes_size(self, landmarks):
        """
        Расчет размеров футболки на основе ключевых точек.
        :param landmarks: Ключевые точки позы.
        :return: Ширина и высота футболки, начальные координаты.
        """
        # Координаты плеч и бедер
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]

        # Преобразование нормализованных координат в пиксели
        height, width, _ = self.person_image.shape
        left_shoulder_x = int(left_shoulder.x * width)
        left_shoulder_y = int(left_shoulder.y * height)
        right_shoulder_x = int(right_shoulder.x * width)
        left_hip_y = int(left_hip.y * height)

        # Расчет размеров футболки
        clothes_width = abs(right_shoulder_x - left_shoulder_x) * 2.1  # Увеличение ширины
        clothes_height = abs(left_hip_y - left_shoulder_y) * 1.7  # Увеличение высоты

        # Начальные координаты для наложения
        start_x = min(left_shoulder_x, right_shoulder_x) - int(clothes_width * 0.28)  # Смещение для центрирования
        start_y = left_shoulder_y - int(clothes_height * 0.26)  # Смещение для центрирования

        return clothes_width, clothes_height, start_x, start_y

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


# pose_detector = PoseDetector()
# tshirt_fitting = TShirtFitting(person_image, clothes_image)
#
# # Обнаружение позы
# landmarks = pose_detector.detect_pose(person_image)
#
# # Расчет размеров и наложение футболки
# clothes_width, clothes_height, start_x, start_y = tshirt_fitting.calculate_clothes_size(landmarks)
# clothes_resized = tshirt_fitting.resize_clothes(clothes_width, clothes_height)
# tshirt_fitting.overlay_clothes(clothes_resized, start_x, start_y)
#
# # Отображение результата
# tshirt_fitting.show_result()