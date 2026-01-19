import sys  # 导入系统模块
from isaacsim.simulation_app import SimulationApp  # 导入 SimulationApp

print("[SMOKE] SimulationApp starting")  # 输出启动提示
sys.stdout.flush()  # 刷新标准输出

simulation_app = SimulationApp({"headless": True})  # 启动无窗口模式
print("[SMOKE] SimulationApp started")  # 输出启动完成
sys.stdout.flush()  # 刷新标准输出

simulation_app.update()  # 执行一次更新
simulation_app.close()  # 关闭应用

print("[SMOKE] SimulationApp closed")  # 输出关闭完成
sys.stdout.flush()  # 刷新标准输出
