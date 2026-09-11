# ADR-0001：统一到 Vercel 的应用运行架构

- **状态：** Accepted for the migration target
- **日期：** 2026-09-11
- **决策人：** 项目维护者（用户已确认“应用和接口统一部署 Vercel，数据与 AI 使用托管服务”）
- **基线：** `dev` @ `243a19d`

## 背景

当前仓库同时包含 `frontend/web`（Next.js）和独立的 FastAPI 后端。FastAPI 通过本地 SQLite、`backend/uploads` 和进程内 `asyncio.create_task` 保存状态；这些实现适合本地原型，却不能保证 Vercel Function 在冷启动、并发和响应结束后仍能访问同一状态。浏览器还默认请求 `localhost:8000`，媒体上传会把完整文件读进函数内存，AI 结果是随机模拟值。

目标是只运营一个 Vercel 项目，同时保留 Python 研究代码作为离线工具。架构必须支持多用户归属隔离、刷新后恢复任务、私有媒体和可审计的人工复核报告。

## 决策

### 1. 一个 Next.js 项目承载页面和业务 API

- Vercel Root Directory 固定为 `frontend/web`，Node 使用项目声明的 22.x LTS。
- 页面和 `app/api/v1/**/route.ts` Route Handlers 同源部署；浏览器只调用相对路径 `/api/v1`。
- 服务端模块按边界拆分为会话、数据库、媒体、任务、AI adapter 和报告，客户端组件不能导入含密钥或数据库连接的模块。
- 现有 FastAPI 在迁移期继续作为本地契约参考；迁移完成前不把它当作 Vercel 生产依赖，也不在请求中启动第二个常驻服务。

### 2. PostgreSQL 是业务状态唯一来源

- 通过 Vercel Marketplace 接入托管 PostgreSQL；连接使用池化 URL，Preview 与 Production 使用不同数据库和凭据。
- User/Session、Inspection、MediaAsset、AnalysisJob、Finding、ReportVersion、AuditEvent 由 migration 管理。
- 所有查询和变更都从已验证的服务端 session 得到 `userId`，并把 owner 条件放入数据库查询；缺少用户身份时直接拒绝。
- migration 在独立发布步骤执行，绝不在普通请求、构建或函数冷启动时修改数据库。

### 3. 媒体使用私有 Blob 客户端直传

- API 先验证 session、巡检归属、MIME、大小、数量和配额，再签发短期、受限的客户端上传凭证。
- 浏览器把照片或浏览器抽帧后的证据图片直传私有 Blob；Next.js Function 只保存元数据和完成校验，不代理原视频字节。
- 数据库保存 `blobKey`、实际 MIME、字节数、hash、采集时间和保留期。读取通过短期授权信息完成，不保存永久公开 URL。

### 4. AI 分析是持久、幂等、可恢复的任务

- `AnalysisJob` 状态固定为 `queued → processing → succeeded | failed | cancelled`，任务、尝试次数、租约、错误码和报告 ID 全部落库。
- 创建任务必须带 `Idempotency-Key`，唯一键为 `userId + idempotencyKey`；重试最多三次并使用有界退避。
- 第一版只向外部视觉 AI 发送经过限制的证据图片批次。供应商调用封装在服务端 adapter 中，模型返回值经运行时 schema 校验；超时、429、非法 JSON 和供应商故障都落为可解释状态。
- 任务执行器采用可重入的短步骤。需要超过函数时限的工作时，再接入经过验证的 Vercel Workflow/托管队列或供应商回调；不依赖响应返回后的无人管理后台协程。

### 5. 服务端会话与统一 API 契约

- 采用维护中的服务端认证方案，使用 HttpOnly、Secure、SameSite Cookie；客户端不保存 access/refresh token。
- 写操作校验可信 Origin/CSRF，所有受保护路由重新验证会话签名、过期和撤销状态。middleware 的 Cookie 存在检查不能替代授权。
- API 使用统一的 HTTP 状态码、camelCase JSON、ISO 8601 日期、UUID 字符串和稳定 `error.code`；客户端不能提交 `ownerId`/`userId` 改变归属。

## 未在本 ADR 中决定的事项

- PostgreSQL、Blob 和 AI 的具体供应商与区域：在获得授权样本、隐私要求、延迟、配额和成本数据后选择。
- 长任务执行产品：先以短批次和持久状态完成 MVP，再用 Preview 压测结果决定 Workflow、队列或供应商异步回调。
- 认证库：先定义上述应用契约，再评估维护状态、旧密码兼容、CSRF 支持和迁移成本。
- PDF 生成：MVP 提供真实 HTML/JSON 和浏览器打印；只有确认 Vercel 运行时和字体依赖后才引入服务端 PDF。

## 备选方案及取舍

| 方案 | 取舍 | 结论 |
| --- | --- | --- |
| Next.js 页面/API + 托管数据服务 | 同源鉴权和部署面最小；需要迁移 Python CRUD | **采用** |
| Vercel Next.js + FastAPI Function | 可复用部分 Python；保留两套运行时、契约和依赖，不能解决本地存储/内存任务 | 迁移过渡期仅作对照 |
| 浏览器本地模型与存储 | 云依赖少；移动端性能、多用户同步、隐私删除和模型质量无法满足 MVP | 不采用 |
| 自托管 Docker/Redis/Celery/GPU | 适合长任务；与“只在 Vercel 部署”边界冲突，运维和成本高 | 不采用 |

## 影响与风险

- 需要新增 TypeScript 数据访问层、migration、Blob adapter、任务恢复和契约测试；旧 FastAPI 代码不会自动迁移。
- Vercel Function 有请求体、执行时长和包体限制；大媒体必须直传，AI 输入必须有界。只提高 `maxDuration` 不能解决丢任务问题。
- 外部 AI 会产生费用和隐私边界。上线前必须配置每用户配额、并发限制、超时、费用熔断、供应商数据保留和删除流程。
- 该决策不代表当前代码已经可部署。生产门槛仍以 `docs/PROJECT_STATUS.md` 和 `docs/ROADMAP.md` 为准。

## 迁移顺序与回滚

1. 在 `dev` 建立 Node 22/Python CI 和 schema/契约测试。
2. 先接入服务端会话与空库 migration，再迁移巡检 CRUD。
3. 加入私有 Blob 直传和媒体完成校验；旧本地上传路径保持开发专用并明确禁用生产。
4. 加入持久 AnalysisJob、外部 AI adapter、人工复核和报告版本。
5. 在 Vercel Preview 用独立资源验收后，才讨论 `main` 发布。

每一步都保持前后兼容的 migration，失败时回退应用版本并在恢复副本验证修复；破坏性数据库迁移、生产部署、真实凭据和数据删除需要项目维护者明确批准。

## 验收证据

实现本 ADR 的功能时，至少记录以下证据：两个账号的跨用户拒绝、过期会话、重复幂等键、上传超限、任务冷启动/刷新恢复、AI 429/超时/非法响应、报告 HTML 转义、数据库恢复和 Vercel Preview 构建。构建成功本身不作为生产可行性的证明。
