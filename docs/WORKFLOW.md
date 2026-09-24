# 协作流程

## 分支策略

```
main                 ← 稳定发布，仅合并已验证的翻译
├── dev/resources    ← 跟随 IDEA 新版本更新英文资源
└── dev/translate    ← 日常翻译（从 main 或 dev/resources 拉取）
```

### 资源更新（dev/resources）

1. 安装目标版本 IDEA
2. 在 `dev/resources` 分支执行：
   ```powershell
   python scripts/l10n.py extract --force
   python scripts/l10n.py sync
   ```
3. 提交英文资源变更与 sync 产生的新增键
4. 合并到 `main`，通知翻译组执行 `sync`

### 日常翻译（dev/translate）

1. 从最新 `main` 合并
2. 运行 `python scripts/l10n.py sync` 获取新键
3. 按模块翻译，本地 `validate`
4. PR 到 `main`，由维护者 Review

### 发布

1. `main` 上运行 `validate --strict`
2. `build --version x.y.z`
3. 创建 Git Tag `vX.Y.Z`
4. 上传 `dist/*.jar` 到 Releases
5. 更新 `config/project.json` 中的 `untilBuild`（如有新版本）

## Issue 模板建议

**翻译认领**

- 模块 / 文件路径
- IDEA 版本
- 预计完成时间

**译文讨论**

- 英文原文
- 当前译文 / 建议译文
- 理由与截图（如有）

## 角色分工

| 角色 | 职责 |
|------|------|
| 维护者 | 合并 PR、发版、更新资源、维护术语表 |
| 翻译 | 按模块提交译文 |
| 审校 | Review 术语与语气，不要求会打包 |
| 资源同步 | 新版本 IDEA 发布后更新 `resources/en` |

## 沟通渠道（可自行补充）

- GitHub Issues：任务认领与译文讨论
- GitHub Discussions：规范与流程
- 即时群组：（待建立）

## 版本对应

在 README 或 Release 说明中注明：

- 语言包版本
- 测试通过的 IDEA 版本范围
- 基于的 `resources_en.jar` 提取日期
