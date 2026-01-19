import os  # 导入操作系统模块

from .utils.log import log_warn  # 导入警告日志函数


def default_config():  # 返回默认配置
    return {  # 配置字典
        "n_particles": 50,  # 粒子数量
        "rest_length": 0.05,  # 约束静止长度
        "radius": 0.02,  # 粒子半径
        "gravity": [0.0, -9.81, 0.0],  # 重力向量
        "iterations": 20,  # 约束迭代次数
        "fixed_dt": 1.0 / 60.0,  # 固定时间步长
        "compliance": 0.0,  # XPBD 软度参数
        "damping": 0.5,  # 速度阻尼系数
        "prototype_path": "/World/Prototypes/Sphere",  # 原型球体路径
        "instancer_path": "/World/Particles/Instancer",  # 点实例器路径
        "rebuild_usd_prims": False,  # 是否重建 USD 原语
    }  # 返回配置字典


def _parse_value(value):  # 解析配置值
    value = value.strip()  # 去掉首尾空白
    if value.startswith("[") and value.endswith("]"):  # 解析数组
        inner = value[1:-1].strip()  # 获取数组内部
        if not inner:  # 空数组
            return []  # 返回空列表
        parts = [p.strip() for p in inner.split(",")]  # 分割元素
        return [float(p) for p in parts]  # 转为浮点数列表
    try:  # 尝试数值解析
        if "." in value or "e" in value.lower():  # 判断浮点格式
            return float(value)  # 返回浮点数
        return int(value)  # 返回整数
    except Exception:  # 解析失败
        if value.lower() in ("true", "false"):  # 布尔类型
            return value.lower() == "true"  # 返回布尔值
        return value  # 原样返回字符串


def load_yaml_like(path):  # 读取类似 YAML 的配置文件
    cfg = default_config()  # 获取默认配置
    if not os.path.exists(path):  # 文件不存在
        log_warn(f"Config not found: {path}, using defaults.")  # 输出警告
        return cfg  # 返回默认配置

    with open(path, "r", encoding="utf-8") as f:  # 打开配置文件
        for line in f:  # 逐行读取
            line = line.strip()  # 去掉空白
            if not line or line.startswith("#"):  # 跳过空行和注释
                continue  # 继续下一行
            if ":" not in line:  # 没有键值分隔符
                continue  # 继续下一行
            key, val = line.split(":", 1)  # 拆分键值
            cfg[key.strip()] = _parse_value(val)  # 解析并写入配置
    return cfg  # 返回最终配置
