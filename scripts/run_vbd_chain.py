import os
import sys
import argparse
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from isaac_pbd_lab.app import PbdApp
from isaac_pbd_lab.config import load_yaml_like
import omni.kit.app
import carb


_HEADLESS_SUB = None


def _run_headless(app, frames, dt, timeout):
    global _HEADLESS_SUB
    kit_app = omni.kit.app.get_app()
    start_time = time.time()
    counter = {"n": 0}

    def _on_update(_e):
        app.step_once(dt_override=dt)
        counter["n"] += 1
        if counter["n"] >= frames or (time.time() - start_time) > timeout:
            kit_app.post_quit()

    _HEADLESS_SUB = kit_app.get_update_event_stream().create_subscription_to_pop(_on_update)
    print(f"[VBD] Headless test started: frames={frames} dt={dt} timeout={timeout}")


def _get_app_arg(name, default=None):
    settings = carb.settings.get_settings()
    for path in (f"/app/args/--{name}", f"/app/args/{name}"):
        val = settings.get(path)
        if val is not None:
            return val
    return default


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless-test", action="store_true", help="Run a short headless self-test and quit")
    parser.add_argument("--frames", type=int, default=60, help="Number of frames for headless test")
    parser.add_argument("--dt", type=float, default=None, help="Override dt for headless test")
    parser.add_argument("--timeout", type=float, default=30.0, help="Max seconds for headless test before force quit")
    args = parser.parse_args()

    config_path = os.path.join(ROOT, "configs", "default.yaml")
    cfg = load_yaml_like(config_path)
    app = PbdApp(cfg, solver_type="vbd")

    headless_flag = args.headless_test or bool(_get_app_arg("headless-test", False))
    frames = int(_get_app_arg("frames", args.frames))
    dt = args.dt if args.dt is not None else _get_app_arg("dt", None)
    dt = float(dt) if dt is not None else None
    timeout = float(_get_app_arg("timeout", args.timeout))

    if headless_flag:
        _run_headless(app, frames, dt, timeout)
        return app

    app.start()
    return app


if __name__ == "__main__":
    _APP = main()
