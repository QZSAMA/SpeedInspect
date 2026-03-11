# SpeedInspect - 房屋状态智能识别系统

<div align="center">
  <img src="docs/assets/logo.png" alt="SpeedInspect Logo" width="120">
  <h3>AI驱动的房屋状况智能检查平台</h3>
  <p>基于计算机视觉和深度学习技术，快速、客观、全面地评估房屋状况</p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
  [![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)](https://nextjs.org/)
  [![TensorFlow.js](https://img.shields.io/badge/TensorFlow.js-4.10+-orange.svg)](https://www.tensorflow.org/js)
</div>

## ✨ 核心功能

### 🎯 智能检测
- **AI图像识别**：自动识别墙面裂缝、水渍、霉斑、家具磨损、水电设施问题等15+类房屋问题
- **视频分析**：支持上传房屋视频，自动提取关键帧进行逐帧分析
- **严重程度分级**：MINOR/LOW/MODERATE/HIGH/CRITICAL五级分级
- **置信度评估**：每个检测结果提供置信度评分

### 📊 自动报告
- **综合评分**：自动生成0-100分的房屋综合状况评分
- **问题统计**：按严重程度分类统计问题数量
- **费用估算**：自动计算预估修复总费用
- **修复建议**：针对每个问题提供专业修复建议
- **多格式导出**：支持PDF/HTML/JSON三种格式报告导出

### 💰 订单管理
- **多种服务套餐**：标准版/高级版/企业版，满足不同用户需求
- **在线支付**：支持微信/支付宝/银行卡等多种支付方式
- **订单跟踪**：实时查看订单状态和处理进度
- **历史记录**：完整的订单和报告历史记录

### 🔐 用户系统
- **多方式登录**：支持手机号/邮箱/用户名登录
- **角色权限**：普通用户/企业用户/管理员/超级管理员多级权限
- **数据安全**：JWT认证，数据加密存储，用户数据隔离

## 🏗️ 技术架构

### 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 开发语言 |
| FastAPI | 0.104+ | Web框架 |
| Uvicorn | 0.24+ | ASGI服务器 |
| SQLAlchemy | 2.0+ | ORM框架 |
| PostgreSQL | 16+ | 关系型数据库 |
| Redis | 7+ | 缓存和会话存储 |
| Celery | 5.3+ | 异步任务队列 |
| Pydantic | 2.5+ | 数据验证 |
| Alembic | 1.12+ | 数据库迁移 |
| Structlog | 23.2+ | 结构化日志 |

### 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.1+ | 开发语言 |
| Next.js | 14.0 | React框架 |
| React | 18.2 | UI框架 |
| Redux Toolkit | 1.9+ | 状态管理 |
| Tailwind CSS | 3.3+ | CSS框架 |
| TensorFlow.js | 4.11+ | 前端AI推理 |
| Axios | 1.5+ | HTTP客户端 |
| Lucide React | 0.292+ | 图标库 |

### AI技术栈
- **深度学习框架**：TensorFlow / PyTorch
- **目标检测**：YOLOv8 / SSD
- **图像分类**：ResNet / EfficientNet
- **部署方案**：TensorFlow.js (前端) / TorchServe (后端)

## 🚀 快速开始

### 环境要求
- Python 3.12+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+ (可选，用于异步任务)

### 后端部署
```bash
# 1. 克隆项目
git clone https://github.com/QZSAMA/SpeedInspect.git
cd SpeedInspect/backend

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. 安装依赖
uv sync --all-extras

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息

# 5. 数据库迁移
alembic upgrade head

# 6. 启动服务
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端部署
```bash
# 1. 进入前端目录
cd ../frontend/web

# 2. 安装依赖
npm install

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置API地址

# 4. 启动开发服务器
npm run dev
```

### 访问地址
- 前端地址：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs
- Redoc文档：http://localhost:8000/redoc

## 📖 API文档

### 核心接口
| 模块 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 认证 | `/api/v1/auth/register` | POST | 用户注册 |
| 认证 | `/api/v1/auth/login` | POST | 用户登录 |
| 文件 | `/api/v1/files/upload` | POST | 上传文件 |
| AI | `/api/v1/ai/analyze` | POST | 提交视频分析任务 |
| AI | `/api/v1/ai/analysis/{task_id}/status` | GET | 查询分析状态 |
| 报告 | `/api/v1/reports` | GET | 获取报告列表 |
| 报告 | `/api/v1/reports/{report_id}` | GET | 获取报告详情 |
| 报告 | `/api/v1/reports/{report_id}/download` | GET | 下载报告 |
| 订单 | `/api/v1/orders` | POST | 创建订单 |
| 订单 | `/api/v1/orders/{order_id}/pay` | POST | 支付订单 |

完整API文档请访问：http://localhost:8000/docs

## 📁 项目结构

```
SpeedInspect/
├── backend/                 # 后端服务
│   ├── src/
│   │   └── app/
│   │       ├── core/        # 核心模块（数据库、安全、错误处理）
│   │       ├── features/    # 业务功能模块
│   │       │   ├── auth/    # 认证模块
│   │       │   ├── users/   # 用户模块
│   │       │   ├── files/   # 文件模块
│   │       │   ├── ai/      # AI分析模块
│   │       │   ├── reports/ # 报告模块
│   │       │   ├── orders/  # 订单模块
│   │       │   └── health/  # 健康检查模块
│   │       ├── shared/      # 公共组件
│   │       ├── config.py    # 配置管理
│   │       └── main.py      # 应用入口
│   ├── migrations/          # 数据库迁移
│   ├── tests/               # 测试用例
│   └── pyproject.toml       # 项目配置
├── frontend/                # 前端应用
│   └── web/
│       ├── app/             # Next.js App Router
│       ├── components/      # 公共组件
│       ├── lib/             # 工具库
│       ├── store/           # Redux状态管理
│       └── types/           # TypeScript类型定义
├── ai-engine/               # AI模型和算法
├── deploy/                  # 部署配置
├── docs/                    # 项目文档
│   ├── API.md               # API详细文档
│   ├── DATABASE_DESIGN.md   # 数据库设计文档
│   ├── DEPLOYMENT.md        # 部署指南
│   └── DEVELOPMENT.md       # 开发指南
├── scripts/                 # 工具脚本
└── README.md                # 项目说明
```

## 🧪 测试

### 后端测试
```bash
cd backend
uv run pytest
```

### 前端测试
```bash
cd frontend/web
npm run test
```

## 🚢 部署

### Docker部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

详细部署说明请参考 [部署指南](docs/DEPLOYMENT.md)

## 📚 相关文档

点击链接可以直接跳转到详细文档：
- [API接口文档](docs/API.md) - 完整的接口说明和使用示例
- [数据库设计文档](docs/DATABASE_DESIGN.md) - 详细的表结构设计和设计理念
- [开发指南](docs/DEVELOPMENT.md) - 本地开发环境搭建和开发规范
- [部署指南](docs/DEPLOYMENT.md) - 生产环境部署教程和配置说明
- [AI模型训练文档](ai-engine/README.md) - AI模型训练和优化指南

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Python Web框架
- [Next.js](https://nextjs.org/) - React全栈框架
- [TensorFlow.js](https://www.tensorflow.org/js) - 前端深度学习框架
- [YOLO](https://pjreddie.com/darknet/yolo/) - 目标检测算法

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 [Issue](https://github.com/QZSAMA/SpeedInspect/issues)
- 发送邮件到：KELVINCHAO1996@GMAIL.COM

---

**⚠️ 注意**：本项目当前为开发版本，生产环境使用请充分测试。
