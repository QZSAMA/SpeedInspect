# SpeedInspect - 房屋状态智能识别SaaS

基于AI技术的智能房屋验房系统，为租客/房东提供全自动验房、状态评估、报告生成服务，解决传统验房效率低、不透明、纠纷多的痛点。

## 📁 项目结构
```
SpeedInspect/
├── 📁 frontend/                    # 前端所有项目
│   ├── 📁 web/                     # Next.js H5端 + 管理后台（现有代码已迁移至此）
│   ├── 📁 app/                     # React Native 移动端（iOS+安卓）
│   └── 📁 miniprogram/             # Taro 小程序端（微信/支付宝/抖音）
├── 📁 backend/                     # 后端所有服务（FastAPI微服务）
│   ├── 📁 user-service/            # 用户服务
│   ├── 📁 order-service/           # 订单服务
│   ├── 📁 report-service/          # 报告服务
│   ├── 📁 agent-service/           # Agent调度服务
│   └── 📁 common/                  # 公共库
├── 📁 ai-engine/                   # AI引擎模块（独立部署）
│   ├── 📁 detection/               # 目标检测模块
│   ├── 📁 ocr/                     # OCR识别模块
│   ├── 📁 llm/                     # LLM报告生成模块
│   └── 📁 agent/                   # Agent核心逻辑
├── 📁 docs/                        # 项目文档
├── 📁 deploy/                      # 部署配置
├── 📁 scripts/                     # 工具脚本
└── README.md
```

## 🚀 快速开始
### 前端Web端开发
```bash
cd frontend/web
npm install
npm run dev
```
访问 http://localhost:3000

## 🛠️ 技术栈
- **前端**：Next.js 14 + React 18 + TypeScript + Tailwind CSS + Redux Toolkit
- **后端**：Python 3.12 + FastAPI + PostgreSQL + Redis
- **AI引擎**：PyTorch + YOLOv8 + PaddleOCR + LangChain + LangGraph
- **部署**：Docker + Kubernetes + GitHub Actions

## ✨ 核心功能
- ✅ 完整的验房流程：房屋类型选择 → 视频录制 → AI分析 → 报告生成
- ✅ 浏览器端AI推理，支持离线使用
- ✅ 智能识别8大类房屋缺陷，自动估算维修成本
- ✅ 自动生成专业验房报告，支持下载和分享
- 🔄 后续开发：云端存储、AI助手、多端适配等

## 📚 文档
- [技术方案](./docs/技术方案.md)
- [dev分支代码分析报告](./docs/dev分支代码分析报告.md)
- [API文档](./docs/API文档.md)
- [部署文档](./docs/部署文档.md)

## 🤝 贡献
欢迎提交PR和Issue，共同完善项目！
