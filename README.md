# Isaac Sim PBD/XPBD/VBD Learning Lab

一个“从 0 到 1”的学习型工程：在 Isaac Sim 4.5 里用 **UsdGeom.PointInstancer** 自己实现粒子系统与约束求解（PBD → XPBD → VBD）。

## 你将学到什么
- 如何在 Isaac Sim 的 Kit runtime 内创建 USD stage，并用 PointInstancer 做粒子可视化
- 如何用纯 Python/numpy 维护粒子系统状态（x, v, inv_mass）
- 如何按阶段实现 PBD、XPBD、VBD 的最小可运行版本
- 如何写清晰可扩展的仿真架构（场景、系统、求解器、工具）

## 目录结构
- README.md
- docs/ (索引见 [docs/README.md](docs/README.md))
- src/isaac_pbd_lab/
- scripts/
- configs/
- tests/
- outputs/ (录屏/截图/日志输出目录)

## 快速开始（UI Script Editor）
1. 用 UI 启动 Isaac Sim 4.5
2. 打开 Script Editor
3. 运行 [scripts/run_pbd_chain.py](scripts/run_pbd_chain.py)

预期现象：一串小球组成的链条在重力下下垂摆动，第 0 个球固定不动。

## 快速开始（CLI）
你是以 root 方式运行 Isaac Sim，因此 CLI 推荐使用 `isaac-sim.sh --allow-root` 并指定 python 脚本：
- /isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=/cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_pbd_chain.py
- /isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=/cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_xpbd_chain.py
- /isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=/cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_vbd_chain.py

## 学习阶段路线（PBD → XPBD → VBD）
### Stage 1: PBD Chain
- 学习目标：实现距离约束的 PBD 投影；理解迭代次数与“硬度”的关系
- 需要改哪些文件：
  - [src/isaac_pbd_lab/sim/pbd.py](src/isaac_pbd_lab/sim/pbd.py)
  - [src/isaac_pbd_lab/sim/system.py](src/isaac_pbd_lab/sim/system.py)
  - [scripts/run_pbd_chain.py](scripts/run_pbd_chain.py)
- 运行命令：见上方“快速开始”
- 预期现象：链条下垂摆动，第 0 点固定；迭代次数越大越“硬”
- 最小验收：运行后视口可见链条，日志每秒输出一次

### Stage 2: XPBD Chain
- 学习目标：实现 lambda 累积与 compliance，引入 $\alpha = \frac{compliance}{dt^2}$
- 需要改哪些文件：
  - [src/isaac_pbd_lab/sim/xpbd.py](src/isaac_pbd_lab/sim/xpbd.py)
  - [scripts/run_xpbd_chain.py](scripts/run_xpbd_chain.py)
- 运行命令：见上方“快速开始”
- 预期现象：在相同 compliance 下，dt 改变“硬度”观感基本一致
- 最小验收：对比 $dt=1/30,1/60,1/120$，链条长度变化不明显

### Stage 3: VBD View
- 学习目标：从能量/变分角度理解约束，建立与 XPBD 的联系
- 需要改哪些文件：
  - [src/isaac_pbd_lab/sim/vbd.py](src/isaac_pbd_lab/sim/vbd.py)
  - [docs/12_vbd.md](docs/12_vbd.md)
- 运行命令：见上方“快速开始”
- 预期现象：至少可运行并输出残差/收敛指标
- 最小验收：日志输出最大约束残差随迭代下降

## 实验清单
见 [docs/20_experiments.md](docs/20_experiments.md)

## FAQ
常见问题见 [docs/90_faq.md](docs/90_faq.md)

## 说明
- 不依赖外部资产包
- 不需要 pip 安装第三方库
- 所有 prim 由脚本创建
- 默认复用已有 prim，可在配置里设置删除重建
