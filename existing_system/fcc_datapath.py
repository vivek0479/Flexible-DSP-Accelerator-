"""
Flexible Computational Component (FCC) Datapath for Existing System
Implements:
  - Conventional Two's Complement flexible datapath (Galanis et al. [4] & Fig. 4(a))
  - Operation Templates T1 - T5 using sequential Carry-Propagate Adders (CPA)
  - Integrated Clock Gating (ICG) cell for unit and register bank
  - Area, Delay, Switching Activity, and Energy estimation
"""

from typing import Dict, Any, List
from .arithmetic_units import CarryPropagateAdder, ModifiedBoothMultiplier16, to_signed16, to_unsigned16
from .clock_gating import ClockGatingCell, SwitchingActivityTracker


class FCCRegisterBank:
    """
    Scratch Register Bank for Existing Datapath.
    Stores intermediate 16-bit Two's Complement values.
    Controlled by Integrated Clock Gating (ICG).
    """

    def __init__(self, num_registers: int = 8, bit_width: int = 16):
        self.num_registers = num_registers
        self.bit_width = bit_width
        self.registers = [0] * num_registers
        self.icg = ClockGatingCell(name="FCC_RegBank_ICG")
        self.trackers = [SwitchingActivityTracker(bit_width=bit_width) for _ in range(num_registers)]

    def read(self, reg_idx: int) -> int:
        return self.registers[reg_idx % self.num_registers]

    def write(self, reg_idx: int, value: int, clk: bool = True, clk_gate_en: bool = True):
        """
        Write to register with clock gating.
        :param reg_idx: Register index
        :param value: 16-bit value
        :param clk: Clock signal
        :param clk_gate_en: Clock Gating Input (True = Clock enabled, False = Gated)
        """
        gated_clk = self.icg.evaluate(clk=clk, enable=clk_gate_en)
        if gated_clk:
            idx = reg_idx % self.num_registers
            self.registers[idx] = to_signed16(value)
            self.trackers[idx].record_transition(value, clock_enabled=True)
        else:
            # Gated: no write and no switching activity
            idx = reg_idx % self.num_registers
            self.trackers[idx].record_transition(self.registers[idx], clock_enabled=False)


