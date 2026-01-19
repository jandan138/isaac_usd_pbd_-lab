# 00 Overview

本项目目标：在 Isaac Sim 4.5 中用 **UsdGeom.PointInstancer** 实现一个“可视化 + 自定义求解器”的粒子系统学习工程。

你将逐步完成：
1. PBD 距离约束（链条）
2. XPBD（compliance + lambda 累积）
3. VBD 视角（能量/变分/增广拉格朗日）

整个工程强调：
- 结构清晰（场景、系统、求解器、工具）
- 纯净依赖（只用 USD/omni/numpy）
- 可复现运行（UI 与 CLI 两种方式）

文档索引见 [docs/README.md](README.md)
