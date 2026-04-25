# 人脸识别系统

基于 OpenCV 和 scikit-learn 的人脸录入和识别系统。

## 功能

- 人脸录入：通过摄像头收集人脸数据
- 人脸识别：实时识别摄像头中的人脸
- 模型管理：训练和加载识别模型

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 录入人脸

```bash
python main.py --enroll 张三
```

按照提示，对准摄像头，系统会自动采集30张人脸照片。

### 2. 训练模型

```bash
python main.py --retrain
```

### 3. 实时识别

```bash
python main.py --recognize
```

### 4. 查看已录入人员

```bash
python main.py --list
```

## 目录结构

```
face_relate/
├── face_enroll.py      # 人脸录入模块
├── face_recognize.py   # 人脸识别模块
├── main.py             # 主程序
├── requirements.txt    # 依赖列表
└── face_data/          # 人脸数据目录（自动创建）
```

## 注意事项

- 确保摄像头可用
- 录入时保持光线充足
- 建议每人录入至少30张照片以获得更好的识别效果
