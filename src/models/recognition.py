"""
识别模块接口占位：为后续接入本地模型（人脸/物体识别）预留。
实现者可以在此类中实现 load_model() 与 predict()，并在 GUI 中调用。
"""
from typing import List, Any

class Recognizer:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        """加载模型（占位）。
        实际项目中可加载 ONNX、PyTorch、TensorFlow 等本地模型。
        """
        self.model = None

    def predict(self, image_path: str) -> List[Any]:
        """对单张图片做识别，返回识别结果占位列表。"""
        # 返回空列表表示未识别任何东西（占位）
        return []
