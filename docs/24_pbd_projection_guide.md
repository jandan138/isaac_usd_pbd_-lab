# 24 PBD 约束投影与代码解读（新手版）

本文目标：让你看懂 [src/isaac_pbd_lab/sim/pbd.py](../src/isaac_pbd_lab/sim/pbd.py) 里**约束函数**和**投影**是怎么用的，以及这些数学概念如何对应到具体代码。读完后你应该能把“公式 → 代码 → 行为”串起来。

---

## 一、先用一句话理解 PBD 投影

**PBD 的做法是：先让粒子自由走一步，再把它们“拉回到满足约束的位置”。**

这个“拉回去”的动作，就叫 **投影（Projection）**。

---

## 二、约束函数是什么？（通俗版）

约束函数就是一条“必须为 0 的规则”。

比如距离约束：
- 你希望粒子 i 和 j 的距离等于 $L$
- 那么约束函数就是：

$$C(x) = ||x_i - x_j|| - L$$

当 $C(x) = 0$，说明距离刚好是 L。
当 $C(x) > 0$，说明距离太长。
当 $C(x) < 0$，说明距离太短。

**PBD 的目标：把 $C(x)$ 拉回到 0。**

---

## 三、投影的核心公式（距离约束）

距离约束的投影公式：

$$\lambda = -\frac{C}{w_i ||\nabla_i||^2 + w_j ||\nabla_j||^2}$$

$$x_i \leftarrow x_i + w_i \lambda \nabla_i$$

$$x_j \leftarrow x_j + w_j \lambda \nabla_j$$

解释：
- $\lambda$：这一次要“拉回去多少”
- $w_i, w_j$：逆质量（固定点为 0，意味着不动）
- $\nabla_i$：约束对粒子 i 的方向（也就是梯度）

**直觉**：
- $\lambda$ 越大，调整越多
- 固定点的 $w=0$，所以不会移动

---

## 四、公式如何体现在代码里

文件：[src/isaac_pbd_lab/sim/pbd.py](../src/isaac_pbd_lab/sim/pbd.py)

### 1) 约束函数 $C(x)$ 的代码对应

```python
C = dist - c.rest_length
```
- `dist` 是 $||x_i - x_j||$
- `c.rest_length` 是 $L$
- 所以 `C` 就是 $C(x)$

### 2) 梯度 $\nabla$ 的代码对应

```python
grad_i = delta / dist
grad_j = -grad_i
```
- `delta = x_i - x_j`
- `grad_i` 是单位方向向量
- `grad_j` 方向相反

### 3) 分母 $w_i ||\nabla_i||^2 + w_j ||\nabla_j||^2$

```python
denom = w_i * np.dot(grad_i, grad_i) + w_j * np.dot(grad_j, grad_j)
```
- 因为 `grad` 是单位向量，所以它的平方通常是 1
- 但代码里仍然按通用形式写，便于以后扩展

### 4) 拉回步长 $\lambda$

```python
lam = -C / denom
```

### 5) 更新位置

```python
x_pred[c.i] += w_i * lam * grad_i
x_pred[c.j] += w_j * lam * grad_j
```

如果某个粒子的 `w=0`，就不会动。

---

## 五、为什么要迭代多次？

PBD 不是一次就“拉到完美”，而是多次迭代逐步逼近。

代码里是：
```python
for _ in range(iterations):
    for c in constraints:
        ...
```

- `iterations` 越大，约束越“硬”
- `iterations` 越小，约束越“软”

---

## 六、为什么要检查 dist < 1e-8？

```python
if dist < 1e-8:
    continue
```

这是为了避免除以 0：
- 当两个粒子几乎重合时，`dist` 太小
- `delta / dist` 会导致数值爆炸

所以直接跳过，避免不稳定。

---

## 七、用“人话”把整个函数描述一遍

`solve_constraints_pbd()` 做了这几件事：
1. 重复多次（迭代）
2. 对每一条约束：
   - 算出当前距离偏差
   - 算出“要往哪个方向推”
   - 算出“要推多大力”
   - 把位置拉回去

这就是“约束投影”的全过程。

---

## 八、一个最小示例（帮助理解）

假设只有两个粒子：
- 目标距离是 1
- 实际距离是 1.2

那么：
- $C = 1.2 - 1 = 0.2$
- 算出 $\lambda$ 后，把两边往中间拉
- 距离逐渐变回 1

这就是 PBD 的直觉。

---

## 九、你读完应该能回答的问题

- 约束函数 $C(x)$ 在代码里是哪一行？
- $\lambda$ 的作用是什么？
- 为什么固定点不会动？
- 为什么要迭代多次？

如果你能答出来，就说明你已经理解了核心逻辑。
