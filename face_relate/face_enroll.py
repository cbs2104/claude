"""
人脸录入模块
收集人脸数据并保存到本地数据库
"""

import cv2
import os
import numpy as np
from datetime import datetime


class FaceEnroll:
    def __init__(self, data_dir="face_data"):
        self.data_dir = data_dir
        self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        os.makedirs(self.data_dir, exist_ok=True)

    def enroll_person(self, name, num_samples=30):
        """录入一个人的人脸数据"""
        person_dir = os.path.join(self.data_dir, name)
        os.makedirs(person_dir, exist_ok=True)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头")
            return False

        print(f"正在录入 {name} 的人脸数据... 按 'q' 退出")
        print(f"需要采集 {num_samples} 张照片")

        count = 0
        while count < num_samples:
            ret, frame = cap.read()
            if not ret:
                print("无法读取摄像头画面")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                face_roi = gray[y:y+h, x:x+w]

                # 保存人脸图像
                img_path = os.path.join(person_dir, f"{name}_{count}.jpg")
                cv2.imwrite(img_path, face_roi)
                count += 1
                print(f"已采集 {count}/{num_samples}")

                if count >= num_samples:
                    break

            cv2.imshow('Face Enrollment', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if count >= num_samples:
            print(f"✓ {name} 的人脸数据录入完成，共采集 {count} 张")
            return True
        else:
            print(f"✗ 录入被中断，仅采集 {count} 张")
            return False

    def list_enrolled(self):
        """列出已录入的人员"""
        persons = [d for d in os.listdir(self.data_dir)
                   if os.path.isdir(os.path.join(self.data_dir, d))]
        return persons


if __name__ == "__main__":
    enroller = FaceEnroll()
    print("已录入人员:", enroller.list_enrolled())
    name = input("请输入要录入的人员姓名: ")
    enroller.enroll_person(name)
