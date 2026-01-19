import argparse  # 导入参数解析模块
import os  # 导入操作系统模块
import sys  # 导入系统模块
import time  # 导入时间模块

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 获取工程根目录
SRC = os.path.join(ROOT, "src")  # 拼接源码目录
if SRC not in sys.path:  # 若源码路径未加入
    sys.path.insert(0, SRC)  # 插入到搜索路径

from isaacsim.simulation_app import SimulationApp  # 导入 SimulationApp


def main():  # 主入口函数
    parser = argparse.ArgumentParser()  # 创建参数解析器
    parser.add_argument("--headless", action="store_true", help="Run headless (default)")  # 添加 headless 参数
    parser.add_argument("--gui", action="store_true", help="Run with UI")  # 添加 GUI 参数
    parser.add_argument("--headless-test", action="store_true", help="Run a short headless self-test and quit")  # 添加测试参数
    parser.add_argument("--frames", type=int, default=300, help="Number of frames to run")  # 添加帧数参数
    parser.add_argument("--dt", type=float, default=None, help="Override dt for headless run")  # 添加 dt 参数
    parser.add_argument("--timeout", type=float, default=60.0, help="Max seconds before force quit")  # 添加超时参数
    parser.add_argument("--log-interval-frames", type=int, default=60, help="Print tail position every N frames in headless")  # 添加日志间隔参数
    args = parser.parse_args()  # 解析命令行参数

    headless = True  # 默认 headless
    if args.gui:  # 若显式 GUI
        headless = False  # 关闭 headless
    if args.headless:  # 若显式 headless
        headless = True  # 开启 headless

    simulation_app = SimulationApp({"headless": headless})  # 启动 SimulationApp

    from isaac_pbd_lab.app import PbdApp  # 延迟导入应用
    from isaac_pbd_lab.config import load_yaml_like  # 延迟导入配置读取

    config_path = os.path.join(ROOT, "configs", "default.yaml")  # 配置文件路径
    cfg = load_yaml_like(config_path)  # 读取配置
    app = PbdApp(cfg, solver_type="pbd")  # 创建 PBD 应用

    if args.headless_test:  # 若是 headless 测试
        frames = min(args.frames, 60)  # 限制帧数
    else:  # 非测试
        frames = args.frames  # 使用指定帧数

    dt = args.dt  # 获取 dt 覆盖值
    timeout = args.timeout  # 获取超时
    log_interval = max(1, int(args.log_interval_frames))  # 计算日志间隔
    start = time.time()  # 记录起始时间

    if headless or args.headless_test:  # headless 逻辑
        for idx in range(frames):  # 循环指定帧数
            app.step_once(dt_override=dt)  # 执行一步
            simulation_app.update()  # 更新仿真
            if (idx + 1) % log_interval == 0:  # 到达日志间隔
                tail = app.system.positions[-1]  # 读取末端位置
                print(f"[PBD] frame={idx + 1} tail=({tail[0]:.4f}, {tail[1]:.4f}, {tail[2]:.4f})")  # 输出末端位置
            if time.time() - start > timeout:  # 超时判断
                break  # 退出循环
        tail = app.system.positions[-1]  # 读取最终末端位置
        print(f"[PBD] tail=({tail[0]:.4f}, {tail[1]:.4f}, {tail[2]:.4f})")  # 输出最终末端位置
        simulation_app.close()  # 关闭应用
        return  # 结束函数

    app.start()  # 启动 UI 事件循环
    while simulation_app.is_running():  # 当应用运行
        simulation_app.update()  # 更新应用
        if time.time() - start > timeout:  # 超时判断
            break  # 退出循环
    simulation_app.close()  # 关闭应用


if __name__ == "__main__":  # 入口判断
    main()  # 调用主函数
