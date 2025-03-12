import cv2
import mediapipe as mp


class PoseDetector:
    def __init__(self):
        """
        Инициализация класса для обнаружения позы.
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=True)

    def detect_pose(self, person_image):
        """
        Обнаружение позы человека на изображении.
        :param person_image: Изображение человека (в формате numpy array).
        :return: Ключевые точки позы (landmarks).
        """
        # Преобразование изображения в RGB
        image_rgb = cv2.cvtColor(person_image, cv2.COLOR_BGR2RGB)

        # Обработка изображения с помощью MediaPipe Pose
        results = self.pose.process(image_rgb)

        if results.pose_landmarks:
            return results.pose_landmarks.landmark
        else:
            raise ValueError("Поза не обнаружена. Убедитесь, что на изображении видно тело человека.")
