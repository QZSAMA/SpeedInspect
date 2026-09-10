# 开发指南

## 环境

推荐 Git、Node.js 22.x、npm 和 Python 3.12 + uv。`frontend/web/package.json` 当前声明 `>=20.9 <23`，Vercel、CI 与本地应固定同一 Node 22.x；审查机器的 Node 25 构建结果不能替代该环境验证。

## 获取代码

```bash
git clone https://github.com/QZSAMA/SpeedInspect.git
cd SpeedInspect
git switch dev
git pull --ff-only origin dev
```

开始前阅读根 [AGENTS.md](../AGENTS.md) 和 [项目状态](PROJECT_STATUS.md)。不要从 `main` 开发，除非处理经授权的发布或热修复。

## 前端

```bash
cd frontend/web
npm ci
npm run dev
```

当前页面请求独立 FastAPI，本地另开后端后设置 `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`。生产目标是同源 Next.js API；不要把 localhost rewrite 当作 Vercel 配置。

验证：

```bash
npm run lint
npx tsc --noEmit
npm test -- --runInBand
npm run build
npm audit --omit=dev
```

当前 Jest 没有用例，`npm test` 失败是已知基线，不能用 `--passWithNoTests` 冒充通过。新增高风险行为时先写能复现问题的测试。

## 旧 FastAPI 后端

```bash
cd backend
uv sync --frozen --extra dev
# Windows PowerShell
$env:SECRET_KEY='local-development-only-change-me'
$env:JWT_SECRET='local-development-only-change-me'
$env:DATABASE_URL='sqlite+aiosqlite:///./speedinspect.local.db'
uv run uvicorn src.app.main:app --reload
```

验证：

```bash
uv run pytest
uv run ruff check src
```

pytest 当前有安全/路由回归；Ruff 能运行但有较多遗留告警。不要一次性自动修复整个后端并混入功能提交。

## 环境与数据规则

- 复制 `.env.example` 到本地环境文件，绝不提交真实凭据。
- `frontend/web/.env.example` 只放公开的本地开发配置；`NEXT_PUBLIC_*` 会进入浏览器 bundle，不能放数据库、JWT、加密、Blob 或 AI 密钥。
- 测试使用合成媒体、临时数据库和假密钥。不要使用或打印生产凭据。
- SQLite、上传目录、coverage、`.next`、`node_modules` 和虚拟环境不进入 Git。
- Alembic/后续数据库迁移是源码，必须跟踪和审查。
- mock 摄像头只在开发环境显式启用；随机 AI、模拟支付不能作为可验收结果。

## 提交前

检查 `git diff --check`、`git status --short`，运行与改动对应的检查，明确记录退出码、警告和未验证项。使用显式路径 stage，提交信息采用 `feat:`、`fix:`、`docs:`、`test:` 或 `chore:`。
