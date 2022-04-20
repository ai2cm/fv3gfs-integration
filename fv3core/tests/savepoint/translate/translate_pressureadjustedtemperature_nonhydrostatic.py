from fv3core.stencils import temperature_adjust
from fv3core.stencils.dyn_core import get_nk_heat_dissipation
from pace.dsl.dace.orchestrate import computepath_method
from pace.stencils.testing import TranslateDycoreFortranData2Py


class PressureAdjustedTemperature_Wrapper:
    def __init__(self, stencil_factory, namelist, grid):
        n_adj = get_nk_heat_dissipation(
            config=namelist.d_grid_shallow_water,
            npz=grid.grid_indexing.domain[2],
        )
        self.stencil = stencil_factory.from_origin_domain(
            temperature_adjust.compute_pkz_tempadjust,
            origin=stencil_factory.grid_indexing.origin_compute(),
            domain=stencil_factory.grid_indexing.restrict_vertical(
                nk=n_adj
            ).domain_compute(),
        )

    @computepath_method
    def __call__(self, delp, delz, cappa, heat_source, pt, pkz, delt_time_factor):
        self.stencil(delp, delz, cappa, heat_source, pt, pkz, delt_time_factor)


class TranslatePressureAdjustedTemperature_NonHydrostatic(
    TranslateDycoreFortranData2Py
):
    def __init__(self, grid, namelist, stencil_factory):
        super().__init__(grid, namelist, stencil_factory)
        self.namelist = namelist
        self.compute_func = PressureAdjustedTemperature_Wrapper(
            stencil_factory, namelist, grid
        )
        self.in_vars["data_vars"] = {
            "cappa": {},
            "delp": {},
            "delz": {},
            "pt": {},
            "heat_source": {"serialname": "heat_source_dyn"},
            "pkz": grid.compute_dict(),
        }
        self.in_vars["parameters"] = ["bdt"]
        self.out_vars = {"pt": {}, "pkz": grid.compute_dict()}

    def compute_from_storage(self, inputs):
        inputs["delt_time_factor"] = abs(inputs["bdt"] * self.namelist.delt_max)
        del inputs["bdt"]
        self.compute_func(**inputs)
        return inputs
