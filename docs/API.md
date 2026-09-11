# SpeedInspect API 现状与 Vercel 目标契约

> 更新日期：2026-09-11<br>
> 审查基线：`dev` @ `bf6e7ab`，并包含报告路由、文件归属、Vercel ADR 与 CI 基线<br>
> 状态：迁移规格。第一部分记录现有 FastAPI 的真实行为；第二部分是尚未实现的 Next.js/Vercel 目标契约。

本文用于避免把旧接口骨架当成已经可上线的服务。当前接口事实来自 `backend/src/app/main.py`、各 feature router/schema/service、`frontend/web/lib/apiClient.ts` 和生成的 FastAPI OpenAPI；目标契约与 [技术方案](技术方案.md) 一致。代码行为与本文冲突时，当前行为以代码为准，目标行为以通过评审后的契约测试为准。

## 1. 当前 FastAPI 契约

### 1.1 基础约定

- 服务默认监听 `http://localhost:8000`，业务前缀为 `/api/v1`；`/`、`/health`、`/ready` 不带该前缀。
- 除注册、登录、根路径和健康检查外，业务接口使用 `Authorization: Bearer <access_token>`。JWT 由浏览器 JavaScript 保存到 `localStorage` 和非 HttpOnly Cookie，这只是当前实现，不是目标安全方案。
- `DEBUG=true` 时提供 `/docs`、`/redoc` 和 `/openapi.json`；生产配置会关闭它们。
- 当前成功包装通常是下列 snake_case 结构，`timestamp` 是 Unix 秒：

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "details": null,
  "request_id": "uuid",
  "timestamp": 1789000000
}
```

- 错误没有统一结构。自定义 `AppError` 返回字符串 `code` 和正确 HTTP 状态；FastAPI 参数校验及多个 `HTTPException` 返回 `{"detail": ...}`；部分代码调用 `ApiResponse.error(...)` 却仍返回 HTTP 200。
- 当前 JSON 模型主要使用 snake_case。UUID 在 JSON 中表现为字符串，日期通常由 FastAPI/Pydantic 序列化为 ISO 字符串；前端类型却混用 camelCase 和 JavaScript `Date`，没有统一 adapter。
- 列表接口声明的 `PaginatedResponse` 正确字段应为 `items`、`total`、`page`、`page_size`、`has_next`。报告和订单 router 实际传入 `data`、`message` 并遗漏 `items`、`has_next`，因此当前列表调用会发生响应构造错误。

### 1.2 路由清单

下表中的“当前结果”描述实现，而不是产品承诺。“Bearer”只表示路由挂载了认证依赖，不代表会话方案已经达到生产要求。

#### 根路径、健康与认证

| 方法与路径 | 鉴权 | 当前输入 | 当前结果与限制 |
| --- | --- | --- | --- |
| `GET /` | 无 | 无 | 返回服务名、版本 `0.1.0`、环境和可选 docs 地址。 |
| `GET /health` | 无 | 无 | HTTP 200，返回进程级 `healthy`；不检查数据库、Blob 或 AI。 |
| `GET /ready` | 无 | 无 | 执行数据库 `SELECT 1`。数据库失败时 body 的 `code` 为 `503`，但实现未设置 HTTP 状态，仍可能是 HTTP 200。 |
| `POST /api/v1/auth/register` | 无 | JSON `UserCreate` | HTTP 201，创建用户。字段为 `phone?`、`email?`、`nickname?`、`avatar_url?`、`password`；密码要求 8–128 字符，但 phone/email 均未要求至少存在一个。 |
| `POST /api/v1/auth/login` | 无 | JSON `{account, password}` | HTTP 200，返回 access/refresh JWT、`expires_at` 和用户。`account` 只按手机号或邮箱查询。 |
| `POST /api/v1/auth/refresh-token` | 无 | 必填 **query** 参数 `refresh_token` | HTTP 200，轮换两枚 JWT。它不是 JSON body 参数，也没有持久化撤销机制。 |

#### 用户

| 方法与路径 | 鉴权 | 当前输入 | 当前结果与限制 |
| --- | --- | --- | --- |
| `GET /api/v1/users/profile` | Bearer，active 用户 | 无 | 返回当前用户。 |
| `PUT /api/v1/users/profile` | Bearer，active 用户 | JSON `UserUpdate` | 可更新 `phone`、`email`、`nickname`、`avatar_url`、`password`。这是全量语义的 `PUT`，schema 实际允许全部字段缺省。 |
| `GET /api/v1/users/{user_id}` | Bearer，`admin`/`superadmin` | UUID path | 返回指定用户；未找到时调用 `ApiResponse.error(code=404)`，HTTP 状态仍为 200。 |
| `DELETE /api/v1/users/{user_id}` | Bearer，`superadmin` | UUID path | 软删除用户，HTTP 200 包装响应。 |

#### 本地文件与模拟分析

| 方法与路径 | 鉴权 | 当前输入 | 当前结果与限制 |
| --- | --- | --- | --- |
| `POST /api/v1/files/upload` | Bearer | `multipart/form-data`，字段 `file` | HTTP 200；将整个文件一次性读入内存，再写入 `STORAGE_LOCAL_PATH/{userId}`。没有 MIME、字节数、内容或配额限制。 |
| `POST /api/v1/files/upload-batch` | Bearer | `multipart/form-data`，重复字段 `files` | 逐个执行同一本地上传逻辑，没有文件数和总大小上限。 |
| `GET /api/v1/files/{file_id}` | Bearer | UUID 字符串 path | 在当前工作区修复后，仅在当前用户 UUID 目录中查找；返回文件名、大小、占位 MIME、下载 URL 和文件系统时间。元数据没有数据库记录。 |
| `GET /api/v1/files/{file_id}/download` | Bearer | UUID 字符串 path | 所有者可从本地磁盘下载，响应 MIME 固定为 `application/octet-stream`。 |
| `DELETE /api/v1/files/{file_id}` | Bearer | UUID 字符串 path | 删除当前用户目录中的本地文件。 |
| `POST /api/v1/ai/analyze` | Bearer | JSON `{file_id, options?}` | HTTP 200，立即返回 `pending` task。服务不在提交时拒绝不存在的文件，后台结果由随机模板生成，不是真实 AI。 |
| `GET /api/v1/ai/analysis/{task_id}/status` | Bearer | task ID path | 设计上应返回所有者的任务状态；实际上每次请求新建 `AIService` 和空字典，无法查到 POST 创建的任务，且 404 分支因局部变量遮蔽 `status` 模块而可能返回 500。 |

当前 AI schema 使用状态 `pending | processing | completed | failed`，包含数值 `progress`、`problems` 和可选 `report_id`。`POST /ai/analyze` 只返回已提交状态，前端却立即把它当完成结果读取。后台路径还把 `HouseProblem` 对象列表传给只接受字典的报告摘要逻辑，报告生成会失败。进程重启或无服务器函数回收后，所有内存 task 都会丢失。

#### 报告

| 方法与路径 | 鉴权 | 当前输入 | 当前结果与限制 |
| --- | --- | --- | --- |
| `GET /api/v1/reports` | Bearer | query `page=1`、`page_size=10`（1–100） | 计划返回当前用户报告列表；当前分页响应字段和计数查询都不正确，不能可靠工作。 |
| `GET /api/v1/reports/{report_id}` | Bearer | UUID path | 按 `report_id + current_user.id` 查询，未命中返回 404 `detail`。 |
| `POST /api/v1/reports` | Bearer | JSON `InspectionReportCreate` | HTTP 201。body 仍强制要求 `user_id`，router 随后又用当前用户覆盖它。摘要由服务端重算。 |
| `PUT /api/v1/reports/{report_id}` | Bearer | 完整 `InspectionReportCreate` | 计划按所有者更新；service 先返回 Pydantic schema，随后把它当 SQLAlchemy 实体 `refresh`，当前会失败。body 中的 `user_id` 也不应由客户端控制。 |
| `DELETE /api/v1/reports/{report_id}` | Bearer | UUID path | 计划按所有者删除；同样把 Pydantic schema 传给 ORM delete，当前会失败。 |
| `GET /api/v1/reports/{report_id}/download?format=pdf\|html\|json` | Bearer | UUID path；format 默认 `pdf` | handler 导入不存在的 `ReportGenerator`，当前各格式都会失败。即使补齐导入，`pdf` 分支也只是 HTML 占位。 |
| `GET /api/v1/reports/{report_id}/share?expire_days=7` | Bearer | 1–30 天 | 随机生成 URL，但不保存分享码、过期时间或访问策略；返回的链接不可用。GET 还产生服务端状态，不符合安全的资源创建语义。 |

当前报告创建模型字段如下。`user_id` 不应出现在客户端目标模型中。

```text
user_id, property_type, address?, problems[], summary?,
video_file_id?, thumbnail_url?

