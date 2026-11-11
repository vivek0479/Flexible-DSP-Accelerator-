"""
Clock Gating Module for Existing System
Implements:
  - Integrated Clock Gating (ICG) cell simulation (latch-based)
  - Switching activity tracking on word buses and registers
  - Dynamic and static power estimation for conventional two's complement datapath
"""

from typing import Dict, Any


class ClockGatingCell:
    """
    Models a negative-latch-based Integrated Clock Gating (ICG) cell.
    Logic:
      - When clock is LOW, latch captures enable input: latch_state = enable
      - Gated clock output = clock AND latch_state
    This guarantees glitch-free clock gating.
    """

    def __init__(self, name: str = "ICG"):
        self.name = name
        self.latch_state = False
        self.gated_clk = False
        self.total_cycles = 0
        self.gated_cycles = 0  # cycles where clock was shut off (enable == False)

    def evaluate(self, clk: bool, enable: bool) -> bool:
        """
        Evaluate clock gate on clock edge/phase.
        :param clk: Clock level (True = High, False = Low)
        :param enable: Clock gate enable (True = Clock ON / active, False = Clock GATED / sleep)
        :return: Gated clock signal
        """
        # In cycle-based simulation where clk is evaluated once per cycle,
        # the latch captures enable during the setup / low phase preceding the active edge.
        self.latch_state = enable
        self.gated_clk = clk and self.latch_state

        if clk:  # Count at rising edge / high phase
            self.total_cycles += 1
            if not self.latch_state:
                self.gated_cycles += 1

        return self.gated_clk

    @property
    def gating_efficiency(self) -> float:
        """Percentage of cycles the unit was safely clock-gated."""
        if self.total_cycles == 0:
            return 0.0
        return (self.gated_cycles / self.total_cycles) * 100.0


class SwitchingActivityTracker:
    """
    Monitors bit flips (0->1 and 1->0) on registers and arithmetic units.
    Calculates dynamic power dissipation based on CMOS switching activity:
      P_dyn = 0.5 * alpha * C_eff * Vdd^2 * f_clk
    """

    def __init__(self, bit_width: int = 16, unit_cap_pf: float = 0.05, vdd: float = 1.0, clk_freq_mhz: float = 500.0):
        self.bit_width = bit_width
        self.unit_cap_pf = unit_cap_pf  # Effective capacitance per bit transition
        self.vdd = vdd  # Supply voltage in Volts
        self.clk_freq_mhz = clk_freq_mhz  # Clock frequency in MHz
        self.last_value = 0
        self.total_bit_toggles = 0
        self.eval_count = 0

    def record_transition(self, new_value: int, clock_enabled: bool = True) -> int:
        """
        Record bit toggles when clock is active.
        If clock is gated (clock_enabled=False), no register switching occurs.
        """
        self.eval_count += 1
        if not clock_enabled:
            # Gated: No switching in register or subsequent combinational cone
            return 0

        mask = (1 << self.bit_width) - 1
        val = new_value & mask
        toggles = bin(val ^ (self.last_value & mask)).count("1")
        self.total_bit_toggles += toggles
        self.last_value = val
        return toggles

    def calculate_power(self, gate_equivalent_area: float) -> Dict[str, float]:
        """
        Calculates dynamic power, static leakage power, and total energy.
        :param gate_equivalent_area: Circuit area in Gate Equivalents (Ag)
        :return: Dictionary containing power metrics
        """
        # Average switching activity factor alpha
        cycles = max(1, self.eval_count)
        alpha = self.total_bit_toggles / (cycles * self.bit_width)

        # Dynamic power in mW: P_dyn = alpha * (bit_width * C_bit) * Vdd^2 * f
        c_eff_f = (self.bit_width * self.unit_cap_pf * 1e-12)
        p_dynamic_w = alpha * c_eff_f * (self.vdd ** 2) * (self.clk_freq_mhz * 1e6)
        p_dynamic_mw = p_dynamic_w * 1e3

        # Leakage power model proportional to circuit area (approx 0.0005 mW per Ag at 65nm)
        p_leakage_mw = gate_equivalent_area * 0.0005

        total_power_mw = p_dynamic_mw + p_leakage_mw
        total_time_ns = cycles * (1000.0 / self.clk_freq_mhz)
        energy_pj = total_power_mw * total_time_ns

        return {
            "total_toggles": self.total_bit_toggles,
            "avg_switching_activity_alpha": alpha,
            "dynamic_power_mw": p_dynamic_mw,
            "leakage_power_mw": p_leakage_mw,
            "total_power_mw": total_power_mw,
            "total_time_ns": total_time_ns,
            "energy_pj": energy_pj,
        }
