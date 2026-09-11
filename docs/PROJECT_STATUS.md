# SpeedInspect 项目状态

> 最近审查：2026-09-11<br>
> 仓库：`https://github.com/QZSAMA/SpeedInspect`<br>
> 审查起始基线：`dev` @ `243a19d`；本轮文档/CI 更新后远端头为 `bf6e7ab`
> 状态口径：以 Git 历史、锁文件、当前代码和实际执行命令为准；历史方案中的规划不计为已实现。

## 结论

SpeedInspect 当前是一个可以继续演进的房屋巡检**技术原型和后端业务骨架**，还不是可部署到生产环境的完整产品。浏览器端已有房型选择、摄像头录制、上传和结果展示界面；FastAPI 已有认证、用户、文件、订单、报告和 AI 任务接口骨架；`ai-engine` 包含三种离线研究脚本。但是，现有“AI 检测”会随机生成结果，支付是模拟成功，PDF 与分享未完成，主页面与异步分析接口协议不匹配，关键任务和媒体仍依赖进程内内存及本地磁盘。

仅使用 Vercel 承载应用和接口是可行的，但需要先把运行架构收敛成单个 Next.js 项目，并接入托管 PostgreSQL、私有对象存储和外部 AI API。当前 `frontend/web` 与独立 FastAPI 后端、SQLite/本地上传目录、后台 `asyncio.create_task` 的组合不能直接作为 Vercel 生产架构。

当前上线判断：**No-Go**。本地原型可继续开发；生产部署必须先完成本文 P0 阻断项并通过云端验收。

## 分支与合并状态

本轮整合前，远端可见三个分支引用：

| 分支 | SHA | 与 `dev` 的关系 | 用途与状态 |
| --- | --- | --- | --- |
| `dev` / `origin/dev` | `bf6e7ab` | CI、Vercel ADR 与状态更新已加入的开发头 | 已设为远端默认分支，后续日常开发基线 |
| `origin/trae/solo-agent-p6YsKQ` | `ed1887c` | 与 `dev` 完全相同，无独有提交 | 开发成果已进入 `dev`，无需再次合并 |
| `main` / `origin/main` | `ebe4cc7` | `main` 是 `dev` 的祖先；`dev` 比它多 35 个提交，`main` 无独有提交 | 保留为发布快照，未经明确批准不向生产发布 |

现存各分支的代码已经汇入 `dev`：`main` 的全部历史包含在 `dev` 中，Trae 分支与 `dev` 同指针。历史功能分支的成果也已通过合并提交进入 `dev`，包括 PR #6（HTTPS 响应）、#7（自签名证书与方案文档）、#8（模拟摄像头）。本轮没有需要解决的分支冲突，也没有把 `dev` 反向合并到 `main`。

GitHub API 复核显示 `dev` 和 `main` 目前都没有分支保护规则。当前规则允许单 Agent 直接在 `dev` 小步开发；多人共享或准备发布前，应由仓库管理员明确决定是否为 `main` 启用 PR、必需检查和禁止强推保护，不能由 Agent 擅自改变远端治理方式。

## 当前技术基线

| 层 | 代码事实 | 当前定位 |
| --- | --- | --- |
| Web | Next.js `15.5.24`、React `18.3.1`、TypeScript `5.1.6`、Redux Toolkit、Tailwind CSS | 浏览器端原型与登录/注册界面 |
| API | FastAPI、Pydantic 2、SQLAlchemy Async、Alembic 配置、JWT | 独立 Python 后端骨架，尚未迁入 Vercel Next.js API |
| 数据 | SQLAlchemy 支持 PostgreSQL/SQLite；仓库曾提交开发 SQLite 文件 | 本地开发可用，生产托管 PostgreSQL及迁移链未验收 |
| 媒体 | FastAPI 将整个上传读入内存并写入 `backend/uploads` | 仅适合本地开发，不适用于 Vercel 函数生产持久化 |
| AI | 前后端均有随机模拟检测；`ai-engine` 有 YOLOv8、CNN、CLIP 研究脚本 | 研究/演示代码，无已验证模型、权重、数据集或在线推理链路 |
| 部署 | Docker Compose、Nginx、自签名证书等旧部署资料 | 与“单个 Vercel 项目”目标不一致，不能视为生产方案 |