problem:
  id, category, description, severity(1..5), confidence(0..1),
  location, frame_timestamp?, bounding_box?, repair_suggestion,
  estimated_cost, image_url?
```

当前模型把模型自报 `confidence` 和单值 `estimated_cost` 当普通数值保存，但没有校准、报价来源、地区或日期；这些字段不得被解释为准确概率或正式报价。

#### 订单

| 方法与路径 | 鉴权 | 当前输入 | 当前结果与限制 |
| --- | --- | --- | --- |
| `GET /api/v1/orders` | Bearer | query `page=1`、`page_size=10`（1–100） | 计划返回当前用户订单；与报告列表相同，分页响应和计数查询错误。 |
| `GET /api/v1/orders/{order_id}` | Bearer | UUID path | 按所有者查询订单。 |
| `GET /api/v1/orders/number/{order_number}` | Bearer | order number path | 按订单号和所有者查询。 |
| `POST /api/v1/orders` | Bearer | JSON `OrderCreate` | HTTP 201；总价直接依据客户端提交的 `quantity * unit_price` 计算，没有服务端商品目录。 |
| `POST /api/v1/orders/{order_id}/pay` | Bearer | JSON `{payment_method, return_url?}` | 没有支付网关，代码直接模拟成功并标记已支付；不能在生产开放。 |
| `POST /api/v1/orders/{order_id}/cancel` | Bearer | 可选 **query** 参数 `reason` | 按当前状态尝试取消。 |
| `PUT /api/v1/orders/{order_id}/status` | Bearer，`admin`/`superadmin` | 必填 **query** 参数 `status` | 计划由管理员更新状态；service 同样混用 Pydantic schema 与 ORM 对象，不能可靠工作。 |

订单和支付不属于已确认的 Vercel MVP。迁移期间必须显示为不可用，不得保留“模拟支付成功”的生产路径。

### 1.3 已知客户端与服务端不匹配

| 位置 | 当前不匹配 | 用户影响 |
| --- | --- | --- |
| API 地址 | 浏览器默认使用绝对地址 `http://localhost:8000/api/v1`；Next rewrite 只代理同源 `/api/*`。 | 未设置环境变量的部署会请求访问者自己的 localhost，Vercel rewrite 也不会生效。 |
| 注册 | Web 发送 `username`，API 只接受 `nickname`；Web 允许 6 位密码，API 至少 8 位；空字符串 phone 也可能触发 pattern 校验。 | 用户名被忽略，6–7 位密码或空 phone 请求得到 422。 |
| 刷新令牌 | Web 发送 JSON `{refresh_token}`，FastAPI 将 `refresh_token` 定义为 query 参数。 | access token 过期后的自动刷新得到 422，然后被迫退出。 |
| 登录会话 | Web 把 JWT 写入 localStorage 和脚本可读 Cookie；middleware 只检查 Cookie 是否存在，不验证签名或过期。 | XSS 可读取 token，伪造任意非空 Cookie 也能通过页面门禁；真正 API 鉴权仍由 FastAPI Bearer 完成。 |
| 分析提交 | API 返回 pending task；页面立即读取 `problems`/`report_id`，没有轮询状态 endpoint。 | `report_id` 为 undefined，主巡检流程无法完成。下载进度也被误当作推理进度。 |
| 任务存储 | POST 和 GET 各自创建新的 `AIService.tasks = {}`。 | 即使同一 Python 进程中也无法跨请求查询任务，更无法承受 Vercel 实例回收。 |
| 报告字段 | API 使用 `created_at`、`property_type`、`repair_suggestion` 等 snake_case；UI 使用 `createdAt`、`propertyType`、`repairSuggestion` 等 camelCase 和 `Date`。 | 后端报告直接写入 Redux 后字段为 undefined，日期也没有转换。 |
| 报告创建 | API body 强制 `user_id`；Web 发送 `Partial<InspectionReport>`，通常没有该字段且字段风格不同。 | 创建/更新通常得到 422；客户端还被迫接触本应由会话决定的 owner。 |
| 分页 | router 构造 `{data, message}`，response model 需要 `{items, has_next}`；service 用实体查询的 `scalar_one()` 计算总数。 | 0 条、多条或响应校验阶段都可能失败。 |
| 错误 | `AppError`、`HTTPException`、校验错误和 `ApiResponse.error` 返回四种语义。 | 客户端无法稳定判断错误码、HTTP 状态与可重试性。 |
| 下载 | 页面按 PDF 文件名保存响应；API 的 PDF 是 HTML 占位，当前还会因不存在的导入直接 500。 | 用户可能拿到损坏或伪装格式的文件。 |

