import numpy as np  # 导入数值计算库

from .constraints import build_chain_constraints  # 导入约束构建函数
from .pbd import solve_constraints_pbd  # 导入 PBD 求解
from .xpbd import solve_constraints_xpbd, init_lambdas  # 导入 XPBD 求解与 lambda 初始化
from .vbd import solve_constraints_vbd  # 导入 VBD 求解


class ParticleSystem:  # 粒子系统类
    def __init__(self, n_particles, rest_length, gravity, radius, iterations,  # 初始化参数
                 solver_type="pbd", compliance=0.0, damping=0.0):  # 继续初始化参数
        self.n_particles = n_particles  # 粒子数量
        self.rest_length = rest_length  # 约束静止长度
        self.gravity = np.array(gravity, dtype=np.float32)  # 重力向量
        self.radius = radius  # 粒子半径
        self.iterations = iterations  # 约束迭代次数
        self.solver_type = solver_type  # 求解器类型
        self.compliance = compliance  # XPBD 软度参数
        self.damping = float(damping)  # 阻尼系数

        self.positions = np.zeros((n_particles, 3), dtype=np.float32)  # 初始化位置数组
        self.velocities = np.zeros((n_particles, 3), dtype=np.float32)  # 初始化速度数组
        self.inv_mass = np.ones((n_particles,), dtype=np.float32)  # 初始化逆质量
        self.inv_mass[0] = 0.0  # 固定第 0 个粒子为锚点

        # init chain along x  # 沿 x 轴初始化链条
        start = np.array([0.0, 1.0, 0.0], dtype=np.float32)  # 设置起始位置
        for i in range(n_particles):  # 遍历每个粒子
            self.positions[i] = start + np.array([i * rest_length, 0.0, 0.0], dtype=np.float32)  # 设置初始位置

        self.constraints = build_chain_constraints(n_particles, rest_length)  # 构建链条约束
        self.lambdas = init_lambdas(self.constraints)  # 初始化 XPBD lambda

    def step(self, dt):  # 进行单步仿真
        x_old = self.positions.copy()  # 保存上一帧位置

        # external forces  # 外力作用
        self.velocities += dt * self.gravity  # 施加重力到速度
        x_pred = self.positions + dt * self.velocities  # 预测位置

        # constraints  # 约束求解
        if self.solver_type == "pbd":  # PBD 分支
            max_residual = solve_constraints_pbd(  # 调用 PBD 求解
                x_pred, self.inv_mass, self.constraints, self.iterations  # 传入求解参数
            )  # 结束 PBD 求解
        elif self.solver_type == "xpbd":  # XPBD 分支
            max_residual = solve_constraints_xpbd(  # 调用 XPBD 求解
                x_pred, self.inv_mass, self.constraints,  # 传入位置和约束
                self.lambdas, self.compliance, dt, self.iterations  # 传入 lambda 和参数
            )  # 结束 XPBD 求解
        elif self.solver_type == "vbd":  # VBD 分支
            max_residual = solve_constraints_vbd(  # 调用 VBD 求解
                x_pred, self.inv_mass, self.constraints, dt, self.iterations  # 传入求解参数
            )  # 结束 VBD 求解
        else:  # 其他类型回退
            max_residual = solve_constraints_pbd(  # 回退到 PBD
                x_pred, self.inv_mass, self.constraints, self.iterations  # 传入求解参数
            )  # 结束回退求解

        # simple ground projection (keep fixed particles anchored)  # 简单地面投影并保持锚点
        x_pred[:, 1] = np.maximum(x_pred[:, 1], self.radius)  # 限制 y 不低于地面
        fixed_mask = self.inv_mass == 0.0  # 获取固定粒子掩码
        if np.any(fixed_mask):  # 若存在固定粒子
            x_pred[fixed_mask] = x_old[fixed_mask]  # 还原固定粒子位置

        # velocity update  # 更新速度
        self.velocities[:] = (x_pred - x_old) / max(dt, 1e-6)  # 使用位置差更新速度

        # simple velocity damping to reduce oscillation  # 速度阻尼降低震荡
        if self.damping > 0.0:  # 若启用阻尼
            damp_factor = max(0.0, 1.0 - self.damping * dt)  # 计算阻尼因子
            self.velocities *= damp_factor  # 应用阻尼

        # write back  # 写回位置
        self.positions[:] = x_pred  # 更新位置数组

        return max_residual  # 返回最大残差
