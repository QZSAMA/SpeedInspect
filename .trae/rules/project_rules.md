# 项目开发规则配置

## 技术栈规范
- **前端**: React 18.2.0, Tailwind CSS 3.3.0, Redux Toolkit 1.9.5
- **后端**: Next.js 14.0.0, Node.js 18.17.0, MongoDB 6.0.0, JWT 9.0.2
- **依赖**: npm 9.6.7，版本在package.json中明确定义

## 测试标准
- **框架**: 前端Jest + React Testing Library，后端Mocha + Chai
- **覆盖率**: 单元测试≥80%，集成测试≥90%，端到端测试≥95%
- **规范**: 测试文件命名为`*.test.js`

## API使用限制
- **前端禁止**: `document.write()`, `eval()`, `with`语句, `innerHTML`
- **后端禁止**: `child_process.execSync()`, `fs.readFileSync()`, `Buffer()`构造函数

## 多端兼容性
- **响应式**: 移动优先，使用Flexbox和Grid布局
- **断点**: 移动端<768px，平板768-1024px，桌面>1024px
- **兼容**: 支持Chrome、Firefox、Safari最新两个版本，Edge最新版本
- **迁移**: 组件模块化，状态管理与UI分离，使用CSS变量