## 2. Vercel Next.js 目标契约（尚未实现）

目标是由 `frontend/web` 中的 Next.js Route Handlers 提供同源 API，页面和接口一起部署到 Vercel；PostgreSQL、私有 Blob 和外部视觉 AI 使用托管服务。旧 FastAPI 路由只有在迁移完成前用于本地对照，不作为 Vercel 生产依赖。

### 2.1 全局规则

1. **地址与版本**：浏览器固定调用同源 `/api/v1`，不再使用 `NEXT_PUBLIC_API_URL` 指向独立后端。需要破坏性调整时升级 API 版本。
2. **认证**：使用服务端会话和 `HttpOnly; Secure; SameSite=Lax` Cookie。客户端不接收或保存 refresh token；写操作验证可信 Origin，并按所选认证库实施 CSRF 防护。每个查询和变更都从会话取得 `userId` 并校验资源归属。
3. **格式**：JSON 字段统一 camelCase；ID 为 UUID 字符串；日期为带时区的 ISO 8601 字符串；金额使用整数最小货币单位和明确区间。客户端不能提交 `ownerId`/`userId` 来改变归属。
4. **状态码**：创建资源用 201，异步任务用 202，成功删除用 204；认证失败 401、归属或权限失败 403、资源不存在 404、冲突 409、校验失败 422、限流 429、外部依赖暂不可用 503。不能用 HTTP 200 包装失败。
5. **幂等与并发**：分析任务创建要求 `Idempotency-Key`；唯一约束为 `userId + idempotencyKey`。报告编辑携带当前 `revision` 或 `If-Match`，冲突返回 409，防止覆盖他人或另一设备的修改。
6. **分页**：列表采用有上限的 cursor 分页，响应 `pageInfo.nextCursor`；服务端限制 `limit`，不返回未受控全量集合。
7. **输入边界**：所有 body 经过运行时 schema 校验。AI 只接受已归属且状态为 ready 的 `mediaIds`，不接受任意远端 URL、Blob key、提示词或模型名。状态转换由服务端校验。
8. **可观察性**：每个响应包含 `X-Request-ID`；错误 body 也返回同一个 `requestId`。日志只记录资源 ID、稳定错误码和耗时，不记录 Cookie、密钥、完整媒体或敏感地址。