版本真值来自 `frontend/web/package-lock.json`、`frontend/web/package.json`、`backend/uv.lock` 和 `backend/pyproject.toml`。当前锁定的 Next.js 为 15.5.24；旧文档中 React 19、Kubernetes、GPU 集群、Milvus、MongoDB 等均为历史规划，并非当前实现。

## 功能矩阵

状态定义：

- **已实现**：代码路径存在，可承担所述的有限行为，但不代表已完成生产验收。
- **模拟**：界面或接口存在，业务结果由占位逻辑生成，生产必须禁用。
- **部分实现**：只有骨架或局部链路，尚不能稳定完成用户任务。
- **未实现**：没有可工作的产品链路。

| 能力 | 状态 | 代码现状 | 生产缺口 |
| --- | --- | --- | --- |
| 房型选择与巡检流程 UI | 部分实现 | 首页包含房型选择、录制、上传、分析进度和结果视图 | 后端异步协议不匹配，端到端流程无法可靠完成 |
| 浏览器摄像头录制 | 已实现（未完成设备验收） | 支持真实 `getUserMedia`/`MediaRecorder`；可通过公开环境变量切换模拟摄像头 | 尚未覆盖 iOS Safari、Android、权限拒绝、编解码兼容和弱网 |
| 模拟摄像头 | 模拟 | Canvas 生成演示流和占位 WebM | 只能用于开发；生产环境必须显式关闭并显示真实状态 |
| 注册、登录与刷新令牌 | 部分实现 | FastAPI 有用户持久化和 JWT 接口，Web 有登录/注册页面 | 前端将令牌存入 `localStorage` 和可被脚本读取的 Cookie；middleware 只检查 Cookie 是否存在；刷新请求体与后端参数形式不一致；注册字段和密码最小长度不一致 |
| 文件上传、读取、下载、删除 | 部分实现 | FastAPI 本地文件接口存在；本轮已限制按用户 UUID 目录查找 | 没有大小、MIME、内容和配额校验；上传整文件进入函数内存；缺少私有 Blob 与签名直传 |
| AI 分析任务 | 模拟且不可持久 | 接口创建任务后用 `asyncio.create_task` 运行；提交时不校验文件存在或归属，文件缺失仍继续生成 3–5 个随机模板结果 | 每个请求创建新的 `AIService`，状态字典不会跨请求共享；实例重启即丢失；Vercel 返回响应后的后台任务不可靠 |
| 真实缺陷识别 | 未实现 | 浏览器 `aiAnalyzer.ts` 及后端 `_simulate_detection` 都使用随机结果；研究脚本未接入 API | 需要选定外部多模态 AI、定义受控 schema、保存证据与人工复核记录并做真实数据评估 |
| 报告 CRUD | 部分实现 | SQLAlchemy 模型、路由和按用户查询骨架存在；本轮修正了重复 `/reports/reports` 前缀 | 分页响应、计数、更新/删除 ORM 对象存在代码级缺陷；未完成数据库集成测试；前后端字段命名/日期类型需统一 |
| 报告导出与分享 | 部分实现 | 前端可生成 HTML/JSON；后端 JSON/HTML 路径有骨架 | 后端 PDF 标记为 TODO；分享码未持久化；HTML 模板未系统验证不可信内容转义 |
| 订单 | 部分实现 | 创建、查询、取消和状态接口存在 | 无业务页面与端到端测试；金额由请求项计算，需服务端商品定价与状态机校验 |
| 支付 | 模拟 | `process_payment` 跳过网关并直接把订单设为已支付 | 生产必须禁用，接入真实支付、Webhook、幂等和对账后才可开放 |
| 健康检查 | 已实现（有限） | `/health` 检查进程，`/ready` 检查数据库 | 尚未检查 Blob、AI、队列等托管依赖 |
| 历史记录与多设备同步 | 部分实现 | 后端报告/订单模型可持久化；前端 Redux 仅保存当前浏览器会话 | 当前用户主流程未可靠写入并读取云端报告 |
| PDF/Word、OCR、状态比对、Agent 对话、RAG、维修对接 | 未实现 | 只在历史方案或 TODO 中出现 | 需要在核心巡检链路稳定后按路线图逐项立项 |

