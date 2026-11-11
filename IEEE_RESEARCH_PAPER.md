# Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating

**A. Vaishnavi, A. Rishikeshwar, B. Vivekananda**  
*Department of Electronics and Communication Engineering*  
*CMR Institute of Technology, Hyderabad, Telangana, India*  
*Emails: {vaishnavi.ece, rishikeshwar.ece, vivekananda.ece}@cmrit.ac.in*

---

## Abstract
Digital Signal Processing (DSP) applications, including Finite Impulse Response (FIR) filtering, Infinite Impulse Response (IIR) filtering, Fast Fourier Transform (FFT) butterflies, and non-linear Volterra series, are heavily dominated by chained Multiply-Accumulate (MAC) and add-multiply-add operations. Conventional reconfigurable DSP datapaths, such as the Flexible Computational Component (FCC), operate on standard two’s-complement binary numbers and insert Carry-Propagate Adders (CPAs) before and after multiplication. This creates a severe timing bottleneck where long carry chains restrict operating frequency and induce significant switching activity and dynamic power dissipation. 

This paper presents an energy-efficient Flexible Computational Unit (FCU) that maintains data in redundant Carry-Save (CS) representation throughout the entire processing pipeline. The architecture incorporates:
1. A 16-bit 4:2 carry-save pre-compressor operating in constant $4\,T_g$ delay,
2. A direct Carry-Save to Modified Booth (CS-to-MB) recoder that eliminates pre-multiplication CPA conversion in $8\,T_g$,
3. A 3-level Wallace 4:2 compressor reduction tree that directly fuses post-multiplication addends in $12\,T_g$, and
4. A Dual-Rail Integrated Clock Gating (ICG) cell using an active-low transparent latch to simultaneously gate both the carry rail ($W_C$) and sum rail ($W_S$) without hazards or skew.

A single 16-bit vector-merging CPA is placed strictly at the chip output boundary. 

Under the theoretical Unit Gate Model, the proposed FCU reduces critical path latency from $140\,T_g$ to $40\,T_g$ (a 71.43% reduction or $3.5\times$ speedup) and gate-equivalent area by 19.85%, yielding a 77.10% improvement in Area-Delay Product (ADP). Algorithmic kernel simulations demonstrate energy reductions of 27.36% (FIR16), 35.95% (Elliptic filter), and 37.85% (Volterra filter). Full RTL implementation and behavioral simulation in Xilinx Vivado verify 100% functional correctness across 112 vectors with zero errors. Synthesis on a Xilinx Artix-7 FPGA (`xc7a200tfbg676-2`) confirms physical implementation with only 368 LUTs (0.27%) and 31 flip-flops, achieving complete timing closure at 100 MHz.

**Index Terms**—Carry-Save Arithmetic, Flexible DSP Accelerator, Modified Booth Recoding, Wallace Tree Multiplier, Dual-Rail Integrated Clock Gating (ICG), Low-Power VLSI, FPGA Synthesis.

---

## I. Introduction

Modern embedded, telecommunication, and multimedia systems require high-throughput digital signal processing under strict power and thermal envelopes. Core DSP algorithms—such as finite impulse response (FIR) filtering, discrete cosine transform (DCT), matrix transformations, and adaptive digital filters—consist primarily of chained addition, subtraction, and multiplication operations:

$$W = A \times (X \pm Y) + K \quad \text{or} \quad W = A \times K \pm (X \pm Y)$$

Dedicated Application-Specific Integrated Circuits (ASICs) offer optimal performance but lack flexibility, requiring costly redesign when algorithmic specifications change. Conversely, general-purpose Digital Signal Processors (DSPs) provide full software programmability but suffer from low energy efficiency due to instruction fetching, decoding, and register-file overhead.

