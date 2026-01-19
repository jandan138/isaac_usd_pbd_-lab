import os  # 导入操作系统模块
import sys  # 导入系统模块
import numpy as np  # 导入数值计算库

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 获取工程根目录
SRC = os.path.join(ROOT, "src")  # 拼接源码目录
if SRC not in sys.path:  # 若源码路径未加入
    sys.path.insert(0, SRC)  # 插入到搜索路径

from isaac_pbd_lab.sim.constraints import DistanceConstraint  # 导入距离约束
from isaac_pbd_lab.sim.pbd import solve_constraints_pbd  # 导入 PBD 求解


def test_distance_constraint_projection():  # 测试距离约束投影
    x = np.array([[0.0, 0.0, 0.0], [0.2, 0.0, 0.0]], dtype=np.float32)  # 初始化位置
    inv_mass = np.array([0.0, 1.0], dtype=np.float32)  # 设置逆质量
    constraints = [DistanceConstraint(0, 1, 0.1)]  # 创建距离约束
    max_res = solve_constraints_pbd(x, inv_mass, constraints, iterations=10)  # 执行 PBD 求解
    dist = np.linalg.norm(x[0] - x[1])  # 计算距离
    assert abs(dist - 0.1) < 1e-4  # 断言距离满足约束
    assert max_res < 1e-4  # 断言残差足够小


if __name__ == "__main__":  # 入口判断
    test_distance_constraint_projection()  # 运行测试
    print("test_distance_constraint_projection: OK")  # 输出成功信息
