# SpeedInspect - 房屋状况智能检查系统

基于AI技术的房屋状况智能检查系统，帮助用户快速、客观、全面地了解房屋状况。

## 功能特性

### 核心模块
- **视频采集模块**：支持移动设备录制房屋视频，提供防抖处理和清晰度优化
- **AI图像分析模块**：视频帧提取、图像预处理及深度学习分析
- **问题识别与分类**：识别15+类常见房屋问题
- **报告生成**：自动生成结构化检查报告
- **用户界面**：直观的移动端友好界面

### 支持的问题类型
- 墙面损坏（裂缝、水渍、霉斑）
- 家具磨损（划痕、凹陷、褪色）
- 水电设施异常（管道漏水、插座损坏、开关故障）
- 地板、天花板、门窗问题
- 卫生间、厨房、照明问题
- 油漆、霉斑、水渍、虫害、安全隐患等

## 技术栈

- **前端**：React 18.2.0, Next.js 14.0.0, TypeScript
- **样式**：Tailwind CSS 3.3.0
- **状态管理**：Redux Toolkit 1.9.5
- **AI/ML**：TensorFlow.js
- **加密**：Crypto-js
- **图标**：Lucide React

## 快速开始

### 安装依赖

```bash
npm install
```

### 配置环境变量

```bash
cp .env.example .env.local
# 编辑 .env.local 文件，填入您的配置
```

### 启动开发服务器

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

### 构建生产版本

```bash
npm run build
npm start
```

## 项目结构

```
SpeedInspect/
├── app/                    # Next.js App Router
│   ├── page.tsx           # 主页面
│   ├── layout.tsx         # 根布局
│   └── globals.css        # 全局样式
├── components/            # React组件
│   ├── VideoCapture.tsx   # 视频采集组件
│   ├── AnalysisProgress.tsx # 分析进度组件
│   └── ProblemList.tsx    # 问题列表组件
├── lib/                   # 核心库
│   ├── videoCapture.ts    # 视频采集模块
│   ├── aiAnalyzer.ts      # AI分析模块
│   ├── reportGenerator.ts # 报告生成模块
│   └── encryption.ts      # 加密存储模块
├── store/                 # Redux状态管理
│   ├── slices/
│   │   └── inspectionSlice.ts
│   ├── index.ts
│   └── providers.tsx
├── types/                 # TypeScript类型定义
│   └── index.ts
└── package.json
```

## 使用说明

1. **选择房屋类型**：在欢迎页面选择适合的房屋类型（公寓、独栋房屋、办公室等）
2. **录制视频**：启动摄像头，缓慢移动拍摄房屋各个角落
3. **AI分析**：系统自动使用深度学习模型分析视频内容
4. **查看结果**：查看检测到的问题列表和综合评分
5. **下载报告**：下载详细的HTML格式检查报告

## 数据安全

- 用户视频和检查报告使用AES加密存储
- 符合数据隐私保护法规
- 支持本地离线分析模式

## 开发规范

- 使用TypeScript进行类型安全开发
- 遵循React和Next.js最佳实践
- 代码提交前运行lint和类型检查
- 单元测试覆盖率≥80%

## 许可证

MIT License