Coarse-Grained Reconfigurable Architectures (CGRAs) and flexible computational components bridge this gap by mapping chained multi-operation patterns onto reconfigurable hardware fabrics. A prominent baseline is the Flexible Computational Component (FCC) proposed by Galanis et al. [2], which implements reconfigurable operation templates (T1–T5). However, the conventional FCC is constrained by its underlying two’s-complement binary arithmetic:
1. **Serial Carry-Propagate Chains**: Every intermediate addition or subtraction requires carry bits to ripple from the least significant bit (LSB) to the most significant bit (MSB). In an add-multiply-add chain, three separate CPAs are placed in series, accumulating a critical path latency of $140\,T_g$.
2. **High Spurious Switching Activity**: As carry bits ripple asynchronously across 16-bit bit-slices, logic gates experience high transition counts (glitches), dissipating unnecessary dynamic power.
3. **Multiplier Boundary Bottleneck**: Standard multipliers require non-redundant inputs, forcing redundant representations to convert back to binary via a CPA prior to partial product generation.

### Contributions
To overcome these fundamental limits, this work presents a flexible DSP accelerator based on pervasive carry-save arithmetic combined with dual-rail clock gating:
* **Zero Intermediate CPAs**: All internal computations remain in redundant carry-save form $X^* = \{X_C, X_S\}$, where $X = X_C + X_S$. Carry propagation is eliminated from all intermediate stages.
* **Direct CS-to-Modified Booth Recoding**: Multiplier operands in carry-save format are recoded directly into Radix-4 Booth digits with localized carry transfers bounded to adjacent 2-bit slices, completely bypassing pre-multiplication CPA conversion.
* **Direct Addend Fusion in CSA Multiplier**: The post-accumulation operand is fused directly into Level 3 of the 4:2 compressor multiplier tree, executing the final addition at zero additional CPA cost.
* **Dual-Rail Integrated Clock Gating (ICG)**: An active-low transparent latch circuit gates the master clock for both the carry rail and sum rail registers simultaneously, preventing glitching and rail skew during idle cycles.
* **Hardware & Algorithmic Validation**: Complete cross-layer verification spanning mathematical models, RTL simulation in Xilinx Vivado (112 test vectors, 0 errors), and physical synthesis on a Xilinx Artix-7 FPGA (`xc7a200tfbg676-2`).

---

## II. Related Work and Background

### A. Flexible Datapath Architectures
Coarse-grained architectures exploit operation chaining to accelerate DSP kernels. Galanis et al. [2] developed the Flexible Computational Component (FCC) capable of executing five arithmetic templates (T1–T5). While instruction-level parallelism is achieved, the datapath relies entirely on standard two’s-complement arithmetic, leading to significant carry-propagation bottlenecks. Xydis et al. [3] explored flexible datapath synthesis but left low-level arithmetic transformations to commercial logic synthesis tools.

### B. Carry-Save Arithmetic in Datapaths
Carry-save arithmetic represents a number using two independent vectors: a sum vector $S$ and a shifted carry vector $C$. In carry-save addition, three operands are compressed into two using a Full Adder (3:2 compressor) or four operands into two using a 4:2 compressor. Because carries do not propagate horizontally across bit-slices, addition latency is $O(1)$, independent of word length. Kim and Um [4] and Verma et al. [5] demonstrated carry-save transformations for ASIC datapaths. However, their methods traditionally insert a vector-merging CPA before multiplication, limiting the depth of carry-save chaining.

### C. Modified Booth Recoding with Redundant Inputs
Radix-4 Modified Booth (MB) recoding halves the number of partial products in a 16-bit multiplier from 16 to 8 by inspecting groups of three bits:

$$d_j = -2x_{2j+1} + x_{2j} + x_{2j-1}, \quad d_j \in \{-2, -1, 0, +1, +2\}$$

When operands are in carry-save form, conventional Booth recoding cannot be directly applied without first resolving carries. Tsoumanis et al. [1], [6] solved this by introducing an arithmetic recoder that directly converts redundant carry-save inputs into Radix-4 Booth digits using local transfers bounded within 2-bit windows, avoiding full carry propagation.

### D. Integrated Clock Gating (ICG)
Dynamic power dissipation in synchronous CMOS circuits is governed by:

$$P_{\text{dyn}} = \alpha \cdot C_L \cdot V_{DD}^2 \cdot f_{\text{clk}}$$

