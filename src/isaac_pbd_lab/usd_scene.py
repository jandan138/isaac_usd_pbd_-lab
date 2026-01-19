from pxr import UsdGeom, Gf

from .utils.log import log_error, log_info

try:
    import omni.usd
except Exception as exc:
    log_error("omni.usd not available. Run inside Isaac Sim/Kit.")
    raise


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


def build_pointinstancer(stage, positions_np, prototype_path, instancer_path, radius,
                         rebuild=False, set_orientations=True, set_scales=True):
    # Parents
    ensure_xform(stage, "/World")
    ensure_xform(stage, "/World/Prototypes")
    ensure_xform(stage, "/World/Particles")

    # Optional rebuild
    if rebuild:
        if stage.GetPrimAtPath(instancer_path).IsValid():
            stage.RemovePrim(instancer_path)
        if stage.GetPrimAtPath(prototype_path).IsValid():
            stage.RemovePrim(prototype_path)

    # Prototype sphere
    sphere_prim = stage.GetPrimAtPath(prototype_path)
    if not sphere_prim or not sphere_prim.IsValid():
        sphere = UsdGeom.Sphere.Define(stage, prototype_path)
    else:
        sphere = UsdGeom.Sphere(sphere_prim)
    sphere.CreateRadiusAttr(radius)

    # PointInstancer
    instancer_prim = stage.GetPrimAtPath(instancer_path)
    if not instancer_prim or not instancer_prim.IsValid():
        instancer = UsdGeom.PointInstancer.Define(stage, instancer_path)
    else:
        instancer = UsdGeom.PointInstancer(instancer_prim)

    try:
        instancer.CreatePrototypesRel().SetTargets([sphere.GetPrim().GetPath()])
    except Exception as exc:
        log_error(f"Failed to set prototypes on {instancer_path}: {exc}")
        raise

    # protoIndices
    proto_indices = [0] * positions_np.shape[0]
    instancer.CreateProtoIndicesAttr().Set(proto_indices)

    if set_orientations:
        orientations = [Gf.Quath(1.0, Gf.Vec3h(0.0, 0.0, 0.0))] * positions_np.shape[0]
        instancer.CreateOrientationsAttr().Set(orientations)

    if set_scales:
        scales = [Gf.Vec3f(1.0, 1.0, 1.0)] * positions_np.shape[0]
        instancer.CreateScalesAttr().Set(scales)

    set_instancer_positions(instancer, positions_np)
    log_info(f"PointInstancer ready: {instancer_path}")
    return instancer


def set_instancer_positions(instancer, positions_np):
    try:
        positions = [Gf.Vec3f(float(p[0]), float(p[1]), float(p[2])) for p in positions_np]
        instancer.GetPositionsAttr().Set(positions)
    except Exception as exc:
        log_error(f"Failed to write positions to {instancer.GetPath()}: {exc}")
        raise
