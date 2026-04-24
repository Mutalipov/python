import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from deepface import DeepFace
import os
import threading
import numpy as np

# --- Настройки ---
REFERENCE_IMG = "owner.jpeg"
MODEL_PATH = "detector.bundle" # См. примечание ниже

class FaceIDSystem:
    def __init__(self):
        self.is_verified = False
        self.lock = threading.Lock()
        self.counter = 0
        
        # Загрузка детектора лиц (MediaPipe Task)
        # Нужно скачать файл модели: https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite
        base_options = python.BaseOptions(model_asset_path='face_detector.tflite')
        options = vision.FaceDetectorOptions(base_options=base_options)
        self.detector = vision.FaceDetector.create_from_options(options)

    def verify_face(self, frame):
        """Фоновая проверка лица через DeepFace"""
        try:
            # Используем более быструю модель Facenet512 или VGG-Face
            result = DeepFace.verify(frame, REFERENCE_IMG, 
                                     model_name="VGG-Face", 
                                     enforce_detection=False,
                                     detector_backend="skip") # Пропускаем детекцию, т.к. она уже сделана
            with self.lock:
                self.is_verified = result['verified']
        except Exception as e:
            print(f"Ошибка анализа: {e}")

    def run(self):
        cap = cv2.VideoCapture(0)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            # Конвертация для MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Детекция лиц
            detection_result = self.detector.detect(mp_image)

            if detection_result.detections:
                for detection in detection_result.detections:
                    bbox = detection.bounding_box
                    x, y, w, h = bbox.origin_x, bbox.origin_y, bbox.width, bbox.height
                    
                    # Рисуем рамку
                    color = (0, 255, 0) if self.is_verified else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    
                    # Запускаем проверку раз в 30 кадров в отдельном потоке
                    self.counter += 1
                    if self.counter % 30 == 0:
                        thread = threading.Thread(target=self.verify_face, args=(frame.copy(),))
                        thread.start()

            cv2.imshow('FaceID Python 3.12', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Важно: скачайте модель детектора face_detector.tflite перед запуском!
    if not os.path.exists(REFERENCE_IMG):
        print(f"Ошибка: положите файл {REFERENCE_IMG} в папку")
    else:
        app = FaceIDSystem()
        app.run()