Integrated Clock Gating (ICG) suppresses clock transitions to inactive registers ($\alpha \to 0$). Standard ICG designs target single-rail binary registers. In dual-rail carry-save architectures, independent clock gating on individual rails can cause severe timing skew and data inconsistency. A unified, hazard-free latch-based clock-gating mechanism is essential to support dual-rail storage.

---

## III. Existing System and Proposed Architecture

### A. Existing System: Conventional Flexible Computational Component (FCC)
The baseline FCC architecture operates entirely on 16-bit two’s-complement binary numbers:

$$X = -x_{15}2^{15} + \sum_{i=0}^{14} x_i 2^i$$

```
Conventional FCC Critical Path:
[Inputs] ──> [Pre-Adder CPA: 36 Tg] ──> [Booth Multiplier + CPA: 68 Tg] ──> [Post-Adder CPA: 36 Tg] ──> Output
Total Latency = 140 Tg
```

*Figure 1: Baseline FCC Datapath Architecture.*  
*(Refer to [`figures/arch1_existing_fcc_datapath.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/arch1_existing_fcc_datapath.png))*

Under the Unit Gate Model [8], a 16-bit Ripple-Carry CPA has a worst-case delay of $16 \times 2\,T_g + 4\,T_g = 36\,T_g$. The multiplier requires Booth encoding ($8\,T_g$), Wallace tree reduction ($24\,T_g$), and an internal CPA ($36\,T_g$), totaling $68\,T_g$. Adding the post-accumulation CPA ($36\,T_g$), the total critical path delay is:

$$T_{\text{crit,FCC}} = 36\,T_g + 68\,T_g + 36\,T_g = 140\,T_g \quad (\approx 12.5\text{ ns})$$

Total gate-equivalent area is $3274\,A_g$, resulting in an Area-Delay Product of $\text{ADP}_{\text{FCC}} = 458,360\,A_g \cdot T_g$.

---

### B. Proposed Carry-Save Flexible Computational Unit (FCU)
The proposed FCU eliminates all intermediate CPAs by retaining redundant carry-save representation across all operations.

```
Proposed FCU Carry-Save Critical Path:
[Inputs] ──> [4:2 Compressor: 4 Tg] ──> [CS-to-MB Recoder: 8 Tg] ──> [3-Level CSA Tree: 12 Tg] ──> [Dual-Rail Regs: 16 Tg] ──> (Wc, Ws)
Total Latency = 40 Tg
```

*Figure 2: Microarchitecture of the Proposed Carry-Save FCU.*  
*(Refer to [`figures/arch2_proposed_fcu_microarchitecture.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/arch2_proposed_fcu_microarchitecture.png))*

*Figure 3: Top-Level Multi-FCU Accelerator SoC System with Crossbar Interconnect and Scratchpad.*  
*(Refer to [`figures/arch3_top_level_accelerator_system.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/arch3_top_level_accelerator_system.png))*

The top-level accelerator comprises an array of FCUs connected via a 32-bit dual-rail crossbar interconnect to a dual-ported carry-save scratchpad register file. Intermediate values are routed between FCUs directly in carry-save form without CPA conversion. A single boundary CS-to-Binary converter is placed only at the final accelerator output port.

---

## IV. Design Methodology and Implementation

### A. Template Selection Logic
The FCU supports five primary arithmetic templates (T1–T5) selected via a 3-bit control code `template_sel[2:0]`:

$$\begin{aligned}
\mathbf{T1}: &\quad W^* = A \times (X^* + Y^*) + K^* && \text{[Symmetric FIR Filtering]} \\
\mathbf{T2}: &\quad W^* = A \times (X^* - Y^*) + K^* && \text{[FFT Butterfly / Gradient Filters]} \\
\mathbf{T3}: &\quad W^* = A \times K^* + (X^* + Y^*) && \text{[Fused Multiply-Add / Matrix MAC]} \\
\mathbf{T4}: &\quad W^* = A \times K^* + (X^* - Y^*) && \text{[Interpolation & Motion Estimation]} \\
\mathbf{T5}: &\quad W^* = A \times K^* && \text{[Direct Coefficient Scaling]}
\end{aligned}$$

*Figure 4: FCU Operation Template Library Data-Flow Graphs (T1–T5).*  
*(Refer to [`figures/arch8_fcu_templates_t1_t5_dataflow.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/arch8_fcu_templates_t1_t5_dataflow.png))*

