"""
房屋检查AI模型训练 - 方案选择与配置
请根据文档选择合适的训练方案
"""

__version__ = "1.0.0"

# 各个方案的入口
from .scheme1_yolov8 import Scheme1YOLOv8
from .scheme2_cnn import Scheme2MultiStageCNN
from .scheme3_clip import Scheme3CLIPTransformer

__all__ = ["Scheme1YOLOv8", "Scheme2MultiStageCNN", "Scheme3CLIPTransformer"]
