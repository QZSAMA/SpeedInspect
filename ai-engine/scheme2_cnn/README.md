# 方案2: 多阶段CNN分类方案

## 📋 方案概述
采用两阶段分类策略:
1. **Stage 1**: 粗分类 - 将问题分为结构问题、设施问题、外观问题
2. **Stage 2**: 细分类 - 对每个大类训练专门的子分类器

## 🎯 适用场景
- ✅ 高准确率需求
- ✅ 图像分类任务（不需要bbox标注）
- ✅ 类别层次结构清晰
- ✅ 大规模分类任务

## 📊 技术特点
| 特性 | 描述 |
|------|------|
| 模型架构 | EfficientNetV2 / ConvNeXt / ResNet |
| 推理速度 | 中等（需要两次前向传播） |
| 标注要求 | 只需分类标签（不需要bbox） |
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
视频帧 → YOLOv8检测（定位） → Crop → CNN分类（识别） → 输出结果
```

## 📚 参考资料
- EfficientNetV2: https://arxiv.org/abs/2104.00298
- ConvNeXt: https://arxiv.org/abs/2201.03545
- TIMM库: https://github.com/huggingface/pytorch-image-models
