"""
Flexible Computational Unit (FCU) Datapath for Proposed System
Implements:
  - Proposed Carry-Save Flexible Architecture (Fig. 1, 2, 3 of IEEE TVLSI 2016)
  - Configurable MUX network (MUX0, MUX1, MUX2, MUX3) supporting Templates T1 - T5
  - Direct Carry-Save chaining between operations without intermediate CPAs
  - Final CStoBin ripple-carry module
  - Dual-rail Clock Gating (ICG) and switching activity tracking
"""

from typing import Dict, Any, List, Optional
from .cs_arithmetic import CarrySaveNumber, CarrySaveCompressor42, to_signed16, to_unsigned16
from .csa_tree_multiplier import CSATreeMultiplier
from .clock_gating import CSClockGatingCell, CSSwitchingActivityTracker


class FCURegisterBank:
    """
    Scratch Register Bank storing Carry-Save formatted operands.
    Each register holds a pair of vectors: {XC, XS}.
    Integrated with clock gating.
    """

    def __init__(self, num_registers: int = 8, bit_width: int = 16):
        self.num_registers = num_registers
        self.bit_width = bit_width
        self.registers = [CarrySaveNumber(0, 0, bit_width) for _ in range(num_registers)]
        self.icg = CSClockGatingCell(name="FCU_RegBank_ICG")
        self.trackers = [CSSwitchingActivityTracker(bit_width=bit_width) for _ in range(num_registers)]

    def read(self, reg_idx: int) -> CarrySaveNumber:
        return self.registers[reg_idx % self.num_registers]

    def write(self, reg_idx: int, val: CarrySaveNumber, clk: bool = True, clk_gate_en: bool = True):
        gated_clk = self.icg.evaluate(clk=clk, enable=clk_gate_en)
        idx = reg_idx % self.num_registers
        if gated_clk:
            self.registers[idx] = val
            self.trackers[idx].record_cs_transition(val.carry, val.sum, clock_enabled=True)
        else:
            self.trackers[idx].record_cs_transition(self.registers[idx].carry, self.registers[idx].sum, clock_enabled=False)


class CStoBinModule:
    """
    CStoBin Module (Fig. 1 of paper).
    Ripple-carry / carry-propagate adder placed only at the accelerator boundary
    to convert the final Carry-Save output to Two's Complement binary.
    Runs in parallel with other FCU operations.
    Area: 112 Ag, Delay: 32 Tg.
    """

    def __init__(self, bit_width: int = 16):
        self.bit_width = bit_width
        self.mask = (1 << bit_width) - 1
        self.area_ag = 112
        self.delay_tg = 32
        self.tracker = CSSwitchingActivityTracker(bit_width=bit_width)

    def convert(self, cs_num: CarrySaveNumber, clock_enabled: bool = True) -> int:
        if not clock_enabled:
            self.tracker.record_cs_transition(0, 0, clock_enabled=False)
            return 0
        raw_sum = (cs_num.carry + cs_num.sum) & self.mask
        if raw_sum >= (1 << (self.bit_width - 1)):
            signed_val = raw_sum - (1 << self.bit_width)
        else:
            signed_val = raw_sum
        self.tracker.record_cs_transition(cs_num.carry, cs_num.sum, clock_enabled=True)
        return signed_val


