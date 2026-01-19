# 10 PBD

## 距离约束
对粒子 $i,j$：
$$C(x) = ||x_i - x_j|| - L = 0$$

梯度：
$$\nabla_{x_i} C = \frac{x_i - x_j}{||x_i-x_j||}, \quad \nabla_{x_j} C = -\nabla_{x_i} C$$

质量加权投影：
$$\lambda = -\frac{C}{w_i ||\nabla_i||^2 + w_j ||\nabla_j||^2}$$
$$\Delta x_i = w_i \lambda \nabla_i, \quad \Delta x_j = w_j \lambda \nabla_j$$

## 代码位置
- 求解器：[src/isaac_pbd_lab/sim/pbd.py](../src/isaac_pbd_lab/sim/pbd.py)
- 粒子系统：[src/isaac_pbd_lab/sim/system.py](../src/isaac_pbd_lab/sim/system.py)

## TODO
- 增加更多约束类型
- 增加碰撞与摩擦
