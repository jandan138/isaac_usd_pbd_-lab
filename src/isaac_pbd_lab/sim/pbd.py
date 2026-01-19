import numpy as np

from .constraints import max_distance_residual


def solve_constraints_pbd(x_pred, inv_mass, constraints, iterations):
    for _ in range(iterations):
        for c in constraints:
            w_i = inv_mass[c.i]
            w_j = inv_mass[c.j]
            if w_i == 0.0 and w_j == 0.0:
                continue

            delta = x_pred[c.i] - x_pred[c.j]
            dist = np.linalg.norm(delta)
            if dist < 1e-8:
                continue

            C = dist - c.rest_length
            grad_i = delta / dist
            grad_j = -grad_i

            denom = w_i * np.dot(grad_i, grad_i) + w_j * np.dot(grad_j, grad_j)
            if denom < 1e-8:
                continue

            lam = -C / denom

            if w_i > 0.0:
                x_pred[c.i] += w_i * lam * grad_i
            if w_j > 0.0:
                x_pred[c.j] += w_j * lam * grad_j

    return max_distance_residual(x_pred, constraints)
