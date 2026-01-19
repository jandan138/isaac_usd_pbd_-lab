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