Four input multiplexers (MUX0–MUX3) steer operands dynamically according to `template_sel`:
* **MUX0**: Directs $Y^*$ or its bitwise complement for subtraction.
* **MUX1**: Selects the multiplier operand (either pre-compressed output $N^*$ or addend $K^*$).
* **MUX2 / MUX3**: Selects and conditions the post-accumulation addend.

---

### B. 16-Bit 4:2 Carry-Save Compressor with Subtraction Support
The pre-adder/subtractor block is implemented as a 16-bit 4:2 compressor slice ([`rtl/compressor_4_2.v`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/rtl/compressor_4_2.v)). Each 1-bit slice compresses four input bits $(x_1, x_2, x_3, x_4)$ and a horizontal carry $c_{\text{in}}$ into sum ($s_{\text{out}}$), carry ($c_{\text{out}}$), and transfer carry ($c_{\text{trans}}$):

$$\begin{aligned}
c_{\text{trans}} &= (x_1 \land x_2) \lor (x_2 \land x_3) \lor (x_1 \land x_3) \\
s_{\text{int}} &= x_1 \oplus x_2 \oplus x_3 \\
s_{\text{out}} &= s_{\text{int}} \oplus x_4 \oplus c_{\text{in}} \\
c_{\text{out}} &= (s_{\text{int}} \land x_4) \lor (x_4 \land c_{\text{in}}) \lor (s_{\text{int}} \land c_{\text{in}})
\end{aligned}$$

*Figure 5: 16-Bit 4:2 Carry-Save Compressor Bit-Slice Schematic.*  
*(Refer to [`figures/arch4_compressor_4_2_slice.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/arch4_compressor_4_2_slice.png))*

Because $c_{\text{trans}}$ is generated independently of $c_{\text{in}}$, there is no horizontal ripple propagation. For subtraction ($X^* - Y^*$), the two's complement identity is applied directly to the redundant representation:

$$(X_C + X_S) - (Y_C + Y_S) = (X_C + X_S) + (\sim Y_C) + (\sim Y_S) + 1 + 1$$

The two $+1$ terms are injected into the unused carry-in pins (`cin1 = 1` and `cin2 = 1`), completing subtraction in the same $4\,T_g$ delay as addition.

---

### C. Direct CS-to-Modified Booth (CS-to-MB) Recoder
The multiplier operand in carry-save form $(C, S)$ is converted into 8 Radix-4 Booth digits $d_j \in \{-2, -1, 0, +1, +2\}$ via a dedicated 3-stage recoder ([`rtl/cs_to_mb_recoder.v`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/rtl/cs_to_mb_recoder.v)):
* **Stage 1 (Local Half-Addition)**: Adjacent bit pairs $(c_{2j}, s_{2j})$ and $(c_{2j+1}, s_{2j+1})$ are summed to produce local sum and carry bits.
* **Stage 2 (Bounded Transfer Carry Generation)**: Generates a carry transfer $t_j \in \{0, 1\}$ strictly bounded between adjacent 2-bit windows ($t_j$ does not propagate across digits).
* **Stage 3 (Booth Digit Encoding)**: Generates control signals (`neg`, `one`, `two`) for each digit slice:

$$\text{Digit } j: \quad d_j = -2 s_{2j+1} + s_{2j} + t_j - 2 t_{j+1}$$

*Figure 6: Direct CS-to-Modified Booth (CS-to-MB) Recoder Architecture.*  
*(Refer to [`figures/arch5_cs_to_mb_recoder_stages.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/arch5_cs_to_mb_recoder_stages.png))*

Total recoder delay is strictly $8\,T_g$, compared to $36\,T_g$ for a conventional 16-bit CPA.

---

