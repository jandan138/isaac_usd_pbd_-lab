from .pbd import solve_constraints_pbd
from .constraints import max_distance_residual


def solve_constraints_xpbd(x_pred, inv_mass, constraints, lambdas, compliance, dt, iterations):
    """
    XPBD stub.
    TODO:
    - Implement lambda accumulation per-constraint
    - Use alpha = compliance / dt^2
    - Update lambdas and positions accordingly
    """
    # Fallback to PBD for now to keep demo running
    return solve_constraints_pbd(x_pred, inv_mass, constraints, iterations)


def init_lambdas(constraints):
    return [0.0 for _ in constraints]
