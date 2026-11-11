"""
Interactive and Standalone Simulator for Proposed System
Runs:
  - Operation Template unit tests (T1 to T5) in Carry-Save arithmetic
  - DSP Kernel executions (FIR16, ELLIPTIC, VOLTERRA)
  - Clock Gating impact analysis (Gated vs Non-Gated Dynamic Power)
"""

import sys
from typing import List
from proposed_system.cs_arithmetic import CarrySaveNumber
from proposed_system.fcu_datapath import FlexibleComputationalUnit
from proposed_system.dsp_kernels import ProposedDSPKernelRunner


def run_template_demo():
    print("=" * 70)
    print(" PROPOSED SYSTEM: FCU CARRY-SAVE TEMPLATE DEMO (T1 - T5)")
    print("=" * 70)

    fcu = FlexibleComputationalUnit(bit_width=16)

    test_vectors = [
        ("T1", 25, 100, 50, 10, "W* = A * (X* + Y*) + K* = 25 * 150 + 10 = 3760"),
        ("T2", 15, 200, 80, 5, "W* = A * (X* - Y*) + K* = 15 * 120 + 5 = 1805"),
        ("T3", 30, 40, 60, 12, "W* = A * K* + (X* + Y*) = 30 * 12 + 100 = 460"),
        ("T4", 20, 150, 50, 8, "W* = A * K* + (X* - Y*) = 20 * 8 + 100 = 260"),
        ("T5", 45, 0, 0, 16, "W* = A * K* = 45 * 16 = 720"),
    ]

    for tmpl, a, x_val, y_val, k_val, formula in test_vectors:
        x_cs = CarrySaveNumber.from_signed(x_val)
        y_cs = CarrySaveNumber.from_signed(y_val)
        k_cs = CarrySaveNumber.from_signed(k_val)

        res = fcu.execute(tmpl, A=a, X=x_cs, Y=y_cs, K=k_cs, clk=True, clk_gate_en=True)
        w_cs = res["result_cs"]
        bin_val = res["result_binary"]

        print(f"[{tmpl}] Formula: {formula}")
        print(f"       CS Result: {w_cs}")
        print(f"       CStoBin Output: {bin_val} | Crit. Delay: {res['critical_delay_tg']} Tg")

    print("\nSimulating Clock Gated cycle (clk_gate_en = False):")
    zero_cs = CarrySaveNumber.from_signed(0)
    gated_res = fcu.execute("T1", A=25, X=zero_cs, Y=zero_cs, K=zero_cs, clk=True, clk_gate_en=False)
    print(f"Gated execution: Status = {gated_res['status']} | Output = {gated_res['result_binary']}")

    metrics = fcu.get_power_metrics()
    print("\nFCU Hardware Metrics (Proposed System):")
    print(f"  - Gate Equivalent Area: {metrics['area_ag']:.1f} Ag")
    print(f"  - Critical Path Delay:  {metrics['critical_delay_tg']:.1f} Tg (vs 140 Tg in Existing FCC!)")
    print(f"  - Area-Delay Product:   {metrics['area_delay_product_adp']:.1f} Ag*Tg")
    print(f"  - Dynamic Power:        {metrics['dynamic_power_mw']:.4f} mW")
    print(f"  - Total Energy:         {metrics['energy_pj']:.4f} pJ")


def run_clock_gating_comparison():
    print("\n" + "=" * 70)
    print(" PROPOSED SYSTEM: CLOCK GATING POWER COMPARISON")
    print("=" * 70)

    samples = [10, 25, -15, 40, -50, 65, 80, -30, 20, 45, 90, -10]

    runner_no_cg = ProposedDSPKernelRunner()
    res_no_cg = runner_no_cg.run_fir16(samples, enable_clock_gating=False)

    runner_cg = ProposedDSPKernelRunner()
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
