# 数据库设计文档

## 🎯 设计原则
1. **微服务导向**：表结构按业务模块拆分，便于后续服务拆分
2. **扩展性优先**：使用JSON字段存储非结构化数据，避免频繁表结构变更
3. **软删除**：所有业务表使用`is_deleted`字段实现软删除，保留数据历史
4. **UUID主键**：使用UUID作为主键，避免ID泄露和分库分表问题
5. **索引优化**：针对高频查询字段建立索引，提升查询性能
6. **符合范式**：遵循第三范式，减少数据冗余，保证数据一致性

## 📊 数据库表结构

### 1. users - 用户表
**核心用户信息存储**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 用户唯一ID |
| phone | VARCHAR(20) | UNIQUE, INDEX | 手机号（可空） |
| email | VARCHAR(100) | UNIQUE, INDEX | 邮箱（可空） |
| username | VARCHAR(50) | | 用户名 |
| nickname | VARCHAR(50) | | 用户昵称 |
| avatar_url | VARCHAR(255) | | 头像URL |
| password_hash | VARCHAR(255) | | 密码哈希（不存储明文） |
| role | VARCHAR(20) | DEFAULT 'user' | 用户角色：user/admin/enterprise/superadmin |
| status | VARCHAR(20) | DEFAULT 'active' | 用户状态：active/locked/disabled |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |
| is_deleted | BOOLEAN | DEFAULT FALSE | 软删除标记 |

**设计原因**：
- 手机号和邮箱都允许为空，支持多种注册方式
- 角色字段支持多级权限管理，满足不同业务场景（普通用户、企业用户、管理员）
- 密码单独存储为哈希值，安全合规
- 状态字段支持灵活的用户生命周期管理

### 2. reports - 检查报告表
**房屋检查报告主表**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 报告唯一ID |
| user_id | UUID | FOREIGN KEY, INDEX | 所属用户ID |
| property_type | VARCHAR(50) | NOT NULL | 房屋类型：apartment/house/villa/office/commercial |
| address | VARCHAR(255) | | 房屋地址 |
| problems | JSON | DEFAULT '[]' | 检测到的问题列表（JSON数组） |
| summary | JSON | DEFAULT '{}' | 报告摘要（包含统计数据和评分） |
| video_file_id | VARCHAR(100) | | 关联视频文件ID |
| thumbnail_url | VARCHAR(255) | | 报告缩略图URL |
| status | VARCHAR(20) | DEFAULT 'completed' | 报告状态：draft/completed/archived |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |
| is_deleted | BOOLEAN | DEFAULT FALSE | 软删除标记 |

**设计原因**：
- 问题和摘要使用JSON存储，灵活支持不同的检测结果格式，无需修改表结构
- 只存储视频文件ID而非实际文件，解耦文件存储和业务逻辑
- 状态字段支持报告草稿、完成、归档等生命周期管理
- user_id索引加速用户报告列表查询

### 3. orders - 订单表
**服务订单表**

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 订单唯一ID |
| user_id | UUID | FOREIGN KEY, INDEX | 所属用户ID |
| order_number | VARCHAR(32) | UNIQUE, INDEX | 订单号（业务唯一标识） |
| type | VARCHAR(50) | NOT NULL | 订单类型：standard_inspection/premium_inspection等 |
| status | VARCHAR(20) | DEFAULT 'pending' | 订单状态：pending/paid/processing/completed/cancelled/refunded |
| items | JSON | DEFAULT '[]' | 订单项列表（JSON数组） |
| total_amount | FLOAT | NOT NULL | 订单总金额 |
| paid_amount | FLOAT | DEFAULT 0 | 已支付金额 |
| payment_method | VARCHAR(50) | | 支付方式：wechat/alipay/card等 |
| property_address | VARCHAR(255) | | 服务房屋地址 |
| contact_name | VARCHAR(100) | | 联系人姓名 |
| contact_phone | VARCHAR(20) | | 联系电话 |
| notes | TEXT | | 备注信息 |
| paid_at | DATETIME | | 支付时间 |
| completed_at | DATETIME | | 完成时间 |
| cancelled_at | DATETIME | | 取消时间 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |
| is_deleted | BOOLEAN | DEFAULT FALSE | 软删除标记 |

