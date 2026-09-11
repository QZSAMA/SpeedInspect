# SpeedInspect

房屋巡检证据采集与 AI 辅助分析项目。

> 当前是开发原型，尚不具备完整生产巡检能力。2026-09-10 已将活动分支汇集到 `dev`，并将 GitHub 默认分支改为 `dev`。AI 检测和支付仍含模拟实现，Vercel 生产架构尚待迁移。

## 开发入口

```bash
git clone https://github.com/QZSAMA/SpeedInspect.git
cd SpeedInspect
git switch dev
```

Agent 开工前先读 [AGENTS.md](AGENTS.md)。本地启动和验证见 [开发指南](docs/DEVELOPMENT.md)。

## 文档

- [实际开发进度与代码审查](docs/PROJECT_STATUS.md)
- [Vercel 统一部署技术方案](docs/技术方案.md)
- [Vercel 架构决策记录 ADR-0001](docs/adr/0001-vercel-unified-runtime.md)
- [房屋租赁巡检业务方案](docs/房屋租赁巡检完整方案.md)
- [路线图与验收标准](docs/ROADMAP.md)
- [Vercel 部署指南](docs/DEPLOYMENT.md)
- [API 现状与目标契约](docs/API.md)
- [Agent 维护手册](docs/AGENT_RUNBOOK.md)
- [Git 工作流](docs/GIT_WORKFLOW.md)
- [数据库设计](docs/DATABASE_DESIGN.md)
- [变更记录](CHANGELOG.md)

## 目录状态

| 目录 | 当前用途 |
|---|---|
| `frontend/web` | Next.js 15.5 / React 18.3 原型；目标统一页面和 API 入口 |
| `backend` | FastAPI / SQLAlchemy 旧后端；迁移前用于开发和契约对照 |
| `ai-engine` | YOLO/CNN/CLIP 离线研究脚本；未接入在线分析 |
| `docs` | 当前事实、目标方案、路线图和维护规范 |
| `deploy`、`certs`、Docker 配置 | 历史自托管资料，不是目标 Vercel 部署路径 |

目标是一个 Vercel 项目承载应用和 API，数据、媒体和 AI 使用托管服务。许可证：[MIT](LICENSE)。
