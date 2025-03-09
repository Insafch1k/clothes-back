import cv2
import mediapipe as mp

# Инициализация MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# Загрузка изображения
image_path = 'person.jpg'  # Убедитесь, что путь правильный
image = cv2.imread(image_path)

# Проверка, загружено ли изображение
if image is None:
    print(f"Ошибка: Не удалось загрузить изображение по пути: {image_path}")
else:
    # Преобразование изображения в RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Обработка изображения с помощью MediaPipe Pose
    results = pose.process(image_rgb)

    # Проверка результатов
    if results.pose_landmarks:
        # Копия изображения для рисования
        annotated_image = image.copy()

        # Инициализация утилит для рисования
        mp_drawing = mp.solutions.drawing_utils

        # Рисование ключевых точек и соединений
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),  # Зеленый цвет для точек
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)  # Красный цвет для линий
        )

        # Сохранение результата
        cv2.imwrite('annotated_image.jpg', annotated_image)

        # Показ результата
        cv2.imshow('Annotated Image', annotated_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Поза не обнаружена. Убедитесь, что на изображении видно тело человека.")