import numpy as np  # 导入数值计算库

from .constraints import max_distance_residual  # 导入残差计算函数


def solve_constraints_pbd(x_pred, inv_mass, constraints, iterations):  # 进行 PBD 约束投影
    for _ in range(iterations):  # 迭代多次提高刚性
        for c in constraints:  # 遍历每个约束
            w_i = inv_mass[c.i]  # 读取粒子 i 的逆质量
            w_j = inv_mass[c.j]  # 读取粒子 j 的逆质量
            if w_i == 0.0 and w_j == 0.0:  # 两点都固定则跳过
                continue  # 跳过该约束

            delta = x_pred[c.i] - x_pred[c.j]  # 计算位移向量
            dist = np.linalg.norm(delta)  # 计算当前距离
            if dist < 1e-8:  # 距离过小则跳过
                continue  # 避免除零

            C = dist - c.rest_length  # 计算约束函数值
            grad_i = delta / dist  # 计算粒子 i 的梯度
            grad_j = -grad_i  # 计算粒子 j 的梯度

            denom = w_i * np.dot(grad_i, grad_i) + w_j * np.dot(grad_j, grad_j)  # 计算分母
            if denom < 1e-8:  # 分母过小则跳过
                continue  # 避免不稳定

            lam = -C / denom  # 计算拉格朗日乘子

            if w_i > 0.0:  # 若粒子 i 可动
                x_pred[c.i] += w_i * lam * grad_i  # 修正粒子 i 位置
            if w_j > 0.0:  # 若粒子 j 可动
                x_pred[c.j] += w_j * lam * grad_j  # 修正粒子 j 位置

    return max_distance_residual(x_pred, constraints)  # 返回最大残差
