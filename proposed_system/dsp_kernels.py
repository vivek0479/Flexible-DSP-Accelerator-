"""
DSP Benchmark Kernels mapped onto the Proposed FCU Architecture
Kernels from Table I & II of the IEEE TVLSI paper:
  1. FIR16: 16-tap Finite Impulse Response Filter
  2. ELLIPTIC: 6th-order Elliptic Filter section
  3. VOLTERRA: Nonlinear Volterra Filter
Key advantage:
  All chained intermediate values remain in Carry-Save format W* = {WC, WS}.
  Zero intermediate Carry-Propagate Adders are invoked!
  Final output is converted via CStoBin only when exiting the accelerator.
"""

from typing import List, Dict, Any
from .fcu_datapath import FlexibleComputationalUnit
from .cs_arithmetic import CarrySaveNumber, to_signed16


class ProposedDSPKernelRunner:
    """
    Executes benchmark DSP kernels on the proposed Flexible Computational Unit (FCU).
    Demonstrates Carry-Save operation chaining, high clock frequency, and clock gating.
    """

    def __init__(self, bit_width: int = 16):
        self.fcu = FlexibleComputationalUnit(bit_width=bit_width)

    def run_fir16(self, input_samples: List[int], coefficients: List[int] = None, enable_clock_gating: bool = True) -> Dict[str, Any]:
        """
        Executes a 16-tap FIR filter on the proposed FCU datapath.
        y[n] = sum_{k=0}^{15} h[k] * x[n-k]
        """
        if coefficients is None:
            coefficients = [12, -24, 48, -96, 180, -320, 600, -1200, 1200, -600, 320, -180, 96, -48, 24, -12]

        taps = len(coefficients)
        # Delay line holds Carry-Save numbers
        delay_line = [CarrySaveNumber.from_signed(0) for _ in range(taps)]
        outputs = []

        total_cycles = 0
        gated_cycles = 0

        zero_cs = CarrySaveNumber.from_signed(0)

        for sample in input_samples:
            # Insert new sample in Carry-Save form
            delay_line.pop()
            delay_line.insert(0, CarrySaveNumber.from_signed(sample))

            # Carry-Save accumulator
            accum_cs = CarrySaveNumber.from_signed(0)

            for i in range(0, taps, 2):
                h0 = coefficients[i]
                x0_cs = delay_line[i]
                h1 = coefficients[i + 1] if (i + 1) < taps else 0
                x1_cs = delay_line[i + 1] if (i + 1) < taps else zero_cs

                # Cycle 1: Multiply h0 * x0_cs directly in Carry-Save form
                res1 = self.fcu.execute("T5", A=h0, X=zero_cs, Y=zero_cs, K=x0_cs, clk=True, clk_gate_en=True)
                total_cycles += 1

                # Cycle 2: Accumulate h1 * x1_cs + previous accum_cs (Template T3)
                # Entire accumulation is in Carry-Save domain!
                res2 = self.fcu.execute("T3", A=h1, X=res1["result_cs"], Y=accum_cs, K=x1_cs, clk=True, clk_gate_en=True)
                accum_cs = res2["result_cs"]
                total_cycles += 1

            # Idle cycle with clock gating
            if enable_clock_gating:
                self.fcu.execute("T5", A=0, X=zero_cs, Y=zero_cs, K=zero_cs, clk=True, clk_gate_en=False)
                gated_cycles += 1
                total_cycles += 1

            # Final conversion to binary only at the output boundary
            out_binary = self.fcu.csto_bin.convert(accum_cs, clock_enabled=True)
            outputs.append(out_binary)

        power_metrics = self.fcu.get_power_metrics()
        return {
            "kernel": "FIR16",
            "outputs": outputs,
            "total_cycles": total_cycles,
            "gated_cycles": gated_cycles,
            "power_metrics": power_metrics,
        }

    def run_elliptic(self, input_samples: List[int], enable_clock_gating: bool = True) -> Dict[str, Any]:
        """
        Executes a 6th-order Elliptic filter section on the Proposed FCU.
        Intermediate values s1, s2, s3, s4 remain entirely in Carry-Save format!
        """
        outputs = []
        zero_cs = CarrySaveNumber.from_signed(0)
        s1 = CarrySaveNumber.from_signed(0)
        s2 = CarrySaveNumber.from_signed(0)
        s3 = CarrySaveNumber.from_signed(0)
        s4 = CarrySaveNumber.from_signed(0)

        c1, c2, c3, c4 = 345, -512, 128, 890
        total_cycles = 0

        for sample in input_samples:
            x_in = CarrySaveNumber.from_signed(sample)

            # Node 1: T1 template in Carry-Save: W1* = c1 * (x_in* + s1*) + s2*
            res1 = self.fcu.execute("T1", A=c1, X=x_in, Y=s1, K=s2, clk=True, clk_gate_en=True)
            w1_cs = res1["result_cs"]
            total_cycles += 1

            # Node 2: T2 template in Carry-Save: W2* = c2 * (w1* - s3*) + s4*
            res2 = self.fcu.execute("T2", A=c2, X=w1_cs, Y=s3, K=s4, clk=True, clk_gate_en=True)
            w2_cs = res2["result_cs"]
            total_cycles += 1

            # Node 3: T3 template in Carry-Save: W3* = c3 * s1* + (w1* + w2*)
            res3 = self.fcu.execute("T3", A=c3, X=w1_cs, Y=w2_cs, K=s1, clk=True, clk_gate_en=True)
            w3_cs = res3["result_cs"]
            total_cycles += 1

            # State updates (pure CS register transfers, zero conversion overhead)
            s4 = s3
            s3 = w2_cs
            s2 = s1
            s1 = w1_cs

            if enable_clock_gating:
                self.fcu.execute("T5", A=0, X=zero_cs, Y=zero_cs, K=zero_cs, clk=True, clk_gate_en=False)
                total_cycles += 1

            # Output converted via CStoBin
            out_bin = self.fcu.csto_bin.convert(w3_cs, clock_enabled=True)
            outputs.append(out_bin)

        power_metrics = self.fcu.get_power_metrics()
        return {
            "kernel": "ELLIPTIC",
            "outputs": outputs,
            "total_cycles": total_cycles,
            "power_metrics": power_metrics,
        }

    def run_volterra(self, input_samples: List[int], enable_clock_gating: bool = True) -> Dict[str, Any]:
        """
        Executes a 2nd-order Volterra filter on the Proposed FCU.
        """
        outputs = []
        zero_cs = CarrySaveNumber.from_signed(0)
        x_prev = CarrySaveNumber.from_signed(0)
        a, b, c, d = 420, 210, 15, 30
        total_cycles = 0

        for sample in input_samples:
            x_curr = CarrySaveNumber.from_signed(sample)

            # Term 1: a * (x_curr* + x_prev*)
            res1 = self.fcu.execute("T1", A=a, X=x_curr, Y=x_prev, K=zero_cs, clk=True, clk_gate_en=True)
            term1_cs = res1["result_cs"]
            total_cycles += 1

            # Term 2: c * (x_curr * x_curr)
            # Standalone mult using binary multiplicand x_curr.to_signed()
            res2 = self.fcu.execute("T5", A=x_curr.to_signed(), X=zero_cs, Y=zero_cs, K=x_curr, clk=True, clk_gate_en=True)
            x_sq_cs = res2["result_cs"]
            res3 = self.fcu.execute("T5", A=c, X=zero_cs, Y=zero_cs, K=x_sq_cs, clk=True, clk_gate_en=True)
            term2_cs = res3["result_cs"]
            total_cycles += 2

            # Term 3: d * (x_curr * x_prev) + term1 + term2
            res4 = self.fcu.execute("T5", A=x_curr.to_signed(), X=zero_cs, Y=zero_cs, K=x_prev, clk=True, clk_gate_en=True)
            cross_cs = res4["result_cs"]
            res5 = self.fcu.execute("T3", A=d, X=term1_cs, Y=term2_cs, K=cross_cs, clk=True, clk_gate_en=True)
            y_cs = res5["result_cs"]
            total_cycles += 2

            x_prev = x_curr

            if enable_clock_gating:
                self.fcu.execute("T5", A=0, X=zero_cs, Y=zero_cs, K=zero_cs, clk=True, clk_gate_en=False)
                total_cycles += 1

            y_out = self.fcu.csto_bin.convert(y_cs, clock_enabled=True)
            outputs.append(y_out)

        power_metrics = self.fcu.get_power_metrics()
        return {
            "kernel": "VOLTERRA",
            "outputs": outputs,
            "total_cycles": total_cycles,
            "power_metrics": power_metrics,
        }
