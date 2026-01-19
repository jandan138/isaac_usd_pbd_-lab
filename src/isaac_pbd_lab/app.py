import time

from .usd_scene import get_or_create_stage, build_pointinstancer, set_instancer_positions
from .sim.system import ParticleSystem
from .utils.log import log_info, log_error, log_warn
from .utils.time import FpsTimer

try:
    import omni.kit.app
    import omni.timeline
except Exception as exc:
    log_error("omni.kit/omni.timeline not available. Run inside Isaac Sim/Kit.")
    raise


class PbdApp:
    def __init__(self, config, solver_type="pbd"):
        self.config = config
        self.solver_type = solver_type
        self.sim_running = True

        self.stage = get_or_create_stage()
        self.system = ParticleSystem(
            n_particles=config["n_particles"],
            rest_length=config["rest_length"],
            gravity=config["gravity"],
            radius=config["radius"],
            iterations=config["iterations"],
            solver_type=solver_type,
            compliance=config.get("compliance", 0.0),
        )

        self.instancer = build_pointinstancer(
            self.stage,
            self.system.positions,
            config["prototype_path"],
            config["instancer_path"],
            config["radius"],
            rebuild=config.get("rebuild_usd_prims", False),
        )

        self._update_sub = None
        self._timeline = None
        self._timer = FpsTimer(interval_sec=1.0)

    def _get_dt(self):
        if self._timeline is None:
            try:
                self._timeline = omni.timeline.get_timeline_interface()
            except Exception:
                self._timeline = None
        if self._timeline is not None:
            dt = self._timeline.get_delta_time()
            if dt and dt > 0:
                return float(dt)
        return float(self.config.get("fixed_dt", 1.0 / 60.0))

    def update(self, _e):
        if not self.sim_running:
            return

        dt = self._get_dt()
        max_residual = self.system.step(dt)
        set_instancer_positions(self.instancer, self.system.positions)

        should_log, fps, elapsed = self._timer.tick()
        if should_log:
            p0 = self.system.positions[0]
            log_info(
                f"{self.solver_type.upper()} fps={fps:.1f} dt={dt:.4f} "
                f"N={self.system.positions.shape[0]} "
                f"p0=({p0[0]:.3f}, {p0[1]:.3f}, {p0[2]:.3f}) "
                f"max_res={max_residual:.6f}"
            )

    def start(self):
        app = omni.kit.app.get_app()
        self._update_sub = app.get_update_event_stream().create_subscription_to_pop(self.update)
        log_info("Simulation started. sim_running=True")

    def stop(self):
        self._update_sub = None
        log_info("Simulation stopped.")
