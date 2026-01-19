import sys
from isaacsim.simulation_app import SimulationApp

print("[SMOKE] SimulationApp starting")
sys.stdout.flush()

simulation_app = SimulationApp({"headless": True})
print("[SMOKE] SimulationApp started")
sys.stdout.flush()

simulation_app.update()
simulation_app.close()

print("[SMOKE] SimulationApp closed")
sys.stdout.flush()
