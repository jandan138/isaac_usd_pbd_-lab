# 03 Kit / SimulationApp / 运行方式对比

本页解释：
- 什么是 Kit
- 什么是 SimulationApp
- 为什么有些命令不能稳定进入 Python
- 稳定运行与不稳定运行的对比

## 1) Kit 是什么（通俗版）
Kit 可以理解为 Isaac Sim 的“程序内核/引擎”。它负责：
- 加载插件（extensions）
- 建立 USD Stage
- 渲染与事件循环
- 提供 `omni.*` 模块运行环境

没有启动 Kit，就无法使用 `omni.*`。

## 2) SimulationApp 是什么
`SimulationApp` 是一个“启动器/胶水”类：
- 在 Python 脚本里启动 Kit
- 配置 headless/渲染参数
- 提供 `update()` 和 `close()` 控制生命周期

因此：只要 Python 脚本被执行，`SimulationApp` 就能确保 Kit 启动成功。

## 3) 稳定运行的方式（推荐）
**Python 模式：**
- 用 `/isaac-sim/python.sh` 启动脚本
- 脚本内部创建 `SimulationApp`

示例命令：
- /isaac-sim/python.sh /cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_pbd_chain_python.py --headless-test
- /cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_pbd_chain_python.sh --headless-test

原理：
1. python.sh 确保使用 Isaac Sim 自带 Python 环境
2. 脚本运行 -> `SimulationApp` 启动 Kit
3. Kit 就绪 -> 执行你写的 PBD 逻辑

## 4) 不稳定运行方式（已弃用）
**Kit CLI 模式：**
- /isaac-sim/isaac-sim.sh --/app/pythonScript=...
- /isaac-sim/isaac-sim.sh --/app/exec=...

问题：
- 在 headless 场景下，`pythonScript` 或 `exec` **可能不会被触发**
- 表现为：日志出现 “Isaac Sim Full App is loaded”，但没有进入脚本逻辑
- 这类方式依赖 Kit 的启动阶段钩子，某些环境下无法稳定触发

## 5) 稳定方式 vs 不稳定方式（对比）
| 对比项 | Python 模式（稳定） | Kit CLI 模式（不稳定） |
| --- | --- | --- |
| 是否保证执行 Python 逻辑 | 是 | 否（可能不触发） |
| 进入脚本时机 | Python 进程启动即执行 | 依赖 Kit 启动钩子 |
| 适合 headless | 是 | 不稳定 |
| 推荐程度 | ✅ 推荐 | ❌ 已弃用 |

## 6) 结论
- **稳定运行请使用 Python 模式 + SimulationApp**
- Kit CLI 模式在 headless 环境可能不执行脚本，不再推荐
