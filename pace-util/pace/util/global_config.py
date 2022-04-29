import functools
import os
from typing import Optional
import pace.util as util


def getenv_bool(name: str, default: str) -> bool:
    indicator = os.getenv(name, default).title()
    return indicator == "True"


def set_backend(new_backend: str):
    global _BACKEND
    _BACKEND = new_backend


def get_backend() -> str:
    return _BACKEND


def set_rebuild(flag: bool):
    global _REBUILD
    _REBUILD = flag


def get_rebuild() -> bool:
    return _REBUILD


def set_validate_args(new_validate_args: bool):
    global _VALIDATE_ARGS
    _VALIDATE_ARGS = new_validate_args


# Set to "False" to skip validating gt4py stencil arguments
@functools.lru_cache(maxsize=None)
def get_validate_args() -> bool:
    return _VALIDATE_ARGS


# Options
# CPU: numpy, gt:cpu_ifirst, gt:cpu_kfirst
# GPU: gt:gpu, cuda
_BACKEND: Optional[str] = None

# If TRUE, all caches will bypassed and stencils recompiled
# if FALSE, caches will be checked and rebuild if code changes
_REBUILD: bool = getenv_bool("FV3_STENCIL_REBUILD_FLAG", "False")
_VALIDATE_ARGS: bool = True


def get_partitioner() -> Optional[util.CubedSpherePartitioner]:
    global _PARTITIONER
    return _PARTITIONER


def set_partitioner(partitioner: Optional[util.CubedSpherePartitioner]) -> None:
    global _PARTITIONER
    if _PARTITIONER is not None:
        print("re-setting the partitioner, why is that?")
    _PARTITIONER = partitioner


def set_partitioner_once(partitioner: Optional[util.CubedSpherePartitioner]) -> None:
    global _PARTITIONER
    if _PARTITIONER is None:
        _PARTITIONER = partitioner


# Partitioner from fv3core
_PARTITIONER: Optional[util.CubedSpherePartitioner] = None
