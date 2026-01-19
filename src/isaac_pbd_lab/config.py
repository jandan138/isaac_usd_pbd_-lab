import os

from .utils.log import log_warn


def default_config():
    return {
        "n_particles": 50,
        "rest_length": 0.05,
        "radius": 0.02,
        "gravity": [0.0, -9.81, 0.0],
        "iterations": 20,
        "fixed_dt": 1.0 / 60.0,
        "compliance": 0.0,
        "damping": 0.5,
        "prototype_path": "/World/Prototypes/Sphere",
        "instancer_path": "/World/Particles/Instancer",
        "rebuild_usd_prims": False,
    }


def _parse_value(value):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        parts = [p.strip() for p in inner.split(",")]
        return [float(p) for p in parts]
    try:
        if "." in value or "e" in value.lower():
            return float(value)
        return int(value)
    except Exception:
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        return value


def load_yaml_like(path):
    cfg = default_config()
    if not os.path.exists(path):
        log_warn(f"Config not found: {path}, using defaults.")
        return cfg

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            cfg[key.strip()] = _parse_value(val)
    return cfg
