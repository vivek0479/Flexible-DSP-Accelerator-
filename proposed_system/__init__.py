"""
Proposed Flexible DSP Accelerator Datapath Package
Exploiting Carry-Save Arithmetic with CS-to-MB Recoding,
4:2 Compressors, CSA Tree Multipliers, and Integrated Clock Gating.
"""

from .clock_gating import CSClockGatingCell, CSSwitchingActivityTracker
from .cs_arithmetic import CarrySaveNumber, CarrySaveCompressor42, to_signed16, to_unsigned16
from .cs_to_mb_recoder import CSToMBRecoder
from .csa_tree_multiplier import CSATreeMultiplier
from .fcu_datapath import FlexibleComputationalUnit, FCURegisterBank, CStoBinModule
from .dsp_kernels import ProposedDSPKernelRunner

__all__ = [
    "CSClockGatingCell",
    "CSSwitchingActivityTracker",
    "CarrySaveNumber",
    "CarrySaveCompressor42",
    "to_signed16",
    "to_unsigned16",
    "CSToMBRecoder",
    "CSATreeMultiplier",
    "FlexibleComputationalUnit",
    "FCURegisterBank",
    "CStoBinModule",
    "ProposedDSPKernelRunner",
]
