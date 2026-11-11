"""
CSA Tree Multiplier with Direct Carry-Save Accumulation
Implements:
  - Partial Product Generation (PPG) from CS-to-MB recoded digits
  - Carry-Save Adder (CSA) Wallace/Dadda compression tree
  - Fusion of third CS operand (K* or N*) directly into the CSA tree (Fig. 2)
  - Produces outputs directly in Carry-Save format W* = {WC, WS}
"""

from typing import List, Tuple, Dict, Any, Optional
from .cs_arithmetic import CarrySaveNumber, to_signed16, to_unsigned16
from .cs_to_mb_recoder import CSToMBRecoder
from .clock_gating import CSSwitchingActivityTracker


def _comp42(xc: int, xs: int, yc: int, ys: int, cin1: int = 0, cin2: int = 0, width: int = 16) -> Tuple[int, int]:
    final_s = 0
    final_c = 0
    c_horiz = cin1
    for i in range(width):
        xci = (xc >> i) & 1
        xsi = (xs >> i) & 1
        yci = (yc >> i) & 1
        ysi = (ys >> i) & 1
        sum1 = xsi ^ ysi ^ yci
        cout1 = (xsi & ysi) | (ysi & yci) | (xsi & yci)
        fs = sum1 ^ xci ^ c_horiz
        fc = (sum1 & xci) | (c_horiz & (sum1 ^ xci))
        final_s |= (fs << i)
        final_c |= (fc << i)
        c_horiz = cout1
    nc = ((final_c << 1) & ((1 << width) - 1)) | (cin2 & 1)
    ns = final_s & ((1 << width) - 1)
    return nc, ns


class CSATreeMultiplier:
    """
    Multiplier exploiting Carry-Save arithmetic and CS-to-MB recoding.
    Multiplies 16-bit 2's complement multiplicand A by Carry-Save multiplier P* = {PC, PS},
    and fuses an external Carry-Save operand ext_addend* = {ext_C, ext_S} directly
    into the CSA compression tree without any CPA!

    Output:
      W* = {WC, WS} in Carry-Save format.

    Unit Gate Model (IEEE TVLSI 2016):
      - PPG Area: ~450 Ag
      - CSA Tree Area: ~1500 Ag
      - Critical Delay: Delay(PPG) + Delay(CSA Tree) = 4 Tg + 24 Tg = 28 Tg
    """

    def __init__(self, bit_width: int = 16):
        self.bit_width = bit_width
        self.mask = (1 << bit_width) - 1
        self.recoder = CSToMBRecoder(bit_width=bit_width)
        self.area_ag = 450 + 1500  # 1950 Ag
        self.delay_tg = 28         # Fast CSA tree without final carry propagation
        self.tracker = CSSwitchingActivityTracker(bit_width=bit_width)

    def generate_partial_products(self, A: int, mb_digits: List[Dict[str, int]]) -> List[int]:
        """
        Generates 8 shifted partial products from 16-bit signed multiplicand A.
        """
        a_s = to_signed16(A)
        partial_products = []

        for digit_info in mb_digits:
            d = digit_info["digit"]
            shift = digit_info["shift"]
            if d == 0:
                pp = 0
            elif d == 1:
                pp = a_s
            elif d == -1:
                pp = -a_s
            elif d == 2:
                pp = a_s << 1
            elif d == -2:
                pp = -(a_s << 1)
            else:
                pp = d * a_s

            partial_products.append(pp << shift)

        return partial_products

    def multiply_and_accumulate(
        self,
        A: int,
        P: CarrySaveNumber,
        ext_addend: Optional[CarrySaveNumber] = None,
        subtract_ext: bool = False,
        clock_enabled: bool = True,
    ) -> CarrySaveNumber:
        """
        Performs W* = A * P* + ext_addend* (or - ext_addend*).
        Entire computation is carried out in the Carry-Save domain.
        """
        if not clock_enabled:
            self.tracker.record_cs_transition(0, 0, clock_enabled=False)
            return CarrySaveNumber(0, 0, self.bit_width)

        # Step 1: CS-to-MB recoding
        mb_digits = self.recoder.recode(P)

        # Step 2: Partial Product Generation (8 modulo 2^16 partial products)
        a_s = to_signed16(A)
        pps = []
        for d_info in mb_digits:
            d = d_info["digit"]
            sh = d_info["shift"]
            cand = d * a_s
            pps.append((cand << sh) & self.mask)
        while len(pps) < 8:
            pps.append(0)

        # Step 3: Structural CSA Reduction Tree (Level 1 and Level 2)
        ca, sa = _comp42(pps[0], pps[1], pps[2], pps[3], width=self.bit_width)
        cb, sb = _comp42(pps[4], pps[5], pps[6], pps[7], width=self.bit_width)
        cc, sc = _comp42(ca, sa, cb, sb, width=self.bit_width)

        # Step 4: Level 3 External Operand Fusion (fusing {ext_c, ext_s} without intermediate CPA)
        if ext_addend is not None:
            if subtract_ext:
                ext_c_in = (~ext_addend.carry) & self.mask
                ext_s_in = (~ext_addend.sum) & self.mask
                c1, c2 = 1, 1
            else:
                ext_c_in = ext_addend.carry & self.mask
                ext_s_in = ext_addend.sum & self.mask
                c1, c2 = 0, 0
        else:
            ext_c_in, ext_s_in, c1, c2 = 0, 0, 0, 0

        # Authentic dual-rail Carry-Save outputs from final 4:2 compressor
        w_carry, w_sum = _comp42(cc, sc, ext_c_in, ext_s_in, cin1=c1, cin2=c2, width=self.bit_width)

        result = CarrySaveNumber(carry=w_carry, sum_val=w_sum, bit_width=self.bit_width)
        self.tracker.record_cs_transition(result.carry, result.sum, clock_enabled=True)
        return result