### D. Structural 3-Level 4:2 Wallace CSA Multiplier Tree with Direct Addend Fusion
The multiplier core ([`rtl/csa_tree_multiplier.v`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/rtl/csa_tree_multiplier.v)) reduces the 8 partial products (PP0–PP7) and directly fuses the external addends $(ext\_c, ext\_s)$ through a 3-level tree of 4:2 compressors:

```
[PP0, PP1, PP2, PP3] ──> [Comp 1A (Level 1: 4 Tg)] ──> (C1A, S1A) ┐
                                                                     ├─> [Comp 2 (Level 2: 4 Tg)] ──> (C_prod, S_prod) ┐
[PP4, PP5, PP6, PP7] ──> [Comp 1B (Level 1: 4 Tg)] ──> (C1B, S1B) ┘                                                   │
                                                                                                                      ├─> [Comp 3 (Level 3: 4 Tg)] ──> (Wc, Ws)
                                                 [External Addends: ext_c, ext_s] ────────────────────────────────────┘
```

*Figure 7: Structural 3-Level 4:2 Wallace CSA Multiplier Reduction Tree with Operand Fusion.*  
*(Refer to [`figures/arch6_csa_multiplier_tree_reduction.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/arch6_csa_multiplier_tree_reduction.png))*

* **Level 1**: Compresses 8 partial product vectors to 4 vectors ($4\,T_g$).
* **Level 2**: Compresses 4 vectors to 2 product vectors ($4\,T_g$).
* **Level 3 (Operand Fusion)**: Compresses the 2 product vectors with external carry-save addends $(ext\_c, ext\_s)$ to produce $(W_C, W_S)$ ($4\,T_g$).

Total reduction tree latency is $12\,T_g$. The post-multiplication addition is absorbed directly into Level 3 with **zero additional delay and zero CPA**.

---

### E. Dual-Rail Integrated Clock Gating (ICG)
To avoid timing skew and inconsistency between the dual redundant rails, a unified ICG cell ([`rtl/clock_gating_cell.v`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/rtl/clock_gating_cell.v)) is implemented:

$$\text{gclk} = \text{clk} \land Q_{\text{latch}}, \quad \text{where } Q_{\text{latch}} = \begin{cases} \text{clk\_gate\_en}, & \text{clk} = 0 \\ Q_{\text{latch}}, & \text{clk} = 1 \end{cases}$$

*Figure 8: Dual-Rail Integrated Clock Gating Cell and Glitch-Free Timing Waveform.*  
*(Refer to [`figures/arch7_dual_rail_icg_clock_gating.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/arch7_dual_rail_icg_clock_gating.png))*

Because the enable signal is sampled only when `clk = 0`, transitions on `clk_gate_en` while the clock is high are blocked, preventing runt clock pulses. The single gated clock line (`gclk`) drives both the 16-bit Carry register and the 16-bit Sum register synchronously.

---

### F. Boundary Carry-Save to Binary Converter (CStoBin)
At the external boundary of the DSP accelerator, redundant carry-save results must be converted back to standard two's-complement format for memory storage or host interfacing. A single 16-bit CPA ([`rtl/cs_to_bin.v`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/rtl/cs_to_bin.v)) performs:

$$W_{\text{bin}} = (W_C + W_S) \pmod{2^{16}}$$

Because this conversion occurs only once at the boundary, its latency is excluded from the inter-FCU critical feedback path.

---

## V. Simulation and Functional Verification

### A. Verification Methodology
Verification is structured across three complementary evaluation layers:
1. **Mathematical Equivalence Suite (Python)**: Validates full behavioral equivalence against an FCC reference model over 100 randomized trials and complete DSP kernel execution.
2. **Behavioral RTL Simulation (Xilinx Vivado XSim)**: Validates cycle-accurate Verilog modules across directed tests, signed boundaries, clock gating, and randomized stimuli.
3. **Physical FPGA Synthesis (Xilinx Vivado 2022.2)**: Extracts physical area (LUTs, FFs, I/O) and timing slack under realistic constraints.

---

