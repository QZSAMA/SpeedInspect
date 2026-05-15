"""
方案2: 多阶段CNN分类方案
=========================
【推荐指数】★★★★☆
【适用场景】图像分类、已有类别标签、高准确率需求
【优势】准确率高、可解释性好、适合大规模分类
【成本】中等 - 需要分类标注，但不需要bbox
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Scheme2MultiStageCNNConfig:
    """多阶段CNN方案配置"""
    
    # 骨干网络选择
    backbone: str = "efficientnet_v2_s"  # resnet50, efficientnet_v2_s/m/l, convnext_tiny
    use_pretrained: bool = True
    
    # 训练配置
    epochs: int = 50
    batch_size: int = 32
    img_size: int = 384
    learning_rate: float = 0.001
    lr_scheduler: str = "cosine"  # cosine, step, plateau
    
    # 多阶段配置
    stage1_classes: List[str] = field(default_factory=lambda: [
        "structure",  # 结构问题 (墙/地板/天花板)
        "fixtures",   # 设施问题 (电器/ plumbing/门窗)
        "cosmetic"    # 外观问题 (油漆/家具/装饰)
    ])
    
    stage2_structure: List[str] = field(default_factory=lambda: [
        "wall_crack",
        "wall_damage",
        "floor_wear",
        "floor_damage",
        "ceiling_stain",
        "ceiling_crack"
    ])
    
    stage2_fixtures: List[str] = field(default_factory=lambda: [
        "electrical_hazard",
        "plumbing_issue",
        "window_damage",
        "door_damage",
        "appliance_damage"
    ])
    
    stage2_cosmetic: List[str] = field(default_factory=lambda: [
        "peeling_paint",
        "mold",
        "water_stain",
        "furniture_damage",
        "discoloration"
    ])
    
    # 数据增强
    use_augmentation: bool = True
    auto_augment: str = "rand-m9-mstd0.5-inc1"
    
    # 训练策略
    freeze_backbone: bool = False
    use_mixup: bool = True
    use_cutmix: bool = True
    label_smoothing: float = 0.1


class Scheme2MultiStageCNN:
    """多阶段CNN分类方案实现类"""
    
    def __init__(self, config: Optional[Scheme2MultiStageCNNConfig] = None):
        self.config = config or Scheme2MultiStageCNNConfig()
        self.base_dir = Path(__file__).parent
        self.working_dir = self.base_dir / "scheme2_cnn"
        self.working_dir.mkdir(exist_ok=True)
        
    def prepare_data_structure(self, raw_data_dir: Path, output_dir: Path):
        """
        准备多阶段分类的数据结构
        
        原始数据目录结构:
            raw_data_dir/
                class_a/
                    img1.jpg
                    img2.jpg
                    ...
                class_b/
                    ...
                    
        输出目录结构:
            output_dir/
                stage1/
                    train/
                        structure/
                        fixtures/
                        cosmetic/
                    val/
                    test/
                stage2/
                    structure/
                        train/
                            wall_crack/
                            ...
                        val/
                    fixtures/
                        ...
                    cosmetic/
                        ...
        """
        print("📁 准备多阶段数据结构...")
        print(f"输入目录: {raw_data_dir}")
        print(f"输出目录: {output_dir}")
        
        # 这里只是创建目录结构的模板
        # 实际项目中需要根据映射关系移动/复制文件
        
        structure = {
            "stage1": self.config.stage1_classes,
            "stage2": {
                "structure": self.config.stage2_structure,
                "fixtures": self.config.stage2_fixtures,
                "cosmetic": self.config.stage2_cosmetic
            }
        }
        
        for stage_name, stage_data in structure.items():
            if stage_name == "stage1":
                for split in ["train", "val", "test"]:
                    for cls in stage_data:
                        (output_dir / stage_name / split / cls).mkdir(parents=True, exist_ok=True)
            else:
                for sub_stage, classes in stage_data.items():
                    for split in ["train", "val", "test"]:
                        for cls in classes:
                            (output_dir / stage_name / sub_stage / split / cls).mkdir(parents=True, exist_ok=True)
        
        mapping_file = output_dir / "class_mapping.json"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 数据结构已准备, 映射文件: {mapping_file}")
        return output_dir
    
    def generate_training_code(self, data_dir: Path, output_dir: Optional[Path] = None):
        """
        生成PyTorch训练代码
        
        Args:
            data_dir: 数据集目录
            output_dir: 输出目录
        """
        output_dir = output_dir or self.working_dir
        output_dir.mkdir(exist_ok=True)
        
        # Stage 1 训练脚本
        stage1_script = '''
"""
多阶段CNN分类 - Stage 1: 粗分类
将问题分为结构问题、设施问题、外观问题三大类
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.transforms import autoaugment
import timm
from tqdm import tqdm
import numpy as np
from pathlib import Path
import argparse
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# 配置
CONFIG = {
    "backbone": "efficientnet_v2_s",
    "img_size": 384,
    "batch_size": 32,
    "epochs": 50,
    "lr": 0.001,
    "num_classes": 3,
    "data_dir": "data/stage1",
    "output_dir": "output/stage1"
}


