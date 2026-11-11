"""
Master Execution and Verification Script
"Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic"
(IEEE TVLSI 2016) with Clock Gating Input for Both Existing and Proposed Systems.
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from existing_system.simulator import run_template_demo as run_existing_demo
from proposed_system.simulator import run_template_demo as run_proposed_demo
from benchmarks.verify_equivalence import verify_templates, verify_dsp_kernels
from benchmarks.compare_metrics import (
    compare_hardware_metrics,
    compare_dsp_kernel_energy,
    compare_clock_gating_savings,
)


def print_banner():
    banner = """
==============================================================================
   FLEXIBLE DSP ACCELERATOR ARCHITECTURE EXPLOITING CARRY-SAVE ARITHMETIC
       Kostas Tsoumanis, Sotirios Xydis, Georgios Zervakis, Kiamal Pekmestzi
                  IEEE Transactions on VLSI Systems (2016)
   --------------------------------------------------------------------------
   Includes Integrated Clock Gating (ICG) Input for Existing and Proposed
==============================================================================
"""
    print(banner)


def main():
    print_banner()

    print("\n>>> STEP 1: RUNNING EXISTING SYSTEM SIMULATION (FCC Datapath)")
    run_existing_demo()

    print("\n>>> STEP 2: RUNNING PROPOSED SYSTEM SIMULATION (Carry-Save FCU Datapath)")
    run_proposed_demo()

    print("\n>>> STEP 3: RUNNING MATHEMATICAL EQUIVALENCE VERIFICATION")
    tmpl_ok = verify_templates(num_random_trials=100)
    kern_ok = verify_dsp_kernels()

    if not (tmpl_ok and kern_ok):
        print("[ERROR] Equivalence check failed! Please review discrepancies.")
        sys.exit(1)

    print("\n>>> STEP 4: HARDWARE & ENERGY COMPARISON (TABLE I & II REPRODUCTION)")
    compare_hardware_metrics()
    compare_dsp_kernel_energy()

    print("\n>>> STEP 5: CLOCK GATING POWER SAVINGS ANALYSIS")
    compare_clock_gating_savings()

    print("=" * 78)
    print(" ALL SIMULATIONS, VERIFICATIONS, AND BENCHMARKS COMPLETED SUCCESSFULLY!")
    print("=" * 78)


if __name__ == "__main__":
    main()