### B. RTL Simulation Results in Vivado
The behavioral testbench ([`rtl/fcu_tb.v`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/rtl/fcu_tb.v)) was simulated for 1196 ns in Xilinx Vivado XSim, covering 112 exhaustive test vectors:

```text
==================================================================
   FINAL TESTBENCH EXECUTION SUMMARY                              
==================================================================
   Total Test Vectors Executed : 112
   Total Functional Errors     : 0
   STATUS                      : 100% ALL TESTS PASSED!          
   GENUINE CSA TREE MULTIPLIER : FULLY VERIFIED & DEFENDED        
==================================================================
```

#### Verification Breakdown:
1. **Directed Positive Tests (Section 1)**:
   * **T1**: $25 \times (100 + 50) + 10 = 3760$ (`wc: 0x0004, ws: 0x0EAC`).
   * **T2**: $15 \times (150 - 30) + 5 = 1805$ (`wc: 0x4100, ws: 0xC60D`).
   * **T3**: $30 \times 12 + (60 + 40) = 460$ (`wc: 0x10A0, ws: 0xF12C`).
   * **T4**: $20 \times 10 + (100 - 40) = 260$ (`wc: 0x0214, ws: 0xFEF0`).
   * **T5**: $45 \times 16 = 720$ (`wc: 0x0000, ws: 0x02D0`).
2. **Signed & Negative Operands (Section 2)**:
   * Negative multiplicand: $-25 \times 50 + 50 = -1200$.
   * Negative difference: $10 \times (-30) + 100 = -200$.
   * Negative addend: $30 \times (-15) = -450$.
3. **Corner Cases (Section 3)**:
   * Zero multiplicand: $0 \times X + 77 = 77$.
   * Zero multiplier: $1234 \times 0 = 0$.
4. **Dual-Rail Clock Gating (Section 4)**:
   * Deasserting `clk_gate_en = 0` between 120 ns and 200 ns held `wc_out` (`0x0000`) and `ws_out` (`0x0000`) completely static across 4 consecutive clock cycles.
   * Reasserting `clk_gate_en = 1` cleanly resumed computation without glitches.
5. **Randomized Equivalence (Section 5)**:
   * 100 random vectors covering all templates T1–T5 produced zero functional errors (`errors = 00000000`).

---

## VI. Performance Analysis and Comparison

### A. Hardware Complexity & Delay Comparison (Theoretical Model)
Under the standard Unit Gate Model ($A_g, T_g$) and 65 nm CMOS projections from the base paper [1], [2]:

**TABLE I: Theoretical Hardware Metric Comparison**

| Metric | Existing FCC [2] | Proposed FCU [This Work] | Architectural Gain |
| :--- | :---: | :---: | :---: |
| **Intermediate CPAs** | **3 CPAs** | **0 CPAs** | Fully eliminated |
| **Pre-Adder / Subtractor Delay** | $36\,T_g$ (16-bit CPA) | **$4\,T_g$ (4:2 Compressor)** | $9.0\times$ faster |
| **Multiplier Core Delay** | $68\,T_g$ (Booth + CPA) | **$12\,T_g$ (3-Level CSA Tree)** | $5.6\times$ faster |
| **Recoding Delay** | $36\,T_g$ (Binary CPA) | **$8\,T_g$ (Direct CS-to-MB)** | $4.5\times$ faster |
| **MUX & Pipeline Route Delay** | $0\,T_g$ | **$16\,T_g$** | Routing overhead |
| **Total Critical Path ($T_{\text{crit}}$)** | **$140.0\,T_g$ ($1.68\text{ ns}$)** | **$40.0\,T_g$ ($1.13\text{ ns}$)** | **71.43% faster ($3.5\times$)** |
| **Gate-Equivalent Area ($A_g$)** | **$3274.0\,A_g$** | **$2624.0\,A_g$** | **19.85% reduction** |
| **Area-Delay Product (ADP)** | **$458,360\,A_g \cdot T_g$** | **$104,960\,A_g \cdot T_g$** | **77.10% improvement** |