def get_transforms(train: bool = True):
    '''获取数据变换'''
    if train:
        return transforms.Compose([
            transforms.Resize((CONFIG['img_size'], CONFIG['img_size'])),
            autoaugment.RandAugment(),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            transforms.RandomErasing(p=0.2)
        ])
    else:
        return transforms.Compose([
            transforms.Resize((CONFIG['img_size'], CONFIG['img_size'])),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])


def get_dataloaders(data_dir: str):
    '''获取数据加载器'''
    train_dataset = datasets.ImageFolder(
        root=f"{data_dir}/train",
        transform=get_transforms(train=True)
    )
    
    val_dataset = datasets.ImageFolder(
        root=f"{data_dir}/val",
        transform=get_transforms(train=False)
    )
    
    test_dataset = datasets.ImageFolder(
        root=f"{data_dir}/test",
        transform=get_transforms(train=False)
    )
    
    train_loader = DataLoader(
        train_dataset, batch_size=CONFIG['batch_size'],
        shuffle=True, num_workers=4, pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset, batch_size=CONFIG['batch_size'],
        shuffle=False, num_workers=4, pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset, batch_size=CONFIG['batch_size'],
        shuffle=False, num_workers=4, pin_memory=True
    )
    
    return train_loader, val_loader, test_loader, train_dataset.classes


def create_model(num_classes: int, backbone: str = "efficientnet_v2_s"):
    '''创建分类模型'''
    if backbone.startswith("resnet"):
        model = models.__dict__[backbone](pretrained=True)
        num_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_features, num_classes)
        )
    elif backbone.startswith("efficientnet"):
        model = timm.create_model(backbone, pretrained=True, num_classes=0)
        num_features = model.num_features
        model = nn.Sequential(
            model,
            nn.Dropout(0.3),
            nn.Linear(num_features, num_classes)
        )
    elif backbone.startswith("convnext"):
        model = timm.create_model(backbone, pretrained=True, num_classes=num_classes)
    else:
        raise ValueError(f"不支持的backbone: {backbone}")
    
    return model


def train_one_epoch(model, loader, criterion, optimizer, device, epoch):
    '''训练一个epoch'''
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    pbar = tqdm(loader, desc=f"Epoch {epoch}")
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        pbar.set_postfix({"loss": f"{loss.item():.4f}", "acc": f"{100.*correct/total:.2f}%"})
    
    return total_loss / len(loader), 100. * correct / total


