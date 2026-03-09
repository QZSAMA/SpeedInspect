# SpeedInspect 后端服务

房屋状态智能识别系统后端服务，基于FastAPI开发的微服务架构。

## 🚀 快速开始

### 环境要求
- Python 3.12+
- uv 包管理器
- PostgreSQL 16+
- Redis 7+

### 安装依赖
```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate
uv sync --all-extras
```

### 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis等连接信息
```

### 数据库迁移
```bash
# 初始化迁移（首次执行）
alembic init migrations

# 生成迁移文件
alembic revision --autogenerate -m "init tables"

# 执行迁移
alembic upgrade head
```

### 启动服务
```bash
# 开发环境
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uv run gunicorn src.app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 访问接口文档
- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 📁 项目结构
```
backend/
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── dependencies.py      # 公共依赖
│   │   ├── middleware.py        # 中间件
│   │   ├── core/                # 核心模块
│   │   │   ├── database.py      # 数据库连接
│   │   │   ├── security.py      # 安全相关（JWT、加密）
│   │   │   ├── errors.py        # 自定义异常
│   │   │   └── logging.py       # 日志配置
│   │   ├── features/            # 业务模块
│   │   │   ├── auth/            # 认证模块
│   │   │   ├── users/           # 用户模块
│   │   │   ├── files/           # 文件模块
│   │   │   ├── orders/          # 订单模块
│   │   │   ├── reports/         # 报告模块
│   │   │   └── ai/              # AI服务调用模块
│   │   └── shared/              # 公共组件
│   │       ├── pagination.py    # 分页工具
│   │       ├── responses.py     # 统一返回格式
│   │       └── validators.py    # 自定义校验器
├── migrations/                  # 数据库迁移
├── tests/                       # 测试用例
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   └── conftest.py              # pytest配置
├── scripts/                     # 工具脚本
├── pyproject.toml               # 项目配置
├── .env.example                 # 环境变量示例
└── README.md
```

## 🧪 测试
```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest tests/unit/

# 运行集成测试
uv run pytest tests/integration/

# 生成覆盖率报告
uv run pytest --cov=src --cov-report=html
```

## 🔧 开发规范
### 代码检查
```bash
# 代码格式检查
uv run ruff check .

# 自动修复格式问题
uv run ruff check . --fix

# 格式化代码
uv run ruff format .

# 类型检查
uv run mypy src/
```

### 提交规范
代码提交前必须通过：
1. ruff 格式检查
2. mypy 类型检查
3. 单元测试通过

## 📚 API 规范
所有接口遵循RESTful设计规范：
- 版本号：`/api/v1/xxx`
- 统一返回格式：
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {},
    "request_id": "xxx",
    "timestamp": 1234567890
  }
  ```
- 错误码规范：
  - 2xxxx：参数错误
  - 3xxxx：权限错误
  - 4xxxx：业务错误
  - 5xxxx：系统错误

## 🐳 Docker 部署
```bash
# 构建镜像
docker build -t speedinspect-backend .

# 运行容器
docker run -d -p 8000:8000 --env-file .env speedinspect-backend
```

## 📊 性能指标
- 普通接口响应时间：P95 < 200ms
- AI相关接口响应时间：P95 < 2s
- 支持QPS：≥ 1000
- 服务可用性：≥ 99.9%
