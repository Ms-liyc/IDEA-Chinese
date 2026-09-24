# 翻译规范

## 基本原则

1. **准确**：忠实原意，不增删功能含义
2. **简洁**：IDE 界面空间有限，避免冗长
3. **一致**：同一概念全项目统一译法（见术语表）
4. **可本地化**：保留 `{0}` 等占位符，不硬编码数字或单位

## 语气与风格

- 使用现代简体中文，避免港台用语
- 按钮、菜单项：动词或动宾短语（如「保存」「运行配置」）
- 设置项：名词或名词短语（如「编辑器」「代码风格」）
- 提示信息：陈述句，必要时使用「请…」

## 常见译法

| 英文 | 推荐译法 | 避免 |
|------|----------|------|
| Settings | 设置 | 设定、配置（作菜单名时） |
| Preferences | 偏好设置 | — |
| Plugin | 插件 | 外挂 |
| Inspection | 检查 | 视察 |
| Intention | 意图动作 | 意向 |
| Refactor | 重构 | 重构代码（冗余） |
| Debug | 调试 | — |
| Run | 运行 | 执行（与 Execute 区分时再用「执行」） |
| Commit | 提交 | — |
| Branch | 分支 | — |

完整列表见 [glossary/terms.csv](../glossary/terms.csv)。

## properties 文件

- 编码：**UTF-8**
- 键名：与英文文件完全一致，禁止修改
- 值：可含 `\n` 换行；打包时会自动转为 `\uXXXX`
- 注释行 `# ...` 可保留英文或补充翻译说明

示例：

```properties
# 运行当前配置
action.run.text=运行
action.run.description=运行所选运行/调试配置
```

## HTML 描述文件

`inspectionDescriptions`、`intentionDescriptions`、`fileTemplates` 等目录下的 HTML：

- 保持原有 HTML 标签结构
- 正文翻译为中文，代码示例不翻译
- 文件编码 UTF-8

## 不宜翻译的内容

- 类名、方法名、快捷键（如 `Ctrl+Alt+S`）
- 协议名、文件扩展名（如 `.gitignore`）
- 品牌名 JetBrains、IntelliJ IDEA
- 已广泛使用的英文术语（如 Git、Docker），首次出现可加中文注释

## 质量自检

提交前请确认：

- [ ] 该文件所有键均有译文
- [ ] 占位符 `{n}` 与英文一致
- [ ] 无错别字与多余空格
- [ ] 与术语表无冲突
