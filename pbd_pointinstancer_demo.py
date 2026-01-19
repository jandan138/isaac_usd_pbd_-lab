# Minimal PBD chain demo using UsdGeom.PointInstancer in Isaac Sim 4.5
# Run in Script Editor or with Isaac Sim Python.

import time
import numpy as np

from pxr import Usd, UsdGeom, Gf

try:
    import omni
    import omni.usd
    import omni.kit.app
    import omni.timeline
except Exception as exc:
    print("[ERROR] omni modules not available. This script must run inside Isaac Sim/Kit.")
    raise


# -----------------------------
# Config
# -----------------------------
N_PARTICLES = 50
REST_LENGTH = 0.05
RADIUS = 0.02
GRAVITY = np.array([0.0, -9.81, 0.0], dtype=np.float32)
ITERATIONS = 20
FIXED_DT = 1.0 / 60.0

PROTOTYPE_PATH = "/World/Prototypes/Sphere"
INSTANCER_PATH = "/World/Particles/Instancer"

# Global sim toggle
sim_running = True


# -----------------------------
# USD helpers
# -----------------------------

def get_or_create_stage():
    ctx = omni.usd.get_context()
    stage = ctx.get_stage()
    if stage is None:
        ctx.new_stage()
        stage = ctx.get_stage()
    if stage is None:
        raise RuntimeError("Failed to create or get USD stage.")
    return stage


def ensure_xform(stage, path):
    prim = stage.GetPrimAtPath(path)
    if prim and prim.IsValid():
        return prim
    return stage.DefinePrim(path, "Xform")


def build_pointinstancer(stage, positions_np):
    # Ensure parents
    ensure_xform(stage, "/World")
    ensure_xform(stage, "/World/Prototypes")
    ensure_xform(stage, "/World/Particles")

    # Prototype sphere
    sphere_prim = stage.GetPrimAtPath(PROTOTYPE_PATH)
    if not sphere_prim or not sphere_prim.IsValid():
        sphere = UsdGeom.Sphere.Define(stage, PROTOTYPE_PATH)
    else:
        sphere = UsdGeom.Sphere(sphere_prim)
    sphere.CreateRadiusAttr(RADIUS)

    # PointInstancer
    instancer_prim = stage.GetPrimAtPath(INSTANCER_PATH)
    if not instancer_prim or not instancer_prim.IsValid():
        instancer = UsdGeom.PointInstancer.Define(stage, INSTANCER_PATH)
    else:
        instancer = UsdGeom.PointInstancer(instancer_prim)

    # Set prototypes
    instancer.CreatePrototypesRel().SetTargets([sphere.GetPrim().GetPath()])

    # Set protoIndices
    proto_indices = np.zeros((positions_np.shape[0],), dtype=np.int32)
    instancer.CreateProtoIndicesAttr().Set(proto_indices.tolist())

    # Optional orientations (identity quaternions)
    orientations = [Gf.Quath(1.0, Gf.Vec3h(0.0, 0.0, 0.0))] * positions_np.shape[0]
    instancer.CreateOrientationsAttr().Set(orientations)

    # Optional scales (uniform)
    scales = [Gf.Vec3f(1.0, 1.0, 1.0)] * positions_np.shape[0]
    instancer.CreateScalesAttr().Set(scales)

    # Initial positions
    set_instancer_positions(instancer, positions_np)

    return instancer


def set_instancer_positions(instancer, positions_np):
    # Convert numpy array to list of Gf.Vec3f
    positions = [Gf.Vec3f(float(p[0]), float(p[1]), float(p[2])) for p in positions_np]
    instancer.GetPositionsAttr().Set(positions)


# -----------------------------
# PBD core
# -----------------------------

def init_chain(n_particles, rest_length):
    positions = np.zeros((n_particles, 3), dtype=np.float32)
    velocities = np.zeros((n_particles, 3), dtype=np.float32)
    inv_mass = np.ones((n_particles,), dtype=np.float32)

    # Anchor first particle
    inv_mass[0] = 0.0

    # Place chain along +X with some height
    start = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    for i in range(n_particles):
        positions[i] = start + np.array([i * rest_length, 0.0, 0.0], dtype=np.float32)

    return positions, velocities, inv_mass


