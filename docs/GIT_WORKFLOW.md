# Git 工作流

更新日期：2026-09-10。用户已明确要求后续在 `dev` 开发，本规则覆盖旧文档中“禁止直接提交 dev”的约束。

- `dev`：GitHub 默认分支，也是开发与集成入口。
- `main`：保留为经过明确批准的发布快照。Vercel Production Branch 建议配置为 `main`。
- 单 Agent 在干净的 `dev` 上小步开发。需要隔离或并行时，从最新 `dev` 创建短期分支或 worktree，最终回归 `dev`。
- 多个 Agent 不得同时修改同一文件。

开工命令：

```bash
git status --short --branch
git fetch origin --prune
git switch dev
git pull --ff-only origin dev
```

发现未提交变更或分叉时，先确认来源。禁止自动 `reset`、`stash`、force push 或覆盖用户改动。提交时显式列出路径，并在任务记录中保存验证命令和结果。

本次整合结果：`main@ebe4cc7` 是整合后 `dev@ed1887c` 的祖先；`trae/solo-agent-p6YsKQ@ed1887c` 与 `dev` 同指针，没有独有提交。整合使用 fast-forward 合并并推送到 `dev`，无冲突、无历史重写，远端短期分支暂未删除。审查时 `dev` 和 `main` 都没有 GitHub 分支保护；不要擅自更改远端规则，发布前由仓库管理员决定 `main` 的 PR/检查保护。

发布流程：完成 [路线图](ROADMAP.md) 的发布门槛 → 同一提交在 Preview 验收 → 用户明确批准 → 晋级 `main` → 验证 Production。代码回滚使用 revert 或 Vercel 已知部署版本；数据恢复使用预演后的迁移或备份方案。
