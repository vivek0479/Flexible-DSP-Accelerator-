# Existing System: Conventional Flexible Datapath (FCC)

## Architecture Overview
The Existing System implements the conventional two's complement flexible datapath based on the **Flexible Computational Component (FCC)** (Galanis et al. [4]) and the conventional chained arithmetic architecture analyzed in Section IV (Fig. 4(a)) of the IEEE TVLSI paper.

### Key Characteristics
1. **Two's Complement Arithmetic**: All internal datapaths, intermediate registers, and execution units operate on standard 16-bit signed two's complement binary numbers.
2. **Carry-Propagate Adders (CPA)**:
   - Fusing additions before multiplication requires a 16-bit CPA.
   - Accumulating results after multiplication requires another 16-bit CPA.
   - Long carry-propagation chains: $T_{\text{crit}} = T_{\text{CPA1}} + T_{\text{Mult}} + T_{\text{CPA2}} \approx 140 \, T_g$.
3. **Modified Booth Multiplier**:
   - Standard Radix-4 Modified Booth multiplier taking 16-bit two's complement binary inputs.
   - Cannot directly accept Carry-Save formatted operands.
4. **Integrated Clock Gating (ICG)**:
   - Explicit `clk_gate_en` / `cg_enable` inputs to freeze register clock transitions and combinational switching activity during inactive/sleep cycles.

---

## File Structure
- `clock_gating.py`: Negative-latch Integrated Clock Gating (ICG) cell and switching activity power tracker.
- `arithmetic_units.py`: Bit-level 16-bit Carry Propagate Adder (CPA) and Radix-4 Booth Multiplier.
- `fcc_datapath.py`: Flexible Computational Component with operation templates T1 to T5.
- `dsp_kernels.py`: DSP benchmark mappings: 16-tap FIR filter (`FIR16`), 6th-order Elliptic filter (`ELLIPTIC`), and Volterra filter (`VOLTERRA`).
- `simulator.py`: Standalone testbench and simulation runner.

---

## Supported Operation Templates
- **T1**: $W = A \times (X + Y) + K$
- **T2**: $W = A \times (X - Y) + K$
- **T3**: $W = A \times K + (X + Y)$
- **T4**: $W = A \times K + (X - Y)$
- **T5**: $W = A \times K$

---

## How to Run
```bash
python -m existing_system.simulator
```
