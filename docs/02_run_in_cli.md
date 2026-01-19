# 02 Run in CLI

本页只保留**稳定可执行**的命令。不可稳定执行的命令与原因已移至
[03_kit_simapp_and_run_modes.md](03_kit_simapp_and_run_modes.md)。

## 稳定运行（推荐）
使用 Isaac Sim 自带 Python + `SimulationApp` 启动 Kit：

- /isaac-sim/python.sh /cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_pbd_chain_python.py --headless-test
- /cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_pbd_chain_python.sh --headless-test

如需 smoke 验证 Python 模式是否执行：

- /cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_headless_smoke_python.sh
