# 90 FAQ

## Q: 提示找不到 omni / pxr 模块
A: 你必须在 Isaac Sim 内运行脚本（UI Script Editor 或 ./python.sh）。

## Q: 运行后没有任何动画
A: 确认运行了 [scripts/run_pbd_chain.py](../scripts/run_pbd_chain.py)；检查是否暂停了 `sim_running`。

## Q: dt 始终为 0
A: 某些情况下 timeline 未播放。脚本会自动回退到固定 dt=1/60。

## Q: root 权限运行问题
A: 你已经使用 --allow-root 启动 UI。CLI 也需要在同一环境下运行。

## Q: 视口没有球
A: 检查 Stage 是否被清空；检查路径 /World/Prototypes/Sphere 和 /World/Particles/Instancer 是否存在。

## Q: 启动日志看起来“启动了两次”
A: 通常是第一次启动过程中抛错退出（或你手动重试），所以日志里出现两段启动信息。
这次的具体原因是 `omni.timeline` 在 Isaac Sim 4.5 中没有 `get_delta_time()`，导致脚本报错退出。

解决办法：
- 已在代码中兼容 `get_time_codes_per_second()` / `get_time_step()`，没有该方法就回退到固定 $dt$。
- 如果仍不确定，可在命令里显式传 `--dt`，或先运行 headless 测试确认启动正常。