## 本轮已复现并处理的问题

以下修复已经完成本轮综合验证，并随本次 `dev` 提交保存：

| 问题 | 原始表现 | 当前处理 | 验证状态 |
| --- | --- | --- | --- |
| 文件越权读取/删除 | 指定用户目录未命中后会全局 `rglob`，其他用户知道文件 ID 即可访问；文件 ID 还被直接当作 glob 模式 | 强制提供合法用户 UUID 和文件 UUID，只允许在该用户的已解析目录内查找 | 新增所有者、跨用户、缺少所有者和非法标识符回归；10 个后端用例整体通过，仍需 API/真实存储综合验证 |
| 报告路由重复前缀 | 应用以 `/api/v1/reports` 挂载一个自带 `/reports` 的 router，公开路径实际变成 `/api/v1/reports/reports` | 移除 router 内重复前缀 | OpenAPI 路由回归通过，仍需报告 CRUD 集成验证 |
| 前端类型错误 | `VideoCaptureClass` 是运行时值，却被用作 ref 类型 | 导出 `VideoCaptureInstance` 联合实例类型并用于 ref | `npx tsc --noEmit` 和 `npm run build` 均通过；审查机 Node 25 不在声明的 Node 20/22 支持范围 |
| Next.js tracing root | `outputFileTracingRoot` 使用相对字符串 | 改为基于 `__dirname` 的绝对路径 | `npm run build` 通过；仍需在 Node 22.x/Vercel Preview 复验 |
| Ruff 配置不可用 | `indent-width` 位于不接受该键的 formatter 配置段，并包含当前版本不支持的规则项 | 移动配置并移除无效项 | Ruff 已能启动；`uv run ruff check .` 仍报告 470 个遗留问题，其中 397 个可自动修复，本轮未批量改写业务代码 |
| 运行时数据进入 Git | 仓库跟踪了一个 SQLite 文件和 5 个 WebM 文件 | 从当前索引移除并补充忽略规则；迁移脚本恢复为应跟踪源码 | 删除项和忽略规则已纳入本次提交 |
| 前端环境变量示例误导 | 示例曾列出 MongoDB URI、JWT 与公开客户端加密 key，容易被误作可保密配置 | 仅保留公开的本地 API 地址与显式关闭的 mock 摄像头开关 | 目标会话、数据库、Blob 与 AI 密钥仍待迁入服务端 Next.js API |

## 仍未修复的阻断项与风险

### P0：阻止 Vercel 生产部署

