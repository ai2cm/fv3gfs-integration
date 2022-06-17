import enum
from typing import Optional

from pace.util.communicator import CubedSphereCommunicator


class DaCeOrchestration(enum.Enum):
    """
    Orchestration mode for DaCe

        Python: python orchestration
        Build: compile & save SDFG only
        BuildAndRun: compile & save SDFG, then run
        Run: load from .so and run, will fail if .so is not available
    """

    Python = 0
    Build = 1
    BuildAndRun = 2
    Run = 3


class DaceConfig:
    def __init__(
        self,
        communicator: Optional[CubedSphereCommunicator],
        backend: str,
        orchestration: Optional[DaCeOrchestration] = None,
    ):
        # Temporary. This is a bit too out of the ordinary for the common user.
        # We should refactor the architecture to allow for a `gtc:orchestrated:dace:X`
        # backend that would signify both the `CPU|GPU` split and the orchestration mode
        import os

        if orchestration is None:
            self._orchestrate = DaCeOrchestration[os.getenv("FV3_DACEMODE", "Python")]
        else:
            self._orchestrate = orchestration

        self._backend = backend
        from pace.dsl.dace.build import (
            set_distributed_caches,
            read_target_rank,
            write_decomposition,
        )

        # Distributed build required info
        if communicator:
            self.my_rank = communicator.rank
            self.rank_size = communicator.comm.Get_size()
            from gt4py import config as gt_config

            config_path = (
                f"{gt_config.cache_settings['root_path']}/.layout/decomposition.yml"
            )
            self.target_rank = read_target_rank(
                rank=self.my_rank,
                partitioner=communicator.partitioner,
                config=self,
                layout_filepath=config_path,
            )
        else:
            self.my_rank = 0
            self.rank_size = 1
            self.target_rank = 0

        set_distributed_caches(self)

        if (
            (
                self._orchestrate == DaCeOrchestration.Build
                or self._orchestrate == DaCeOrchestration.BuildAndRun
            )
            and self.my_rank == 0
            and self.rank_size > 1
        ):
            write_decomposition(communicator.partitioner)

        if (
            self._orchestrate != DaCeOrchestration.Python
            and "dace" not in self._backend
        ):
            raise RuntimeError(
                "DaceConfig: orchestration can only be leverage "
                f"on gtc:dace or gtc:dace:gpu not on {self._backend}"
            )

    def is_dace_orchestrated(self) -> bool:
        return self._orchestrate != DaCeOrchestration.Python

    def is_gpu_backend(self) -> bool:
        return "gpu" in self._backend

    def get_backend(self) -> str:
        return self._backend

    def get_orchestrate(self) -> DaCeOrchestration:
        return self._orchestrate

    def get_communicator(self) -> CubedSphereCommunicator:
        return self._communicator
