"""
Arithmetic Primitives for Existing System (Two's Complement Datapath)
Implements:
  - 16-bit Two's Complement Integer Helpers
  - Bit-accurate Carry-Propagate Adder (CPA)
  - Radix-4 Modified Booth Multiplier (requiring 2's complement binary inputs)
  - Unit Gate Model Metrics (Area in Ag, Delay in Tg) as defined in the IEEE TVLSI paper
"""

from typing import Tuple, List
from .clock_gating import SwitchingActivityTracker


def to_signed16(val: int) -> int:
    """Converts an integer to signed 16-bit two's complement (-32768 to 32767)."""
    val = val & 0xFFFF
    if val >= 0x8000:
        return val - 0x10000
    return val


def to_unsigned16(val: int) -> int:
    """Converts a signed integer to unsigned 16-bit representation (0 to 65535)."""
    return val & 0xFFFF


class CarryPropagateAdder:
    """
    16-bit Carry-Propagate Adder (CPA / Ripple Carry Adder).
    Performs A + B + Cin with bit-level carry propagation.
    Unit Gate Model (IEEE TVLSI 2016 Section IV):
      - Full Adder (FA): Area = 7 Ag, Delay = 4 Tg
      - Half Adder (HA): Area = 3 Ag, Delay = 2 Tg
      - 16-bit Ripple-Carry CPA Area: 16 * 7 = 112 Ag
      - 16-bit Critical Delay: 2 * 16 Tg = 32 Tg
    """

    def __init__(self, bit_width: int = 16):
        self.bit_width = bit_width
        self.area_ag = bit_width * 7  # 112 Ag for 16 bits
        self.delay_tg = 2 * bit_width  # 32 Tg for ripple carry
        self.tracker = SwitchingActivityTracker(bit_width=bit_width)

    def compute(self, a_val: int, b_val: int, c_in: int = 0, clock_enabled: bool = True) -> Tuple[int, int]:
        """
        Bit-level addition.
        :param a_val: First 16-bit operand (signed or unsigned)
        :param b_val: Second 16-bit operand
        :param c_in: Carry-in bit (0 or 1)
        :param clock_enabled: Clock gating enable
        :return: (sum_16bit, carry_out)
        """
        a_u = to_unsigned16(a_val)
        b_u = to_unsigned16(b_val)
        carry = c_in & 1
        sum_bits = []

        for bit in range(self.bit_width):
            a_bit = (a_u >> bit) & 1
            b_bit = (b_u >> bit) & 1
            s_bit = a_bit ^ b_bit ^ carry
            carry = (a_bit & b_bit) | (carry & (a_bit ^ b_bit))
            sum_bits.append(s_bit)

        result = 0
        for bit, val in enumerate(sum_bits):
            if val:
                result |= (1 << bit)

        # Track switching activity
        self.tracker.record_transition(result, clock_enabled=clock_enabled)
        return to_signed16(result), carry


class ModifiedBoothMultiplier16:
    """
    Conventional Radix-4 Modified Booth Multiplier for 16-bit signed operands.
    Standard approach:
      - Requires 2's complement binary inputs.
      - If input was Carry-Save, an intermediate CPA must first convert it to binary.
      - Generates 8 partial products using Radix-4 recoding:
          d_i in {-2, -1, 0, 1, 2}
      - Partial products accumulated using Carry-Propagate / Wallace tree.
    Unit Gate Model Area: ~2800 Ag, Critical Delay: ~65 Tg (at 65nm approx 1.68ns)
    """

    def __init__(self, bit_width: int = 16):
        self.bit_width = bit_width
        self.area_ag = 2800  # Gate equivalents for 16x16 Booth multiplier with CPA reduction
        self.delay_tg = 68   # Critical path delay in Tg
        self.tracker = SwitchingActivityTracker(bit_width=bit_width)

    def recode_radix4(self, b_val: int) -> List[int]:
        """
        Generates 8 Radix-4 Booth digits from 16-bit signed operand B.
        Triplet (b_{2i+1}, b_{2i}, b_{2i-1}) with b_{-1} = 0.
        digit = -2*b_{2i+1} + b_{2i} + b_{2i-1}
        """
        b_u = to_unsigned16(b_val)
        # Sign extend to 18 bits for proper recoding
        sign_bit = (b_u >> 15) & 1
        extended = b_u | (sign_bit << 16) | (sign_bit << 17)

        digits = []
        for i in range(8):
            b_low = (b_u >> (2 * i - 1)) & 1 if i > 0 else 0
            b_mid = (b_u >> (2 * i)) & 1
            b_high = (extended >> (2 * i + 1)) & 1
            digit = -2 * b_high + b_mid + b_low
            digits.append(digit)
        return digits

    def multiply(self, a_val: int, b_val: int, clock_enabled: bool = True) -> int:
        """
        Performs 16-bit x 16-bit multiplication.
        As specified in paper Section III.A:
          Product is truncated/scaled to 16 bits (MSB portion or wrapped 16-bit arithmetic)
        """
        a_s = to_signed16(a_val)
        b_s = to_signed16(b_val)

        if not clock_enabled:
            # Gated: multiplier output frozen
            self.tracker.record_transition(0, clock_enabled=False)
            return 0

        digits = self.recode_radix4(b_s)
        accum = 0
        for i, digit in enumerate(digits):
            pp = digit * a_s
            accum += (pp << (2 * i))

        # Paper: inputs are 16-bit, product MSBs or lower 16 bits depending on scaling.
        # In DSP accelerators, standard fixed-point Q15 or 16-bit integer output:
        # We retain 16-bit signed range (or Q15 fractional scaling >> 15, or lower 16-bit wrap)
        # For integer DSP templates:
        result = to_signed16(accum)
        self.tracker.record_transition(result, clock_enabled=clock_enabled)
        return result
