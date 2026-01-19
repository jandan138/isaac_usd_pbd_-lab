from .pbd import solve_constraints_pbd


def solve_constraints_vbd(x_pred, inv_mass, constraints, dt, iterations):
    """
    VBD stub.
    TODO:
    - Implement energy-based or augmented Lagrangian formulation
    - Provide convergence metrics for residuals
    """
    # Fallback to PBD for now to keep demo running
    return solve_constraints_pbd(x_pred, inv_mass, constraints, iterations)
