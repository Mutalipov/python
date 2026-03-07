import cv2
import mediapipe as mp
from deepface import DeepFace
import os

# Путь к вашему фото
REFERENCE_IMG = "owner.jpg"

# Инициализация MediaPipe для быстрого обнаружения лиц
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)


def check_face(frame):
    """Сравнивает лицо на кадре с эталоном"""
    try:
        # DeepFace сравнивает лицо на кадре с вашим фото
        result = DeepFace.verify(frame, REFERENCE_IMG, model_name="VGG-Face", enforce_detection=False)
        return result['verified']
    except Exception as e:
        return False


def main():
    if not os.path.exists(REFERENCE_IMG):
        print(f"Пожалуйста, положите фото {REFERENCE_IMG} в папку со скриптом!")
        return

    cap = cv2.VideoCapture(0)
    print("Система запущена. Нажмите 'q' для выхода.")

    counter = 0  # Счетчик кадров, чтобы не перегружать процессор проверкой каждую секунду

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Быстрое обнаружение лица через MediaPipe
        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.detections:
            for detection in results.detections:
                # Рисуем рамку
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                    int(bboxC.width * iw), int(bboxC.height * ih)

                cv2.rectangle(frame, bbox, (255, 0, 255), 2)

                # 2. Каждые 30 кадров проверяем, вы ли это (чтобы не тормозило)
                counter += 1
                if counter % 30 == 0:
                    if check_face(frame):
                        print("✅ ДОСТУП РАЗРЕШЕН")
                        # Здесь можно вставить команду разблокировки
                    else:
                        print("❌ ЛИЦО НЕ УЗНАНО")

        cv2.imshow('MediaPipe FaceID', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()