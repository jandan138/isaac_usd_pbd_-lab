# 01 Run in UI (Script Editor)

## 步骤
1. 启动 Isaac Sim 4.5（UI 模式）
2. 打开 Script Editor
3. 运行 [scripts/run_pbd_chain.py](../scripts/run_pbd_chain.py)

## 预期现象
- 视口中出现一串球形粒子
- 第 0 个粒子固定，其余在重力下下垂摆动
- Console 每秒输出 fps/dt/粒子数/第一粒子位置/最大残差

## 可选
- 修改 [configs/default.yaml](../configs/default.yaml) 中的参数
- 在 [scripts/run_pbd_chain.py](../scripts/run_pbd_chain.py) 中切换 solver 类型
