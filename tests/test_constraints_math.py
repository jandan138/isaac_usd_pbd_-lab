import os
import sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from isaac_pbd_lab.sim.constraints import DistanceConstraint
from isaac_pbd_lab.sim.pbd import solve_constraints_pbd


def test_distance_constraint_projection():
    x = np.array([[0.0, 0.0, 0.0], [0.2, 0.0, 0.0]], dtype=np.float32)
    inv_mass = np.array([0.0, 1.0], dtype=np.float32)
    constraints = [DistanceConstraint(0, 1, 0.1)]
    max_res = solve_constraints_pbd(x, inv_mass, constraints, iterations=10)
    dist = np.linalg.norm(x[0] - x[1])
    assert abs(dist - 0.1) < 1e-4
    assert max_res < 1e-4


if __name__ == "__main__":
    test_distance_constraint_projection()
    print("test_distance_constraint_projection: OK")
