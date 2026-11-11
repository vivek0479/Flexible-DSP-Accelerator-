"""
Clock Gating Module for Proposed System (Carry-Save Datapath)
Implements:
  - Integrated Clock Gating (ICG) cell simulation
  - Dual-rail (Carry + Sum) switching activity tracking
  - Dynamic and static power models reflecting the Carry-Save architecture
"""

from typing import Dict, Any, Tuple


class CSClockGatingCell:
    """
    Negative-latch Integrated Clock Gating (ICG) cell for the Proposed FCU datapath.
    Guarantees glitch-free gating across both Carry and Sum arithmetic branches.
    """

    def __init__(self, name: str = "FCU_ICG"):
        self.name = name
        self.latch_state = False
        self.gated_clk = False
        self.total_cycles = 0
        self.gated_cycles = 0

    def evaluate(self, clk: bool, enable: bool) -> bool:
        """
        Evaluate clock gate on clock edge/phase.
        :param clk: Clock signal
        :param enable: Clock gate enable (True = active clock, False = gated/sleep)
        """
        # In cycle-based simulation where clk is evaluated once per cycle,
        # the latch captures enable during the setup / low phase preceding the active edge.
        self.latch_state = enable
        self.gated_clk = clk and self.latch_state

        if clk:
            self.total_cycles += 1
            if not self.latch_state:
                self.gated_cycles += 1

        return self.gated_clk

    @property
    def gating_efficiency(self) -> float:
        if self.total_cycles == 0:
            return 0.0
        return (self.gated_cycles / self.total_cycles) * 100.0


class CSSwitchingActivityTracker:
    """
    Tracks switching transitions on Carry-Save dual-rail buses (Carry vector + Sum vector).
    Each Carry-Save operand has 2x bits compared to standard 2's complement.
    However, eliminating intermediate carry-propagation glitches drastically reduces
    unnecessary switching activity in subsequent stages.
    """

    def __init__(self, bit_width: int = 16, unit_cap_pf: float = 0.035, vdd: float = 1.0, clk_freq_mhz: float = 625.0):
        self.bit_width = bit_width
        self.unit_cap_pf = unit_cap_pf  # Effective cap per bit (smaller wire lengths in CSA vs carry ripple)
        self.vdd = vdd
        self.clk_freq_mhz = clk_freq_mhz  # Higher clock frequency achievable in proposed FCU
        self.last_carry = 0
        self.last_sum = 0
        self.total_carry_toggles = 0
        self.total_sum_toggles = 0
        self.eval_count = 0

    def record_cs_transition(self, new_carry: int, new_sum: int, clock_enabled: bool = True) -> Tuple[int, int]:
        """
        Records transitions on both Carry and Sum words.
        If clock is gated, registers and downstream logic do not toggle.
        """
        self.eval_count += 1
        if not clock_enabled:
            return (0, 0)

        mask = (1 << self.bit_width) - 1
        c_val = new_carry & mask
        s_val = new_sum & mask

        c_toggles = bin(c_val ^ (self.last_carry & mask)).count("1")
        s_toggles = bin(s_val ^ (self.last_sum & mask)).count("1")

        self.total_carry_toggles += c_toggles
        self.total_sum_toggles += s_toggles

        self.last_carry = c_val
        self.last_sum = s_val

        return (c_toggles, s_toggles)

    def calculate_power(self, gate_equivalent_area: float) -> Dict[str, float]:
        cycles = max(1, self.eval_count)
        total_toggles = self.total_carry_toggles + self.total_sum_toggles
        # Dual-rail bus width = 2 * bit_width
        total_bus_bits = 2 * self.bit_width
        alpha = total_toggles / (cycles * total_bus_bits)

        # Dynamic power: P_dyn = alpha * C_eff * Vdd^2 * f
        c_eff_f = (total_bus_bits * self.unit_cap_pf * 1e-12)
        p_dynamic_w = alpha * c_eff_f * (self.vdd ** 2) * (self.clk_freq_mhz * 1e6)
        p_dynamic_mw = p_dynamic_w * 1e3

        # Leakage power at 65nm (~0.00045 mW per Ag)
        p_leakage_mw = gate_equivalent_area * 0.00045

        total_power_mw = p_dynamic_mw + p_leakage_mw
        total_time_ns = cycles * (1000.0 / self.clk_freq_mhz)
        energy_pj = total_power_mw * total_time_ns

        return {
            "total_carry_toggles": self.total_carry_toggles,
            "total_sum_toggles": self.total_sum_toggles,
            "total_toggles": total_toggles,
            "avg_switching_activity_alpha": alpha,
            "dynamic_power_mw": p_dynamic_mw,
            "leakage_power_mw": p_leakage_mw,
            "total_power_mw": total_power_mw,
            "total_time_ns": total_time_ns,
            "energy_pj": energy_pj,
        }