class FlexibleComputationalComponent:
    """
    Conventional Flexible Computational Component (FCC).
    Implements Operation Templates T1 to T5:
      T1: W = A * (X + Y) + K
      T2: W = A * (X - Y) + K
      T3: W = A * K + (X + Y)
      T4: W = A * K + (X - Y)
      T5: W = A * K  (or standalone additions/multiplications)

    Key characteristic of Existing System:
      Every addition/subtraction chained with multiplication uses a Carry-Propagate Adder (CPA).
      Critical Path: Delay(CPA1) + Delay(Multiplier) + Delay(CPA2) + Delay(MUXes).
    """

    def __init__(self, bit_width: int = 16, clk_freq_mhz: float = 500.0):
        self.bit_width = bit_width
        self.clk_freq_mhz = clk_freq_mhz

        # Functional Units
        self.pre_adder = CarryPropagateAdder(bit_width=bit_width)
        self.multiplier = ModifiedBoothMultiplier16(bit_width=bit_width)
        self.post_adder = CarryPropagateAdder(bit_width=bit_width)
        self.reg_bank = FCCRegisterBank(num_registers=8, bit_width=bit_width)

        # Clock Gating Unit for FCC
        self.icg = ClockGatingCell(name="FCC_Core_ICG")
        self.output_tracker = SwitchingActivityTracker(bit_width=bit_width, clk_freq_mhz=clk_freq_mhz)

        # Gate Equivalent Area (Ag) and Delay (Tg) from paper Table II and Fig. 4(a)
        # Pre-adder CPA: 112 Ag, Multiplier: 2800 Ag, Post-adder CPA: 112 Ag, MUXes & glue: ~250 Ag
        self.area_ag = 112 + 2800 + 112 + 250  # ~3274 Ag per FCC
        # Critical delay: 32 Tg (CPA1) + 68 Tg (Multiplier) + 32 Tg (CPA2) + 8 Tg (MUX) = 140 Tg (~1.68ns at 65nm)
        self.delay_tg = 140

    def execute(
        self,
        template: str,
        A: int,
        X: int,
        Y: int,
        K: int,
        clk: bool = True,
        clk_gate_en: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes an operation template with explicit clock gating input.
        :param template: One of 'T1', 'T2', 'T3', 'T4', 'T5'
        :param A: Multiplicand (16-bit 2's complement)
        :param X: Addend 1 (16-bit 2's complement)
        :param Y: Addend 2 (16-bit 2's complement)
        :param K: Accumulator/Offset (16-bit 2's complement)
        :param clk: Clock line
        :param clk_gate_en: Clock Gating Input (True = Active, False = Gated)
        :return: Execution trace dict containing result, delays, and power metrics
        """
        gated_clk = self.icg.evaluate(clk=clk, enable=clk_gate_en)

        if not gated_clk:
            # Fully clock-gated: No switching in functional units
            self.pre_adder.tracker.record_transition(0, clock_enabled=False)
            self.multiplier.tracker.record_transition(0, clock_enabled=False)
            self.post_adder.tracker.record_transition(0, clock_enabled=False)
            self.output_tracker.record_transition(0, clock_enabled=False)
            return {
                "template": template,
                "result": 0,
                "gated": True,
                "cycles": 1,
                "critical_delay_tg": self.delay_tg,
                "status": "CLOCK_GATED",
            }

        result = 0
        intermediate_steps = {}

        if template == "T1":
            # W = A * (X + Y) + K
            # Step 1: Pre-addition via CPA
            sum_xy, _ = self.pre_adder.compute(X, Y, c_in=0, clock_enabled=True)
            intermediate_steps["X_plus_Y"] = sum_xy

            # Step 2: Multiplication via Booth Multiplier
            prod = self.multiplier.multiply(A, sum_xy, clock_enabled=True)
            intermediate_steps["A_mult_sum"] = prod

            # Step 3: Post-addition via CPA
            result, _ = self.post_adder.compute(prod, K, c_in=0, clock_enabled=True)

        elif template == "T2":
            # W = A * (X - Y) + K
            # Subtraction using 2's complement: X + (~Y) + 1
            y_inv = (~to_unsigned16(Y)) & 0xFFFF
            diff_xy, _ = self.pre_adder.compute(X, y_inv, c_in=1, clock_enabled=True)
            intermediate_steps["X_minus_Y"] = diff_xy

            prod = self.multiplier.multiply(A, diff_xy, clock_enabled=True)
            intermediate_steps["A_mult_diff"] = prod

            result, _ = self.post_adder.compute(prod, K, c_in=0, clock_enabled=True)

        elif template == "T3":
            # W = A * K + (X + Y)
            # Step 1: Multiplication A * K
            prod = self.multiplier.multiply(A, K, clock_enabled=True)
            intermediate_steps["A_mult_K"] = prod

            # Step 2: Pre-addition (X + Y)
            sum_xy, _ = self.pre_adder.compute(X, Y, c_in=0, clock_enabled=True)
            intermediate_steps["X_plus_Y"] = sum_xy

            # Step 3: Post-addition CPA prod + sum_xy
            result, _ = self.post_adder.compute(prod, sum_xy, c_in=0, clock_enabled=True)

        elif template == "T4":
            # W = A * K + (X - Y)
            prod = self.multiplier.multiply(A, K, clock_enabled=True)
            y_inv = (~to_unsigned16(Y)) & 0xFFFF
            diff_xy, _ = self.pre_adder.compute(X, y_inv, c_in=1, clock_enabled=True)
            result, _ = self.post_adder.compute(prod, diff_xy, c_in=0, clock_enabled=True)

        elif template == "T5":
            # W = A * K (standalone multiplication)
            result = self.multiplier.multiply(A, K, clock_enabled=True)

        else:
            raise ValueError(f"Unknown template: {template}. Supported: T1, T2, T3, T4, T5")

        self.output_tracker.record_transition(result, clock_enabled=True)

        return {
            "template": template,
            "inputs": {"A": A, "X": X, "Y": Y, "K": K},
            "intermediate": intermediate_steps,
            "result": result,
            "gated": False,
            "cycles": 1,
            "critical_delay_tg": self.delay_tg,
            "status": "COMPLETED",
        }

    def get_power_metrics(self) -> Dict[str, Any]:
        """Collects combined power and switching metrics across all units."""
        pre_p = self.pre_adder.tracker.calculate_power(self.pre_adder.area_ag)
        mult_p = self.multiplier.tracker.calculate_power(self.multiplier.area_ag)
        post_p = self.post_adder.tracker.calculate_power(self.post_adder.area_ag)
        out_p = self.output_tracker.calculate_power(self.area_ag)

        total_dynamic_mw = pre_p["dynamic_power_mw"] + mult_p["dynamic_power_mw"] + post_p["dynamic_power_mw"]
        total_leakage_mw = out_p["leakage_power_mw"]
        total_power_mw = total_dynamic_mw + total_leakage_mw
        total_energy_pj = total_power_mw * out_p["total_time_ns"]

        return {
            "area_ag": self.area_ag,
            "critical_delay_tg": self.delay_tg,
            "area_delay_product_adp": self.area_ag * self.delay_tg,
            "icg_gating_efficiency_pct": self.icg.gating_efficiency,
            "total_cycles": self.icg.total_cycles,
            "gated_cycles": self.icg.gated_cycles,
            "dynamic_power_mw": total_dynamic_mw,
            "leakage_power_mw": total_leakage_mw,
            "total_power_mw": total_power_mw,
            "energy_pj": total_energy_pj,
        }
