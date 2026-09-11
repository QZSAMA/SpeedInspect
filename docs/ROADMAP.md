# SpeedInspect 路线图

更新日期：2026-09-11。审查代码基线：`dev` @ `bf6e7ab`。开始新任务前以 `git fetch origin --prune` 取得实际开发头。优先级按“先得到可安全部署的最小闭环，再增加业务范围”排序。每一阶段必须在 `dev` 独立可验收；没有完成前置门槛时不开始收费或多角色扩展。

## Phase 0：建立可信工程基线

当前进度：CI 已加入并在 Node 22/Python 3.12 上定义前端与后端必需检查；Vercel 目标边界已由 ADR-0001 固化。Next 16/ESLint CLI 迁移、漏洞清理和真实前端行为测试仍未完成，因此 Phase 0 尚未关闭。

完成条件：

- 固定 Node 22.x、Python 版本和锁文件；建立 CI，使 `npm ci`、lint、typecheck、build、后端测试在受支持运行时可重复。
- 清除运行时依赖的 critical/high 漏洞，记录无法立即修复的传递依赖与缓解措施；Next 16 升级和替换 `next lint` 单独做迁移与回归。
- 修复当前文件越权、报告路径和摄像头类型问题；停止跟踪数据库与用户媒体。
- 建立 `AGENTS.md`、项目状态、部署、API、开发、运维和变更记录。
- 生产 UI 不显示随机 AI 和模拟支付成功。开发 mock 必须由显式环境变量开启，并有醒目标识。

## Phase 1：Vercel 安全会话与数据库

交付：

- 将 `frontend/web` 升级为统一 Next.js 页面与 API 项目。
- 选定维护中的认证方案，使用 HttpOnly/Secure/SameSite Cookie、CSRF/Origin 校验和服务端授权。
- 定义 PostgreSQL schema 与迁移：User、Session、Inspection、MediaAsset、AnalysisJob、Finding、ReportVersion、AuditEvent。
- Preview/Production 数据库隔离，建立迁移、备份、恢复和种子数据规则。
- 为两用户资源隔离、会话过期、非法状态和幂等 mutation 编写集成测试。

验收：两个账号不能读取、修改或删除对方任何资源；刷新、登出、撤销和并发请求可验证；Preview 数据不会进入 Production。

## Phase 2：私有证据上传

交付：

- 手机照片采集和短视频浏览器抽帧；照片上传作为兼容入口。
- 服务端鉴权后签发私有 Blob 直传 token，绑定巡检、MIME、大小、数量和有效期。
- MediaAsset 持久化 hash、大小、采集时间、归属、保留期；删除和孤儿清理可重试。
- 上传失败、刷新、弱网重试、取消和恢复 UI。

验收：大媒体不经过函数 body；伪造 ownerId、路径、MIME、超限文件和过期 token 被拒绝；iOS Safari 与 Android Chrome 真机通过。

## Phase 3：真实 AI 与持久任务

交付：

- 基于授权样本评测并选定外部多模态供应商，定义版本化 prompt 和严格输出 schema。
- AnalysisJob 状态机、幂等键、lease、最多 3 次重试、超时、取消、429 退避和费用硬限制。
- 外部调用只获取当前用户获授权的有限证据；供应商回调验签、防重放。
- 前端查询真实任务状态，断网/刷新后恢复；失败不会显示模拟结果。

验收：非法 JSON、超时、429、重复请求、重复回调、函数中止均能落入可解释终态或被补偿恢复；同一幂等键不重复收费或生成报告。

## Phase 4：人工复核与报告闭环

交付：

- 证据帧与 Finding 绑定；用户可接受、修改、拒绝和标记无法判断。
- ReportVersion 保存原始建议、人工修改、确认者、生成模型和 prompt 版本。
- 安全 HTML/JSON 导出、浏览器打印；如确需 PDF，再选适合 Vercel 的生成方案。
- 报告删除、导出、分享（若启用）均按归属/短期令牌授权并留审计。

验收：从真机采集到报告导出可完整完成；刷新和多设备后仍能恢复；输出不宣称结构安全、责任或法律结论；不可信模型文本不能注入 HTML。

## Phase 5：Vercel Preview 发布准备

交付：

- Vercel Root Directory、Node 版本、Preview 保护、环境隔离、数据库区域、Blob 和 AI 凭据配置。
- 错误监控、结构化日志与脱敏、requestId、SLO 基线、费用/配额告警和应用熔断。
- 数据库恢复、Blob 清理、密钥轮换、部署回退演练。
- 目标地区网络、真实设备、并发与隐私流程验收。

验收：所有发布门槛有日期、提交 SHA、环境和证据链接。用户审查 Preview 后，才请求 Production 部署授权。

## 后续独立阶段

在 MVP 真实使用数据支持下依次评估：房源/租约与成员邀请、入住退房证据配对、维修工单、通知、OCR、咨询助手、支付和自有模型。每项单独设计，不把历史文档中的规划视为实现承诺。
