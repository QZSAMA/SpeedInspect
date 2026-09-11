# 任务记录：Next.js 16 前端基线与 Vercel 迁移准备

## 目标

在已整合的 `dev` 上完成 Next.js 16 工程基线，修复认证门禁回归，确保 CI 执行前端测试，并把当前实现、Vercel 限制和后续验收条件同步到项目文档。

## 范围

- 升级 `frontend/web` 到 Next.js 16.3.4、ESLint 9 Flat Config；迁移 `middleware.ts` 为 `proxy.ts`。
- 默认 API 地址改为同源 `/api/v1`，移除旧的 localhost rewrite。
- 增加 Proxy/API 地址 Jest 回归；修复 Bearer header 空白匹配；CI 运行 Jest。
- 更新 Agent 规则、状态、路线图、API、部署、开发和变更文档。

## 非目标

- 本任务不实现 Next.js Route Handlers、服务端会话、PostgreSQL、Blob、外部 AI 或支付。
- 不创建 Vercel 项目、不配置真实密钥、不部署 Production、不修改 `main`。

## 基线与分支

- 分支：`dev`
- 基线 SHA：`757998b`
- 远端：`origin/dev`；GitHub 默认分支仍为 `dev`
- `origin/main`：`ebe4cc7`，是 `dev` 的祖先，无独有提交
- `origin/trae/solo-agent-p6YsKQ`：`ed1887c`，其提交已全部包含在 `dev`

## 验收命令与结果

以下命令在 2026-09-11、Windows 工作区执行；本机 Node 25.8.2 / Python 3.14，不是项目支持的最终运行时证据。

| 命令 | 结果 |
| --- | --- |
| `cd frontend/web; npm ci --ignore-scripts --no-audit --no-fund` | 退出码 0；因 Node 25 超出 `<23` 有 EBADENGINE 警告 |
| `npm test -- --runInBand` | 退出码 0；2 个套件、7 个用例通过 |
| `npm run lint` | 退出码 0 |
| `npx next typegen` | 退出码 0 |
| `npx tsc --noEmit` | 退出码 0 |
| `npm run build` | 退出码 0；Next.js 16.3.4/Turbopack，生成 `/`、`/login`、`/register`、`/_not-found` |
| `npm audit --omit=dev --json` | 退出码 0；生产依赖 0 个漏洞 |
| `npm audit --json` | 退出码 1；8 个开发/传递依赖告警，另立工具链升级任务，不使用 `--force` |
| `cd backend; uv sync --frozen --extra dev` | 退出码 0 |
| `uv run pytest` | 退出码 0；10 个用例通过，3 个 Pydantic 弃用警告；coverage 55% 只代表当前用例触达 |
| `git diff --check` | 退出码 0 |
| GitHub Actions CI（`0469fca`） | Node 22 前端与 Python 3.12 后端 job 均通过；运行：`https://github.com/QZSAMA/SpeedInspect/actions/runs/34573992721` |

## 未解决风险与限制

- 当前同源 `/api/v1` 没有对应的 Next.js Route Handlers；登录、注册、巡检业务尚不能在 Vercel 完成。
- 会话仍是旧 FastAPI JWT/localStorage 方案；Proxy 只是导航门禁，不能替代服务端授权。
- 上传、分析任务和报告仍使用本地/进程内原型实现；必须先接 PostgreSQL、私有 Blob、可恢复任务和真实 AI adapter。
- 尚未在 Node 22、Vercel Preview、真实 PostgreSQL/Blob/AI、iOS Safari 或 Android Chrome 上验收。
- 完整 npm audit 的 8 个开发依赖告警需另行评估；生产树审计为 0 不代表开发工具链无风险。

## 回滚方式

- 代码回滚使用新提交的 `git revert`，不重写共享历史。
- 若升级出现阻断，可回退到基线 `757998b` 的已知部署版本；生产数据和密钥不在本任务中操作。

## 交接下一步

1. 为浏览器登录、Cookie 刷新和主巡检流程增加 Playwright 验收。
2. 按 `docs/ROADMAP.md` Phase 1 实现服务端会话、PostgreSQL schema/migration 与同源 Route Handlers。
3. 在 Preview 完成权限隔离、Blob 直传、任务恢复、AI 错误路径和移动端验收后，才讨论 Production；任何生产部署仍需用户明确批准。
