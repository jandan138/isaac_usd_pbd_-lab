# 02 Run in CLI

你是以 root 方式运行 Isaac Sim，因此在 Isaac Sim 安装目录执行：

- /isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=/cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_pbd_chain.py
- /isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=/cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_xpbd_chain.py
- /isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=/cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/run_vbd_chain.py

说明：
- 该方式会直接启动 Isaac Sim Kit，并运行指定脚本
- 若报错缺少 omni 模块，请确认使用 `isaac-sim.sh --allow-root` 启动
