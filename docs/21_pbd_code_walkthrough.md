# 21 PBD 代码通读指南（新手版）

本文目标：让你**从零基础**也能完整读懂本项目的 PBD 模拟代码。内容包含：
- 阅读顺序（从入口到求解器）
- 每个文件的作用与关键变量
- 你应该重点理解的概念
- 每一段代码如何串起来
- 常见困惑与自检问题

> 建议你准备两件事：
> 1) 打开 VS Code 的搜索（Ctrl+Shift+F）
> 2) 打开本文，按“阅读顺序”逐段跟读

---

## 一、阅读顺序（强烈推荐）

**第 1 遍：只看整体结构**
1. 项目入口与运行方式：
   - [README.md](../README.md)
   - [docs/01_run_in_ui.md](01_run_in_ui.md)
   - [docs/02_run_in_cli.md](02_run_in_cli.md)

2. 场景与渲染：
   - [src/isaac_pbd_lab/usd_scene.py](../src/isaac_pbd_lab/usd_scene.py)

3. 程序入口与主循环：
   - [scripts/run_pbd_chain.py](../scripts/run_pbd_chain.py)
   - [scripts/run_pbd_chain_python.py](../scripts/run_pbd_chain_python.py)

4. 应用层封装：
   - [src/isaac_pbd_lab/app.py](../src/isaac_pbd_lab/app.py)

5. 物理系统与求解器：
   - [src/isaac_pbd_lab/sim/system.py](../src/isaac_pbd_lab/sim/system.py)
   - [src/isaac_pbd_lab/sim/constraints.py](../src/isaac_pbd_lab/sim/constraints.py)
   - [src/isaac_pbd_lab/sim/pbd.py](../src/isaac_pbd_lab/sim/pbd.py)

6. 了解参数：
   - [configs/default.yaml](../configs/default.yaml)
   - [src/isaac_pbd_lab/config.py](../src/isaac_pbd_lab/config.py)

**第 2 遍：逐行跟读**
- 从 [scripts/run_pbd_chain_python.py](../scripts/run_pbd_chain_python.py) 开始，顺着调用链一路读到 `pbd.py`。

**第 3 遍：带着问题读**
- 本文每节末尾都有“自检问题”，你可以直接回答来验证理解程度。

---

## 二、你必须先理解的 3 个核心概念

### 1) 粒子系统 = 状态 + 规则
- 状态：位置 `x`、速度 `v`、质量 `inv_mass`
- 规则：重力、约束投影、地面投影、阻尼

### 2) 约束投影（PBD）
PBD 的核心思想是：
- 先“自由运动”得到预测位置 `x_pred`
- 然后把 `x_pred` 拉回到满足约束的“合法位置”

### 3) USD 可视化只是“显示结果”
- 物理更新在 numpy 数组里
- 结果通过 `set_instancer_positions()` 写回 USD

---

## 三、入口文件：如何启动程序

### 1) [scripts/run_pbd_chain_python.py](../scripts/run_pbd_chain_python.py)
**作用**：最稳定的 CLI 入口（推荐）

你要关注：
- `SimulationApp(...)`：启动 Kit，保证 `omni.*` 可用
- `load_yaml_like()`：加载配置参数
- `PbdApp(...)`：创建应用对象
- headless 循环：每一帧调用 `app.step_once()`

**阅读方式**：先理解它只是“启动器”，它不会做物理，只负责**生命周期与循环**。

**自检问题**：
- 程序每一帧是在哪个 for 循环里推进的？
- 入口文件本身有没有任何约束求解逻辑？

### 2) [scripts/run_pbd_chain.py](../scripts/run_pbd_chain.py)
**作用**：Kit CLI 入口（不如 Python 入口稳定）

你要关注：
- `_run_headless()`：订阅 Kit 的更新事件
- `app.step_once()`：真正的物理步进仍在 `PbdApp` 中

**自检问题**：
- 这里是否会创建 `SimulationApp`？
- `app.step_once()` 被谁调用？

