# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Isaac Sim PBD/XPBD/VBD Learning Lab — a structured learning project implementing particle systems and constraint solvers in Isaac Sim 4.5 using `UsdGeom.PointInstancer` for visualization. Solvers progress in three stages: **PBD** (complete) → **XPBD** (stub/TODO) → **VBD** (stub/TODO).

No external pip dependencies. All physics is pure Python/NumPy on top of Isaac Sim's USD/Omni modules.

## Running Simulations

**Recommended — Python mode via SimulationApp:**
```bash
/isaac-sim/python.sh scripts/run_pbd_chain_python.py --headless-test
# or via shell wrapper:
./scripts/run_pbd_chain_python.sh --headless-test
```

**Kit CLI mode (less reliable in headless):**
```bash
/isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=$(pwd)/scripts/run_pbd_chain.py
/isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=$(pwd)/scripts/run_xpbd_chain.py
/isaac-sim/isaac-sim.sh --allow-root --/app/pythonScript=$(pwd)/scripts/run_vbd_chain.py
```

**Runtime flags:**
- `--headless-test` — run short test and exit
- `--frames N` — number of frames to simulate
- `--dt FLOAT` — override timestep
- `--timeout SECONDS` — max execution time (script also has a hard +10s kill)

## Running Tests

```bash
python tests/test_constraints_math.py
```

The test validates PBD distance constraint projection math (no Isaac Sim required).

## Architecture

### Class Hierarchy

```
PbdApp (app.py)               # Orchestrates event loop, USD scene, solver
  ├── ParticleSystem           # (sim/system.py) — owns particle state arrays
  │   ├── positions [N×3]
  │   ├── velocities [N×3]
  │   ├── inv_mass [N]
  │   └── constraints: List[DistanceConstraint]
  └── USD Scene (usd_scene.py) # Stage + PointInstancer + Prototype Sphere
```

### Physics Step (`sim/system.py`)

Each `step(dt)` call:
1. Apply gravity to velocities
2. Predict positions (`x_pred = x + v * dt`)
3. Dispatch to solver: `solve_constraints_pbd()` / `xpbd()` / `vbd()`
4. Ground projection + fixed-particle anchoring (particle 0)
5. Velocity damping
6. Write back positions and velocities

### Solvers (`src/isaac_pbd_lab/sim/`)

| File | Status | Notes |
|------|--------|-------|
| `pbd.py` | Complete | Iterative constraint projection; `λ = -C / (w_i·∇Cᵢ² + w_j·∇Cⱼ²)` |
| `xpbd.py` | **Stub** | Must implement lambda accumulation + compliance `α = compliance/dt²` |
| `vbd.py` | **Stub** | Must implement energy/variational formulation with residual output |

Both stubs currently fall back to calling the PBD solver.

### Constraint Representation (`sim/constraints.py`)

```python
@dataclass
class DistanceConstraint:
    i: int              # particle index 1
    j: int              # particle index 2
    rest_length: float  # target distance
```

### Configuration (`configs/default.yaml`)

Key defaults: `n_particles=50`, `rest_length=0.05m`, `fixed_dt=1/60s`, `iterations=20`, `compliance=0.0001`. Parsed by a minimal YAML-like parser in `config.py` with no external dependencies.

### USD Scene (`usd_scene.py`)

Creates a prototype sphere prim under `/World/Prototypes/Sphere` and a `PointInstancer` at `/World/Particles/Instancer`. The instancer's `positions` attribute is updated each frame. Set `rebuild_usd_prims: true` in config to force prim teardown/recreation on startup.

### VS Code Python Interpreter

The workspace is configured to use `/cpfs/shared/simulation/zhuzihou/dev/isaac_usd_pbd_lab/scripts/python_isaacsim.sh` as the Python interpreter. Analysis paths include `src/`. This gives Pylance access to Isaac Sim modules without running a full Kit instance.

## Learning Stages

- **Stage 1 (PBD):** Edit `sim/pbd.py` and `sim/system.py`. Run `run_pbd_chain_python.py`. Expected: chain hangs under gravity, particle 0 anchored.
- **Stage 2 (XPBD):** Implement `sim/xpbd.py`. Verify dt-independence: chain length should stay consistent across `dt=1/30, 1/60, 1/120`.
- **Stage 3 (VBD):** Implement `sim/vbd.py`. Expected: log output shows max constraint residual decreasing per iteration.

See `docs/` for mathematical derivations (`10_pbd.md`, `11_xpbd.md`, `12_vbd.md`) and experiment guidelines (`20_experiments.md`).
