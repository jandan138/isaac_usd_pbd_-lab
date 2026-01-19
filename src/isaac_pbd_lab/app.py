import time  # 导入时间模块

from .usd_scene import get_or_create_stage, build_pointinstancer, set_instancer_positions  # 导入场景与实例器工具
from .sim.system import ParticleSystem  # 导入粒子系统
from .utils.log import log_info, log_error, log_warn  # 导入日志函数
from .utils.time import FpsTimer  # 导入帧率计时器

try:  # 尝试导入 Isaac Sim 模块
    import omni.kit.app  # 导入 Kit 应用接口
    import omni.timeline  # 导入时间线接口
except Exception as exc:  # 捕获导入异常
    log_error("omni.kit/omni.timeline not available. Run inside Isaac Sim/Kit.")  # 输出错误提示
    raise  # 抛出异常


class PbdApp:  # PBD 应用封装类
    def __init__(self, config, solver_type="pbd"):  # 初始化应用
        self.config = config  # 保存配置
        self.solver_type = solver_type  # 保存求解器类型
        self.sim_running = True  # 仿真运行标记

        self.stage = get_or_create_stage()  # 获取或创建 USD Stage
        self.system = ParticleSystem(  # 创建粒子系统
            n_particles=config["n_particles"],  # 读取粒子数量
            rest_length=config["rest_length"],  # 读取静止长度
            gravity=config["gravity"],  # 读取重力
            radius=config["radius"],  # 读取半径
            iterations=config["iterations"],  # 读取迭代次数
            solver_type=solver_type,  # 传入求解器类型
            compliance=config.get("compliance", 0.0),  # 传入软度参数
            damping=config.get("damping", 0.0),  # 传入阻尼参数
        )  # 结束粒子系统创建

        self.instancer = build_pointinstancer(  # 创建点实例器
            self.stage,  # 传入舞台
            self.system.positions,  # 传入位置数组
            config["prototype_path"],  # 传入原型路径
            config["instancer_path"],  # 传入实例器路径
            config["radius"],  # 传入半径
            rebuild=config.get("rebuild_usd_prims", False),  # 传入重建选项
        )  # 结束实例器创建

        self._update_sub = None  # 更新订阅句柄
        self._timeline = None  # 时间线接口缓存
        self._timer = FpsTimer(interval_sec=1.0)  # 创建帧率计时器

    def _get_dt(self):  # 获取时间步长
        if self._timeline is None:  # 若时间线未初始化
            try:  # 尝试获取时间线接口
                self._timeline = omni.timeline.get_timeline_interface()  # 获取时间线接口
            except Exception:  # 获取失败
                self._timeline = None  # 置空时间线
        if self._timeline is not None:  # 若时间线可用
            if hasattr(self._timeline, "get_delta_time"):  # 若存在 delta time 接口
                dt = self._timeline.get_delta_time()  # 获取 delta time
                if dt and dt > 0:  # 检查有效性
                    return float(dt)  # 返回 dt
            if hasattr(self._timeline, "get_time_codes_per_second"):  # 若存在 tps 接口
                tps = self._timeline.get_time_codes_per_second()  # 获取 tps
                if tps and tps > 0:  # 检查有效性
                    return float(1.0 / tps)  # 由 tps 计算 dt
            if hasattr(self._timeline, "get_time_step"):  # 若存在 time_step 接口
                dt = self._timeline.get_time_step()  # 获取 time_step
                if dt and dt > 0:  # 检查有效性
                    return float(dt)  # 返回 dt
        return float(self.config.get("fixed_dt", 1.0 / 60.0))  # 回退到固定 dt

    def update(self, _e):  # 更新回调
        self.step_once()  # 执行一步仿真

    def step_once(self, dt_override=None):  # 执行单步仿真
        if not self.sim_running:  # 若暂停
            return  # 直接返回

        dt = float(dt_override) if dt_override is not None else self._get_dt()  # 选择 dt
        max_residual = self.system.step(dt)  # 推进一步并获取残差
        set_instancer_positions(self.instancer, self.system.positions)  # 写入位置到实例器

        should_log, fps, _elapsed = self._timer.tick()  # 更新计时器
        if should_log:  # 到达日志间隔
            p0 = self.system.positions[0]  # 读取第 0 个粒子位置
            log_info(  # 输出日志
                f"{self.solver_type.upper()} fps={fps:.1f} dt={dt:.4f} "  # 输出 fps 和 dt
                f"N={self.system.positions.shape[0]} "  # 输出粒子数量
                f"p0=({p0[0]:.3f}, {p0[1]:.3f}, {p0[2]:.3f}) "  # 输出第 0 粒子位置
                f"max_res={max_residual:.6f}"  # 输出最大残差
            )  # 结束日志输出

    def start(self):  # 启动仿真
        app = omni.kit.app.get_app()  # 获取 Kit 应用
        self._update_sub = app.get_update_event_stream().create_subscription_to_pop(self.update)  # 订阅更新事件
        log_info("Simulation started. sim_running=True")  # 输出启动日志

    def stop(self):  # 停止仿真
        self._update_sub = None  # 释放订阅
        log_info("Simulation stopped.")  # 输出停止日志