目标成功响应：

```json
{
  "data": {},
  "requestId": "01J..."
}
```

目标列表响应：

```json
{
  "data": [],
  "pageInfo": { "nextCursor": null },
  "requestId": "01J..."
}
```

目标错误响应：

```json
{
  "error": {
    "code": "MEDIA_TOO_LARGE",
    "message": "文件超过本次巡检允许的大小",
    "details": { "maxBytes": 10485760 }
  },
  "requestId": "01J..."
}
```

`error.code` 是客户端分支判断使用的稳定值；`message` 可本地化；`details` 不能暴露堆栈、SQL、供应商响应或密钥。

### 2.2 目标公开路由

#### 会话

| 方法与路径 | 输入 | 成功结果 | 约束 |
| --- | --- | --- | --- |
| `POST /api/v1/auth/register` | `{email, password, nickname?}` | 201，用户摘要，并设置会话 Cookie | email 规范化；密码策略由认证模块统一；不回传 token。 |
| `POST /api/v1/auth/login` | `{account, password}` | 200，用户摘要，并轮换会话 Cookie | 统一失败消息和共享限流，避免账号枚举。 |
| `GET /api/v1/auth/session` | 无 | 200，当前用户与 session 过期时间 | 失效或撤销的 session 返回 401。 |
| `POST /api/v1/auth/logout` | 无 | 204，撤销服务端 session 并清 Cookie | 操作幂等。 |

若最终选用的认证库保留其内部 callback 路由，应把这些内部路由单独记录；页面业务只能依赖上表的稳定应用契约。

#### 巡检

| 方法与路径 | 输入 | 成功结果 | 约束 |
| --- | --- | --- | --- |
| `POST /api/v1/inspections` | `{propertyType, address?, rooms?}` | 201，`Inspection` | owner 只取会话；初始状态为 `draft`。地址可选且按敏感数据处理。 |
| `GET /api/v1/inspections?cursor=&limit=` | cursor、limit | 200，当前用户巡检列表 | `limit` 设硬上限；稳定排序。 |
| `GET /api/v1/inspections/{inspectionId}` | UUID path | 200，巡检详情 | 每次读取校验 owner。 |
| `PATCH /api/v1/inspections/{inspectionId}` | `{revision, propertyType?, address?, rooms?}` | 200，更新后的巡检 | 不允许客户端直接跳转服务端状态。 |
| `DELETE /api/v1/inspections/{inspectionId}` | UUID path | 204 | 删除/保留策略必须同步数据库、Blob 和 AI 供应商数据；操作可审计。 |

