"""
Direct Carry-Save to Modified Booth (CS-to-MB) Recoder
Implements the recoding technique of Tsoumanis et al. [19] (IEEE TCAS-I 2014 & IEEE TVLSI 2016):
  Directly recodes a Carry-Save operand P* = {PC, PS} into Radix-4 Modified Booth digits
  d_i in {-2, -1, 0, 1, 2} WITHOUT any prior Carry-Propagate Addition!
"""

from typing import List, Dict, Tuple
from .cs_arithmetic import CarrySaveNumber, to_signed16, to_unsigned16


class CSToMBRecoder:
    """
    Direct Carry-Save to Modified Booth (CS-to-MB) Recoder.
    Eliminates the CPA converter bottleneck before the multiplier.

    Mathematical Principle:
      At each radix-4 digit position i (weight 2^{2i}):
        val_i = 2 * (PC[2i+1] + PS[2i+1]) + (PC[2i] + PS[2i]) + Cin_i
      Then val_i is partitioned as:
        val_i = d_i + 4 * Cout_i
      where d_i in {-2, -1, 0, 1, 2} and Cout_i in {0, 1, 2}.

    Unit Gate Model:
      Area: ~240 Ag (constant logic per radix-4 digit)
      Critical Delay: ~8 Tg (local lookahead, no global carry ripple)
    """

    def __init__(self, bit_width: int = 16):
        self.bit_width = bit_width
        self.num_digits = (bit_width + 1) // 2  # 8 digits for 16 bits
        self.area_ag = 240
        self.delay_tg = 8

    def recode(self, P: CarrySaveNumber) -> List[Dict[str, int]]:
        """
        Recodes the Carry-Save operand P* = {PC, PS} into Radix-4 digits.
        :param P: CarrySaveNumber {PC, PS}
        :return: List of digit descriptor dictionaries containing:
                 - 'digit': numerical value in {-2, -1, 0, 1, 2}
                 - 'zero': 1 if digit == 0 else 0
                 - 'one': 1 if abs(digit) == 1 else 0
                 - 'two': 1 if abs(digit) == 2 else 0
                 - 'neg': 1 if digit < 0 else 0
        """
        pc = P.carry
        ps = P.sum

        # Sign extend to handle two's complement sign
        # MSB sign bits:
        pc_sign = (pc >> (self.bit_width - 1)) & 1
        ps_sign = (ps >> (self.bit_width - 1)) & 1

        # Extend carry and sum by 2 bits for 17-bit intermediate arithmetic (Section III.A)
        pc_ext = pc | (pc_sign << self.bit_width) | (pc_sign << (self.bit_width + 1))
        ps_ext = ps | (ps_sign << self.bit_width) | (ps_sign << (self.bit_width + 1))

        digits = []
        c_transfer = 0

        for i in range(self.num_digits):
            bit2i = 2 * i
            bit2i_p1 = 2 * i + 1

            pc_0 = (pc_ext >> bit2i) & 1
            ps_0 = (ps_ext >> bit2i) & 1
            pc_1 = (pc_ext >> bit2i_p1) & 1
            ps_1 = (ps_ext >> bit2i_p1) & 1

            # Sum of weighted bits at this radix-4 position:
            val_i = 2 * (pc_1 + ps_1) + (pc_0 + ps_0) + c_transfer

            # Direct mapping from val_i to (d_i, Cout_i)
            # val_i = d_i + 4 * Cout_i with d_i in {-2, -1, 0, 1, 2}
            if val_i == 0:
                d_i, c_transfer = 0, 0
            elif val_i == 1:
                d_i, c_transfer = 1, 0
            elif val_i == 2:
                d_i, c_transfer = 2, 0
            elif val_i == 3:
                d_i, c_transfer = -1, 1
            elif val_i == 4:
                d_i, c_transfer = 0, 1
            elif val_i == 5:
                d_i, c_transfer = 1, 1
            elif val_i == 6:
                d_i, c_transfer = 2, 1
            elif val_i == 7:
                d_i, c_transfer = -1, 2
            elif val_i == 8:
                d_i, c_transfer = 0, 2
            else:
                d_i, c_transfer = (val_i % 4), (val_i // 4)

            # Format Booth control signals
            digits.append({
                "digit": d_i,
                "zero": 1 if d_i == 0 else 0,
                "one": 1 if abs(d_i) == 1 else 0,
                "two": 1 if abs(d_i) == 2 else 0,
                "neg": 1 if d_i < 0 else 0,
                "position": i,
                "shift": 2 * i,
            })

        return digits
