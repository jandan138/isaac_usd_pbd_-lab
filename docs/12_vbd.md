# 12 VBD

## 视角
VBD（Variational/Optimization-Based Dynamics）从能量最小化角度理解约束，常与增广拉格朗日方法联系。

可以将 XPBD 看作某种“隐式/正则化”的约束求解步骤：
- 目标：最小化 $E(x) + \sum_k \lambda_k C_k(x) + \frac{1}{2\alpha} C_k(x)^2$
- 其中 $\alpha$ 与 compliance、$dt$ 对应

## 代码位置
- 求解器占位：[src/isaac_pbd_lab/sim/vbd.py](../src/isaac_pbd_lab/sim/vbd.py)

## 验收建议
- 打印残差随迭代下降
- 与 XPBD 的收敛曲线做对比

## TODO
- 推导具体的梯度与线性化
- 选择一个简化的能量最小化例子实现
