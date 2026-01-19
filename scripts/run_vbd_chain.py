import os  # 导入操作系统模块
import sys  # 导入系统模块
import argparse  # 导入参数解析模块
import time  # 导入时间模块

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 获取工程根目录
SRC = os.path.join(ROOT, "src")  # 拼接源码目录
if SRC not in sys.path:  # 若源码路径未加入
    sys.path.insert(0, SRC)  # 插入到搜索路径

from isaac_pbd_lab.app import PbdApp  # 导入 PBD 应用
from isaac_pbd_lab.config import load_yaml_like  # 导入配置读取
import omni.kit.app  # 导入 Kit 应用接口
import carb  # 导入 carb 设置接口


_HEADLESS_SUB = None  # headless 订阅句柄


def _run_headless(app, frames, dt, timeout):  # 运行 headless 测试
    global _HEADLESS_SUB  # 使用全局订阅句柄
    kit_app = omni.kit.app.get_app()  # 获取 Kit 应用
    start_time = time.time()  # 记录起始时间
    counter = {"n": 0}  # 帧计数器

    def _on_update(_e):  # 每帧回调
        app.step_once(dt_override=dt)  # 执行一步仿真
        counter["n"] += 1  # 计数加一
        if counter["n"] >= frames or (time.time() - start_time) > timeout:  # 结束条件
            kit_app.post_quit()  # 请求退出应用

    _HEADLESS_SUB = kit_app.get_update_event_stream().create_subscription_to_pop(_on_update)  # 订阅更新事件
    print(f"[VBD] Headless test started: frames={frames} dt={dt} timeout={timeout}")  # 输出启动信息


def _get_app_arg(name, default=None):  # 读取应用参数
    settings = carb.settings.get_settings()  # 获取设置对象
    for path in (f"/app/args/--{name}", f"/app/args/{name}"):  # 遍历两种格式
        val = settings.get(path)  # 读取参数
        if val is not None:  # 若存在
            return val  # 返回参数
    return default  # 返回默认值


def main():  # 主入口函数
    parser = argparse.ArgumentParser()  # 创建参数解析器
    parser.add_argument("--headless-test", action="store_true", help="Run a short headless self-test and quit")  # 添加测试参数
    parser.add_argument("--frames", type=int, default=60, help="Number of frames for headless test")  # 添加帧数参数
    parser.add_argument("--dt", type=float, default=None, help="Override dt for headless test")  # 添加 dt 参数
    parser.add_argument("--timeout", type=float, default=30.0, help="Max seconds for headless test before force quit")  # 添加超时参数
    args = parser.parse_args()  # 解析命令行参数

    config_path = os.path.join(ROOT, "configs", "default.yaml")  # 配置文件路径
    cfg = load_yaml_like(config_path)  # 读取配置
    app = PbdApp(cfg, solver_type="vbd")  # 创建 VBD 应用

    headless_flag = args.headless_test or bool(_get_app_arg("headless-test", False))  # 判断 headless
    frames = int(_get_app_arg("frames", args.frames))  # 获取帧数
    dt = args.dt if args.dt is not None else _get_app_arg("dt", None)  # 获取 dt
    dt = float(dt) if dt is not None else None  # 转换 dt
    timeout = float(_get_app_arg("timeout", args.timeout))  # 获取超时

    if headless_flag:  # 若 headless
        _run_headless(app, frames, dt, timeout)  # 运行 headless
        return app  # 返回应用

    app.start()  # 启动仿真
    return app  # 返回应用


if __name__ == "__main__":  # 入口判断
    _APP = main()  # 运行主函数
