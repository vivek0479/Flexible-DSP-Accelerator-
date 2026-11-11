"""
Interactive and Standalone Simulator for Existing System
Runs:
  - Template unit tests (T1 to T5)
  - DSP Kernel executions (FIR16, ELLIPTIC, VOLTERRA)
  - Clock Gating impact analysis (Gated vs Non-Gated Dynamic Power)
"""

import sys
from typing import List
from existing_system.fcc_datapath import FlexibleComputationalComponent
from existing_system.dsp_kernels import ExistingDSPKernelRunner


def run_template_demo():
    print("=" * 70)
    print(" EXISTING SYSTEM: TEMPLATE EXECUTION DEMO (T1 - T5)")
    print("=" * 70)

    fcc = FlexibleComputationalComponent(bit_width=16)

    # Test cases for T1 - T5
    test_vectors = [
        ("T1", 25, 100, 50, 10, "W = A * (X + Y) + K = 25 * 150 + 10 = 3760"),
        ("T2", 15, 200, 80, 5, "W = A * (X - Y) + K = 15 * 120 + 5 = 1805"),
        ("T3", 30, 40, 60, 12, "W = A * K + (X + Y) = 30 * 12 + 100 = 460"),
        ("T4", 20, 150, 50, 8, "W = A * K + (X - Y) = 20 * 8 + 100 = 260"),
        ("T5", 45, 0, 0, 16, "W = A * K = 45 * 16 = 720"),
    ]

    for tmpl, a, x, y, k, formula in test_vectors:
        res = fcc.execute(tmpl, A=a, X=x, Y=y, K=k, clk=True, clk_gate_en=True)
        print(f"[{tmpl}] Formula: {formula}")
        print(f"       Result: {res['result']} | Status: {res['status']} | Crit. Delay: {res['critical_delay_tg']} Tg")

    print("\nSimulating Clock Gated cycle (clk_gate_en = False):")
    gated_res = fcc.execute("T1", A=25, X=100, Y=50, K=10, clk=True, clk_gate_en=False)
    print(f"Gated execution result: {gated_res['result']} | Status: {gated_res['status']}")

    metrics = fcc.get_power_metrics()
    print("\nFCC Hardware Metrics (Existing System):")
    print(f"  - Gate Equivalent Area: {metrics['area_ag']:.1f} Ag")
    print(f"  - Critical Path Delay:  {metrics['critical_delay_tg']:.1f} Tg")
    print(f"  - Area-Delay Product:   {metrics['area_delay_product_adp']:.1f} Ag*Tg")
    print(f"  - Dynamic Power:        {metrics['dynamic_power_mw']:.4f} mW")
    print(f"  - Total Energy:         {metrics['energy_pj']:.4f} pJ")


def run_clock_gating_comparison():
    print("\n" + "=" * 70)
    print(" EXISTING SYSTEM: CLOCK GATING POWER COMPARISON")
    print("=" * 70)

    samples = [10, 25, -15, 40, -50, 65, 80, -30, 20, 45, 90, -10]

    # Run without clock gating (clock always active)
    runner_no_cg = ExistingDSPKernelRunner()
    res_no_cg = runner_no_cg.run_fir16(samples, enable_clock_gating=False)

    # Run with clock gating enabled during idle phases
    runner_cg = ExistingDSPKernelRunner()
    res_cg = runner_cg.run_fir16(samples, enable_clock_gating=True)

    p_no_cg = res_no_cg["power_metrics"]
    p_cg = res_cg["power_metrics"]

    print(f"{'Metric':<32} | {'No Clock Gating':<18} | {'With Clock Gating':<18}")
    print("-" * 72)
    print(f"{'Total Clock Cycles':<32} | {p_no_cg['total_cycles']:<18} | {p_cg['total_cycles']:<18}")
    print(f"{'Gated Cycles':<32} | {p_no_cg['gated_cycles']:<18} | {p_cg['gated_cycles']:<18}")
    print(f"{'Gating Efficiency (%)':<32} | {p_no_cg['icg_gating_efficiency_pct']:<18.2f} | {p_cg['icg_gating_efficiency_pct']:<18.2f}")
    print(f"{'Dynamic Power (mW)':<32} | {p_no_cg['dynamic_power_mw']:<18.4f} | {p_cg['dynamic_power_mw']:<18.4f}")
    print(f"{'Total Power (mW)':<32} | {p_no_cg['total_power_mw']:<18.4f} | {p_cg['total_power_mw']:<18.4f}")
    print(f"{'Total Energy (pJ)':<32} | {p_no_cg['energy_pj']:<18.4f} | {p_cg['energy_pj']:<18.4f}")

    if p_no_cg['dynamic_power_mw'] > 0:
        dyn_savings = ((p_no_cg['dynamic_power_mw'] - p_cg['dynamic_power_mw']) / p_no_cg['dynamic_power_mw']) * 100.0
        print(f"\n>> Dynamic Power Reduction via Clock Gating: {dyn_savings:.2f}%")


def main():
    run_template_demo()
    run_clock_gating_comparison()


if __name__ == "__main__":
    main()
