-- 初始化数据库脚本
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建默认用户（可选）
-- INSERT INTO users (id, username, email, role, password_hash)
-- VALUES (
--   uuid_generate_v4(),
--   'admin',
--   'admin@speedinspect.com',
--   'superadmin',
--   '$2b$12$EixZaYb4U/4QkMf/8W7hHeXmI96aB5y9e9X5Q8w7e4r3t2y1u0o9p' -- 密码: admin123
-- ) ON CONFLICT (email) DO NOTHING;
