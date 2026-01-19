from pxr import UsdGeom, Gf  # 导入 USD 几何与数学类型

from .utils.log import log_error, log_info  # 导入日志函数

try:  # 尝试导入 omni.usd
    import omni.usd  # 导入 USD 上下文接口
except Exception as exc:  # 捕获导入异常
    log_error("omni.usd not available. Run inside Isaac Sim/Kit.")  # 输出错误提示
    raise  # 抛出异常


def get_or_create_stage():  # 获取或创建 USD Stage
    ctx = omni.usd.get_context()  # 获取 USD 上下文
    stage = ctx.get_stage()  # 获取当前 Stage
    if stage is None:  # 若不存在 Stage
        ctx.new_stage()  # 创建新 Stage
        stage = ctx.get_stage()  # 重新获取 Stage
    if stage is None:  # 若仍不存在
        raise RuntimeError("Failed to create or get USD stage.")  # 抛出错误
    return stage  # 返回 Stage


def ensure_xform(stage, path):  # 确保 Xform 节点存在
    prim = stage.GetPrimAtPath(path)  # 获取指定路径 prim
    if prim and prim.IsValid():  # 若 prim 有效
        return prim  # 返回已有 prim
    return stage.DefinePrim(path, "Xform")  # 创建并返回 Xform prim


def build_pointinstancer(stage, positions_np, prototype_path, instancer_path, radius,  # 构建 PointInstancer
                         rebuild=False, set_orientations=True, set_scales=True):  # 继续参数说明
    # Parents  # 创建父节点
    ensure_xform(stage, "/World")  # 确保 /World 存在
    ensure_xform(stage, "/World/Prototypes")  # 确保 /World/Prototypes 存在
    ensure_xform(stage, "/World/Particles")  # 确保 /World/Particles 存在

    # Optional rebuild  # 可选重建
    if rebuild:  # 若启用重建
        if stage.GetPrimAtPath(instancer_path).IsValid():  # 若实例器存在
            stage.RemovePrim(instancer_path)  # 删除实例器
        if stage.GetPrimAtPath(prototype_path).IsValid():  # 若原型存在
            stage.RemovePrim(prototype_path)  # 删除原型

    # Prototype sphere  # 原型球体
    sphere_prim = stage.GetPrimAtPath(prototype_path)  # 获取原型 prim
    if not sphere_prim or not sphere_prim.IsValid():  # 若原型无效
        sphere = UsdGeom.Sphere.Define(stage, prototype_path)  # 创建球体原型
    else:  # 原型有效
        sphere = UsdGeom.Sphere(sphere_prim)  # 获取球体对象
    sphere.CreateRadiusAttr(radius)  # 设置球体半径

    # PointInstancer  # 点实例器
    instancer_prim = stage.GetPrimAtPath(instancer_path)  # 获取实例器 prim
    if not instancer_prim or not instancer_prim.IsValid():  # 若实例器无效
        instancer = UsdGeom.PointInstancer.Define(stage, instancer_path)  # 创建实例器
    else:  # 实例器有效
        instancer = UsdGeom.PointInstancer(instancer_prim)  # 获取实例器对象

    try:  # 尝试设置原型关联
        instancer.CreatePrototypesRel().SetTargets([sphere.GetPrim().GetPath()])  # 绑定原型路径
    except Exception as exc:  # 捕获设置异常
        log_error(f"Failed to set prototypes on {instancer_path}: {exc}")  # 输出错误信息
        raise  # 抛出异常

    # protoIndices  # 设置原型索引
    proto_indices = [0] * positions_np.shape[0]  # 创建索引列表
    instancer.CreateProtoIndicesAttr().Set(proto_indices)  # 写入索引属性

    if set_orientations:  # 是否设置朝向
        orientations = [Gf.Quath(1.0, Gf.Vec3h(0.0, 0.0, 0.0))] * positions_np.shape[0]  # 创建朝向数组
        instancer.CreateOrientationsAttr().Set(orientations)  # 写入朝向属性

    if set_scales:  # 是否设置缩放
        scales = [Gf.Vec3f(1.0, 1.0, 1.0)] * positions_np.shape[0]  # 创建缩放数组
        instancer.CreateScalesAttr().Set(scales)  # 写入缩放属性

    set_instancer_positions(instancer, positions_np)  # 写入位置数组
    log_info(f"PointInstancer ready: {instancer_path}")  # 输出就绪日志
    return instancer  # 返回实例器


def set_instancer_positions(instancer, positions_np):  # 设置实例器位置
    try:  # 尝试写入位置
        positions = [Gf.Vec3f(float(p[0]), float(p[1]), float(p[2])) for p in positions_np]  # 转换为 USD 向量
        instancer.GetPositionsAttr().Set(positions)  # 写入位置属性
    except Exception as exc:  # 捕获写入异常
        log_error(f"Failed to write positions to {instancer.GetPath()}: {exc}")  # 输出错误信息
        raise  # 抛出异常
