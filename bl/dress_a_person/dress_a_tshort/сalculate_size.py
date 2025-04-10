import mediapipe as mp

class ClothesCalculator:
    def __init__(self, person_image):
        self.person_image = person_image

    def calculate_clothes_size(self, landmarks):
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]

        height, width, _ = self.person_image.shape
        left_shoulder_x = int(left_shoulder.x * width)
        left_shoulder_y = int(left_shoulder.y * height)
        right_shoulder_x = int(right_shoulder.x * width)
        left_hip_y = int(left_hip.y * height)

        clothes_width = abs(right_shoulder_x - left_shoulder_x) * 2.1
        clothes_height = abs(left_hip_y - left_shoulder_y) * 1.7

        start_x = min(left_shoulder_x, right_shoulder_x) - int(clothes_width * 0.28)
        start_y = left_shoulder_y - int(clothes_height * 0.26)

        return clothes_width, clothes_height, start_x, start_y