# 方案1: YOLOv8 目标检测方案

## 📋 方案概述
使用YOLOv8进行端到端的目标检测，直接定位和分类房屋问题。

## 🎯 适用场景
- ✅ 快速原型开发
- ✅ 中小型数据集 (< 10,000 标注图像)
- ✅ 需要实时性能的部署场景
- ✅ 目标检测任务（定位+分类）

## 📊 技术特点
| 特性 | 描述 |
|------|------|
| 模型架构 | YOLOv8 (n/s/m/l/x) |
| 推理速度 | 快 (10-100+ FPS) |
| 标注要求 | 需要 bounding box 标注 |
| 训练难度 | 低 |
| 部署难度 | 低 |

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 准备数据集
数据集目录结构:
```
data/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

### 3. 生成配置并训练
```python
from scheme1_yolov8 import Scheme1YOLOv8, Scheme1YOLOv8Config

# 配置
config = Scheme1YOLOv8Config(
    model_size="m",  # 使用中等模型
    epochs=150,
    batch_size=8
)

# 初始化方案
scheme = Scheme1YOLOv8(config)

# 生成数据集配置
data_yaml = scheme.generate_dataset_yaml(Path("data/"))

# 生成训练脚本并训练
train_script = scheme.train(data_yaml)
```

### 4. 标注工具推荐
- LabelImg (https://github.com/HumanSignal/labelImg)
- CVAT (https://github.com/opencv/cvat)
- Roboflow (https://roboflow.com/)

## 📈 预期性能

| 模型大小 | mAP50 | 推理速度 (GPU) | 推理速度 (CPU) |
|---------|-------|----------------|----------------|
| YOLOv8n | ~75%  | 100+ FPS       | 10-15 FPS      |
| YOLOv8s | ~82%  | 80 FPS         | 5-8 FPS        |
| YOLOv8m | ~88%  | 40 FPS         | 2-3 FPS        |
| YOLOv8l | ~90%  | 25 FPS         | 1-2 FPS        |
| YOLOv8x | ~92%  | 15 FPS         | < 1 FPS        |

## 💡 优化建议
1. **数据增强**: 使用mosaic和mixup提高泛化能力
2. **模型集成**: 训练多个不同大小的模型集成推理
3. **类别均衡**: 处理类别不平衡问题
4. **迁移学习**: 使用房屋相关数据集预训练

## 📚 参考资料
- YOLOv8 官方文档: https://docs.ultralytics.com/
- Ultralytics GitHub: https://github.com/ultralytics/ultralytics
