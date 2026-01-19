from dataclasses import dataclass  # 导入数据类装饰器
import numpy as np  # 导入数值计算库


@dataclass  # 使用数据类生成样板代码
class DistanceConstraint:  # 距离约束数据结构
    i: int  # 约束第一个粒子索引
    j: int  # 约束第二个粒子索引
    rest_length: float  # 约束的静止长度


def build_chain_constraints(n_particles, rest_length):  # 构建链条距离约束
    constraints = []  # 初始化约束列表
    for i in range(n_particles - 1):  # 遍历相邻粒子对
        constraints.append(DistanceConstraint(i, i + 1, rest_length))  # 添加距离约束
    return constraints  # 返回约束列表


def max_distance_residual(x, constraints):  # 计算最大距离残差
    max_res = 0.0  # 初始化最大残差
    for c in constraints:  # 遍历所有约束
        delta = x[c.i] - x[c.j]  # 计算位移向量
        dist = np.linalg.norm(delta)  # 计算当前距离
        res = abs(dist - c.rest_length)  # 计算残差
        if res > max_res:  # 如果更大则更新
            max_res = res  # 更新最大残差
    return float(max_res)  # 返回最大残差