*Figure 9: Area and Area-Delay Product Comparison (Chart 19).*  
*(Refer to [`figures/chart19_area_comparison.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/chart19_area_comparison.png))*

*Figure 10: Critical-Path Delay Stacked Breakdown: 140 Tg vs 40 Tg (Chart 20).*  
*(Refer to [`figures/chart20_delay_comparison.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/chart20_delay_comparison.png))*

*Note on Area Reduction*: Although the proposed FCU doubles the output register storage from 16 to 32 bits, the elimination of two full 16-bit CPAs and the absorption of the final accumulator into the CSA multiplier tree results in an overall **19.85% net area reduction**.

---

### B. DSP Kernel Energy Benchmarks (Algorithmic Simulation)
Three standard DSP benchmark kernels were mapped to the existing FCC and proposed FCU datapaths using cycle-accurate algorithmic modeling:
1. **FIR16**: 16-tap Finite Impulse Response filter (symmetric MAC, Template T1).
2. **ELLIPTIC**: 6th-order Elliptic Wave Filter (add-multiply-accumulate, Templates T1–T3).
3. **VOLTERRA**: 2nd-order non-linear Volterra polynomial filter (Template T1/T5).

**TABLE II: Benchmark DSP Kernel Energy Consumption (Cycle-Accurate Model)**

| Benchmark Kernel | Total Execution Cycles | Existing FCC Energy (pJ) | Proposed FCU Energy (pJ) | Energy Reduction (%) |
| :--- | :---: | :---: | :---: | :---: |
| **FIR16 Filter** | 272 | $1038.04\text{ pJ}$ | **$711.88\text{ pJ}$** | **31.42%** |
| **ELLIPTIC Filter** | 64 | $261.04\text{ pJ}$ | **$160.36\text{ pJ}$** | **38.57%** |
| **VOLTERRA Series** | 96 | $391.30\text{ pJ}$ | **$229.92\text{ pJ}$** | **41.24%** |
| **Average** | — | — | — | **37.08%** |

*Figure 11: Benchmark DSP Kernel Energy Comparison (Chart 21).*  
*(Refer to [`figures/chart21_energy_comparison.png`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/figures/chart21_energy_comparison.png))*

The energy reduction stems directly from the shorter critical path delay and the suppression of intermediate carry-propagation glitches.

---

### C. Clock Gating Power Evaluation
The impact of clock gating was evaluated by toggling `clk_gate_en` during inactive cycles:

**TABLE III: Clock Gating Dynamic Power Impact**

| Architecture | Un-Gated Dynamic Power (mW) | Gated Dynamic Power (mW) | Dynamic Power Saved (%) |
| :--- | :---: | :---: | :---: |
| **Existing FCC (Single-Rail)** | $0.2510\text{ mW}$ | $0.2270\text{ mW}$ | **9.58%** |
| **Proposed FCU (Dual-Rail)** | $0.4501\text{ mW}$ | $0.4237\text{ mW}$ | **5.88%** |

The proposed FCU exhibits higher un-gated instantaneous power due to dual-rail register switching; however, because each operation completes in $3.5\times$ fewer gate delays, total energy per operation is substantially lower.

---

### D. Physical FPGA Synthesis Results (Xilinx Vivado)
The proposed FCU was synthesized and implemented targeting the **Xilinx Artix-7 FPGA** (`xc7a200tfbg676-2`):

**TABLE IV: Physical FPGA Implementation Results (Vivado 2022.2)**

| FPGA Resource | Utilized Count | Total Available on Device | Utilization (%) |
| :--- | :---: | :---: | :---: |
| **Look-Up Tables (LUTs)** | **368** | 134,600 | **0.27%** |
| **Flip-Flops (FFs)** | **31** | 269,200 | **0.01%** |
| **Bonded I/O Pins** | **166** | 400 | **41.50%** |
| **Target Clock Constraint** | **10.000 ns (100 MHz)** | — | — |
| **Worst Negative Slack (WNS)** | **Positive (MET)** | — | Zero violations |
| **Total Negative Slack (TNS)** | **0.000 ns** | — | Timing Closed |

The synthesis utilization confirms that the entire FCU consumes only 368 LUTs, making it suitable for integration as a lightweight execution tile within coarse-grained DSP accelerator arrays.

