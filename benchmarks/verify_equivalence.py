"""
Numerical Equivalence and Functional Verification Suite
Asserts that the Proposed Carry-Save FCU Architecture produces mathematically
identical numerical results to the Existing Two's Complement FCC Architecture.
"""

import sys
import random
from existing_system.fcc_datapath import FlexibleComputationalComponent
from proposed_system.fcu_datapath import FlexibleComputationalUnit
from proposed_system.cs_arithmetic import CarrySaveNumber
from existing_system.dsp_kernels import ExistingDSPKernelRunner
from proposed_system.dsp_kernels import ProposedDSPKernelRunner


def verify_templates(num_random_trials: int = 50) -> bool:
    print("=" * 70)
    print(" 1. FUNCTIONAL VERIFICATION: OPERATION TEMPLATES (T1 - T5)")
    print("=" * 70)

    fcc = FlexibleComputationalComponent(bit_width=16)
    fcu = FlexibleComputationalUnit(bit_width=16)

    templates = ["T1", "T2", "T3", "T4", "T5"]
    all_passed = True
    total_checks = 0

    # Deterministic Corner Cases
    corner_cases = [
        (0, 0, 0, 0),
        (1, 1, 1, 1),
        (-1, 1, -1, 1),
        (100, 200, 300, 400),
        (-50, 120, -80, 25),
        (255, -255, 128, -64),
        (1000, 20, 15, -30),
    ]

    for tmpl in templates:
        print(f"Testing Template {tmpl}...")
        for a, x, y, k in corner_cases:
            res_exist = fcc.execute(tmpl, A=a, X=x, Y=y, K=k, clk=True, clk_gate_en=True)["result"]

            x_cs = CarrySaveNumber.from_signed(x)
            y_cs = CarrySaveNumber.from_signed(y)
            k_cs = CarrySaveNumber.from_signed(k)
            res_prop = fcu.execute(tmpl, A=a, X=x_cs, Y=y_cs, K=k_cs, clk=True, clk_gate_en=True)["result_binary"]

            total_checks += 1
            if res_exist != res_prop:
                print(f"  [MISMATCH] {tmpl} with (A={a}, X={x}, Y={y}, K={k}): Existing={res_exist}, Proposed={res_prop}")
                all_passed = False

        # Random vectors
        random.seed(42)
        for _ in range(num_random_trials):
            a = random.randint(-128, 127)
            x = random.randint(-500, 500)
            y = random.randint(-500, 500)
            k = random.randint(-1000, 1000)

            res_exist = fcc.execute(tmpl, A=a, X=x, Y=y, K=k, clk=True, clk_gate_en=True)["result"]
            x_cs = CarrySaveNumber.from_signed(x)
            y_cs = CarrySaveNumber.from_signed(y)
            k_cs = CarrySaveNumber.from_signed(k)
            res_prop = fcu.execute(tmpl, A=a, X=x_cs, Y=y_cs, K=k_cs, clk=True, clk_gate_en=True)["result_binary"]

            total_checks += 1
            if res_exist != res_prop:
                print(f"  [MISMATCH] {tmpl} random trial: Existing={res_exist}, Proposed={res_prop}")
                all_passed = False
                break

    if all_passed:
        print(f">> SUCCESS: All {total_checks} template test vectors matched perfectly (100% equivalence)!\n")
    else:
        print(f">> FAILURE: Discrepancies detected between Existing and Proposed implementations.\n")

    return all_passed


def verify_dsp_kernels() -> bool:
    print("=" * 70)
    print(" 2. FUNCTIONAL VERIFICATION: DSP BENCHMARK KERNELS")
    print("=" * 70)

    samples = [15, -30, 45, -60, 80, 120, -90, 50, 20, -10, 35, 75, -40, 60, -25, 10]
    all_passed = True

    # 1. FIR16 Verification
    runner_ex = ExistingDSPKernelRunner()
    runner_pr = ProposedDSPKernelRunner()

    fir_ex = runner_ex.run_fir16(samples, enable_clock_gating=True)["outputs"]
    fir_pr = runner_pr.run_fir16(samples, enable_clock_gating=True)["outputs"]

    if fir_ex == fir_pr:
        print(f"[FIR16 Kernel]: MATCH! Output sequence length: {len(fir_pr)}")
        print(f"                Sample outputs: {fir_pr[:6]}")
    else:
        print(f"[FIR16 Kernel]: MISMATCH!")
        print(f"  Existing: {fir_ex}")
        print(f"  Proposed: {fir_pr}")
        all_passed = False

    # 2. ELLIPTIC Verification
    ell_ex = runner_ex.run_elliptic(samples, enable_clock_gating=True)["outputs"]
    ell_pr = runner_pr.run_elliptic(samples, enable_clock_gating=True)["outputs"]

    if ell_ex == ell_pr:
        print(f"[ELLIPTIC Kernel]: MATCH! Output sequence length: {len(ell_pr)}")
        print(f"                   Sample outputs: {ell_pr[:6]}")
    else:
        print(f"[ELLIPTIC Kernel]: MISMATCH!")
        all_passed = False

    # 3. VOLTERRA Verification
    volt_ex = runner_ex.run_volterra(samples, enable_clock_gating=True)["outputs"]
    volt_pr = runner_pr.run_volterra(samples, enable_clock_gating=True)["outputs"]

    if volt_ex == volt_pr:
        print(f"[VOLTERRA Kernel]: MATCH! Output sequence length: {len(volt_pr)}")
        print(f"                   Sample outputs: {volt_pr[:6]}")
    else:
        print(f"[VOLTERRA Kernel]: MISMATCH!")
        all_passed = False

    if all_passed:
        print("\n>> SUCCESS: All DSP Benchmark Kernels produced identical output sequences!\n")
    return all_passed


def main():
    tmpl_ok = verify_templates()
    kern_ok = verify_dsp_kernels()
    if tmpl_ok and kern_ok:
        print("=" * 70)
        print(" ALL VERIFICATION CHECKS PASSED: PROPOSED FCU IS BIT-ACCURATE!")
        print("=" * 70)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
