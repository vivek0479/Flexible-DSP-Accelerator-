"""
Existing Flexible DSP Datapath Package
Based on Conventional Two's Complement Chaining with Carry Propagate Adders (CPA)
and Integrated Clock Gating (ICG).
"""

from .clock_gating import ClockGatingCell, SwitchingActivityTracker
from .arithmetic_units import CarryPropagateAdder, ModifiedBoothMultiplier16, to_signed16, to_unsigned16
from .fcc_datapath import FlexibleComputationalComponent, FCCRegisterBank
from .dsp_kernels import ExistingDSPKernelRunner

__all__ = [
    "ClockGatingCell",
    "SwitchingActivityTracker",
    "CarryPropagateAdder",
    "ModifiedBoothMultiplier16",
    "to_signed16",
    "to_unsigned16",
    "FlexibleComputationalComponent",
    "FCCRegisterBank",
    "ExistingDSPKernelRunner",
]