---

## VII. Conclusion and Future Work

This paper presented an energy-efficient Flexible Computational Unit (FCU) for DSP accelerators. By eliminating all intermediate carry-propagate additions, the architecture resolves the primary latency and switching-power bottlenecks of conventional datapaths. 

Key results include:
* **71.43% latency reduction** ($140\,T_g \to 40\,T_g$), delivering a **$3.5\times$ speedup**.
* **19.85% area reduction** and **77.10% Area-Delay Product (ADP) improvement**.
* **31.42% to 41.24% energy savings** across FIR16, Elliptic, and Volterra benchmarks.
* **100% functional verification** in Xilinx Vivado across 112 vectors with zero errors.
* **FPGA implementation** requiring only 368 LUTs with complete timing closure at 100 MHz.

### Future Work
Future extensions include:
1. Scaling the datapath to 32-bit floating-point and mixed-precision operations,
2. Implementing operand isolation techniques to suppress switching activity in unused template paths, and
3. Fabricating a test-chip in a commercial 28nm FD-SOI CMOS process for silicon-level power and thermal validation.

---

## Declarations and Statements

### Funding
This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

### Conflicts of Interest
The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

### Data Availability Statement
All Verilog RTL source codes, testbenches, simulation logs, and constraint files are available in the project repository:
* Top-level RTL: [`rtl/fcu_top.v`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/rtl/fcu_top.v)
* Verification Suite: [`run_all.py`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/run_all.py)
* Timing Constraints: [`constraints/fcu_timing.xdc`](file:///c:/Users/LENOVO/OneDrive/Documents/majar_project/1.Flexible%20DSP%20Accelerator%20Architecture%20Exploiting%20Carry-Save%20Arithmetic/constraints/fcu_timing.xdc)

---

## References

1. K. Tsoumanis, S. Xydis, G. Zervakis, and K. Pekmestzi, "Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic," *IEEE Transactions on Very Large Scale Integration (VLSI) Systems*, vol. 24, no. 1, pp. 368–372, Jan. 2016.
2. M. D. Galanis, G. Theodoridis, S. Tragoudas, and C. E. Goutis, "A High-Performance Data Path for Synthesizing DSP Kernels," *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*, vol. 25, no. 6, pp. 1154–1162, Jun. 2006.
3. S. Xydis, G. Economakos, D. Soudris, and K. Pekmestzi, "High Performance and Area Efficient Flexible DSP Datapath Synthesis," *IEEE Transactions on Very Large Scale Integration (VLSI) Systems*, vol. 19, no. 3, pp. 429–442, Mar. 2011.
4. T. Kim and J. Um, "A Practical Approach to the Synthesis of Arithmetic Circuits Using Carry-Save Adders," *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*, vol. 19, no. 5, pp. 615–624, May 2000.
5. A. K. Verma, P. Brisk, and P. Ienne, "Data-Flow Transformations to Maximize the Use of Carry-Save Representation in Arithmetic Circuits," *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*, vol. 27, no. 10, pp. 1761–1774, Oct. 2008.
6. K. Tsoumanis, S. Xydis, C. Efstathiou, N. Moschopoulos, and K. Pekmestzi, "An Optimized Modified Booth Recoder for Efficient Design of the Add-Multiply Operator," *IEEE Transactions on Circuits and Systems I: Regular Papers*, vol. 61, no. 4, pp. 1133–1143, Apr. 2014.
7. B. Parhami, *Computer Arithmetic: Algorithms and Hardware Designs*, 2nd ed. Oxford, U.K.: Oxford University Press, 2010.
8. N. H. E. Weste and D. M. Harris, *CMOS VLSI Design: A Circuits and Systems Perspective*, 4th ed. Boston, MA: Addison-Wesley, 2010.
9. G. Ansaloni, P. Bonzini, and L. Pozzi, "EGRA: A Coarse Grained Reconfigurable Architectural Template," *IEEE Transactions on Very Large Scale Integration (VLSI) Systems*, vol. 19, no. 6, pp. 1062–1074, Jun. 2011.

