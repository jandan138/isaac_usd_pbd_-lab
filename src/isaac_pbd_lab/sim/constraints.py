from dataclasses import dataclass
import numpy as np


@dataclass
class DistanceConstraint:
    i: int
    j: int
    rest_length: float


def build_chain_constraints(n_particles, rest_length):
    constraints = []
    for i in range(n_particles - 1):
        constraints.append(DistanceConstraint(i, i + 1, rest_length))
    return constraints


def max_distance_residual(x, constraints):
    max_res = 0.0
    for c in constraints:
        delta = x[c.i] - x[c.j]
        dist = np.linalg.norm(delta)
        res = abs(dist - c.rest_length)
        if res > max_res:
            max_res = res
    return float(max_res)
