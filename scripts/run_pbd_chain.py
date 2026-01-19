import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from isaac_pbd_lab.app import PbdApp
from isaac_pbd_lab.config import load_yaml_like


def main():
    config_path = os.path.join(ROOT, "configs", "default.yaml")
    cfg = load_yaml_like(config_path)
    app = PbdApp(cfg, solver_type="pbd")
    app.start()
    return app


if __name__ == "__main__":
    _APP = main()
