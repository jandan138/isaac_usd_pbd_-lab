# 11 XPBD

## 核心思想
XPBD 在 PBD 基础上引入 compliance 与 lambda 累积，使“硬度”对 $dt$ 不敏感。

定义：
$$\alpha = \frac{compliance}{dt^2}$$

对每个约束维护一个 $\lambda$，迭代中更新：
$$\Delta \lambda = \frac{-C - \alpha \lambda}{\sum w_i ||\nabla_i||^2 + \alpha}$$
$$\lambda \leftarrow \lambda + \Delta \lambda$$

然后用 $\Delta \lambda$ 计算位置修正。

## 代码位置
- 求解器：[src/isaac_pbd_lab/sim/xpbd.py](../src/isaac_pbd_lab/sim/xpbd.py)

## 验收建议
- 在相同 compliance 下，分别使用 $dt=1/30,1/60,1/120$，链条“硬度观感”应基本一致。

## TODO
- 实现 lambda 持久化存储
- 与 PBD 比较残差收敛
