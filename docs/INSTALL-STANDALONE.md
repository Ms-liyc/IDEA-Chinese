# 独立汉化安装指南（不依赖官方中文扩展）

本方案**不需要管理员权限**，**不需要**启用 JetBrains 官方 `Chinese (Simplified) Language Pack`。

## 一键安装

```powershell
# 1. 打包（维护者）
python scripts/l10n.py build --version 1.1.0

# 2. 安装到用户目录（普通用户权限）
.\scripts\install-standalone.ps1
```

安装脚本会：
- 将语言包解压到 `%APPDATA%\JetBrains\IntelliJIdea2025.3\plugins\idea-chinese\`
- 自动禁用官方 `com.intellij.zh` 扩展
- **不修改** `Program Files` 安装目录

## 手动安装

1. 下载 `releases/idea-chinese-standalone-1.1.0.zip`
2. 解压到：

```
%APPDATA%\JetBrains\IntelliJIdea2025.3\plugins\idea-chinese\
```

最终结构应为：

```
plugins\idea-chinese\lib\idea-chinese.jar
```

3. 在 IDEA 插件设置中**禁用**官方「Chinese (Simplified) Language Pack」
4. 确认「IntelliJ IDEA 独立中文语言包」**已启用**
5. `Ctrl+Alt+S` → **Appearance & Behavior → System Settings → Language and Region**
6. **Language** 选择 **Chinese (Simplified) 简体中文（独立版）**
7. **完整重启** IDEA

## 与旧版的区别

| 项目 | 旧版 1.0.x | 独立版 1.1.0+ |
|------|-----------|---------------|
| 依赖官方扩展 | 是（必须启用） | **否** |
| 安装方式 | 单 JAR 从磁盘安装 | 目录结构 + install 脚本 |
| languageBundle | 旧格式 | 对齐第三方可用格式 |
| 权限 | 普通用户 | 普通用户 |

## 验证

重启后左侧菜单应显示中文：
- **文件**（File）
- **设置**（Settings）
- **插件**（Plugins）

## 恢复官方汉化

1. 删除 `%APPDATA%\JetBrains\IntelliJIdea2025.3\plugins\idea-chinese\`
2. 从 `disabled_plugins.txt` 移除 `com.intellij.zh`（或运行旧版 fix-locale.ps1 的逆操作）
3. 启用官方中文语言包并重启