---

## 四、配置系统：参数从哪来

### 1) [configs/default.yaml](../configs/default.yaml)
这是你调参的主入口，重要字段：
- `n_particles`：粒子数
- `rest_length`：相邻粒子距离
- `gravity`：重力向量
- `iterations`：约束迭代次数（越大越“硬”）
- `fixed_dt`：没有 timeline 时的步长
- `damping`：阻尼，减少来回摆动

### 2) [src/isaac_pbd_lab/config.py](../src/isaac_pbd_lab/config.py)
`load_yaml_like()` 会把 YAML 读成字典，然后传给 `PbdApp`。

**自检问题**：
- 改 `damping` 会影响哪个文件里的哪行？
- `fixed_dt` 在什么时候会被用到？

---

## 五、应用层：把系统接到 USD

### [src/isaac_pbd_lab/app.py](../src/isaac_pbd_lab/app.py)
这是**最重要的“连接层”**，它把“物理”和“显示”连起来。

核心流程：
1. 初始化 `ParticleSystem`
2. 创建 USD PointInstancer
3. 每帧更新：
   - `system.step(dt)` 更新物理
   - `set_instancer_positions(...)` 写回 USD

你要重点理解的方法：
- `step_once()`：每一帧物理推进的核心入口
- `_get_dt()`：从 timeline 获取 dt（没有则回退）

**自检问题**：
- 哪一行把 numpy 位置写回到 USD？
- `step_once()` 里是否直接求解约束？

---

## 六、场景与渲染：粒子如何显示成小球

### [src/isaac_pbd_lab/usd_scene.py](../src/isaac_pbd_lab/usd_scene.py)
这里的关键点是 `UsdGeom.PointInstancer`。

理解要点：
- `build_pointinstancer()`：创建一个球体原型 + 点实例器
- `set_instancer_positions()`：把位置数组写到 USD

**你必须牢记**：
- 所有物理计算在 numpy 中完成
- USD 只负责显示（“最后一步渲染”）

**自检问题**：
- 如果你把 `set_instancer_positions()` 注释掉，会发生什么？
- `prototype_path` 和 `instancer_path` 由哪个配置控制？

---

## 七、物理系统：粒子状态与步进

### [src/isaac_pbd_lab/sim/system.py](../src/isaac_pbd_lab/sim/system.py)
这是“物理层”的核心。你只要读懂 `step()`，就理解了整个 PBD 过程。

### 1) 初始化部分（`__init__`）
你要关注这些数组：
- `self.positions`：粒子位置，形状是 `(N, 3)`
- `self.velocities`：粒子速度
- `self.inv_mass`：逆质量（0 = 固定点）

关键行为：
- `self.inv_mass[0] = 0.0`：把第 0 个粒子固定
- 位置初始化沿 x 轴展开

**自检问题**：
- 固定点的索引是多少？它初始位置在哪？
- 如果把 `inv_mass[0]` 改成 1，会发生什么？

### 2) 步进部分（`step(dt)`）
**完整顺序如下**：
1. 保存旧位置 `x_old`
2. 重力作用到速度
3. 预测位置 `x_pred = x + v * dt`
4. 约束投影（PBD / XPBD / VBD 任选）
5. 地面投影（`y >= radius`）
6. 固定点回写（保证 anchor 不动）
7. 速度更新 `v = (x_pred - x_old) / dt`
8. 阻尼
9. 写回 `self.positions`

**重要提醒**：
- 本项目把 **Y 轴当作竖直方向**
- “地面”是 `y = radius` 的 XZ 平面
- 如果你在 Isaac Sim 看到 XY 网格，那是默认坐标系（Z 向上），与代码不一致

**自检问题**：
- “预测位置”是哪一行计算的？
- 为什么固定点必须在地面投影之后回写？

---

## 八、约束定义：链条约束怎么来的