建议 `Inspection` 最小结构：

```json
{
  "id": "uuid",
  "propertyType": "apartment",
  "address": null,
  "rooms": [],
  "status": "draft",
  "revision": 1,
  "createdAt": "2026-09-10T09:00:00Z",
  "updatedAt": "2026-09-10T09:00:00Z"
}
```

#### 私有媒体

| 方法与路径 | 输入 | 成功结果 | 约束 |
| --- | --- | --- | --- |
| `POST /api/v1/inspections/{inspectionId}/media-uploads` | `{filename, contentType, sizeBytes, sha256?, capturedAt}` | 201，`mediaId`、短期客户端上传凭证、受控 pathname、过期时间和限制 | 签发前校验 session、inspection owner、MIME、大小和配额；预建 `uploading` 记录。 |
| `GET /api/v1/inspections/{inspectionId}/media?cursor=&limit=` | cursor、limit | 200，媒体元数据列表 | 不返回永久公开 URL。 |
| `GET /api/v1/media/{mediaId}` | UUID path | 200，媒体元数据及按需短期读取信息 | 校验 owner；读取凭证短期有效。 |
| `DELETE /api/v1/media/{mediaId}` | UUID path | 204 | 同时记录 Blob 清理任务和审计事件，可重试。 |

文件字节由浏览器使用签发凭证直传私有 Blob，不穿过 Next.js Function。上传完成由受信任的 Blob callback 或服务端 `head` 校验确认，只有 object key、MIME、实际大小、hash 和 owner 均匹配时，`MediaAsset.status` 才从 `uploading` 变为 `ready`。callback 必须验签、幂等且不信任浏览器提交的完成状态。

原视频只用于本地抽帧或经明确策略保存；AI 请求使用压缩、限量的证据图片。API 不接收任意 URL，也不代理超过 Vercel 响应限制的大媒体下载。

#### 分析任务

| 方法与路径 | 输入 | 成功结果 | 约束 |
| --- | --- | --- | --- |
| `POST /api/v1/inspections/{inspectionId}/analysis-jobs` | header `Idempotency-Key`；JSON `{mediaIds}` | 202，持久化 `AnalysisJob`；设置 `Location` | 媒体必须属于同一用户和巡检且为 ready；限制数量和总字节。 |
| `GET /api/v1/analysis-jobs/{jobId}` | UUID path | 200，最新 job 状态 | 刷新页面或函数实例变化后仍可查询。 |
| `POST /api/v1/analysis-jobs/{jobId}/cancel` | `{reason?}` | 200，更新后的 job | 仅 `queued`/`processing` 可取消；重复取消幂等。 |

目标状态固定为：

```text
queued -> processing -> succeeded | failed | cancelled
```

目标 `AnalysisJob` 示例：

```json
{
  "id": "uuid",
  "inspectionId": "uuid",
  "status": "processing",
  "attempt": 1,
  "progress": { "completed": 2, "total": 6 },
  "error": null,
  "reportId": null,
  "createdAt": "2026-09-10T09:00:00Z",
  "updatedAt": "2026-09-10T09:00:03Z"
}
```

`progress` 只基于可验证步骤或已处理图片数；不能把 HTTP 上传/下载进度包装成模型推理进度。只有 `status=succeeded` 且报告事务已提交时才返回 `reportId`。失败记录稳定错误码，例如 `AI_RATE_LIMITED`、`AI_TIMEOUT`、`AI_INVALID_RESPONSE`；模型原始响应需受限保存并与用户展示隔离。

#### 报告、人工复核与版本

