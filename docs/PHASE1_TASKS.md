# Phase 1 执行清单：Vercel 安全会话与数据库

本文是 `dev` 下一轮开发的执行入口，配合 [路线图](ROADMAP.md)、[API 目标契约](API.md) 和 [Agent 手册](AGENT_RUNBOOK.md) 使用。

## 任务边界

目标是让一个登录用户可以在同源 Next.js API 中创建和读取只属于自己的巡检记录，并在刷新、函数冷启动和会话撤销后保持可验证状态。数据库使用托管 PostgreSQL；本地测试使用临时数据库或隔离测试实例。当前 FastAPI、SQLite、本地上传、随机 AI 和模拟支付不进入本阶段生产路径。

## 任务顺序与验收

### 1. 数据模型和迁移

- 确认 PostgreSQL 连接池方案、迁移工具和 schema 版本策略，并记录 ADR。
- 创建 `users`、`sessions`、`inspections`、`audit_events` 表及索引；所有外键和时间字段使用明确类型，session token 只保存不可逆摘要。
- 为每个迁移编写 forward、重复执行和回滚/恢复演练命令；测试数据库不得使用生产凭据。
- 验收：空库可从头迁移；重复运行不会产生漂移；删除用户或巡检的级联/保留策略有审计记录。

### 2. 服务端会话和请求防护

- 实现 `getSessionUser()` 服务端 helper；缺少、过期、撤销或摘要不匹配时统一返回 401。
- 会话 Cookie 使用 `HttpOnly; Secure; SameSite=Lax; Path=/`，生产和 Preview 使用不同密钥；客户端不接收 access/refresh token。
- 对所有写请求校验可信 `Origin`/`APP_ORIGIN`，拒绝缺失或不匹配来源；加入共享限流和稳定 `requestId`。
- 验收：登出立即撤销；伪造 Cookie、过期 Cookie、跨站 POST 和超过限额的请求均失败且不泄露内部细节。

### 3. 同源认证 API

实现并测试以下路由：

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/session`
- `POST /api/v1/auth/logout`

输入经运行时 schema 校验；邮箱规范化；失败消息不可用于账号枚举；成功响应不包含 token。API 使用 `{data, requestId}` 和统一 `{error, requestId}` 包装。

### 4. 巡检 API 与归属隔离

实现并测试：

- `POST /api/v1/inspections`
- `GET /api/v1/inspections?cursor=&limit=`
- `GET /api/v1/inspections/{inspectionId}`
- `PATCH /api/v1/inspections/{inspectionId}`
- `DELETE /api/v1/inspections/{inspectionId}`

`userId` 只来自 session；客户端提交的 `ownerId`/`userId` 必须被拒绝或忽略。每一条 SQL 都带 owner 条件；revision 冲突返回 409；非法 UUID、超限分页和非法状态返回 422/409。

### 5. Preview 验证

- 创建独立 Preview 数据库和 Blob/AI 空配置；不得复用 Production 数据或账单凭据。
- 在两个账号、两个浏览器和一次函数冷启动后执行注册、登录、刷新、登出、创建、读取、修改、删除和越权尝试。
- 保存提交 SHA、迁移日志、请求 ID、失败路径和回滚证据；未通过项保持 No-Go。

## 必测失败路径

每个 Route Handler 合入前至少覆盖：未登录、过期/撤销 session、跨用户 UUID、伪造 ownerId、非法 UUID、Origin 不匹配、schema 超限、revision 冲突、重复请求和数据库暂时不可用。测试只使用合成邮箱、地址和媒体元数据。

## 完成定义

Phase 1 只有在 CI Node 22 通过、迁移可重复、会话安全属性可观察、两个账号归属隔离集成测试通过、Preview 数据隔离且回滚演练完成时才算完成。此阶段不请求 Production 发布授权。
