# Proposed System: Flexible Computational Unit (FCU) Exploiting Carry-Save Arithmetic

## Architecture Overview
The Proposed System implements the novel accelerator datapath described in:
> **"Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic"**  
> Kostas Tsoumanis, Sotirios Xydis, Georgios Zervakis, and Kiamal Pekmestzi  
> *IEEE Transactions on Very Large Scale Integration (VLSI) Systems*, Vol. 24, No. 1, January 2016.

### Architectural Innovations
1. **Pervasive Carry-Save Representation**:
   - Operands are represented in Carry-Save format: $X^* = \{X_C, X_S\}$, where $X^* = X_C + X_S$.
   - Eliminates intermediate Carry-Propagate Adders (CPA) when chaining additive and multiplicative operations.
2. **4:2 Carry-Save Compressor / Adder**:
   - Fuses additions and subtractions prior to multiplication in constant time ($4 \, T_g$ delay regardless of word length).
3. **Direct Carry-Save to Modified Booth (CS-to-MB) Recoding**:
   - Directly recodes $P^* = \{P_C, P_S\}$ into Radix-4 Modified Booth digits without an intermediate CPA.
   - Eliminates the traditional conversion bottleneck.
4. **CSA Tree Multiplier with Operand Fusion**:
   - Compresses partial products and absorbs the external operand ($K^*$ or $N^*$) directly inside the Carry-Save Adder tree.
5. **Boundary CStoBin Converter**:
   - A single ripple-carry CPA is placed strictly at the output boundary to convert final results to two's complement binary.
6. **Dual-Rail Integrated Clock Gating (ICG)**:
   - Dedicated `clk_gate_en` inputs gate both Carry and Sum logic networks when inactive, cutting dynamic power.

---

## File Structure
- `clock_gating.py`: Dual-rail Integrated Clock Gating (ICG) cell and switching activity tracker.
- `cs_arithmetic.py`: `CarrySaveNumber` class and bit-accurate 4:2 Carry-Save Compressor (`CarrySaveCompressor42`).
- `cs_to_mb_recoder.py`: Direct CS-to-MB Recoder implementing the algorithm of Tsoumanis et al. (IEEE TCAS-I 2014).
- `csa_tree_multiplier.py`: Partial Product Generator and CSA Tree Multiplier.
- `fcu_datapath.py`: Flexible Computational Unit (FCU) with MUX0-MUX3 network and boundary `CStoBinModule`.
- `dsp_kernels.py`: DSP benchmark mappings: 16-tap FIR filter (`FIR16`), 6th-order Elliptic filter (`ELLIPTIC`), and Volterra filter (`VOLTERRA`).
- `simulator.py`: Standalone testbench and simulation runner.

---

## Supported Operation Templates (Fig. 3)
- **T1**: $W^* = A \times (X^* + Y^*) + K^*$
- **T2**: $W^* = A \times (X^* - Y^*) + K^*$
- **T3**: $W^* = A \times K^* + (X^* + Y^*)$
- **T4**: $W^* = A \times K^* + (X^* - Y^*)$
- **T5**: $W^* = A \times K^*$

---

## How to Run
```bash
python -m proposed_system.simulator
```