class FlexibleComputationalUnit:
    """
    Proposed Flexible Computational Unit (FCU).
    Directly operates on Carry-Save formatted operands.
    Supports operation templates T1 to T5 (Fig. 3):
      W* = A * (X* + Y*) + K*  (T1)
      W* = A * (X* - Y*) + K*  (T2)
      W* = A * K* + (X* + Y*)  (T3)
      W* = A * K* + (X* - Y*)  (T4)
      W* = A * K*              (T5)

    Area & Delay (from Section IV & V of paper):
      - 4:2 CS Adder: 224 Ag, 4 Tg
      - CS-to-MB Recoder + PPG: 690 Ag, 8 Tg
      - CSA Tree Multiplier: 1500 Ag, 24 Tg
      - MUX0 - MUX3: ~210 Ag, 4 Tg
      - Total FCU Area: ~2624 Ag (Significant reduction over FCC's 3274 Ag)
      - Total FCU Critical Delay: ~40 Tg (~1.13ns at 65nm, >60% faster than FCC)
    """

    def __init__(self, bit_width: int = 16, clk_freq_mhz: float = 625.0):
        self.bit_width = bit_width
        self.clk_freq_mhz = clk_freq_mhz

        # Functional Units
        self.compressor_42 = CarrySaveCompressor42(bit_width=bit_width)
        self.csa_multiplier = CSATreeMultiplier(bit_width=bit_width)
        self.reg_bank = FCURegisterBank(num_registers=8, bit_width=bit_width)
        self.csto_bin = CStoBinModule(bit_width=bit_width)

        # Clock Gating Unit
        self.icg = CSClockGatingCell(name="FCU_Core_ICG")
        self.output_tracker = CSSwitchingActivityTracker(bit_width=bit_width, clk_freq_mhz=clk_freq_mhz)

        self.area_ag = 2624
        self.delay_tg = 40  # 40 Tg vs 140 Tg in existing FCC!

    def execute(
        self,
        template: str,
        A: int,
        X: CarrySaveNumber,
        Y: CarrySaveNumber,
        K: CarrySaveNumber,
        clk: bool = True,
        clk_gate_en: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes an FCU template operation in Carry-Save arithmetic.
        :param template: 'T1', 'T2', 'T3', 'T4', or 'T5'
        :param A: 16-bit 2's complement multiplicand
        :param X: Carry-Save input X*
        :param Y: Carry-Save input Y*
        :param K: Carry-Save input K*
        :param clk: Clock signal
        :param clk_gate_en: Clock Gating Input
        :return: Execution trace dictionary with Carry-Save output W*
        """
        gated_clk = self.icg.evaluate(clk=clk, enable=clk_gate_en)

        if not gated_clk:
            # Gated: Zero switching across all functional units
            self.compressor_42.tracker.record_cs_transition(0, 0, clock_enabled=False)
            self.csa_multiplier.tracker.record_cs_transition(0, 0, clock_enabled=False)
            self.output_tracker.record_cs_transition(0, 0, clock_enabled=False)
            return {
                "template": template,
                "result_cs": CarrySaveNumber(0, 0, self.bit_width),
                "result_binary": 0,
                "gated": True,
                "cycles": 1,
                "critical_delay_tg": self.delay_tg,
                "status": "CLOCK_GATED",
            }

        # Decode Configuration signals according to Section III.A:
        # CL0: MUX0 (0 -> Y*, 1 -> ~Y*)
        # CL1: MUX1 (0 -> P*=N*, 1 -> P*=K*)
        # CL2: MUX2 (0 -> ext=K*, 1 -> ext=N*)
        # CL3: MUX3 (0 -> add, 1 -> sub)
        if template == "T1":
            cl0, cl1, cl2, cl3 = 0, 0, 0, 0
        elif template == "T2":
            cl0, cl1, cl2, cl3 = 1, 0, 0, 0
        elif template == "T3":
            cl0, cl1, cl2, cl3 = 0, 1, 1, 0
        elif template == "T4":
            cl0, cl1, cl2, cl3 = 1, 1, 1, 0
        elif template == "T5":
            cl0, cl1, cl2, cl3 = 0, 1, 0, 0
        else:
            raise ValueError(f"Unknown FCU template: {template}")

        # Step 1: MUX0 and 4:2 Compressor
        cin_42 = 1 if cl0 == 1 else 0
        N, _ = self.compressor_42.compress(X, Y, c_in=cin_42, clock_enabled=True)

        # Step 2: MUX1 (Selects multiplier input P*)
        P = K if cl1 == 1 else N

        # Step 3: MUX2 and MUX3 (Selects external CSA addend)
        if template == "T5":
            ext_operand = None
            subtract_ext = False
        else:
            ext_operand = N if cl2 == 1 else K
            subtract_ext = (cl3 == 1)

        # Step 4: Multiplier with CS-to-MB recoding and CSA tree accumulation
        W = self.csa_multiplier.multiply_and_accumulate(
            A=A,
            P=P,
            ext_addend=ext_operand,
            subtract_ext=subtract_ext,
            clock_enabled=True,
        )

        self.output_tracker.record_cs_transition(W.carry, W.sum, clock_enabled=True)

        # Convert to binary via CStoBin (only needed if inspected at boundary)
        binary_val = self.csto_bin.convert(W, clock_enabled=True)

        return {
            "template": template,
            "result_cs": W,
            "result_binary": binary_val,
            "gated": False,
            "cycles": 1,
            "critical_delay_tg": self.delay_tg,
            "status": "COMPLETED",
        }

    def get_power_metrics(self) -> Dict[str, Any]:
        """Collects combined power and switching metrics across FCU units."""
        comp_p = self.compressor_42.tracker.calculate_power(self.compressor_42.area_ag)
        mult_p = self.csa_multiplier.tracker.calculate_power(self.csa_multiplier.area_ag)
        out_p = self.output_tracker.calculate_power(self.area_ag)

        total_dynamic_mw = comp_p["dynamic_power_mw"] + mult_p["dynamic_power_mw"]
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