def validate(model, loader, criterion, device):
    '''验证模型'''
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Validating"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    return total_loss / len(loader), 100. * correct / total, all_preds, all_labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default=CONFIG['data_dir'])
    parser.add_argument("--output_dir", type=str, default=CONFIG['output_dir'])
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 数据
    train_loader, val_loader, test_loader, classes = get_dataloaders(args.data_dir)
    print(f"类别: {classes}")
    
    # 模型
    model = create_model(len(classes), CONFIG['backbone'])
    model = model.to(device)
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=CONFIG['lr'], weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=CONFIG['epochs'])
    
    # 训练循环
    best_acc = 0
    train_losses, val_losses = [], []
    train_accs, val_accs = [], []
    
    for epoch in range(CONFIG['epochs']):
        print(f"\\n{'='*60}")
        print(f"Epoch {epoch+1}/{CONFIG['epochs']}")
        
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device, epoch)
        val_loss, val_acc, _, _ = validate(model, val_loader, criterion, device)
        
        scheduler.step()
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}%")
        print(f"Val   Loss: {val_loss:.4f} Acc: {val_acc:.2f}%")
        
        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'classes': classes
            }, output_dir / "best_model.pth")
            print(f"✅ 保存最佳模型 (Acc: {val_acc:.2f}%)")
    
    # 测试
    print("\\n在测试集上评估...")
    checkpoint = torch.load(output_dir / "best_model.pth")
    model.load_state_dict(checkpoint['model_state_dict'])
    test_loss, test_acc, test_preds, test_labels = validate(model, test_loader, criterion, device)
    
    print(f"Test Loss: {test_loss:.4f} Acc: {test_acc:.2f}%")
    print("\\n分类报告:")
    print(classification_report(test_labels, test_preds, target_names=classes))
    
    # 绘制训练曲线
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train')
    plt.plot(val_losses, label='Val')
    plt.title('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(train_accs, label='Train')
    plt.plot(val_accs, label='Val')
    plt.title('Accuracy (%)')
    plt.legend()
    plt.savefig(output_dir / "training_curves.png")
    
    # 绘制混淆矩阵
    cm = confusion_matrix(test_labels, test_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.savefig(output_dir / "confusion_matrix.png")
    
    print(f"\\n✅ 训练完成! 结果保存在: {output_dir}")


if __name__ == "__main__":
    main()
'''
        
        script_path = output_dir / "train_stage1.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(stage1_script)
        
        # Stage 2 训练脚本模板
        stage2_script = '''
"""
多阶段CNN分类 - Stage 2: 细分类
针对每个大类训练专门的子分类器
"""

import sys
import torch
from pathlib import Path

# 复用Stage 1的训练代码逻辑
from train_stage1 import (
    get_transforms, get_dataloaders, create_model,
    train_one_epoch, validate
)

STAGE2_CONFIGS = {
    "structure": {
        "num_classes": 6,
        "epochs": 60,
        "batch_size": 24,
        "backbone": "efficientnet_v2_m"
    },
    "fixtures": {
        "num_classes": 5,
        "epochs": 50,
        "batch_size": 32,
        "backbone": "efficientnet_v2_s"
    },
    "cosmetic": {
        "num_classes": 5,
        "epochs": 50,
        "batch_size": 32,
        "backbone": "efficientnet_v2_s"
    }
}


class MultiStageClassifier:
    """多阶段分类器"""
    
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.stage1_model = None
        self.stage2_models = {}
        self.classes = {}
        
    def load_models(self):
        """加载所有阶段的模型"""
        # 加载Stage 1
        stage1_ckpt = torch.load(self.model_dir / "stage1" / "best_model.pth")
        self.stage1_model = create_model(stage1_ckpt['num_classes'], "efficientnet_v2_s")
        self.stage1_model.load_state_dict(stage1_ckpt['model_state_dict'])
        self.stage1_model.to(self.device)
        self.stage1_model.eval()
        self.classes['stage1'] = stage1_ckpt['classes']
        
        # 加载Stage 2
        for sub_stage in ["structure", "fixtures", "cosmetic"]:
            ckpt_path = self.model_dir / "stage2" / sub_stage / "best_model.pth"
            if ckpt_path.exists():
                ckpt = torch.load(ckpt_path)
                model = create_model(ckpt['num_classes'], STAGE2_CONFIGS[sub_stage]['backbone'])
                model.load_state_dict(ckpt['model_state_dict'])
                model.to(self.device)
                model.eval()
                self.stage2_models[sub_stage] = model
                self.classes[sub_stage] = ckpt['classes']
    
    def predict(self, image_tensor):
        """两阶段预测"""
        # Stage 1: 粗分类
        with torch.no_grad():
            stage1_out = self.stage1_model(image_tensor.unsqueeze(0))
            stage1_pred = torch.argmax(stage1_out, dim=1).item()
            stage1_class = self.classes['stage1'][stage1_pred]
            stage1_conf = torch.softmax(stage1_out, dim=1)[0, stage1_pred].item()
        
        # Stage 2: 细分类
        if stage1_class in self.stage2_models:
            with torch.no_grad():
                stage2_out = self.stage2_models[stage1_class](image_tensor.unsqueeze(0))
                stage2_pred = torch.argmax(stage2_out, dim=1).item()
                stage2_class = self.classes[stage1_class][stage2_pred]
                stage2_conf = torch.softmax(stage2_out, dim=1)[0, stage2_pred].item()
        else:
            stage2_class = None
            stage2_conf = 0.0
        
        return {
            "stage1": {"class": stage1_class, "confidence": stage1_conf},
            "stage2": {"class": stage2_class, "confidence": stage2_conf}
        }


if __name__ == "__main__":
    print("Stage 2 训练脚本")
    print("请为每个子分类器分别运行类似Stage 1的训练代码")
    print("仅需修改: data_dir, num_classes, output_dir")
'''
        
        script_path2 = output_dir / "train_stage2.py"
        with open(script_path2, 'w', encoding='utf-8') as f:
            f.write(stage2_script)
        
        print(f"✅ Stage 1 训练脚本: {script_path}")
        print(f"✅ Stage 2 训练脚本: {script_path2}")
        
        return output_dir
    
    def create_readme(self):
        """创建方案说明文档"""
        readme_content = '''
# 方案2: 多阶段CNN分类方案

## 📋 方案概述
采用两阶段分类策略:
1. **Stage 1**: 粗分类 - 将问题分为结构问题、设施问题、外观问题
2. **Stage 2**: 细分类 - 对每个大类训练专门的子分类器

## 🎯 适用场景
- ✅ 高准确率需求
- ✅ 图像分类任务 (不需要bbox标注)
- ✅ 类别层次结构清晰
- ✅ 大规模分类任务

## 📊 技术特点
| 特性 | 描述 |
|------|------|
| 模型架构 | EfficientNetV2 / ConvNeXt / ResNet |
| 推理速度 | 中等 (需要两次前向传播) |
| 标注要求 | 只需分类标签 (不需要bbox) |
| 训练难度 | 中等 |
| 部署难度 | 中等 |
| 预期准确率 | 85-95% |

## 📁 数据标注
只需图像级分类标注，无需bbox:
```
data/
├── wall_crack/
│   ├── img001.jpg
│   ├── img002.jpg
│   └── ...
├── water_stain/
├── mold/
└── ...
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install torch torchvision timm opencv-python scikit-learn matplotlib seaborn pillow
```

### 2. 准备数据结构
```python
from scheme2_cnn import Scheme2MultiStageCNN, Scheme2MultiStageCNNConfig

config = Scheme2MultiStageCNNConfig()
scheme = Scheme2MultiStageCNN(config)

# 准备数据结构
scheme.prepare_data_structure(
    raw_data_dir=Path("raw_data/"),
    output_dir=Path("processed_data/")
)
```

### 3. 训练Stage 1
```bash
cd scheme2_cnn
python train_stage1.py --data_dir processed_data/stage1 --output_dir output/stage1
```

### 4. 训练Stage 2
分别为每个子类别训练:
```bash
# 结构问题子分类器
python train_stage1.py --data_dir processed_data/stage2/structure --output_dir output/stage2/structure

# 设施问题子分类器
python train_stage1.py --data_dir processed_data/stage2/fixtures --output_dir output/stage2/fixtures

# 外观问题子分类器
python train_stage1.py --data_dir processed_data/stage2/cosmetic --output_dir output/stage2/cosmetic
```

### 5. 使用训练好的模型进行推理
```python
from train_stage2 import MultiStageClassifier

classifier = MultiStageClassifier("output/")
classifier.load_models()

# 预测
result = classifier.predict(image_tensor)
print(f"问题类型: {result['stage2']['class']}")
print(f"置信度: {result['stage2']['confidence']:.2f}")
```

## 📈 多阶段分类优势

1. **准确率提升**: 细分类器专注于特定领域，准确率更高
2. **类别均衡**: 每个子分类器处理更均衡的类别分布
3. **可解释性**: 可以看到分类决策过程
4. **增量训练**: 新增类别时只需训练相关子分类器

## 💡 与目标检测结合使用

可以结合方案1的目标检测，形成完整pipeline:
```
视频帧 → YOLOv8检测 (定位) → Crop → CNN分类 (识别) → 输出结果
```

## 📚 参考资料
- EfficientNetV2: https://arxiv.org/abs/2104.00298
- ConvNeXt: https://arxiv.org/abs/2201.03545
- TIMM库: https://github.com/huggingface/pytorch-image-models
'''
        readme_path = self.working_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        return readme_path
    
    def get_requirements(self) -> List[str]:
        """获取所需依赖"""
        return [
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "timm>=0.9.0",
            "opencv-python>=4.8.0",
            "scikit-learn>=1.3.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "pillow>=10.0.0",
            "tqdm>=4.65.0"
        ]