1. **分析任务无法跨请求读取。** POST 和状态 GET 各自新建 `AIService`，其 `tasks = {}` 只属于单个实例；页面也没有轮询，而是把“任务已提交”的响应直接当作最终 `problems` 和 `report_id`。即使本地进程不退出，这条产品主链路也不成立。
2. **运行模型与 Vercel 不兼容。** FastAPI、本地上传目录、请求返回后的 `asyncio.create_task`、Docker/Nginx 不是已接受的单 Vercel 目标架构；当前 `/api` rewrite 和客户端默认地址还指向 `localhost:8000`，Vercel 上没有该进程。需要迁移到 Next.js Route Handlers/Server Actions、持久任务表及外部 AI API；耗时工作要使用受 Vercel 支持的队列/工作流或可重入轮询步骤。
3. **媒体持久化不成立。** Vercel 函数文件系统是临时的，且当前上传会把完整视频读入函数内存。浏览器应在服务端鉴权后直传私有 Blob，API 只保存元数据，并向 AI 发送受限图片批次或签名读取地址，不能转发整段原视频绕过限制。
4. **身份会话不安全。** 浏览器脚本可读取访问令牌，middleware 不验证签名/过期，缺少完整的服务端会话、CSRF 防护和共享限流。密码哈希前还会静默截断到 72 字节，必须改成明确的现代密码策略及迁移方案。
5. **仍有生产依赖漏洞。** 升级后，`npm audit --omit=dev` 仍报告 1 个 high 和 1 个 moderate；`next@15.5.24` 间接固定 `postcss@8.4.31`，审计自动修复要求 Next 16.3.4 的破坏性迁移，并须同步替换即将移除的 `next lint` 工作流。升级后必须重新执行类型、构建、浏览器和认证回归。
6. **真实 AI 能力不存在。** 当前随机结果可能被界面描述成 AI 检测。生产必须删除或严格隔离模拟路径，并把输出定位为“待人工复核的问题建议”；不得声称判断结构安全、责任归属、法律结论或未经验证的准确率。
7. **数据库迁移和云环境未验收。** 目前没有可审查的完整生产 migration chain，也没有对托管 PostgreSQL 的连接、并发、备份、恢复和归属隔离测试。

`frontend/web/lib/encryption.ts` 使用公开环境变量和硬编码 fallback 作为 AES key；浏览器用户或脚本可以取得该值，因此它不能保护令牌、媒体或报告。该模块当前没有被业务导入，后续若需静态数据加密，密钥必须由服务端管理，并单独评审密钥轮换与恢复。

### P1：核心功能完整性

- 统一前后端 API schema：异步任务状态、报告字段的 snake_case/camelCase、ISO 日期、错误结构和分页结构都必须有显式 adapter 与契约测试。
- 文件与模型输入需校验 UUID、MIME、大小、帧数和状态转换；禁止任意远端 URL、SSRF、提示词注入和 HTML 注入。
- 报告需保留原始证据帧、模型/提示词版本、生成建议、人工修改历史和最终确认人。
- 修复报告/订单列表的分页契约与计数查询：router 以 `data` 构造需要 `items`、`has_next` 的分页模型，service 又对普通实体查询调用 `scalar_one()` 作为总数；多条记录时会失败。
- 修复报告更新/删除的 ORM 生命周期：`get_by_id` 当前先返回 Pydantic schema，后续却将该 schema 当作 SQLAlchemy 实体执行 `setattr`、`refresh` 或 `delete`。
- 修复 AI 状态 404 分支的名称遮蔽：局部变量 `status` 覆盖了 FastAPI `status` 模块，任务不存在时会访问 `None.HTTP_404_NOT_FOUND`。
- 后端报告服务、订单服务、刷新令牌和完整资源归属需要集成测试；模拟支付不得进入生产构建。
- 建立可观察性、审计日志、失败重试、幂等键、超时和用户可理解的失败恢复流程。
- 在 iOS Safari/Android Chrome 验证 `MediaRecorder` 格式协商和照片降级；生产和 Preview 都不能开启公开环境变量控制的模拟摄像头。

### P2：产品与工程完善

- 在真实设备和目标浏览器验证拍摄权限、前后摄像头、录制格式、弱网上传和无障碍体验。
- 完成报告在线预览及安全导出；随后再排 OCR、历史比对、Agent 对话和收费能力。
- 为前端补充少量高价值行为测试和主链路浏览器测试；不要用空 Jest 配置冒充测试通过。
- 建立受支持 Node 22.x 的 CI 基线；当前仓库只有 PR 模板，没有可执行的 CI workflow。

## 验证记录

2026-09-10 至 2026-09-11 审查与修复过程中得到的真实结果如下。覆盖率只来自本轮新增的小范围测试，不代表整个后端质量。