**设计原因**：
- 订单项使用JSON存储，支持灵活的商品/服务组合
- 订单号单独字段，用于业务场景展示和查询
- 状态字段完整覆盖订单全生命周期
- 多个时间字段记录订单关键节点，便于统计和追溯
- contact信息冗余存储，避免用户信息修改导致历史订单信息不一致

### 4. 文件存储设计
**文件不直接存储在数据库中**，采用以下方案：
- 小文件：本地文件系统存储，路径为`uploads/{user_id}/{file_id}.{ext}`
- 大文件：支持对接S3/OSS等对象存储
- 数据库只存储文件元数据（ID、文件名、大小、MIME类型等）

**设计原因**：
- 数据库不适合存储大二进制文件，会严重影响性能
- 文件系统/对象存储更适合海量文件存储，成本更低
- 便于CDN加速和分布式部署

## 🗄️ 索引设计

### 高频查询索引
1. `users(phone)` - 手机号登录查询
2. `users(email)` - 邮箱登录查询
3. `reports(user_id, created_at DESC)` - 用户报告列表按时间倒序查询
4. `orders(user_id, created_at DESC)` - 用户订单列表按时间倒序查询
5. `orders(order_number)` - 订单号查询

### 唯一索引
1. `users(phone)` - 手机号唯一
2. `users(email)` - 邮箱唯一
3. `orders(order_number)` - 订单号唯一

## 🔧 扩展设计

### 未来可扩展的表
1. `ai_tasks` - AI分析任务表（当前使用内存存储，生产环境需要持久化）
   - 存储分析任务状态、进度、结果
   - 支持任务队列和异步处理

2. `payments` - 支付记录表
   - 存储每一笔支付流水
   - 支持对账和退款

3. `invoices` - 发票表
   - 存储发票申请和开具信息
   - 支持财务流程

4. `enterprise_orgs` - 企业组织表
   - 支持多用户企业账号
   - 部门和权限管理

5. `sharing_tokens` - 报告分享令牌表
   - 存储报告分享的令牌和过期时间
   - 支持匿名访问报告

## 📈 性能优化建议

### 读写分离
- 主库处理写操作（用户创建、订单提交、报告生成）
- 从库处理读操作（列表查询、报告查看、统计分析）

### 缓存策略
- 热点数据缓存：用户信息、报告摘要
- 静态资源缓存：前端静态文件、报告模板
- 会话缓存：JWT令牌黑名单、临时验证码

### 分库分表
- 当数据量超过1000万时，按user_id哈希分库分表
- 历史数据归档：超过1年的订单和报告归档到历史库

## 🔒 安全设计
1. **数据加密**：敏感字段（手机号、邮箱）存储时加密
2. **访问控制**：通过`user_id`过滤，用户只能访问自己的数据
3. **审计日志**：重要操作记录审计日志，便于追溯
4. **备份策略**：定期全量备份 + 增量备份，确保数据安全

## 📋 数据库初始化
### 迁移脚本
使用Alembic进行数据库迁移：
```bash
# 生成迁移文件
alembic revision --autogenerate -m "init tables"

# 执行迁移
alembic upgrade head
```

### 初始数据
```sql
-- 创建超级管理员用户
INSERT INTO users (id, username, email, role, password_hash)
VALUES ('a1b2c3d4-5678-90ef-ghij-klmnopqrstuv', 'admin', 'admin@speedinspect.com', 'superadmin', '$2b$12$...');
```

---

**设计优势总结**：
✅ 结构清晰，模块分明，便于维护和扩展
✅ 灵活性高，JSON字段支持业务快速迭代
✅ 性能优秀，合理的索引设计满足高频查询
✅ 安全可靠，软删除和备份机制保障数据安全
✅ 兼容性好，支持从小规模到大规模部署的平滑演进
