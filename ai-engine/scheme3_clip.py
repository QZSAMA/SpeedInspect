"""
方案3: Transformer + CLIP 方案
===============================
【推荐指数】★★★★☆
【适用场景】少样本学习、零样本分类、灵活扩展、高质量描述
【优势】数据效率高、支持零样本、可生成描述、扩展性强
【成本】较高 - 需要大模型，但标注成本低
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Scheme3CLIPTransformerConfig:
    """CLIP + Transformer方案配置"""
    
    # CLIP模型配置
    clip_model: str = "openai/clip-vit-large-patch14"  # 或 "ViT-B/32", "ViT-L/14", "ViT-L/14@336px"
    use_openclip: bool = False  # 使用OpenCLIP替代HuggingFace
    
    # 检测模型
    detector_model: str = "facebook/detr-resnet-50"  # DETR目标检测
    
    # 训练配置
    epochs: int = 20
    batch_size: int = 8
    learning_rate: float = 1e-5
    weight_decay: float = 0.01
    
    # 少样本配置
    num_shots: int = 5  # 每个类别使用的样本数
    use_ensemble: bool = True  # 集成多个提示词
    
    # 提示词工程
    prompts_templates: List[str] = field(default_factory=lambda: [
        "a photo showing {}",
        "an image of a house with {}",
        "this is {} in a house",
        "a close-up of {}",
        "a photo depicts {}",
        "an image featuring {}",
        "this picture shows {}",
        "a view of {}"
    ])
    
    # 问题类别（含描述）
    problem_definitions: Dict[str, str] = field(default_factory=lambda: {
        "wall_crack": "cracks on the wall, wall damage with fissures",
        "water_stain": "water stains, damp spots on ceiling or walls",
        "mold": "mold and mildew growth, fungal spots on surfaces",
        "peeling_paint": "peeling or flaking paint, paint coming off walls",
        "floor_wear": "floor wear and tear, scratches on flooring",
        "furniture_damage": "damaged furniture, scratches on tables and chairs",
        "electrical_hazard": "electrical hazards, broken sockets, exposed wires",
        "plumbing_issue": "plumbing problems, leaking pipes, water damage",
        "window_damage": "damaged windows, broken glass, faulty frames",
        "door_damage": "damaged doors, broken hinges, scratches"
    })
    
    # 严重程度描述
    severity_descriptions: Dict[str, str] = field(default_factory=lambda: {
        "minor": "minor damage, small issues, easy to fix",
        "low": "low severity, slight problems",
        "moderate": "moderate damage, noticeable issues",
        "high": "high severity, significant damage",
        "critical": "critical damage, dangerous, urgent repair needed"
    })


class Scheme3CLIPTransformer:
    """CLIP + Transformer方案实现类"""
    
    def __init__(self, config: Optional[Scheme3CLIPTransformerConfig] = None):
        self.config = config or Scheme3CLIPTransformerConfig()
        self.base_dir = Path(__file__).parent
        self.working_dir = self.base_dir / "scheme3_clip"
        self.working_dir.mkdir(exist_ok=True)
        
    def generate_training_code(self, output_dir: Optional[Path] = None):
        """
        生成CLIP训练和推理代码
        
        Args:
            output_dir: 输出目录
        """
        output_dir = output_dir or self.working_dir
        output_dir.mkdir(exist_ok=True)
        
        # 少样本学习脚本
        few_shot_script = '''
"""
方案3: CLIP 少样本学习
使用预训练CLIP模型进行零样本/少样本分类
"""

import torch
import torch.nn.functional as F
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from transformers import DetrImageProcessor, DetrForObjectDetection
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import json
from tqdm import tqdm
from dataclasses import dataclass
import cv2


@dataclass
class DetectionResult:
    """检测结果"""
    label: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    severity: str = "moderate"
    description: str = ""
    repair_suggestion: str = ""
    estimated_cost: float = 0.0


class HouseInspectionCLIP:
    """基于CLIP的房屋检查系统"""
    
    def __init__(
        self,
        clip_model_name: str = "openai/clip-vit-large-patch14",
        detector_model_name: str = "facebook/detr-resnet-50",
        device: str = None
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {self.device}")
        
        # 加载CLIP模型
        print("加载CLIP模型...")
        self.clip_model = CLIPModel.from_pretrained(clip_model_name).to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
        
        # 加载检测器 (可选)
        print("加载检测器...")
        self.detector = DetrForObjectDetection.from_pretrained(detector_model_name).to(self.device)
        self.detector_processor = DetrImageProcessor.from_pretrained(detector_model_name)
        
        # 问题类别和提示词
        self.problem_classes = {}
        self.prompt_templates = []
        self.text_features = None
        
    def set_problem_definitions(self, problem_definitions: Dict[str, str]):
        """设置问题定义"""
        self.problem_classes = problem_definitions
        
    def set_prompt_templates(self, templates: List[str]):
        """设置提示词模板"""
        self.prompt_templates = templates
        
    def _encode_texts(self) -> torch.Tensor:
        """编码所有问题类别的文本特征"""
        all_texts = []
        for problem_name, problem_desc in self.problem_classes.items():
            for template in self.prompt_templates:
                all_texts.append(template.format(problem_desc))
        
        # 编码
        inputs = self.clip_processor(
            text=all_texts,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)
        
        with torch.no_grad():
            text_features = self.clip_model.get_text_features(**inputs)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
        # 平均每个类别的多个提示词特征
        num_classes = len(self.problem_classes)
        num_templates = len(self.prompt_templates)
        text_features = text_features.view(num_classes, num_templates, -1)
        text_features = text_features.mean(dim=1)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        self.text_features = text_features
        return text_features
    
    def load_few_shot_examples(self, examples_dir: Path):
        """加载少样本示例（可选，用于微调）"""
        print("加载少样本示例...")
        
        few_shot_features = {}
        for class_name in self.problem_classes.keys():
            class_dir = examples_dir / class_name
            if not class_dir.exists():
                continue
                
            features = []
            for img_path in class_dir.glob("*.jpg"):
                image = Image.open(img_path).convert("RGB")
                inputs = self.clip_processor(
                    images=image,
                    return_tensors="pt"
                ).to(self.device)
                
                with torch.no_grad():
                    img_feature = self.clip_model.get_image_features(**inputs)
                    img_feature = img_feature / img_feature.norm(dim=-1, keepdim=True)
                    features.append(img_feature)
            
            if features:
                few_shot_features[class_name] = torch.cat(features, dim=0).mean(dim=0, keepdim=True)
        
        if few_shot_features:
            # 融合少样本特征和文本特征
            if self.text_features is None:
                self._encode_texts()
                
            for i, class_name in enumerate(self.problem_classes.keys()):
                if class_name in few_shot_features:
                    self.text_features[i] = (
                        0.7 * self.text_features[i] + 
                        0.3 * few_shot_features[class_name]
                    )
                    self.text_features[i] = self.text_features[i] / self.text_features[i].norm()
    
    def predict_image(
        self,
        image: Image.Image,
        threshold: float = 0.5,
        top_k: int = 3
    ) -> List[DetectionResult]:
        """
        预测单张图像
        
        Args:
            image: PIL图像
            threshold: 置信度阈值
            top_k: 返回Top-K结果
            
        Returns:
            检测结果列表
        """
        if self.text_features is None:
            self._encode_texts()
        
        # 编码图像
        inputs = self.clip_processor(
            images=image,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # 计算相似度
        similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)
        
        # 获取结果
        values, indices = similarity[0].topk(top_k)
        
        results = []
        for val, idx in zip(values, indices):
            if val < threshold:
                continue
                
            class_name = list(self.problem_classes.keys())[idx]
            results.append(DetectionResult(
                label=class_name,
                confidence=float(val),
                bbox=(0, 0, image.width, image.height),  # 全图（待改进）
                description=self.problem_classes[class_name]
            ))
        
        return results
    
    def detect_objects(self, image: Image.Image) -> List[Dict]:
        """使用DETR检测对象（提供定位）"""
        inputs = self.detector_processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.detector(**inputs)
        
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.detector_processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.5
        )[0]
        
        detections = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i, 2) for i in box.tolist()]
            detections.append({
                "score": float(score),
                "label": self.detector.config.id2label[int(label)],
                "bbox": box
            })
        
        return detections
    
    def predict_with_detection(
        self,
        image: Image.Image,
        threshold: float = 0.4
    ) -> List[DetectionResult]:
        """
        检测 + 分类结合
        
        流程:
            1. DETR检测可能的对象区域
            2. Crop每个区域
            3. CLIP分类每个区域
            4. 合并结果
        """
        # 检测对象
        detections = self.detect_objects(image)
        
        # 如果没有检测到对象，使用全图
        if not detections:
            return self.predict_image(image, threshold)
        
        final_results = []
        img_array = np.array(image)
        
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Crop区域
            crop_img = Image.fromarray(img_array[y1:y2, x1:x2])
            
            # 分类
            clip_results = self.predict_image(crop_img, threshold, top_k=1)
            
            for res in clip_results:
                res.bbox = (x1, y1, x2, y2)
                final_results.append(res)
        
        # 按置信度排序
        final_results.sort(key=lambda x: x.confidence, reverse=True)
        return final_results


def main():
    """示例使用"""
    # 初始化
    inspector = HouseInspectionCLIP()
    
    # 定义问题
    problem_defs = {
        "wall_crack": "cracks on the wall, wall damage",
        "water_stain": "water stains, damp spots",
        "mold": "mold and mildew growth",
        "peeling_paint": "peeling paint, flaking paint",
        "floor_wear": "floor wear and tear"
    }
    
    inspector.set_problem_definitions(problem_defs)
    inspector.set_prompt_templates([
        "a photo showing {}",
        "an image of {}"
    ])
    
    # 编码文本
    inspector._encode_texts()
    
    # 预测示例
    test_image = Image.open("test.jpg").convert("RGB")
    results = inspector.predict_with_detection(test_image, threshold=0.4)
    
    print(f"检测到 {len(results)} 个问题:")
    for res in results:
        print(f"  - {res.label}: {res.confidence:.2f}")


if __name__ == "__main__":
    main()
'''
        
        script_path = output_dir / "clip_inspector.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(few_shot_script)
        
        # 微调脚本
        finetune_script = '''
"""
CLIP模型微调脚本
在标注数据集上微调CLIP
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from pathlib import Path
from tqdm import tqdm
import json
from typing import Dict, List


