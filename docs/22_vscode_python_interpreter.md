# 22 VS Code 使用 Isaac Sim 伪解释器（规范做法）

## 目标
让 VS Code 能进行**代码跳转/补全/导入解析**，同时保持工程设置清晰、可共享、易维护。

## 推荐方案（规范）
**用包装脚本作为解释器**，并把设置写进 workspace。

### 1) 为什么不直接用 /isaac-sim/python.sh
- VS Code 期望的是一个“可执行的解释器路径”
- python.sh 有时会被当成普通脚本，识别不稳定
- 用包装脚本可以更稳、更清晰

### 2) 具体做法
#### 2.1 创建包装脚本
脚本位置：
- [scripts/python_isaacsim.sh](../scripts/python_isaacsim.sh)

它只做一件事：把所有参数转交给 /isaac-sim/python.sh。

#### 2.2 配置 VS Code
配置位置：
- [.vscode/settings.json](../.vscode/settings.json)

核心设置：
- `python.defaultInterpreterPath` 指向包装脚本
- `python.analysis.extraPaths` 包含 `${workspaceFolder}/src`

### 3) 这样做后有什么效果
- `import omni.*` / `import pxr` 的代码能被解析（前提是环境可见）
- `import isaac_pbd_lab` 会被正确识别
- 跳转、补全、悬停说明都更准确

## 常见问题
### Q1: 还是跳不进去 omni/pxr？
A: 把 Isaac Sim 的 site-packages 路径追加到 `python.analysis.extraPaths`。

如何找到路径：
- 运行 `/isaac-sim/python.sh -c "import sys; print(sys.path)"`

### Q2: 这个设置会影响运行吗？
A: 不会。它只影响 VS Code 的“分析器”，不影响你实际运行脚本。

## 最后检查清单
- [ ] 已创建 scripts/python_isaacsim.sh
- [ ] .vscode/settings.json 指向该脚本
- [ ] extraPaths 包含 ${workspaceFolder}/src
