# SpeedInspect 开发错误和问题记录

本文档记录开发过程中遇到的错误、问题及其解决方案，供后续开发参考。

---

## 目录
- [CORS 跨域问题](#cors-跨域问题)
- [摄像头开启问题](#摄像头开启问题)
- [Mock 模式未启动问题](#mock-模式未启动问题)

---

## CORS 跨域问题

### 问题描述
开发环境下，前端 (localhost:3000) 调用后端 API (localhost:8000) 时，浏览器触发跨域拦截，请求失败。

### 根本原因
前后端分离架构，不同端口属于不同源，浏览器的同源策略阻止跨域请求。

### 解决方案
在 FastAPI 后端正确配置 CORS 中间件：

**文件位置**: `backend/src/app/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)
```

**配置解析**: `backend/src/app/config.py`

```python
@field_validator("CORS_ORIGINS", mode="before")
def parse_cors_origins(cls, v: str) -> List[str]:
    """解析CORS_ORIGINS为列表"""
    if isinstance(v, str):
        return [origin.strip() for origin in v.split(",")]
    return v
```

### 排查要点
1. 检查 `CORS_ORIGINS` 是否包含前端实际地址
2. 确认 `CORSMiddleware` 已正确添加到 FastAPI 应用（中间件注册顺序会影响执行）
3. 如果开启 `allow_credentials=True`，`allow_origins` 不能使用通配符 `["*"]`，必须明确指定具体域名

---

## 摄像头开启问题

### 问题描述
前端调用浏览器摄像头 API 时，无法正常启动摄像头，用户无法进行实时拍摄检查。

### 可能原因
1. **HTTPS 要求**：浏览器要求仅在 HTTPS 环境（或 localhost）下才能使用摄像头 API
2. **权限拒绝**：用户未授权摄像头访问权限，或权限已被禁止
3. **设备占用**：摄像头被其他应用占用
4. **浏览器兼容性**：不同浏览器对 MediaDevices API 支持略有差异

### 当前状态
- 开发环境 (localhost) 应该可以正常使用
- 生产环境必须部署在 HTTPS 下
- 需要添加权限错误处理和用户提示

---

## Mock 模式未启动问题

### 问题描述
在无法使用摄像头的环境下，Mock 模式（模拟摄像头，使用上传图片替代）没有自动启动，导致功能不可用。

### 可能原因
1. **功能检测逻辑**：前端检测摄像头不可用后，没有自动切换到 Mock 模式
2. **环境变量配置**：Mock 模式开关没有正确配置
3. **条件判断错误**：Mock 模式的条件判断逻辑有误

### 解决方案
1. 在前端 `lib/api/client.ts` 或配置文件中，确保 `VITE_ENABLE_MOCK` 或对应环境变量已设置
2. 添加完善的功能检测流程：
   ```typescript
   // 伪代码示例
   async function checkCameraAvailability(): Promise<boolean> {
     try {
       if (!navigator?.mediaDevices?.getUserMedia) {
         return false;
       }
       const stream = await navigator.mediaDevices.getUserMedia({ video: true });
       // 成功获取后立即停止
       stream.getTracks().forEach(track => track.stop());
       return true;
     } catch (e) {
       return false;
     }
   }

   // 如果摄像头不可用，自动启用 Mock 模式
   const cameraAvailable = await checkCameraAvailability();
   if (!cameraAvailable) {
     enableMockMode();
   }
   ```
3. 提供手动切换开关，让用户可以强制启用/禁用 Mock 模式

### 当前状态
- 需要在前端实现自动检测逻辑
- Mock 模式应该支持：
  - 上传图片文件替代摄像头流
  - 使用预设测试图片
  - 保留完整的 AI 分析流程

---

## 其他开发注意事项

### 环境变量
- 前端：`.env.local` 用于本地开发配置，不提交到 Git
- 后端：`.env` 用于本地配置，不提交到 Git
- 所有敏感信息都应该通过环境变量传入，不要硬编码

### 数据库
- 开发环境使用独立数据库，不要连接测试/生产库
- 每次修改模型后记得生成并运行 Alembic 迁移

### CORS
- 开发环境允许 `http://localhost:3000`
- 生产环境应该只允许实际部署域名
- 不要在生产环境使用 `["*"]` 通配符
