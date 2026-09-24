<div align="center">

<img src="plugin/assets/logo.png" alt="屿宸网络科技工作室" width="360"/>

# IntelliJ IDEA 简体中文语言包

全量扫描 IDEA 界面 NLS 字符串，合并官方中文基线与社区增量翻译，一键安装后即可中文化菜单、设置、检查项与工具窗口。

**✨ 当前版本 1.0.1**

IDEA 2024.2+ · Language Pack · 约 12 万条基线 + 社区补齐词条

</div>

## 🌟 项目亮点

- **🎯 全量汉化** — 扫描 `lib/` 与 `plugins/` 全部模块 JAR，覆盖 messages / inspection / intention / templates
- **🔒 零侵入安装** — 纯语言包插件，不写 IDE 安装目录，无需管理员权限
- **🌏 官方基线** — 基于 `localization-zh.jar` 增量补齐，避免从零翻译
- **⚡ 安装即用** — 启用插件并在「语言与区域」选择简体中文，重启 IDE 生效
- **📊 缺口可视** — 内置 `l10n report` 工具，待译条目一目了然
- **📜 持续维护** — 屿宸网络科技工作室 / IDEA 汉化组

<div align="center">

![version](https://img.shields.io/badge/version-1.0.1-blue)
![type](https://img.shields.io/badge/type-Language%20Pack-green)
![license](https://img.shields.io/badge/license-MIT-lightgrey)
![locale](https://img.shields.io/badge/locale-zh--CN-orange)
![idea](https://img.shields.io/badge/IDEA-2024.2%2B-blue)

</div>

<div align="center">

说明：本插件仅替换界面文案，不修改 IDE 核心程序。请通过「从磁盘安装插件」安装。

**⚠️ 注意**：安装后建议禁用官方中文语言包以避免冲突；修改语言设置后请完整重启 IDE。

</div>

---

## 快速开始

### 环境要求

- Python 3.10+
- IntelliJ IDEA 2024.2 或更新版本

### 一键初始化

```powershell
git clone https://github.com/Ms-liyc/IDEA-Chinese.git
cd IDEA-Chinese
python scripts/l10n.py init --idea-path "D:\Program Files\JetBrains\IntelliJ IDEA 2025.3.1"
```

### 打包安装

```powershell
python scripts/l10n.py build --version 1.0.1
```

IDEA → **设置 → 插件 → 从磁盘安装插件** → 选择 `dist/com.chinese.idea.localization-1.0.1.jar`

## 常用命令

| 命令 | 说明 |
|------|------|
| `python scripts/l10n.py extract` | 全量提取英文资源 |
| `python scripts/l10n.py import-zh` | 导入官方中文基线 |
| `python scripts/l10n.py sync` | 同步新增键到 zh-CN |
| `python scripts/l10n.py report --output` | 生成缺口报告 |
| `python scripts/l10n.py validate` | 校验翻译完整性 |
| `python scripts/l10n.py build --version x.y.z` | 打包语言包 |

## 项目结构

```
├── config/project.json       # 项目配置
├── resources/zh-CN/          # 中文翻译（协作维护）
├── scripts/                  # 提取 / 同步 / 打包工具
├── plugin/                   # 插件元数据与 Logo
├── glossary/terms.csv        # 术语表
└── docs/                     # 协作文档
```

## 协作

欢迎提交 Issue / Pull Request。详见 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [docs/WORKFLOW.md](docs/WORKFLOW.md)。

## 联系

- **开发者**：屿宸网络科技工作室
- **邮箱**：lyc5202025@126.com
- **仓库**：[github.com/Ms-liyc/IDEA-Chinese](https://github.com/Ms-liyc/IDEA-Chinese)

## 许可

翻译基于 JetBrains 英文 UI 资源；社区译文以 MIT 协议贡献。
