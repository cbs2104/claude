"""
人脸识别系统主程序
"""

import os
import argparse
from face_enroll import FaceEnroll
from face_recognize import FaceRecognizer


def main():
    parser = argparse.ArgumentParser(description="人脸识别系统")
    parser.add_argument('--enroll', metavar='NAME', help='录入人脸，指定人员姓名')
    parser.add_argument('--retrain', action='store_true', help='重新训练模型')
    parser.add_argument('--recognize', action='store_true', help='启动人脸识别')
    parser.add_argument('--list', action='store_true', help='列出已录入人员')

    args = parser.parse_args()

    if args.enroll:
        enroller = FaceEnroll()
        enroller.enroll_person(args.enroll)

    elif args.retrain:
        recognizer = FaceRecognizer()
        recognizer.train()

    elif args.recognize:
        recognizer = FaceRecognizer()
        recognizer.recognize()

    elif args.list:
        enroller = FaceEnroll()
        persons = enroller.list_enrolled()
        if persons:
            print("已录入人员:")
            for p in persons:
                print(f"  - {p}")
        else:
            print("暂无录入人员")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
