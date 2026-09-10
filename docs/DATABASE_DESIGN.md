# 数据库设计

更新日期：2026-09-10。本文描述 Vercel 目标架构。现有 FastAPI 的 User、Order、Report 模型是旧原型，尚无完整可审查的生产迁移链。

## 原则

- 托管 PostgreSQL 是业务状态唯一来源；Blob 保存媒体，数据库只保存私有 object key 和元数据。
- 每个用户资源带 `owner_id`；多角色阶段增加 Membership。所有查询和 mutation 都校验资源归属。
- 主键 UUID，时间为带时区的 UTC，金额使用整数分。状态使用受控 enum/check constraint。
- JSON 只存模型原始结构或不可频繁查询的快照；归属、状态、外键、费用和审计等字段结构化。
- migration 属于源码。Preview 和 Production 独立，迁移独立于请求和普通构建运行。
- 不预先设计读写分离、分库分表或 1000 万级架构；有测量数据后再决定。

## MVP 实体

### users / sessions

`users(id, email, display_name, role, created_at, updated_at, deleted_at)`。email 使用规范化唯一索引。密码/凭据按认证方案保存，不自定义可逆加密。

`sessions(id, user_id, expires_at, revoked_at, created_at, last_seen_at)`。会话可撤销并支持设备审计。

### inspections

`inspections(id, owner_id, property_type, address, status, created_at, updated_at)`。地址可空，按最小必要采集。建议状态：draft、collecting、ready、analyzing、review、completed、archived。

### media_assets

`media_assets(id, inspection_id, owner_id, blob_key, sha256, content_type, size_bytes, captured_at, retention_until, status, created_at)`。唯一约束可放在 `owner_id + blob_key`；索引 `inspection_id, created_at`。客户端 URL 不作为可信定位符。

### analysis_jobs

`analysis_jobs(id, inspection_id, owner_id, status, idempotency_key, attempt, lease_expires_at, error_code, provider, model, prompt_version, report_id, created_at, updated_at)`。

- 唯一约束：`owner_id + idempotency_key`。
- 状态：queued、processing、succeeded、failed、cancelled。
- 失败、重试、回调和补偿都做 compare-and-set，终态不可被重复覆盖。

### findings

`findings(id, inspection_id, analysis_job_id, media_asset_id, category, suggested_severity, description, evidence_json, model_confidence, human_decision, human_note, created_at, updated_at)`。model_confidence 明确标为模型自报值，不能直接展示为概率保证。

### report_versions / audit_events

`report_versions(id, inspection_id, owner_id, version, source_job_id, content_json, content_hash, confirmed_by, created_at)`，唯一 `inspection_id + version`，已有版本不覆盖。

`audit_events(id, actor_id, resource_type, resource_id, action, request_id, metadata_json, created_at)`。审计 metadata 不包含密钥、完整 token、密码或不必要的室内媒体内容。

## 后续实体

租赁协作阶段再增加 properties、leases、memberships、invitations；维修阶段增加 work_orders；商业化阶段增加 products、orders、payments 和 webhook_events。支付金额来自服务端产品表，webhook 事件 ID 唯一并可重放核对。

## 迁移与恢复

1. 每次 schema 变更先创建 migration 与针对空库/已有数据的测试。
2. 扩展型迁移先加兼容字段/表，应用双读写或回填，验证后再收紧约束；破坏性步骤单独审批。
3. Preview 使用独立库演练 migration。Production 迁移记录版本、时间、执行人/Agent、备份点和恢复命令。
4. 定期恢复演练验证备份真的可用。软删除不是备份，也不能替代隐私删除。
