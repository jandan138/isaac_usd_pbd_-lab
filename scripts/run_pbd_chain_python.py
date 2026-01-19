import argparse
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from isaacsim.simulation_app import SimulationApp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", help="Run headless (default)")
    parser.add_argument("--gui", action="store_true", help="Run with UI")
    parser.add_argument("--headless-test", action="store_true", help="Run a short headless self-test and quit")
    parser.add_argument("--frames", type=int, default=300, help="Number of frames to run")
    parser.add_argument("--dt", type=float, default=None, help="Override dt for headless run")
    parser.add_argument("--timeout", type=float, default=30.0, help="Max seconds before force quit")
    args = parser.parse_args()

    headless = True
    if args.gui:
        headless = False
    if args.headless:
        headless = True

    simulation_app = SimulationApp({"headless": headless})

    from isaac_pbd_lab.app import PbdApp
    from isaac_pbd_lab.config import load_yaml_like

    config_path = os.path.join(ROOT, "configs", "default.yaml")
    cfg = load_yaml_like(config_path)
    app = PbdApp(cfg, solver_type="pbd")

    if args.headless_test:
        frames = min(args.frames, 60)
    else:
        frames = args.frames

    dt = args.dt
    timeout = args.timeout
    start = time.time()

    if headless or args.headless_test:
        for _ in range(frames):
            app.step_once(dt_override=dt)
            simulation_app.update()
            if time.time() - start > timeout:
                break
        simulation_app.close()
        return

    app.start()
    while simulation_app.is_running():
        simulation_app.update()
        if time.time() - start > timeout:
            break
    simulation_app.close()


if __name__ == "__main__":
    main()
