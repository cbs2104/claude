"""
人脸识别模块
使用摄像头实时识别人脸
"""

import cv2
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import joblib


class FaceRecognizer:
    def __init__(self, data_dir="face_data", model_path="face_model.pkl"):
        self.data_dir = data_dir
        self.model_path = model_path
        self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.model = None
        self.label_encoder = {}

    def load_training_data(self):
        """加载训练数据"""
        X, y = [], []
        labels = []

        for person_name in os.listdir(self.data_dir):
            person_dir = os.path.join(self.data_dir, person_name)
            if not os.path.isdir(person_dir):
                continue

            if person_name not in self.label_encoder:
                self.label_encoder[person_name] = len(self.label_encoder)

            label_id = self.label_encoder[person_name]
            labels.append(person_name)

            for img_file in os.listdir(person_dir):
                if img_file.endswith('.jpg') or img_file.endswith('.png'):
                    img_path = os.path.join(person_dir, img_file)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

                    if img is not None:
                        # 调整到统一大小
                        img_resized = cv2.resize(img, (100, 100))
                        X.append(img_resized.flatten())
                        y.append(label_id)

        return np.array(X), np.array(y)

    def train(self):
        """训练人脸识别模型"""
        print("正在加载训练数据...")
        X, y = self.load_training_data()

        if len(X) == 0:
            print("✗ 没有找到训练数据，请先录入人脸")
            return False

        print(f"找到 {len(X)} 个样本")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("正在训练模型...")
        self.model = SVC(kernel='linear', probability=True)
        self.model.fit(X_train, y_train)

        accuracy = self.model.score(X_test, y_test)
        print(f"✓ 模型训练完成，准确率: {accuracy:.2%}")

        # 保存模型
        joblib.dump({
            'model': self.model,
            'label_encoder': self.label_encoder,
            'label_names': list(self.label_encoder.keys())
        }, self.model_path)
        print(f"✓ 模型已保存到 {self.model_path}")

        return True

    def load_model(self):
        """加载已训练的模型"""
        if os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.model = data['model']
            self.label_encoder = {name: i for i, name in enumerate(data['label_names'])}
            return True
        return False

    def recognize(self):
        """实时人脸识别"""
        if self.model is None:
            if not self.load_model():
                print("✗ 请先训练模型")
                return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头")
            return

        # 反向映射
        id_to_name = {v: k for k, v in self.label_encoder.items()}

        print("开始人脸识别，按 'q' 退出")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (100, 100))
                face_flat = face_resized.flatten().reshape(1, -1)

                # 预测
                prediction = self.model.predict(face_flat)[0]
                confidence = np.max(self.model.predict_proba(face_flat)[0])

                name = id_to_name.get(prediction, "未知")

                # 设置阈值
                if confidence > 0.6:
                    label = f"{name} ({confidence:.1%})"
                    color = (0, 255, 0)
                else:
                    label = f"未知 ({confidence:.1%})"
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, label, (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            cv2.imshow('Face Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    recognizer = FaceRecognizer()
    recognizer.train()
    recognizer.recognize()
