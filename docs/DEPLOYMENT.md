# Vercel 部署与上线指南

更新日期：2026-09-11。本文是目标配置，当前代码还不能作为完整生产服务部署。

## 官方能力核对

本次直接核对 Vercel 官方文档：

- [Functions 限制](https://vercel.com/docs/functions/limitations)：请求/响应 body 最大 4.5 MB；Fluid compute 当前 Hobby 最长 300 秒，Pro/Enterprise 默认 300 秒、最长 800 秒，扩展时长另有 Beta 条件；Node 包体 250 MB、Python 500 MB。上线时按实际套餐重新核对。
- [存储](https://vercel.com/docs/storage)：Blob 支持公共和私有存储，数据库通过 Marketplace 集成。
- [Blob 客户端上传](https://vercel.com/docs/vercel-blob/client-upload)：大文件由浏览器直传，签发 token 前必须鉴权与授权。
- [FastAPI](https://vercel.com/docs/frameworks/backend/fastapi)：可以作为一个 Vercel Function 部署；框架受支持不等于旧存储和任务实现可用。

## 目标项目设置

1. GitHub 连接本仓库，Framework 选择 Next.js，Root Directory 设置为 `frontend/web`，使用 `npm ci` 和 `npm run build`，输出目录保持框架默认。
2. Vercel Production Branch 建议设置为 `main`，`dev` 只生成 Preview。GitHub 默认分支和 Vercel Production Branch 是独立配置，必须在控制台核对。
3. 当前 `main` 只有旧初始化文档，不能发布。待通过验收的 `dev` 提交明确晋级 `main` 后再部署 Production。
4. 固定 Vercel 支持的 Node LTS，并在本地和 CI 使用同一版本。此次审查机器的 Node 25 不是生产版本承诺。
5. 接入托管 PostgreSQL 和私有 Blob。Preview 与 Production 必须使用独立数据库、存储和凭据，数据库区域靠近函数。
6. Preview 开启访问保护，并在目标手机网络上测试。HTTPS 由 Vercel 提供，不部署 Nginx 或自签名证书。

当前 `next.config.js` 已移除指向 `http://localhost:8000` 的 rewrite，`apiClient.ts` 默认使用同源 `/api/v1`；但对应的 Next.js Route Handlers 尚未实现，Vercel 上的登录、注册和巡检 API 仍不可用。因此不要仅凭构建成功上线当前原型，必须先完成同源 API、会话、数据库和任务迁移。

## 环境变量

| 名称 | 范围 | 状态与用途 |
|---|---|---|
| DATABASE_URL | 服务端 | 目标池化 PostgreSQL |
| BLOB_READ_WRITE_TOKEN | 服务端 | 目标 Blob 集成 |
| AUTH_SECRET | 服务端 | 目标会话；选定认证库后核对准确名称 |
| AI_API_KEY / AI_MODEL | 服务端 | 目标 AI 适配层 |
| APP_ORIGIN | 服务端 | 可信站点和 CSRF 校验 |
| NEXT_PUBLIC_API_URL | 公开 | 迁移期可选的旧 FastAPI 地址；留空时使用同源 `/api/v1`，生产应留空 |
| NEXT_PUBLIC_MOCK_CAMERA | 公开 | 仅开发演示使用 |

目标变量尚未全部被代码消费。仅配置变量不代表服务已经接通。密钥存于 Vercel 加密配置，不提交 `.env`；Preview 不得复用生产数据或账单凭据。

## 大媒体与任务

禁止将大视频 POST 到函数，也不能将 SQLite 或上传目录放到临时磁盘后当作持久化。浏览器压缩并直传私有 Blob；函数只传小型元数据或有界证据帧批次。大媒体下载使用授权的直接读取方案，不能通过 4.5 MB 函数响应代理。

不在 Vercel 运行自托管 Redis/Celery/GPU/Docker。关键任务必须持久化、幂等、有限重试并可恢复；只增加 `maxDuration` 不能解决任务丢失。AI 超时、429 或异常响应必须呈现真实失败，不得改为模拟成功。

## 上线前门槛

- 清除直接依赖中的 critical/high 漏洞，锁定版本；当前锁文件的生产树 `npm audit --omit=dev` 为 0 个漏洞，完整开发依赖审计另行分级；typecheck、build 和必要测试通过，并在 Node 22/Vercel Preview 复验。
- 完成数据库迁移、认证、Blob 授权、任务恢复和真实报告导出。
- 使用两个账号验证跨用户读取/删除拒绝，测试过期会话、CSRF、上传超限和异常模型响应。
- 真机验证 Safari/Chrome 摄像头权限、录制格式、照片替代入口、弱网重试和刷新恢复。
- 配置日志脱敏、错误监控、预算告警和应用硬配额。Vercel 预算告警不等于 AI 费用熔断。
- 演练数据库恢复、Blob 清理、密钥轮换和上一部署版本回退。
- 在中国大陆等目标网络实测可达性和延迟；商用前核对套餐、数据驻留和媒体传给 AI 的隐私说明。

本次没有创建 Vercel 项目、开通收费服务、配置真实凭据或部署生产。完整迁移见 [路线图](ROADMAP.md)。
