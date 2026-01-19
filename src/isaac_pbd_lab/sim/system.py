import numpy as np

from .constraints import build_chain_constraints
from .pbd import solve_constraints_pbd
from .xpbd import solve_constraints_xpbd, init_lambdas
from .vbd import solve_constraints_vbd


class ParticleSystem:
    def __init__(self, n_particles, rest_length, gravity, radius, iterations,
                 solver_type="pbd", compliance=0.0, damping=0.0):
        self.n_particles = n_particles
        self.rest_length = rest_length
        self.gravity = np.array(gravity, dtype=np.float32)
        self.radius = radius
        self.iterations = iterations
        self.solver_type = solver_type
        self.compliance = compliance
        self.damping = float(damping)

        self.positions = np.zeros((n_particles, 3), dtype=np.float32)
        self.velocities = np.zeros((n_particles, 3), dtype=np.float32)
        self.inv_mass = np.ones((n_particles,), dtype=np.float32)
        self.inv_mass[0] = 0.0  # anchor

        # init chain along x
        start = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        for i in range(n_particles):
            self.positions[i] = start + np.array([i * rest_length, 0.0, 0.0], dtype=np.float32)

        self.constraints = build_chain_constraints(n_particles, rest_length)
        self.lambdas = init_lambdas(self.constraints)

    def step(self, dt):
        x_old = self.positions.copy()

        # external forces
        self.velocities += dt * self.gravity
        x_pred = self.positions + dt * self.velocities

        # constraints
        if self.solver_type == "pbd":
            max_residual = solve_constraints_pbd(
                x_pred, self.inv_mass, self.constraints, self.iterations
            )
        elif self.solver_type == "xpbd":
            max_residual = solve_constraints_xpbd(
                x_pred, self.inv_mass, self.constraints,
                self.lambdas, self.compliance, dt, self.iterations
            )
        elif self.solver_type == "vbd":
            max_residual = solve_constraints_vbd(
                x_pred, self.inv_mass, self.constraints, dt, self.iterations
            )
        else:
            max_residual = solve_constraints_pbd(
                x_pred, self.inv_mass, self.constraints, self.iterations
            )

        # simple ground projection (keep fixed particles anchored)
        x_pred[:, 1] = np.maximum(x_pred[:, 1], self.radius)
        fixed_mask = self.inv_mass == 0.0
        if np.any(fixed_mask):
            x_pred[fixed_mask] = x_old[fixed_mask]

        # velocity update
        self.velocities[:] = (x_pred - x_old) / max(dt, 1e-6)

        # simple velocity damping to reduce oscillation
        if self.damping > 0.0:
            damp_factor = max(0.0, 1.0 - self.damping * dt)
            self.velocities *= damp_factor

        # write back
        self.positions[:] = x_pred

        return max_residual