def build_distance_constraints(n_particles, rest_length):
    # constraints as list of (i, j, rest_length)
    constraints = []
    for i in range(n_particles - 1):
        constraints.append((i, i + 1, rest_length))
    return constraints


def solve_constraints_pbd(x_pred, inv_mass, constraints, iterations):
    # Gauss-Seidel style
    for _ in range(iterations):
        for (i, j, rest_length) in constraints:
            w_i = inv_mass[i]
            w_j = inv_mass[j]
            if w_i == 0.0 and w_j == 0.0:
                continue

            delta = x_pred[i] - x_pred[j]
            dist = np.linalg.norm(delta)
            if dist < 1e-8:
                continue
            C = dist - rest_length
            grad_i = delta / dist
            grad_j = -grad_i

            denom = w_i * np.dot(grad_i, grad_i) + w_j * np.dot(grad_j, grad_j)
            if denom < 1e-8:
                continue
            lam = -C / denom

            if w_i > 0.0:
                x_pred[i] += w_i * lam * grad_i
            if w_j > 0.0:
                x_pred[j] += w_j * lam * grad_j


def solve_constraints_xpbd(x_pred, inv_mass, constraints, lambdas, compliance, dt, iterations):
    # Placeholder for XPBD
    pass


def solve_constraints_vbd(x_pred, inv_mass, constraints, dt, iterations):
    # Placeholder for VBD
    pass


def step_pbd(positions, velocities, inv_mass, constraints, dt):
    # Save old positions for velocity update
    x_old = positions.copy()

    # Semi-implicit Euler for external forces
    velocities += dt * GRAVITY
    x_pred = positions + dt * velocities

    # Constraints projection
    solve_constraints_pbd(x_pred, inv_mass, constraints, ITERATIONS)

    # Optional ground collision (project to y >= RADIUS)
    # TODO: add restitution/friction if needed
    x_pred[:, 1] = np.maximum(x_pred[:, 1], RADIUS)

    # Velocity update
    velocities[:] = (x_pred - x_old) / max(dt, 1e-6)

    # Write back
    positions[:] = x_pred


# -----------------------------
# Update callback
# -----------------------------

class Simulation:
    def __init__(self):
        self.stage = get_or_create_stage()
        self.positions, self.velocities, self.inv_mass = init_chain(N_PARTICLES, REST_LENGTH)
        self.constraints = build_distance_constraints(N_PARTICLES, REST_LENGTH)
        self.instancer = build_pointinstancer(self.stage, self.positions)

        self._last_log_time = time.time()
        self._frame_count = 0

        self._update_sub = None
        self._timeline = None

    def _get_dt(self):
        # Try timeline dt
        if self._timeline is None:
            try:
                self._timeline = omni.timeline.get_timeline_interface()
            except Exception:
                self._timeline = None
        if self._timeline is not None:
            dt = self._timeline.get_delta_time()
            if dt and dt > 0:
                return float(dt)
        return FIXED_DT

    def update(self, _e):
        global sim_running
        if not sim_running:
            return

        dt = self._get_dt()
        step_pbd(self.positions, self.velocities, self.inv_mass, self.constraints, dt)
        set_instancer_positions(self.instancer, self.positions)

        # Log once per second
        self._frame_count += 1
        now = time.time()
        if now - self._last_log_time >= 1.0:
            fps = self._frame_count / (now - self._last_log_time)
            p0 = self.positions[0]
            print(
                f"[PBD] fps={fps:.1f} dt={dt:.4f} N={self.positions.shape[0]} p0=({p0[0]:.3f}, {p0[1]:.3f}, {p0[2]:.3f})"
            )
            self._last_log_time = now
            self._frame_count = 0

    def start(self):
        app = omni.kit.app.get_app()
        self._update_sub = app.get_update_event_stream().create_subscription_to_pop(self.update)
        print("[PBD] Simulation started. sim_running=True")

    def stop(self):
        if self._update_sub is not None:
            self._update_sub = None
        print("[PBD] Simulation stopped.")


# -----------------------------
# Entry point
# -----------------------------

def main():
    sim = Simulation()
    sim.start()
    return sim


# Auto-start when run in Script Editor
if __name__ == "__main__":
    _sim = main()
