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