### [src/isaac_pbd_lab/sim/constraints.py](../src/isaac_pbd_lab/sim/constraints.py)
这里只定义了一种约束：相邻粒子距离固定。

关键函数：
- `build_chain_constraints(n_particles, rest_length)`
- `DistanceConstraint(i, j, rest_length)`

这说明：
- 只有“距离约束”，没有弯曲约束、没有自碰撞约束
- 链条只是“长度不变”的一维结构

**自检问题**：
- 约束里保存了哪些字段？
- 如果把 `rest_length` 改大，链条会变成什么形状？

---

## 九、PBD 求解器：距离约束怎么被满足

### [src/isaac_pbd_lab/sim/pbd.py](../src/isaac_pbd_lab/sim/pbd.py)
这是最核心的数学部分。

### 1) 约束形式
距离约束：
$$C(x) = ||x_i - x_j|| - L = 0$$

梯度：
$$\nabla_{x_i} C = \frac{x_i - x_j}{||x_i - x_j||},\quad \nabla_{x_j} C = -\nabla_{x_i} C$$

投影步：
$$\lambda = -\frac{C}{w_i ||\nabla_i||^2 + w_j ||\nabla_j||^2}$$
$$x_i \leftarrow x_i + w_i \lambda \nabla_i,\quad x_j \leftarrow x_j + w_j \lambda \nabla_j$$

### 2) 代码对应关系
在 `solve_constraints_pbd()` 里：
- `delta` 是 $x_i - x_j$
- `dist` 是 $||x_i - x_j||$
- `C` 是约束值
- `grad_i / grad_j` 是梯度
- `lam` 是投影步长

### 3) 迭代的意义
PBD 不一次求完，而是“多次拉回”。
`iterations` 越大，越接近刚性约束。

**自检问题**：
- `lam` 是在哪一行计算的？
- 为什么要判断 `dist < 1e-8`？

---

## 十、常见现象解释

### 1) 为什么会出现“两条线”或 V 形
因为没有自碰撞，链条可以折叠并贴地，视觉上像两条线。

### 2) 为什么一直来回摆动
无阻尼时能量不会衰减，所以会持续振荡。

### 3) 为什么固定点不动
`inv_mass[0] = 0`，并且地面投影后固定点被回写。

---

## 十一、阅读建议：从“变量流动”理解逻辑

只盯住这三个变量流动：
- `positions`：从初始化 → 预测 → 约束投影 → 写回
- `velocities`：重力加速 → 由位置差更新 → 阻尼
- `constraints`：从生成 → 在 PBD 里逐条投影

你只要把这三条线看清楚，就能理解整个系统。

---

## 十二、动手实验（读完后建议做）

1) 改 `iterations`：观察刚性变化
2) 改 `gravity`：观察方向变化
3) 改 `rest_length`：观察链条长度变化
4) 改 `damping`：观察摆动衰减

---

## 十三、快速复盘（30 秒）

一句话总结：
**入口负责循环，`PbdApp` 负责连接 USD，`ParticleSystem.step()` 负责物理，`pbd.py` 负责约束投影。**

如果你能按这句话从代码里找到对应位置，就已经理解了 80%。

---

## 十四、继续学习的下一步

1) 自碰撞：为粒子之间增加最小距离约束
2) 弯曲约束：加入链条弯曲约束，让形态更像绳子
3) XPBD：在 [src/isaac_pbd_lab/sim/xpbd.py](../src/isaac_pbd_lab/sim/xpbd.py) 实现 `lambda` 累积

---

## 十五、你可以用这份检查表自测

- [ ] 我能从入口文件找到每帧调用 `step_once()` 的位置
- [ ] 我能解释 `x_pred` 与 `x_old` 的区别
- [ ] 我知道 `inv_mass=0` 表示固定点
- [ ] 我知道地面投影是 `y >= radius`
- [ ] 我知道 USD 只是显示层
- [ ] 我能定位 `solve_constraints_pbd()` 的核心公式

如果全部打勾，你已经完成入门。