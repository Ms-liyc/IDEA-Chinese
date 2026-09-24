# 贡献指南

感谢参与 IntelliJ IDEA 简体中文汉化！

## 如何开始

1. Fork 本仓库并克隆到本地
2. 阅读 [翻译规范](docs/TRANSLATION_GUIDE.md) 与 [术语表](glossary/terms.csv)
3. 按 README 完成 `extract` → `sync`
4. 在 `resources/zh-CN` 中提交翻译
5. 运行 `python scripts/l10n.py validate` 确保无缺失键
6. 发起 Pull Request

## Pull Request 要求

- **一事一 PR**：每条 PR 聚焦一个模块或主题（如「VCS 相关」「Run/Debug 面板」）
- **说明范围**：在 PR 描述中列出修改的文件或 Bundle 名称
- **保留占位符**：不得改动 `{0}`、`{1}` 等参数顺序
- **术语一致**：新译法请先对照 `glossary/terms.csv`
- **避免机翻直出**：通读上下文，保证语气符合 IDE 界面习惯

## 分工建议

| 模块 | 典型路径 | 说明 |
|------|----------|------|
| 菜单与动作 | `messages/ActionsBundle.properties` | 菜单项、工具栏 |
| 对话框 | `messages/*Dialog*.properties` | 弹窗与向导 |
| 检查项 | `inspectionDescriptions/` | HTML 说明 |
| 意图动作 | `intentionDescriptions/` | 快速修复说明 |
| 文件模板 | `fileTemplates/` | 新建文件模板描述 |

可在 Issues 中认领模块，避免多人重复翻译同一文件。

## 代码审查要点

维护者会检查：

1. 键是否完整、无多余键
2. 占位符是否与英文一致
3. 术语是否符合术语表
4. 是否有明显的机翻或歧义

## 行为准则

- 尊重不同翻译意见，以 Issue 讨论为准
- 不提交与翻译无关的大改动
- 不将本地 IDEA 安装路径或密钥写入仓库
