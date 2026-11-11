"""
DSP Benchmark Kernels mapped onto the Existing System (FCC Datapath)
Kernels from Table I & II of the IEEE TVLSI paper:
  1. FIR16: 16-tap Finite Impulse Response Filter
  2. ELLIPTIC: 6th-order Elliptic Filter section
  3. VOLTERRA: Nonlinear Volterra Filter
Supports explicit clock gating inputs during inactive/active cycles.
"""

from typing import List, Dict, Any
from .fcc_datapath import FlexibleComputationalComponent
from .arithmetic_units import to_signed16


class ExistingDSPKernelRunner:
    """
    Executes benchmark DSP kernels on the conventional Flexible Computational Component (FCC).
    Demonstrates cycle-by-cycle execution, operation chaining, and clock gating.
    """

    def __init__(self, bit_width: int = 16):
        self.fcc = FlexibleComputationalComponent(bit_width=bit_width)

    def run_fir16(self, input_samples: List[int], coefficients: List[int] = None, enable_clock_gating: bool = True) -> Dict[str, Any]:
        """
        Executes a 16-tap FIR filter on the existing FCC datapath.
        y[n] = sum_{k=0}^{15} h[k] * x[n-k]
        Pairwise additive-multiplicative chaining using templates T1 and T3.
        """
        if coefficients is None:
            # Standard 16 symmetric taps
            coefficients = [12, -24, 48, -96, 180, -320, 600, -1200, 1200, -600, 320, -180, 96, -48, 24, -12]

        taps = len(coefficients)
        delay_line = [0] * taps
        outputs = []

        total_cycles = 0
        gated_cycles = 0

        for sample in input_samples:
            # Shift delay line
            delay_line.pop()
            delay_line.insert(0, to_signed16(sample))

            accum = 0
            # Process pairs of taps using chained FCC templates
            # e.g., using T1: W = A * (X + Y) + K or T5/T3
            for i in range(0, taps, 2):
                h0 = coefficients[i]
                x0 = delay_line[i]
                h1 = coefficients[i + 1] if (i + 1) < taps else 0
                x1 = delay_line[i + 1] if (i + 1) < taps else 0

                # Cycle 1: Multiply h0 * x0
                cg_en1 = True
                res1 = self.fcc.execute("T5", A=h0, X=0, Y=0, K=x0, clk=True, clk_gate_en=cg_en1)
                total_cycles += 1

                # Cycle 2: Accumulate h1 * x1 + previous accum
                cg_en2 = True
                res2 = self.fcc.execute("T3", A=h1, X=0, Y=accum, K=x1, clk=True, clk_gate_en=cg_en2)
                accum = to_signed16(res1["result"] + res2["result"])
                total_cycles += 1

            # Simulate an idle bus/cycle between filter blocks if clock gating is enabled
            if enable_clock_gating:
                # Gated cycle: unit is dormant, clk_gate_en=False
                self.fcc.execute("T5", A=0, X=0, Y=0, K=0, clk=True, clk_gate_en=False)
                gated_cycles += 1
                total_cycles += 1

            outputs.append(accum)

        power_metrics = self.fcc.get_power_metrics()
        return {
            "kernel": "FIR16",
            "outputs": outputs,
            "total_cycles": total_cycles,
            "gated_cycles": gated_cycles,
            "power_metrics": power_metrics,
        }

    def run_elliptic(self, input_samples: List[int], enable_clock_gating: bool = True) -> Dict[str, Any]:
        """
        Executes a 6th-order Elliptic filter section.
        DFG contains chained additions and multiplications (AMADFG structure).
        """
        outputs = []
        # State variables
        s1, s2, s3, s4 = 0, 0, 0, 0
        total_cycles = 0

        # Typical elliptic filter coefficients
        c1, c2, c3, c4 = 345, -512, 128, 890

        for sample in input_samples:
            x_in = to_signed16(sample)

            # Node 1: T1 template: W1 = c1 * (x_in + s1) + s2
            res1 = self.fcc.execute("T1", A=c1, X=x_in, Y=s1, K=s2, clk=True, clk_gate_en=True)
            w1 = res1["result"]
            total_cycles += 1

            # Node 2: T2 template: W2 = c2 * (w1 - s3) + s4
            res2 = self.fcc.execute("T2", A=c2, X=w1, Y=s3, K=s4, clk=True, clk_gate_en=True)
            w2 = res2["result"]
            total_cycles += 1

            # Node 3: T3 template: W3 = c3 * s1 + (w1 + w2)
            res3 = self.fcc.execute("T3", A=c3, X=w1, Y=w2, K=s1, clk=True, clk_gate_en=True)
            w3 = res3["result"]
            total_cycles += 1

            # Update states
            s4 = s3
            s3 = w2
            s2 = s1
            s1 = w1

            # Clock gating idle period
            if enable_clock_gating:
                self.fcc.execute("T5", A=0, X=0, Y=0, K=0, clk=True, clk_gate_en=False)
                total_cycles += 1

            outputs.append(w3)

        power_metrics = self.fcc.get_power_metrics()
        return {
            "kernel": "ELLIPTIC",
            "outputs": outputs,
            "total_cycles": total_cycles,
            "power_metrics": power_metrics,
        }

    def run_volterra(self, input_samples: List[int], enable_clock_gating: bool = True) -> Dict[str, Any]:
        """
        Executes a 2nd-order Volterra Filter:
          y[n] = a*x[n] + b*x[n-1] + c*x[n]^2 + d*x[n]*x[n-1]
        """
        outputs = []
        x_prev = 0
        total_cycles = 0
        a, b, c, d = 420, 210, 15, 30

        for sample in input_samples:
            x_curr = to_signed16(sample)

            # Term 1: a * (x_curr + x_prev)
            res1 = self.fcc.execute("T1", A=a, X=x_curr, Y=x_prev, K=0, clk=True, clk_gate_en=True)
            term1 = res1["result"]
            total_cycles += 1

            # Term 2: c * (x_curr * x_curr)
            res2 = self.fcc.execute("T5", A=x_curr, X=0, Y=0, K=x_curr, clk=True, clk_gate_en=True)
            x_sq = res2["result"]
            res3 = self.fcc.execute("T5", A=c, X=0, Y=0, K=x_sq, clk=True, clk_gate_en=True)
            term2 = res3["result"]
            total_cycles += 2

            # Term 3: d * (x_curr * x_prev) + term1 + term2
            res4 = self.fcc.execute("T5", A=x_curr, X=0, Y=0, K=x_prev, clk=True, clk_gate_en=True)
            cross = res4["result"]
            res5 = self.fcc.execute("T3", A=d, X=term1, Y=term2, K=cross, clk=True, clk_gate_en=True)
            y_out = res5["result"]
            total_cycles += 2

            x_prev = x_curr

            if enable_clock_gating:
                self.fcc.execute("T5", A=0, X=0, Y=0, K=0, clk=True, clk_gate_en=False)
                total_cycles += 1

            outputs.append(y_out)

        power_metrics = self.fcc.get_power_metrics()
        return {
            "kernel": "VOLTERRA",
            "outputs": outputs,
            "total_cycles": total_cycles,
            "power_metrics": power_metrics,
        }