| 检查 | 初始结果 | 当前结果 | 解释 |
| --- | --- | --- | --- |
| Git 分支图与远端引用 | 通过 | 通过 | `dev` 远端头为 `bf6e7ab`；Trae 仍为 `ed1887c`（其成果已包含在 dev）；`main` 为 `ebe4cc7` 且无独有提交；`origin/HEAD -> origin/dev` |
| 后端既有测试 | 0 个测试 | 新增 10 个回归测试，10 passed | `ed1887c` 没有受 Git 跟踪的后端测试，不应把 pytest 配置等同于有测试 |
| 新增安全/路由回归 | 红阶段 7 failed / 3 passed | 10 passed | 3 个 Pydantic 弃用 warning；显示 55% coverage 仅是当前新增用例的运行结果，不是完整项目覆盖率承诺 |
| `npm run lint` | 退出码 0，1 个 warning | 退出码 0 | 已补齐 `useCallback` 依赖；检查环境为 Node 25.8.2，不等同于受支持 Node 20/22 的验证 |
| `npx tsc --noEmit` | 失败：摄像头类被当作类型；另曾出现隐式 `any` | 退出码 0 | 当前工作区通过；仍需在 Node 22.x/Vercel Preview 复验 |
| `npm run build` | 失败于 TypeScript 错误 | 退出码 0 | 当前工作区通过；Node 25.8.2 超出 `package.json` 的 `<23` 上限 |
| `npm test -- --runInBand` | 退出码 1，未发现测试 | 退出码 1，未发现测试 | Jest 仍无用例；`.next/standalone` 还会产生 package-name collision warning |
| `npm audit --omit=dev --json` | 20 个漏洞（升级前） | 退出码 1：1 high、1 moderate | 自动修复要求 Next 16.3.4 major migration |
| Ruff | 配置错误，无法正常检查 | 退出码 1，470 个遗留问题 | 397 个标记为可自动修复；需分批处理并审查行为变化 |

尚未验证：真实移动设备、真实 PostgreSQL、私有 Blob、外部 AI API、Vercel Preview/Production、支付网关、备份恢复、负载与并发、真实房屋数据上的模型质量。生产发布必须由用户明确批准。

## 已接受的目标架构

架构决策已记录在 [ADR-0001：统一到 Vercel 的应用运行架构](adr/0001-vercel-unified-runtime.md)，基线为 `dev` @ `243a19d`。ADR 固化了单 Next.js 项目、托管 PostgreSQL、私有 Blob、服务端会话和持久分析任务的边界；具体供应商和长任务产品仍需在 Preview 验证后选择。

用户已允许由 Vercel 承载应用与接口，同时使用托管数据服务和外部 AI API。后续实现应收敛为：

```text
浏览器
  ├─ 页面与同源 API ──> 单个 Vercel Next.js 项目
  ├─ 鉴权直传 ────────> 私有 Blob
  └─ 查询任务/报告 ───> 托管 PostgreSQL
                              │
Vercel 服务端 ──受限证据批次──> 外部多模态 AI API
```

关键原则：数据库、Blob、AI 和会话密钥只存在服务端；`NEXT_PUBLIC_*` 均视为公开；每次数据库、媒体、任务和报告操作都校验用户与资源归属；模型输出只作为待人工复核的建议。

## 下一步执行顺序

1. 在 Node 22.x 建立可重复的 CI 基线，补充前端高价值行为测试，并评估 Next 16 安全升级及 ESLint CLI 迁移。
2. 用 ADR 固化 Vercel 全栈结构、托管 PostgreSQL、私有 Blob、会话方案、任务执行方案和外部 AI provider；然后迁移最小纵向链路。
3. 先交付“安全会话 → 直传一组证据图片 → 持久任务 → 外部 AI 结构化建议 → 人工复核 → 持久报告”闭环，再扩展视频、OCR、比对和收费。
4. 在 Vercel Preview 完成数据库迁移、权限、失败恢复、移动设备和成本边界验收后，再请求生产部署批准。