class CLIPFineTuneDataset(Dataset):
    """CLIP微调数据集"""
    
    def __init__(self, data_dir: str, processor, split: str = "train"):
        self.data_dir = Path(data_dir)
        self.processor = processor
        self.split = split
        
        # 加载数据
        self.samples = []
        split_dir = self.data_dir / split
        
        for class_dir in split_dir.iterdir():
            if not class_dir.is_dir():
                continue
                
            class_name = class_dir.name
            for img_path in class_dir.glob("*.jpg"):
                self.samples.append({
                    "image_path": img_path,
                    "text": f"a photo of {class_name}"
                })
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = Image.open(sample["image_path"]).convert("RGB")
        
        return {
            "image": image,
            "text": sample["text"]
        }


def contrastive_loss(logits: torch.Tensor) -> torch.Tensor:
    """对比损失"""
    labels = torch.arange(len(logits), device=logits.device)
    loss_i = nn.CrossEntropyLoss()(logits, labels)
    loss_t = nn.CrossEntropyLoss()(logits.t(), labels)
    return (loss_i + loss_t) / 2


def finetune_clip(
    model_name: str,
    data_dir: str,
    output_dir: str,
    epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 1e-5
):
    """微调CLIP"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 加载模型
    model = CLIPModel.from_pretrained(model_name).to(device)
    processor = CLIPProcessor.from_pretrained(model_name)
    
    # 数据加载
    train_dataset = CLIPFineTuneDataset(data_dir, processor, "train")
    val_dataset = CLIPFineTuneDataset(data_dir, processor, "val")
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 优化器
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # 训练循环
    best_loss = float('inf')
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(epochs):
        print(f"\\nEpoch {epoch+1}/{epochs}")
        
        # 训练
        model.train()
        train_loss = 0
        
        pbar = tqdm(train_loader, desc="Training")
        for batch in pbar:
            inputs = processor(
                images=batch["image"],
                text=batch["text"],
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(device)
            
            outputs = model(**inputs)
            loss = contrastive_loss(outputs.logits_per_image)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})
        
        train_loss /= len(train_loader)
        
        # 验证
        model.eval()
        val_loss = 0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validation"):
                inputs = processor(
                    images=batch["image"],
                    text=batch["text"],
                    return_tensors="pt",
                    padding=True,
                    truncation=True
                ).to(device)
                
                outputs = model(**inputs)
                loss = contrastive_loss(outputs.logits_per_image)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        scheduler.step()
        
        print(f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        # 保存最佳模型
        if val_loss < best_loss:
            best_loss = val_loss
            model.save_pretrained(output_path / "best_model")
            processor.save_pretrained(output_path / "best_model")
            print(f"✅ 保存最佳模型 (Val Loss: {val_loss:.4f})")
    
    print("\\n微调完成!")


if __name__ == "__main__":
    finetune_clip(
        model_name="openai/clip-vit-base-patch32",
        data_dir="data/",
        output_dir="output/",
        epochs=10,
        batch_size=8
    )
'''
        
        script_path2 = output_dir / "finetune_clip.py"
        with open(script_path2, 'w', encoding='utf-8') as f:
            f.write(finetune_script)
        
        print(f"✅ CLIP推理脚本: {script_path}")
        print(f"✅ CLIP微调脚本: {script_path2}")
        
        return output_dir
    
    def create_readme(self):
        """创建方案说明文档"""
        readme_content = '''
# 方案3: Transformer + CLIP 方案

## 📋 方案概述
利用CLIP（Contrastive Language-Image Pre-training）的强大零样本和少样本学习能力，结合目标检测模型，构建灵活的房屋检查系统。

## 🎯 适用场景
- ✅ 少样本/零样本学习（标注数据有限）
- ✅ 需要灵活扩展新类别
- ✅ 自然语言描述问题
- ✅ 高质量的结果解释

## 📊 技术特点
| 特性 | 描述 |
|------|------|
| 核心模型 | CLIP (ViT-B/32, ViT-L/14) |
| 检测模型 | DETR / Faster R-CNN (可选) |
| 推理速度 | 中等 |
| 标注要求 | 低（少样本）或无（零样本） |
| 训练难度 | 低（零样本）- 中（微调） |
| 部署难度 | 中等 |

## 🚀 核心优势

### 1. 数据效率极高
| 方法 | 所需标注数据 |
|------|------------|
| 传统CNN | 1000+ / 类别 |
| YOLOv8 | 100-500+ / 类别 |
| **CLIP少样本** | **5-20 / 类别** |
| **CLIP零样本** | **0** |

### 2. 提示词工程
使用自然语言描述问题，不需要重新训练即可添加新类别:
```python
problem_definitions = {
    "wall_crack": "cracks on the wall, wall damage with fissures",
    "water_stain": "water stains, damp spots on ceiling or walls",
    "custom_issue": "your custom description here"  # 直接添加！
}
```

### 3. 提示词集成
使用多个提示词模板提升鲁棒性:
```python
templates = [
    "a photo showing {}",
    "an image of a house with {}",
    "this is {} in a house",
    # ...
]
```

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    输入图像/视频帧                        │
└──────────────────────────┬──────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
    ┌───────▼────────┐         ┌──────────▼──────────┐
    │  DETR检测器    │         │   不使用检测        │
    │  (提供定位)    │         │   (全图分类)        │
    └───────┬────────┘         └──────────┬──────────┘
            │                             │
    ┌───────▼────────┐                    │
    │  裁剪候选区域  │                    │
    └───────┬────────┘                    │
            └──────────────┬──────────────┘
                           │
                  ┌────────▼─────────┐
                  │  CLIP 分类器      │
                  │  (图像-文本匹配)  │
                  └────────┬─────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
     ┌────────▼─────────┐    ┌─────────▼─────────┐
     │  严重程度评估     │    │  修复建议生成      │
     │  (可选)           │    │  (可选)            │
     └────────┬─────────┘    └─────────┬─────────┘
              └────────────┬────────────┘
                           │
                  ┌────────▼─────────┐
                  │  最终结果输出     │
                  └──────────────────┘
```

## 📦 快速开始

### 1. 安装依赖
```bash
pip install torch torchvision transformers pillow opencv-python
```

### 2. 零样本使用（无需训练！）
```python
from clip_inspector import HouseInspectionCLIP

# 初始化
inspector = HouseInspectionCLIP()

# 定义问题（使用自然语言描述）
problem_definitions = {
    "wall_crack": "cracks on the wall, wall damage with fissures",
    "water_stain": "water stains, damp spots on ceiling or walls",
    "mold": "mold and mildew growth, fungal spots",
    # 添加新类别只需在这里定义！
}

inspector.set_problem_definitions(problem_definitions)
inspector.set_prompt_templates([
    "a photo showing {}",
    "an image of a house with {}"
])

# 预测
from PIL import Image
image = Image.open("test.jpg")
results = inspector.predict_with_detection(image, threshold=0.4)

for r in results:
    print(f"{r.label}: {r.confidence:.2f}")
```

### 3. 少样本微调（可选）
如果有少量标注数据:
```python
# 准备少量样本
data/
├── train/
│   ├── wall_crack/
│   │   ├── img1.jpg
│   │   └── img2.jpg (只需5-10张)
│   ├── water_stain/
│   └── ...
└── val/
    └── ...

# 加载少样本特征
inspector.load_few_shot_examples(Path("data/train/"))
```

### 4. 全量微调（可选）
```bash
python finetune_clip.py \
    --model_name openai/clip-vit-base-patch32 \
    --data_dir data/ \
    --output_dir output/ \
    --epochs 10
```

## 💡 提示词工程技巧

### 好的提示词示例
```python
# ✅ 好：具体、详细
"wall_crack": "cracks on the wall, wall damage with fissures"

# ✅ 好：多种描述
"water_stain": "water stains, damp spots, water damage on surfaces"

# ✅ 好：包含上下文
"mold": "mold and mildew growth in a house, fungal spots on walls"
```

### 差的提示词示例
```python
# ❌ 差：过于简单
"wall_crack": "crack"

# ❌ 差：模糊
"water_stain": "something wrong"
```

## 📈 性能参考

| CLIP模型 | 零样本准确率 | 少样本(5-shot)准确率 | 推理速度 |
|---------|------------|-------------------|---------|
| ViT-B/32 | ~60-70% | ~75-80% | 快 |
| ViT-B/16 | ~65-75% | ~80-85% | 中 |
| ViT-L/14 | ~70-80% | ~85-90% | 慢 |
| ViT-L/14@336px | ~75-85% | ~88-93% | 最慢 |

## 🔄 与其他方案结合

可以将三种方案结合使用，形成集成系统:
```
集成系统:
├── 方案1 (YOLOv8): 快速检测，提供bbox
├── 方案2 (CNN): 高准确率分类
└── 方案3 (CLIP): 零样本扩展，生成描述
```

## 📚 参考资料
- CLIP论文: https://arxiv.org/abs/2103.00020
- OpenCLIP: https://github.com/mlfoundations/open_clip
- HuggingFace CLIP: https://huggingface.co/docs/transformers/model_doc/clip
- DETR论文: https://arxiv.org/abs/2005.12872
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
            "transformers>=4.30.0",
            "pillow>=10.0.0",
            "opencv-python>=4.8.0",
            "tqdm>=4.65.0"
        ]
