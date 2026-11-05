"""
Sakshi ALPR India - Global PyTorch & Ultralytics Compatibility Patch
Injects fallback modules, enables memory optimizations, and patches torch_load
to prevent 'torch.utils.serialization' and OOM errors across all cloud platforms.
"""
import os
import sys
import types

# Limit thread memory pools to prevent high RSS memory bloat in 512MB containers
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["MALLOC_ARENA_MAX"] = "2"

# 1. Fallback module injection for torch.utils.serialization
try:
    import torch.utils.serialization.config  # type: ignore
except Exception:
    ser_mod = types.ModuleType("torch.utils.serialization")
    cfg_mod = types.ModuleType("torch.utils.serialization.config")

    class _LoadConfig:
        mmap = False
        endianness = None
        mmap_flags = None
        calculate_storage_offsets = False

    class _SaveConfig:
        compute_crc32 = True
        use_pinned_memory_for_d2h = False
        storage_alignment = 64

    cfg_mod.load = _LoadConfig
    cfg_mod.save = _SaveConfig
    ser_mod.config = cfg_mod

    sys.modules["torch.utils.serialization"] = ser_mod
    sys.modules["torch.utils.serialization.config"] = cfg_mod

# 2. Patch torch.load for PyTorch 2.6+ and configure low-memory execution
try:
    import torch
    torch.set_num_threads(1)
    torch.set_grad_enabled(False)
    _orig_torch_load = torch.load

    def _patched_torch_load(*args, **kwargs):
        if "weights_only" not in kwargs:
            kwargs["weights_only"] = False
        return _orig_torch_load(*args, **kwargs)

    torch.load = _patched_torch_load
except Exception:
    pass

# 3. Patch Ultralytics safe_load wrappers
def _safe_load_wrapper(weight, safe_only=None):
    import torch
    ckpt = torch.load(weight, map_location="cpu", weights_only=False)
    if not isinstance(ckpt, dict):
        ckpt = {"model": ckpt.model}
    return ckpt, str(weight)

try:
    import ultralytics.nn.tasks as tasks
    tasks.torch_safe_load = _safe_load_wrapper
except Exception:
    pass

try:
    import ultralytics.engine.model as model_engine
    model_engine.torch_safe_load = _safe_load_wrapper
except Exception:
    pass

try:
    import ultralytics.utils.patches as patches
    patches.torch_load = _patched_torch_load
except Exception:
    pass

