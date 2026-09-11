# Changelog

本文件记录 SpeedInspect 的重要变更。项目尚未发布稳定生产版本；`Unreleased` 记录已进入 `dev`、但尚未晋级生产发布的变更。

## [Unreleased] - 2026-09-11

### 架构决策

- 新增 [ADR-0001](docs/adr/0001-vercel-unified-runtime.md)，明确单个 Next.js/Vercel 项目、托管 PostgreSQL、私有 Blob、服务端会话和可恢复分析任务的迁移边界与回滚要求。

### 工程基线

- 新增 `.github/workflows/ci.yml`：在 Node 22 与 Python 3.12 上运行前端 typegen、类型检查、Lint、构建及后端 pytest。
- 远端 `dev` 已通过非强制快进更新到 `e9c9377`；GitHub 默认分支保持为 `dev`。

### 分支与开发流程

- 将远端默认分支和后续日常开发基线统一为 `dev`。
- 核对三条现存分支：`dev` 与 `trae/solo-agent-p6YsKQ` 均指向 `ed1887c`；`main` 指向 `ebe4cc7`，是 `dev` 的祖先且没有独有提交。现存分支成果均已包含在 `dev`，无需额外合并。
- 约定 `main` 只保留明确批准的发布快照；本轮未部署生产，也未把 `dev` 推入 `main`。

### 安全修复

- 限制本地文件读取与删除只能在经过校验的当前用户 UUID 目录内进行，移除跨用户全局查找 fallback。
- 校验文件 ID 和用户 ID 为 UUID，并阻止 glob 模式和路径型标识符影响文件解析。
- 从当前 Git 索引移除开发 SQLite 数据库和 5 个 WebM 运行时媒体文件，补充数据库、上传目录、环境文件及 Python 缓存忽略规则。
- 恢复数据库 migration 文件应作为源码跟踪的规则。
- 清理前端环境变量示例中的数据库、JWT 与所谓客户端加密密钥，明确 `NEXT_PUBLIC_*` 不能承载秘密。

### 修复

- 去除报告 router 的重复 `/reports` 前缀，使公开契约回到 `/api/v1/reports` 与 `/api/v1/reports/{report_id}`。
- 为真实与模拟摄像头实现增加统一实例类型，修复 TypeScript 将运行时类值用作类型的问题。
- 将 Next.js `outputFileTracingRoot` 改成基于项目目录解析的绝对路径。
- 调整 Ruff 配置位置并移除不受当前版本支持的规则，使检查器能够运行。
- 升级 Next.js 至 15.5.24、React 至 18.3.1，并同步直接依赖与锁文件中的安全更新。

### 测试

- 新增文件所有者访问、跨用户拒绝、删除隔离、缺少所有者、非法 UUID/glob 输入和报告公开路由契约回归，共收集 10 个用例。
- 回归测试遵循红绿过程：修复前 7 failed / 3 passed，最终复跑为 10 passed；仍有 3 个 Pydantic 弃用 warning。
- 本次显示的后端 coverage 为 55%，只反映新增小范围用例触达的代码，不能解释为项目整体测试覆盖率。
- 前端 `npm run lint`、`npx tsc --noEmit`、`npm run build` 均通过；审查机器使用 Node 25.8.2，超出项目声明的 Node 20/22 支持范围，仍需在 Node 22.x 和 Vercel Preview 复验。

### 文档与 Agent 维护准备

- 新增项目级 Agent 规则入口，并补齐真实状态、Vercel 部署约束、开发流程、路线图、API 契约和维护运行手册。
- 明确区分已实现功能、模拟功能、研究代码和目标架构；废止旧分析报告中未经代码和测试支持的完成率、准确率及上线周期说法。
- 将产品定位收敛为房屋巡检辅助工具：保存证据并生成待人工复核的建议，不宣称判断结构安全、责任归属或提供法律鉴定。
- 记录用户已接受的部署边界：页面与接口统一部署在 Vercel，可使用托管 PostgreSQL、私有 Blob 和外部 AI API。

### 已知问题

- AI 分析状态保存在 `AIService` 实例内存中，POST 与 GET 请求不能可靠共享，进程或函数结束后会丢失；返回响应后的 `asyncio.create_task` 不适合 Vercel 关键任务。
- 首页把“任务已提交”响应当成最终分析结果，没有轮询任务状态，随后以空 `report_id` 请求报告；主巡检链路尚未打通。
- AI 状态查询的 404 分支还存在局部变量遮蔽 `status` 模块的问题，任务缺失时可能抛出属性错误。
- AI 提交时不校验文件存在或归属，文件缺失时仍会继续生成随机模板；前后端 AI 检测都使用随机模拟结果，`ai-engine` 仅为离线研究脚本；没有已验证的真实模型服务。
- 认证仍使用 `localStorage` 和脚本可读 Cookie，middleware 只检查令牌是否存在；刷新令牌请求、注册字段和密码约束还存在协议差异。
- `lib/encryption.ts` 的 key 由公开环境变量或硬编码 fallback 提供，不能视为客户端数据加密；该未接入模块启用前必须删除或重新设计为服务端密钥管理。
- 文件上传仍整段读入内存并写本地磁盘，缺少 MIME、大小和内容校验；尚未迁移到私有 Blob 直传。
- PDF 导出、持久分享、OCR、状态比对、Agent 对话和真实支付尚未实现；当前支付接口会模拟成功，不能用于生产。
- 报告/订单列表的分页响应和总数查询不正确；报告更新/删除还会把 Pydantic schema 当作 ORM 实体，数据库 CRUD 需要集成测试与修复。
- 前端没有测试用例，`npm test -- --runInBand` 因未发现测试退出 1，且构建生成的 `.next/standalone` 会产生 Jest package-name collision warning。
- `npm audit --omit=dev` 仍有 1 个 high 和 1 个 moderate 漏洞；`next@15.5.24` 间接固定 `postcss@8.4.31`，审计的自动修复要求迁移到 Next 16.3.4，并同步替换已弃用的 `next lint` 工作流。
- Ruff 虽已能运行，但 `uv run ruff check .` 仍报告 470 个遗留问题（397 个可自动修复）。
- 当前独立 FastAPI、本地磁盘和 Docker/Nginx 部署形态尚未迁移为单个 Vercel Next.js 项目；`/api` 还会 rewrite 到 `localhost:8000`，生产部署仍为 No-Go。

## [0.2.0] - 2026-03-14

### 新增与调整

- 增加可选模拟摄像头，用于无真实硬件时演示录制和上传流程。
- 增加 CORS origins 配置和 AI 服务开发期调整。
- 增加自签名证书、HTTPS 开发支持及相关排障文档。

### 限制

- `0.2.0` 是开发原型标签，不代表真实 AI、支付、生产存储或 Vercel 部署已经完成。