| 方法与路径 | 输入 | 成功结果 | 约束 |
| --- | --- | --- | --- |
| `GET /api/v1/reports?inspectionId=&cursor=&limit=` | 可选 inspectionId、cursor、limit | 200，当前用户报告列表 | owner 查询必须在数据库条件中体现。 |
| `GET /api/v1/reports/{reportId}` | UUID path | 200，工作报告、findings、证据引用和 revision | 模型输出明确标记为待人工复核建议。 |
| `PATCH /api/v1/reports/{reportId}/findings/{findingId}` | `{revision, decision, description?, severity?, repairAdvice?, costEstimate?}` | 200，更新后的 finding 和新 revision | `decision` 为 `confirmed | rejected | uncertain`；记录原始建议、修改者、时间和差异。 |
| `GET /api/v1/reports/{reportId}/versions` | 无 | 200，版本摘要列表 | 版本不可原地修改。 |
| `POST /api/v1/reports/{reportId}/versions` | `{revision, note?}` | 201，人工确认后的不可变快照 | 至少明确所有 finding 的人工决定；冲突返回 409。 |
| `GET /api/v1/reports/{reportId}/versions/{versionId}` | UUID paths | 200，指定版本 | owner 校验覆盖 report 和 version。 |
| `GET /api/v1/reports/{reportId}/versions/{versionId}/export?format=html\|json` | format | 200，真实 MIME 的导出 | HTML 必须转义用户/模型内容；PDF 首版使用浏览器打印，未实现时不返回伪 PDF。 |
| `GET /api/v1/reports/{reportId}/audit-events?cursor=&limit=` | cursor、limit | 200，审计事件 | 不向普通用户暴露密钥、供应商原文或内部堆栈。 |

Finding 必须引用具体 `mediaId`，并可带 `capturedAt`、帧时间点和归一化框选。模型、提示词版本和原始建议在服务端保存；人工编辑不能覆盖原始证据。可选费用只能用参考范围表示，例如：

```json
{
  "currency": "CNY",
  "minMinor": 50000,
  "maxMinor": 120000,
  "source": "来源说明",
  "region": "武汉",
  "asOfDate": "2026-09-10"
}
```

报告及界面不得宣称仅凭图片判断结构安全、隐蔽故障、责任归属或法律结论。模型的 confidence 若保留，应命名为供应商模型分值，并在完成获授权样本校准前不展示为“准确率”。

### 2.3 不属于 MVP 的路由

- 当前 `/orders*` 和 `/pay` 不迁入首个 Vercel 闭环。未接入真实商品目录、支付网关、签名 webhook、幂等和对账前，服务端应返回功能不可用或根本不注册路由。
- 当前 `/reports/{id}/share` 不迁移。只有确定访问者、撤销、过期、下载限制和审计模型后，才新增持久化 share resource，并使用 POST 创建。
- 管理员用户 API、短信、OCR、历史状态比对、维修对接和 Agent 对话另立需求与权限模型，不夹带进首个迁移版本。
- 健康接口目标可保留 `GET /api/health` 作为进程检查；依赖就绪检查不得泄露数据库、Blob 或 AI 的内部错误，平台监控应使用受保护的详细诊断。

## 3. 迁移映射与验收

| 当前 FastAPI | 目标 Next.js/Vercel | 迁移动作 |
| --- | --- | --- |
| Bearer access/refresh JWT | HttpOnly 服务端 session | 选择认证库，完成旧密码兼容或重置策略；删除 localStorage token 与前端 refresh。 |
| `/files/upload*` | inspection 绑定的 Blob 客户端直传 | 先建媒体记录，限制 MIME/大小/数量，验证完成 callback；禁止函数保存原视频。 |
| `/ai/analyze` + 内存字典 | `/analysis-jobs` + PostgreSQL 状态机 | 实现幂等、lease、超时、最多三次重试、取消和过期任务恢复。 |
| 随机 `_simulate_detection` | 外部视觉 AI adapter + schema 校验 | 生产构建禁用模拟结果；输入只接受已授权 media IDs；保存模型/提示词版本。 |
| 报告 CRUD | 报告工作副本、finding 决策、不可变版本 | 统一 camelCase adapter，增加 revision、证据、原始建议和审计事件。 |
| `download?format=pdf` HTML 占位 | HTML/JSON 真格式 + 浏览器打印 | MIME、文件名和内容一致；系统验证 HTML 转义。 |
| `/orders*` 模拟支付 | 首版不提供 | 删除或显式禁用生产路由，未来由独立支付 ADR 恢复。 |

每个目标 Route Handler 合入前至少用契约测试覆盖：未登录、其他用户资源、非法 UUID、错误 MIME/超限、重复幂等键、非法状态转换、AI 429/超时/非法 JSON、revision 冲突、HTML 注入和删除后访问。端到端验收必须证明浏览器刷新、函数冷启动和换一台设备后，任务与报告仍可从 PostgreSQL 恢复；构建成功本身不代表这些行为成立。
