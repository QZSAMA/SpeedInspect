"""
方案1: YOLOv8 目标检测方案
===========================
【推荐指数】★★★★★
【适用场景】快速原型、中小型数据集、目标检测
【优势】训练速度快、部署简单、实时性能优秀
【成本】低 - 可使用预训练模型快速微调
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import json
from dataclasses import dataclass, field


@dataclass
class Scheme1YOLOv8Config:
    """YOLOv8 方案配置"""
    
    # 模型配置
    model_size: str = "n"  # n/s/m/l/x (nano/small/medium/large/xlarge)
    model_type: str = "detection"  # detection/segmentation/classify
    
    # 训练配置
    epochs: int = 100
    batch_size: int = 16
    img_size: int = 640
    learning_rate: float = 0.01
    device: str = "0"  # 0=GPU, cpu=CPU
    
    # 数据配置
    train_split: float = 0.7
    val_split: float = 0.2
    test_split: float = 0.1
    
    # 增强配置
    augment: bool = True
    mosaic: float = 1.0
    mixup: float = 0.15
    
    # 问题类别定义
    problem_classes: List[str] = field(default_factory=lambda: [
        "wall_crack",        # 墙面裂缝
        "water_stain",       # 水渍
        "mold",              # 霉斑
        "peeling_paint",     # 油漆剥落
        "floor_wear",        # 地板磨损
        "furniture_damage",  # 家具损坏
        "electrical_hazard", # 电气隐患
        "plumbing_issue",    #  plumbing问题
        "window_damage",     # 窗户损坏
        "door_damage"        # 门损坏
    ])


class Scheme1YOLOv8:
    """YOLOv8 方案实现类"""
    
    def __init__(self, config: Optional[Scheme1YOLOv8Config] = None):
        self.config = config or Scheme1YOLOv8Config()
        self.base_dir = Path(__file__).parent
        self.working_dir = self.base_dir / "scheme1_yolov8"
        self.working_dir.mkdir(exist_ok=True)
        
    def generate_dataset_yaml(self, data_dir: Path) -> Path:
        """
        生成YOLO格式的数据集配置文件
        
        Args:
            data_dir: 数据集根目录，结构应为:
                     data_dir/
                        images/
                            train/
                            val/
                            test/
                        labels/
                            train/
                            val/
                            test/
        """
        yaml_path = self.working_dir / "dataset.yaml"
        
        yaml_content = {
            "path": str(data_dir.absolute()),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "names": {i: name for i, name in enumerate(self.config.problem_classes)},
            "nc": len(self.config.problem_classes)
        }
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, allow_unicode=True)
            
        print(f"✅ 数据集配置文件已生成: {yaml_path}")
        return yaml_path
    
    def train(self, data_yaml: Path, output_dir: Optional[Path] = None):
        """
        训练YOLOv8模型
        
        Args:
            data_yaml: 数据集配置文件路径
            output_dir: 输出目录
        """
        output_dir = output_dir or self.working_dir / "runs"
        
        print("=" * 50)
        print("🚀 方案1: YOLOv8 目标检测 - 训练启动")
        print("=" * 50)
        print(f"📊 配置信息:")
        print(f"   - 模型大小: {self.config.model_size}")
        print(f"   - 类别数: {len(self.config.problem_classes)}")
        print(f"   - 训练轮数: {self.config.epochs}")
        print(f"   - 批量大小: {self.config.batch_size}")
        print(f"   - 图像尺寸: {self.config.img_size}")
        print()
        
        # 训练脚本模板
        train_script = f'''
"""
YOLOv8 训练脚本
自动生成的训练代码，请安装依赖后运行
"""

from ultralytics import YOLO
import torch

def main():
    # 检查设备
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {{device}}")
    
    # 加载预训练模型
    model = YOLO(f"yolov8{self.config.model_size}.pt")
    
    # 训练配置
    results = model.train(
        data="{data_yaml}",
        epochs={self.config.epochs},
        imgsz={self.config.img_size},
        batch={self.config.batch_size},
        lr0={self.config.learning_rate},
        device=device,
        project="{output_dir}",
        name="house_inspection",
        exist_ok=True,
        augment={self.config.augment},
        mosaic={self.config.mosaic},
        mixup={self.config.mixup},
        patience=50,
        save=True,
        plots=True
    )
    
    # 验证
    print("\\n开始验证...")
    metrics = model.val()
    print(f"mAP50-95: {{metrics.box.map:.4f}}")
    print(f"mAP50: {{metrics.box.map50:.4f}}")
    
    # 导出模型
    print("\\n导出模型...")
    model.export(format="onnx")
    model.export(format="torchscript")
    
    print("\\n✅ 训练完成!")

if __name__ == "__main__":
    main()
'''
        
        script_path = self.working_dir / "train.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(train_script)
            
        print(f"📝 训练脚本已生成: {script_path}")
        print()
        print("📦 安装依赖:")
        print("   pip install ultralytics torch torchvision opencv-python")
        print()
        print("▶️  运行训练:")
        print(f"   cd {self.working_dir} && python train.py")
        
        return script_path
    
    def export_for_inference(self, model_path: Path, export_dir: Optional[Path] = None):
        """
        导出推理模型
        
        Args:
            model_path: 训练好的模型路径
            export_dir: 导出目录
        """
        export_dir = export_dir or self.working_dir / "export"
        export_dir.mkdir(exist_ok=True)
        
        export_script = f'''
"""
模型导出与推理集成脚本
"""

from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

class HouseInspectionDetector:
    \"\"\"房屋检查检测器\"\"\"
    
    def __init__(self, model_path: str, conf_threshold: float = 0.5):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.class_names = {json.load(open("{self.working_dir / 'dataset_yaml'}"))["names"]}
    
    def predict(self, image: np.ndarray) -> List[Dict]:
        \"\"\"
        预测图像中的问题
        
        Args:
            image: OpenCV格式图像 (BGR)
            
        Returns:
            检测结果列表
        \"\"\"
        results = self.model(image, conf=self.conf_threshold)
        
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = self.class_names[cls_id]
                
                detections.append({{
                    "class": class_name,
                    "confidence": conf,
                    "bbox": [float(x1), float(y1), float(x2), float(y2)]
                }})
        
        return detections

if __name__ == "__main__":
    # 使用示例
    detector = HouseInspectionDetector("{model_path}")
    
    # 测试图片
    test_image = cv2.imread("test.jpg")
    if test_image is not None:
        results = detector.predict(test_image)
        print(f"检测到 {{len(results)}} 个问题")
        for r in results:
            print(f"  - {{r['class']}}: {{r['confidence']:.2f}}")
'''
        
        script_path = export_dir / "inference.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(export_script)
            
        print(f"✅ 推理脚本已生成: {script_path}")
        return script_path
    
    def get_requirements(self) -> List[str]:
        """获取所需依赖"""
        return [
            "ultralytics>=8.0.0",
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "opencv-python>=4.8.0",
            "pyyaml>=6.0",
            "numpy>=1.24.0"
        ]
    
    def create_readme(self):
        """创建方案说明文档"""
        readme_content = '''
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
'''
        readme_path = self.working_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        return readme_path
