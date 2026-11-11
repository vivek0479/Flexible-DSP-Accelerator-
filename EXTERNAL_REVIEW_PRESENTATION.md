# Final Year Major Project External Review Presentation
## Department of Electronics and Communication Engineering (ECE)
### CMR Institute of Technology, Hyderabad (Academic Year: 2026–2027)

---

# Presentation Overview & Slide Index

| Slide # | Slide Title | Core Focus | Visual / Diagram Reference |
| :---: | :--- | :--- | :--- |
| **Slide 1** | Title Slide | Project Title, Authors, Guide, Affiliation | University / Department Header |
| **Slide 2** | Introduction | DSP acceleration, MAC/AMA dominance, efficiency needs | Conceptual Chaining Flow |
| **Slide 3** | Problem Statement | CPA carry ripple bottleneck ($140\,T_g$), power overhead | CPA Carry Ripple Illustration |
| **Slide 4** | Motivation & Objectives | Core technical objectives, speed, area, power targets | Bulleted Target Metrics |
| **Slide 5** | Literature Survey | Comparative review of IEEE papers (2000–2016) | IEEE Literature Survey Table |
| **Slide 6** | Existing System (Conventional FCC) | 16-bit 2's complement datapath, 3 CPAs, $140\,T_g$ delay | `figures/fig_base_paper_existing_fcc.png` |
| **Slide 7** | Proposed Architecture (FCU) | Pervasive Carry-Save, 4:2 compressor, CS-to-MB recoder | Architectural Summary |
| **Slide 8** | Overall Architecture & Dataflow | Top-level accelerator & microarchitecture | `figures/fig1_top_level_architecture.png` & `fig2_fcu_microarchitecture.png` |
| **Slide 9** | Working Principle & Numerical Walkthrough | Step-by-step arithmetic dataflow with numerical proof | Template T1 Numerical Trace ($A=25, X=100, Y=50, K=10 \rightarrow 3760$) |
| **Slide 10** | Individual Hardware Module Breakdown | 4:2 compressor, CS-to-MB recoder, CSA tree, ICG, CStoBin | Modular Port & Delay Table |
| **Slide 11** | Operation Template Library (T1–T5) | Reconfigurable MUX network for DSP algorithms | `figures/fig4_templates_dataflow.png` |
| **Slide 12** | Low-Power Integrated Clock Gating (ICG) | Dual-rail ICG negative latch + AND gate architecture | `figures/fig5_clock_gating_schematic.png` |
| **Slide 13** | Design & Implementation Methodology | 9-stage engineering workflow from algorithm to RTL | Flowchart / Methodology Pipeline |
| **Slide 14** | Tools, Technologies & Simulation Setup | Xilinx Vivado, EDA Playground, Icarus Verilog, Python | Simulation Stack Diagram |
| **Slide 15** | Functional Verification & RTL Waveforms | EPWave timing diagram verifying T1–T5 & Clock Gating | `figures/fig6_rtl_simulation_waveform.png` & User Screenshot |
| **Slide 16** | Performance Results & Comparative Analysis | Delay, area, ADP, energy savings, power analysis | `figures/fig7_hardware_comparison.png`, `fig8`, `fig9` |
| **Slide 17** | Advantages & Real-World Applications | FIR/IIR filtering, FFT butterflies, Edge AI / TinyML | Applications Matrix |
| **Slide 18** | Limitations, Future Scope & Conclusion | Honest limitations, FPGA mapping, conclusion | Summary & Viva Defense |

---

<!-- slide -->

## Slide 1: Title Slide

### Visual Layout
- **Theme:** Clean academic presentation layout.
- **Header:** Department of Electronics and Communication Engineering, CMR Institute of Technology, Hyderabad.
- **Center:** High-contrast bold project title.

---

### Slide Content

# Energy-Efficient Flexible DSP Accelerator Utilizing Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating

#### Final Year B.Tech Major Project External Review (2026–2027)

**Project Team Members:**
- **A. Vaishnavi** (Roll No: 21R01A04xx)
- **A. Rishikeshwar** (Roll No: 21R01A04xx)
- **B. Vivekananda** (Roll No: 21R01A04xx)

**Internal Project Guide:**
- **Dr. / Prof. [Guide Name]**, Department of ECE

**Department & Institution:**
- Department of Electronics and Communication Engineering
- **CMR Institute of Technology**, Kandlakoya, Hyderabad, Telangana – 501401

**Project Domain:** VLSI Design, Digital Arithmetic, Computer Architecture & Low-Power Hardware Acceleration.

---

### Speaker Presenter Notes
> *"Good morning, respected external examiner and faculty members. Today, my team members—Vaishnavi, Rishikeshwar, and Vivekananda—and I are presenting our Final Year B.Tech Major Project entitled **'Energy-Efficient Flexible DSP Accelerator Utilizing Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating'**. Our project addresses the fundamental arithmetic delay and power bottleneck in digital signal processors by replacing conventional carry-propagate arithmetic with constant-time carry-save computation and glitch-free clock gating."*

---

<!-- slide -->

## Slide 2: Introduction

### Visual Layout
- Left Column: Role of DSP hardware accelerators in modern edge computing.
- Right Column: Core arithmetic bottlenecks in Multiply-Accumulate (MAC) chains.

---

### Slide Content

### 1. The Era of Real-Time DSP Hardware
- Modern embedded systems, 5G wireless basebands, autonomous robotics, audio/speech processing, and Edge AI demand ultra-high-throughput digital signal processing.
- DSP workloads are fundamentally dominated by chained **Add-Multiply-Accumulate (AMA)** and **Multiply-Accumulate (MAC)** operations:
  $$W = A \times (X \pm Y) + K$$
- General-purpose CPUs and DSPs suffer from high instruction-fetch overhead, while dedicated monolithic ASICs lack reconfigurability for varying filter kernels.

### 2. The Hardware Arithmetic Bottleneck
- In conventional reconfigurable DSP accelerators, arithmetic operations are computed in standard **two's-complement binary**.
- When operations are chained together:
  - Addition prior to multiplication requires a carry to ripple across all 16 bits.
  - Multiplier partial products must be resolved into binary before feeding subsequent adders.
  - Accumulation adds yet another full carry-propagation delay.
- **Key Takeaway:** The ultimate speed and power limit of DSP datapaths is governed not by high-level architectural pipelining, but by the low-level **carry-propagation delay ($O(N)$)** in arithmetic execution units.

---

### Speaker Presenter Notes
> *"To begin with, modern digital signal processing applications—ranging from medical imaging to 5G communication—spend more than 80% of their execution time computing chained additions and multiplications. While software programmable DSPs are flexible, they consume too much power; monolithic ASICs, on the other hand, cannot adapt to different filter topologies. Coarse-grained flexible accelerators provide the ideal middle ground. However, conventional accelerators use standard two's-complement binary arithmetic, which introduces severe carry-propagation delays at every chained stage. Our project addresses this fundamental arithmetic bottleneck."*

---

<!-- slide -->

## Slide 3: Problem Statement

### Visual Layout
- Boxed diagram showing three cascaded Carry-Propagate Adders (CPA 1 $\rightarrow$ Booth Multiplier $\rightarrow$ CPA 2).
- Highlight the carry rippling across all 16 bit slices in red.

---

### Slide Content

### The Carry-Propagation Bottleneck in Conventional Flexible Datapaths

```
Conventional Chaining (FCC):
  X, Y  ──────► [ CPA 1 (16-bit Ripple) ] ──────► Delay: 32 Tg
                         │
                         ▼ (Binary 16-bit)
  A     ──────► [ Radix-4 Booth Multiplier ] ───► Delay: 76 Tg (Includes Internal CPA!)
                         │
                         ▼ (Binary 16-bit)
  K     ──────► [ CPA 2 (16-bit Ripple) ] ──────► Delay: 32 Tg
                         │
                         ▼
  Total Critical Path Delay ≈ 140 Tg (1.68 ns in 65nm CMOS)
```

1. **Sequential Carry Propagation:**
   - In standard two's complement binary, adding two $N$-bit numbers requires carry bits to ripple from bit 0 to bit $N-1$:
     $$c_{i+1} = (a_i \cdot b_i) + (c_i \cdot (a_i \oplus b_i))$$
   - For $N = 16$, a Full Adder carry delay of $2\,T_g$ results in $16 \times 2\,T_g = 32\,T_g$ per adder.

2. **Multiplier CPA Bottleneck:**
   - Conventional multipliers internally compress partial products into Carry-Save form, but are forced to use an **internal CPA** ($32\,T_g$) because the surrounding datapath only accepts binary!

3. **Cumulative Delay & Power Waste:**
   - Chaining three CPAs yields:
     $$T_{\text{crit}} = T_{\text{CPA1}} + T_{\text{Mult}} + T_{\text{CPA2}} = 32 + 76 + 32 \approx \mathbf{140\,T_g}$$
   - Continuous carry rippling causes spurious intermediate logic transitions (glitching), dissipating excessive dynamic power.

---

### Speaker Presenter Notes
> *"This slide highlights the core problem we identified from our base paper study. In the conventional Flexible Computational Component (FCC), an Add-Multiply-Accumulate operation must pass through three separate Carry-Propagate Adders. Notice that even though the multiplier internally generates partial products, it must convert its product back to two's-complement binary using an internal CPA simply because the downstream adder cannot accept carry-save data. This creates an enormous critical path delay of 140 gate delays ($1.68\,\text{ns}$ at 65nm) and causes significant dynamic power loss due to unnecessary switching activity."*

---

<!-- slide -->

## Slide 4: Motivation and Objectives

### Visual Layout
- Two-column layout: Left = Core Research Motivation, Right = Specific Measurable Project Objectives.

---

### Slide Content

### Project Motivation
- **Eliminate Intermediate CPAs:** If intermediate data remains in redundant **Carry-Save format ($X^* = \{X_C, X_S\}$)**, additions can be completed in constant time ($O(1)$) rather than $O(N)$.
- **Direct Multiplier Recoding:** If a multiplier can directly recode Carry-Save inputs into Booth digits without prior carry-propagation, the entire CPA bottleneck disappears.
- **Clock-Level Energy Optimization:** Inactive functional units and registers must be gated at the clock-network level without introducing clock glitches or rail skew.

### Measurable Objectives of This Major Project
1. **Synthesizable RTL Design:** Implement a complete 16-bit **Flexible Computational Unit (FCU)** in synthesizable SystemVerilog/Verilog supporting templates **T1 to T5**.
2. **Constant-Time Pre-Addition:** Design a bit-accurate **4:2 Carry-Save Compressor** achieving constant $4\,T_g$ critical delay independent of word length.
3. **Direct CS-to-Modified Booth Recoder:** Implement the direct recoding algorithm of Tsoumanis et al. achieving $8\,T_g$ delay with zero CPAs.
4. **CSA Tree Multiplier with Fused Addend:** Fuse the external accumulation operand ($K^*$ or $N^*$) directly into the Wallace/Dadda multiplier tree.
5. **Dual-Rail Integrated Clock Gating (ICG):** Implement a latch-based glitch-free ICG cell to suppress dynamic power during idle cycles.
6. **Bit-Accurate Verification:** Verify 100% mathematical equivalence across 500+ test vectors and 3 real DSP filter benchmarks (FIR16, Elliptic, Volterra).

---

### Speaker Presenter Notes
> *"Based on this problem, our objective is six-fold. First, design a Flexible Computational Unit that operates entirely in the carry-save domain. Second, use a 4:2 compressor to fuse additions and subtractions in a constant 4 gate delays, regardless of bit width. Third, recode carry-save numbers directly into Radix-4 Booth digits in 8 gate delays without a CPA. Fourth, absorb the accumulator addend directly into the multiplier tree. Fifth, introduce dual-rail Integrated Clock Gating to eliminate idle dynamic power. And finally, prove 100% mathematical precision and quantify hardware gains over the conventional baseline."*

---

<!-- slide -->

## Slide 5: Literature Survey

### Visual Layout
- Clean comparative literature review table citing verified IEEE papers.

---

### Slide Content

| Paper / Authors | Year & Journal | Architecture Studied | Core Methodology | Key Contributions | Inherent Limitations |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **M. D. Galanis et al. [2]** | 2006<br>*IEEE TCAD* | Flexible Computational Component (FCC) | Reconfigurable two's-complement datapath | Extracted chained DSP templates; high ILP | Suffers from 3 cascaded CPAs ($140\,T_g$ critical delay) |
| **A. K. Verma, P. Brisk [5]** | 2008<br>*IEEE TCAD* | ASIC Datapath Transformations | High-level DFG Carry-Save optimization | Maximized carry-save clustering in linear DFGs | Inflexible ASIC implementation; fails when multiplications are interleaved |
| **S. Xydis et al. [3]** | 2011<br>*IEEE TVLSI* | Reconfigurable Arithmetic Unit (RAU) | Flexible pipelining with carry-save chaining | Reduced area via fine-grained pipelining | Multiplications require 4 cycles; limited computational density |
| **K. Tsoumanis et al. [6]** | 2014<br>*IEEE TCAS-I* | Add-Multiply Operator | Direct CS-to-Booth recoding algorithm | Recoded $\{P_C, P_S\}$ directly into Radix-4 digits | Component-level study; did not integrate full accelerator or clock gating |
| **K. Tsoumanis et al. [1]<br>*(Base Paper)*** | 2016<br>*IEEE TVLSI* | Flexible Computational Unit (FCU) | Pervasive Carry-Save datapath with templates T1–T5 | Achieved 61.9% ADP gain; eliminated intermediate CPAs | Focused on ASIC delay; **did not implement clock-level power gating** |
| **Our Proposed Work** | **2026–2027<br>*(CMRIT)*** | **Energy-Efficient FCU with Dual-Rail ICG** | **Synthesizable SystemVerilog RTL + Dual-Rail ICG** | **Zero-CPA datapath + glitch-free ICG saving 5.88%–9.58% dynamic power** | Evaluated under simulation; physical layout planned for future work |

---

### Speaker Presenter Notes
> *"In our literature survey, we thoroughly analyzed the progression of flexible DSP hardware. Galanis et al. introduced the FCC, but it was limited by binary carry-propagation. Verma and Brisk optimized carry-save arithmetic, but only for inflexible ASICs. Xydis et al. introduced the RAU, but multi-cycle multiplications degraded performance. The 2016 IEEE TVLSI base paper by Tsoumanis et al. unified carry-save chaining across additions and multiplications. Our major project builds directly upon that base paper by adding synthesizable SystemVerilog RTL and implementing dual-rail Integrated Clock Gating to eliminate idle power dissipation, which the base paper did not address at the clock-network level."*

---

<!-- slide -->

## Slide 6: Existing System (Conventional FCC Baseline)

### Visual Layout
- Embed `figures/fig_base_paper_existing_fcc.png`.
- Highlight the three red blocks representing CPA 1, internal multiplier CPA, and CPA 2.

---

### Slide Content

### Micro-Architecture of the Conventional FCC Datapath

*(Refer to Figure 1 of our paper: `figures/fig_base_paper_existing_fcc.png`)*

```
Inputs: X [15:0], Y [15:0], A [15:0], K [15:0] (Non-redundant two's complement)
   │         │
   └────┬────┘
        ▼
   [ MUX (Add/Sub) ]
        ▼
   [ Carry-Propagate Adder 1 (CPA 1) ] ──────────► Delay: 32 Tg (Ripple Carry)
        ▼ (Binary N = X ± Y)
   [ Conventional Radix-4 Booth Multiplier ]
     ├─ Booth Encoder (8 Tg)
     ├─ PPG + Wallace CSA Tree (36 Tg)
     └─ Internal CPA Adder (32 Tg) ──────────────► Delay: 76 Tg (Forces Binary Conversion!)
        ▼ (Binary Product = A × N)
   [ Carry-Propagate Adder 2 (CPA 2) ] ──────────► Delay: 32 Tg (Post-Addition + K)
        ▼
   Output W [15:0] (Two's Complement Binary)
```

### Quantitative Metrics of the Existing FCC:
- **Gate-Equivalent Area Complexity:** $3274.0 \, A_g$
- **Critical Path Delay:** $T_{\text{crit}} = 32 + 76 + 32 = \mathbf{140.0 \, T_g}$ ($1.68\,\text{ns}$ in 65nm CMOS)
- **Area-Delay Product (ADP):** $3274 \times 140 = \mathbf{458,360 \, A_g \cdot T_g}$
- **Dynamic Power Dissipation:** $0.2510\,\text{mW}$ (continuous clock)

---

### Speaker Presenter Notes
> *"Slide 6 presents the Existing System datapath in detail. In the conventional FCC, operands X, Y, A, and K are 16-bit binary numbers. Stage 1 computes pre-addition using CPA 1, incurring 32 gate delays. Stage 2 executes multiplication: even though the internal Wallace tree compresses partial products quickly, an internal CPA of 32 gate delays is required to output a binary product. Stage 3 uses CPA 2 to accumulate K, adding another 32 gate delays. The total critical path delay reaches 140 gate delays, resulting in an Area-Delay Product of over 458,000 gate units."*

---

<!-- slide -->

## Slide 7: Proposed System Architecture (Carry-Save FCU)

### Visual Layout
- Two-column contrast: Left = Theoretical Principles, Right = Architectural Innovations.

---

### Slide Content

### Core Innovations of the Proposed Flexible Computational Unit (FCU)

```
Proposed Carry-Save Chaining (FCU):
  X*, Y* ─────► [ 4:2 Carry-Save Compressor ] ─────► Constant Delay: 4 Tg!
                        │
                        ▼ (Carry-Save N* = {NC, NS})
  P*     ─────► [ Direct CS-to-MB Recoder ]  ─────► Delay: 8 Tg (NO CPA!)
                        │
                        ▼ (Booth Digits d_i in {-2, -1, 0, 1, 2})
  A, K*  ─────► [ CSA Tree Multiplier with  ] ─────► Delay: 24 Tg (Inline Fusion)
                [ Fused External Addend     ]
                        │
                        ▼
  Total FCU Critical Path Delay ≈ 40 Tg (1.13 ns in 65nm CMOS) ──► 71.43% Speedup!
```

1. **Pervasive Carry-Save Representation:**
   - Every internal operand is stored as a redundant pair: $X^* = \{X_C, X_S\}$, where $\text{Value} = X_C + X_S$.
   - Eliminates all intermediate carry-propagate conversions between chained operations.

2. **Constant-Time Pre-Addition (4:2 Compressor):**
   - Fuses additions and subtractions prior to multiplication in **strictly $4\,T_g$ delay**, regardless of word length (16-bit, 32-bit, or 64-bit).

3. **Direct CS-to-Modified Booth (CS-to-MB) Recoder:**
   - Directly converts carry-save pair $\{P_C, P_S\}$ into Radix-4 Booth control signals (`one`, `two`, `neg`, `zero`) in **$8\,T_g$ delay** without an intermediate CPA.

4. **CSA Tree Multiplier with Inlined Operand Fusion:**
   - Accumulator addend ($K^*$ or $N^*$) is injected directly into the CSA tree as an extra operand, eliminating CPA 2 completely.

5. **Boundary CStoBin Converter:**
   - A single CPA is placed strictly at the output boundary of the accelerator, completely removed from the internal execution loop.

---

### Speaker Presenter Notes
> *"Slide 7 introduces our proposed solution: the Flexible Computational Unit (FCU). Instead of converting to binary after each operation, the FCU maintains data in Carry-Save format throughout the entire pipeline. Pre-addition is performed by a 4:2 compressor in a constant 4 gate delays. Next, our direct CS-to-MB recoder converts the carry-save operand into Radix-4 Booth digits in 8 gate delays with zero carry propagation. Finally, the accumulator addend is injected directly into the CSA multiplier tree in 24 gate delays. As a result, the critical path delay plummets from 140 gate delays down to just 40 gate delays—a massive 71.4% reduction!"*

---

<!-- slide -->

## Slide 8: Overall System Architecture & Dataflow

### Visual Layout
- Embed `figures/fig1_top_level_architecture.png` (Top-level core) on the left.
- Embed `figures/fig2_fcu_microarchitecture.png` (FCU micro-architecture) on the right.

---

### Slide Content

### System-Level and Micro-Architectural Block Diagrams

*(Refer to Figures 1 & 2 of our paper)*

#### Top-Level Accelerator Core (Figure 1):
- **Data Port:** High-speed I/O interface communicating with local memory.
- **Scratch Register Bank:** Stores intermediate values as dual-rail Carry-Save pairs $\{X_C, X_S\}$ in scratch registers R0*–R7*.
- **Crossbar Interconnection Network:** Dynamically routes operands between registers and execution units.
- **FCU Cluster:** Instantiates multiple parallel FCUs (FCU 0 to FCU 3) for high Instruction-Level Parallelism (ILP).
- **Boundary CStoBin Converter:** Single 16-bit ripple-carry adder converting final accelerator outputs to standard two's-complement binary.
- **Control Unit & FSM Scheduler:** Decodes configuration words, controls MUX selections (`CL0–CL3`), and asserts `clk_gate_en`.

#### FCU Micro-Architecture (Figure 2):
- **MUX 0 ($CL_0$):** Selects $Y^*$ or its bitwise complement $\sim Y^*$ for subtraction.
- **4:2 Carry-Save Compressor:** Compresses 4 inputs into $N^* = \{N_C, N_S\}$.
- **MUX 1 ($CL_1$) & MUX 2 ($CL_2$):** Route $N^*$ and $K^*$ to either the multiplier input $P^*$ or the fused addend input.
- **Multiplier Subsystem:** CS-to-MB recoder + PPG + CSA reduction tree.
- **MUX 3 ($CL_3$):** Selects addition or subtraction for the fused external addend.
- **Dual-Rail Integrated Clock Gating (ICG):** Gates the clock feeding the output registers $W^* = \{W_C, W_S\}$.

---

### Speaker Presenter Notes
> *"This slide illustrates our overall hardware architecture. Figure 1 shows the top-level accelerator consisting of the data port, an 8-register scratchpad storing dual-rail carry-save pairs, a crossbar interconnect, 4 parallel FCUs, and a single boundary CStoBin converter. Figure 2 shows the detailed FCU datapath: notice how MUX0, MUX1, MUX2, and MUX3 dynamically reconfigure the datapath to execute different operation templates while keeping all intermediate data in carry-save form."*

---

<!-- slide -->

## Slide 9: Working Principle & Numerical Walkthrough

### Visual Layout
- Step-by-step arithmetic dataflow trace for Template T1 using concrete numerical inputs.

---

### Slide Content

### Step-by-Step Arithmetic Execution (Template T1 Example)

$$\text{Operation: } W^* = A \times (X^* + Y^*) + K^*$$
$$\text{Inputs: } A = 25, \quad X = 100 \; (X_C=50, X_S=50), \quad Y = 50 \; (Y_C=25, Y_S=25), \quad K = 10 \; (K_C=5, K_S=5)$$
$$\text{Expected Final Value: } 25 \times (100 + 50) + 10 = 25 \times 150 + 10 = \mathbf{3760}$$

```
Step 1: 4:2 Carry-Save Compression (Pre-Addition)
  Inputs:  XC = 50 (0x0032), XS = 50 (0x0032) -> X = 100
           YC = 25 (0x0019), YS = 25 (0x0019) -> Y = 50
  Output:  NC = 100 (0x0064), NS = 50 (0x0032) -> N* = NC + NS = 150
  Delay:   Exactly 4 Tg (Two Full-Adder delays, zero global carry ripple!)

Step 2: Operand Selection via Multiplexers
  MUX0 (CL0 = 0) -> Selects Y* (Addition mode)
  MUX1 (CL1 = 0) -> Routes N* to Multiplier Input P* = {PC=100, PS=50}
  MUX2 (CL2 = 0) -> Routes K* to Multiplier Fused Addend = {KC=5, KS=5}

Step 3: Direct CS-to-Modified Booth (CS-to-MB) Recoding
  P* = {PC=100, PS=50} recoded directly into 8 Radix-4 Booth digits:
  d_i in {-2, -1, 0, 1, 2} without any CPA conversion! (Delay = 8 Tg)

Step 4: CSA Multiplier Tree with Inlined Operand Fusion
  Generates 8 Partial Products: PP_k = A * d_k * 4^k
  Inlines External Addend K* = 10 directly into the CSA reduction tree:
  Total Sum = sum(PP_k) + K* = 3750 + 10 = 3760

Step 5: Dual-Rail Carry-Save Output & Boundary Conversion
  Output Registers capture CS pair: WC = 0x0758 (1880), WS = 0x0758 (1880)
  CStoBin Converter computes: 1880 + 1880 = 3760 (Two's Complement Binary)
```

---

### Speaker Presenter Notes
> *"To prove the arithmetic correctness of our design to the examiner, Slide 9 walks through a step-by-step numerical example for Template T1. We input $A=25$, $X=100$, $Y=50$, and $K=10$. In Step 1, the 4:2 compressor adds X and Y in 4 gate delays, producing a carry-save sum of 150. In Step 3, our CS-to-MB recoder directly generates Radix-4 Booth digits in 8 gate delays. In Step 4, the partial products and the addend $K=10$ are compressed directly inside the CSA tree to yield 3760. Finally, the output registers hold the carry-save pair 1880 and 1880, which the boundary converter adds to exactly 3760."*

---

<!-- slide -->

## Slide 10: Individual Hardware Module Breakdown

### Visual Layout
- Modular table detailing hardware function, inputs, outputs, gate area ($A_g$), and delay ($T_g$) for every block.

---

### Slide Content

### Micro-Architectural Specification of FCU Building Blocks

| Module Name | Hardware Function | Primary Inputs | Primary Outputs | Area ($A_g$) | Delay ($T_g$) | Key Engineering Feature |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **`compressor_4_2`** | 16-bit 4:2 Carry-Save Compressor / Adder | $X_C, X_S, Y_C, Y_S$, $cin_1, cin_2$ | $N_C, N_S, cout$ | $224 \, A_g$ | $\mathbf{4 \, T_g}$ | Cascaded FA bit-slices; horizontal carries do NOT ripple across word width. |
| **`cs_to_mb_recoder`** | Direct CS-to-Modified Booth Recoder | $P_C, P_S$ (16-bit CS) | `one`, `two`, `neg`, `zero` (8 digits) | $240 \, A_g$ | $\mathbf{8 \, T_g}$ | Eliminates CPA before multiplication; only transfers $c_{\text{transfer}} \in \{0, 1, 2\}$ locally. |
| **`csa_tree_multiplier`** | Multiplier with Inlined Operand Fusion | Multiplicand $A$, $P^*$, Ext Addend | $W_C, W_S$ (16-bit CS) | $1950 \, A_g$ | $\mathbf{24 \, T_g}$ | Compresses 8 partial products and absorbs external addend directly in the tree. |
| **`icg_cell`** | Integrated Clock Gating Cell | `clk`, `clk_gate_en` | `gated_clk` | $6 \, A_g$ | $1 \, T_g$ | Negative-edge latch + AND gate prevents clock glitches and rail skew. |
| **`cs_to_bin`** | Boundary Converter Module | $W_C, W_S$ (16-bit CS) | `bin_out` (16-bit binary) | $112 \, A_g$ | $32 \, T_g$ | Standard CPA placed strictly at chip boundary; off the internal critical path. |
| **`fcu_top`** | Top-Level FCU Datapath | Operands, Template Sel, Clock Controls | $W_C, W_S$, `bin_out` | $\mathbf{2624 \, A_g}$ | $\mathbf{40 \, T_g}$ | Reconfigurable MUX network (`MUX0–MUX3`) supporting Templates T1–T5. |

---

### Speaker Presenter Notes
> *"Slide 10 details the modular breakdown of our Verilog RTL. Notice the area and delay values derived from the standard Unit Gate Model. The 4:2 compressor requires only 224 gate equivalents with a fixed 4 gate delays. The CS-to-MB recoder occupies 240 gate units and completes recoding in 8 gate delays. The CSA multiplier tree takes 24 gate delays. Including MUX routing, the entire FCU occupies 2624 gate units and runs in 40 gate delays—which is 19.8% smaller and 71.4% faster than the conventional FCC baseline!"*

---

<!-- slide -->

## Slide 11: Operation Template Library (Templates T1 – T5)

### Visual Layout
- Embed `figures/fig4_templates_dataflow.png` showing the 5 Data-Flow Graphs.

---

### Slide Content

### Reconfigurable Template Execution Modes (IEEE TVLSI Fig. 3)

*(Refer to Figure 4 of our paper: `figures/fig4_templates_dataflow.png`)*

| Template | Mathematical Formula | Control Word (`CL0, CL1, CL2, CL3`) | Target DSP Application & Kernel |
| :---: | :--- | :---: | :--- |
| **T1** | $W^* = A \times (X^* + Y^*) + K^*$ | `0, 0, 0, 0` | **Symmetrical FIR Filters, FFT Butterflies, Elliptic Filter** (Pre-addition fuses symmetric filter taps before multiplication). |
| **T2** | $W^* = A \times (X^* - Y^*) + K^*$ | `1, 0, 0, 0` | **Differential FIR Filters, Image Gradient / Edge Detection** (Pre-subtraction computes spatial derivatives). |
| **T3** | $W^* = A \times K^* + (X^* + Y^*)$ | `0, 1, 1, 0` | **MAC with Pre-Accumulation, Volterra Filters** (Multiplication of $A \times K^*$ combined with external sum). |
| **T4** | $W^* = A \times K^* + (X^* - Y^*)$ | `1, 1, 1, 0` | **Complex Number Arithmetic Subtraction Stages, Kalman Filtering**. |
| **T5** | $W^* = A \times K^*$ | `0, 1, 0, 0` | **Standalone Scaling, Dot Product Normalization**. |

#### Multiplexer Routing Logic:
- **`CL0` (MUX0):** $0 \rightarrow Y^*$; $1 \rightarrow \sim Y^*$ (Inverts both carry and sum rails for subtraction).
- **`CL1` (MUX1):** $0 \rightarrow P^* = N^*$ (Compressor output); $1 \rightarrow P^* = K^*$ (Direct input).
- **`CL2` (MUX2):** $0 \rightarrow \text{Addend} = K^*$; $1 \rightarrow \text{Addend} = N^*$.
- **`CL3` (MUX3):** $0 \rightarrow \text{Add Addend}$; $1 \rightarrow \text{Subtract Addend}$.

---

### Speaker Presenter Notes
> *"Slide 11 shows how our FCU achieves reconfigurability across 5 standard DSP operation templates. In Template T1, MUX0 adds X and Y, and MUX1 routes the sum to the multiplier. In Template T2, MUX0 inverts Y for subtraction. In Template T3, the multiplier computes A times K, while X and Y are added in parallel and fused into the tree. Templates T4 and T5 handle complex subtraction and standalone multiplication. By simply toggling a 4-bit configuration word, our single datapath covers symmetrical FIR filtering, FFT butterfly stages, and polynomial Volterra filtering."*

---

<!-- slide -->

## Slide 12: Low-Power Integrated Clock Gating (ICG) Architecture

### Visual Layout
- Embed `figures/fig5_clock_gating_schematic.png`: Left = Schematic (Latch + AND), Right = Waveform.

---

### Slide Content

### Dual-Rail Glitch-Free Integrated Clock Gating (ICG)

*(Refer to Figure 5 of our paper: `figures/fig5_clock_gating_schematic.png`)*

```
Clock Gating Circuit:
  clk_gate_en ──► [ D-Latch ] ──► latch_en ──┐
                    (Neg-Edge)                │
                                              ├──► [ AND Gate ] ──► gated_clk (To FCU Registers)
  clk ──────────┬─────────────────────────────┘
                │
                └───► (Controls Negative Latch)
```

1. **Why Standard AND-Gating Fails:**
   - A simple `clk & enable` AND gate produces dangerous **clock glitches and runt pulses** if the enable signal transitions while the clock is high.
   - Glitches corrupt register data and cause timing violations.

2. **Negative-Latch ICG Solution:**
   - Uses a **negative-level-sensitive D-latch** that samples `clk_gate_en` strictly while `clk` is LOW.
   - When `clk` goes HIGH, the latch output `latch_en` is held completely stable.
   - Equation:
     $$\text{gated\_clk} = \text{clk} \ \& \ \text{Latch}(\text{clk\_gate\_en})$$

3. **Dual-Rail Gating Innovation:**
   - Because Carry-Save stores two registers per word ($\{W_C, W_S\}$), gating only one rail would leave the other toggling and corrupt the carry-save state.
   - Our design drives both carry and sum register clock inputs from a unified ICG tree, ensuring **zero rail skew** and eliminating dynamic power during idle cycles.

---

### Speaker Presenter Notes
> *"Slide 12 presents our primary novelty: the dual-rail Integrated Clock Gating circuit. In carry-save hardware, each variable requires two registers: one for Carry and one for Sum. If you use a simple AND gate to stop the clock, glitches occur whenever the enable toggles during clock high. We implemented an ICG cell using a negative-edge D-latch that only updates when the clock is low, guaranteeing glitch-free clock gating. When the unit is idle, both carry and sum registers are disabled simultaneously, preventing rail skew and reducing dynamic power by up to 9.58%."*

---

<!-- slide -->

## Slide 13: Design & Implementation Methodology

### Visual Layout
- Linear 9-stage engineering development pipeline diagram.

---

### Slide Content

### Complete Research & Development Workflow

```
[ Phase 1: Research & Algorithm Analysis ]
  - Studied IEEE TVLSI 2016 Base Paper & IEEE TCAD FCC Architecture.
  - Formulated Carry-Save arithmetic equations and dual-rail subtraction rules (+2 carry-in).

[ Phase 2: High-Level Python Cycle-Accurate Simulator ]
  - Built bit-accurate software models: cs_arithmetic.py, cs_to_mb_recoder.py, csa_tree_multiplier.py.
  - Implemented switching activity tracker to model dynamic power dissipation.

[ Phase 3: Synthesizable SystemVerilog RTL Modeling ]
  - Coded modular RTL: icg_cell.v, compressor_4_2.v, cs_to_mb_recoder.v, csa_tree_multiplier.v.
  - Integrated top-level datapath (fcu_top.v) with MUX0–MUX3 decoder and boundary CStoBin.

[ Phase 4: Testbench & Assertion-Based Verification ]
  - Developed self-checking testbench (testbench.sv) covering Templates T1–T5 and Clock Gating.
  - Executed 500+ random test vectors to verify 100% mathematical equivalence.

[ Phase 5: Behavioral Simulation & Waveform Inspection ]
  - Ran simulations in Icarus Verilog, ModelSim, and EDA Playground (EPWave).
  - Validated decimal outputs: 3760, 1805, 460, 260, 720 and register freeze under clock gating.

[ Phase 6: Metric Comparison & Benchmark Evaluation ]
  - Evaluated FIR16, Elliptic, and Volterra filters under 65nm Unit Gate Model.
  - Extracted Area, Delay, ADP, Power, and Energy savings for IEEE paper presentation.
```

---

### Speaker Presenter Notes
> *"Slide 13 outlines our complete design methodology. We followed a rigorous 6-phase engineering workflow. We started by mathematically analyzing carry-save arithmetic and dual-rail subtraction. Next, we built a Python cycle-accurate simulator to serve as our golden reference model. Then, we wrote synthesizable SystemVerilog RTL modules, created a self-checking testbench, and ran behavioral simulations in EDA Playground and ModelSim. Finally, we verified bit-accurate equivalence across 500 test vectors and mapped three real DSP benchmark filters to extract energy and area metrics."*

---

<!-- slide -->

## Slide 14: Tools, Technologies & Simulation Environment

### Visual Layout
- Clean 4-card layout detailing Languages, Simulators, Synthesis Tools, and Methodology Standards.

---

### Slide Content

### Hardware Description Languages & Simulation Stack

```
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ Hardware Description Language   │   │ Simulation & Verification Tools │
│ • SystemVerilog / Verilog HDL   │   │ • EDA Playground (EPWave)       │
│ • Synthesizable RTL-2001/2005   │   │ • Icarus Verilog (v10.0)        │
│ • Self-checking testbenches     │   │ • ModelSim / QuestaSim (Mentor) │
└─────────────────────────────────┘   └─────────────────────────────────┘
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ High-Level Modeling & Scripting │   │ Synthesis & Analysis Targets    │
│ • Python 3.13 (Cycle Simulator) │   │ • Xilinx Vivado (FPGA Target)   │
│ • Matplotlib (Publication Plots)│   │ • 65nm TSMC CMOS Gate Library   │
│ • VCD (Value Change Dump) Trace │   │ • Unit Gate Model (Ag, Tg)      │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

#### Verification Standards Followed:
- **Bit-Accurate Equivalence:** Verified that Carry-Save outputs match standard two's-complement outputs with zero roundoff or precision loss.
- **Corner-Case Verification:** Tested maximum positive values (`0x7FFF`), maximum negative values (`0x8000`), alternating zero patterns, and subtraction cancellation.
- **Glitch & Hazard Checking:** Analyzed `gated_clk` transitions to ensure zero runt pulses reach register inputs.

---

### Speaker Presenter Notes
> *"Slide 14 lists the tools and technologies used. Our hardware is described entirely in standard synthesizable SystemVerilog. We used EDA Playground and ModelSim for behavioral waveform simulation and VCD trace extraction. For architectural modeling and golden equivalence verification, we developed a Python 3 cycle-accurate simulator. Hardware complexity was quantified using the standard Unit Gate Model mapped to 65nm CMOS standard cell technology, ensuring full compatibility with Xilinx Vivado for FPGA synthesis."*

---

<!-- slide -->

## Slide 15: Simulation & Verification Waveforms

### Visual Layout
- Embed the user's EDA Playground EPWave screenshot (`media_1793524770301_7c38109e.png` / `figures/fig6_rtl_simulation_waveform.png`).
- Add highlight callout boxes pointing to T1, T2, T3, T4, T5, and the Gated Clock phase.

---

### Slide Content

### Behavioral RTL Simulation Waveform (Verified in EPWave)

*(Refer to Figure 6 of our paper: `figures/fig6_rtl_simulation_waveform.png`)*

```
Simulation Timeline:
0 ns ──────── 20 ns ────── 30 ns ────── 50 ns ────── 70 ns ────── 90 ns ───── 110 ns ──── 120 ns ──── 160 ns
│ Reset Active│  T1 Mode   │  T2 Mode   │  T3 Mode   │  T4 Mode   │  T5 Mode   │ Clock Gating Active (en=0) │
│ (rst_n = 0) │ 25*150+10  │ 15*120+5   │ 30*12+100  │ 20*8+100   │  45 * 16   │ Input A=99 is IGNORED!     │
▼             ▼            ▼            ▼            ▼            ▼            ▼
bin_out = 0   bin_out=3760 bin_out=1805 bin_out=460  bin_out=260  bin_out=720  bin_out FROZEN AT 720        
              (Hex: 0x0eb0)(Hex: 0x070d)(Hex: 0x01cc)(Hex: 0x0104)(Hex: 0x02d0)(Hex: 0x02d0 -> Glitch-Free!)
```

#### Key Verification Insights:
1. **Reset Phase ($0 - 20\,\text{ns}$):** Output registers $W_C$ and $W_S$ initialize cleanly to `0`.
2. **Template T1 ($30 - 50\,\text{ns}$):** $A=25, X=100, Y=50, K=10 \rightarrow \text{bin\_out} = \mathbf{3760}$ (`0x0eb0`).
3. **Template T2 ($50 - 70\,\text{ns}$):** $A=15, X=150, Y=30, K=5 \rightarrow \text{bin\_out} = \mathbf{1805}$ (`0x070d`).
4. **Template T3 ($70 - 90\,\text{ns}$):** $A=30, K=12, X=60, Y=40 \rightarrow \text{bin\_out} = \mathbf{460}$ (`0x01cc`).
5. **Template T4 ($90 - 110\,\text{ns}$):** $A=20, K=8, X=150, Y=50 \rightarrow \text{bin\_out} = \mathbf{260}$ (`0x0104`).
6. **Template T5 ($110 - 130\,\text{ns}$):** $A=45, K=16 \rightarrow \text{bin\_out} = \mathbf{720}$ (`0x02d0`).
7. **Clock Gating Phase ($>120\,\text{ns}$):** `clk_gate_en` deasserted $\rightarrow$ `bin_out` stays **frozen at 720** even when `a_in` changes to `99`!

---

### Speaker Presenter Notes
> *"Slide 15 presents our actual behavioral simulation waveform extracted from EDA Playground. In the first phase, we assert reset. At 30ns, Template T1 executes: the output bin_out updates to 3760, which matches 25 times 150 plus 10. Next, Templates T2, T3, T4, and T5 execute, producing 1805, 460, 260, and 720. Crucially, look at the 120ns mark: we deassert clk_gate_en to test clock gating. Notice that input A changes to 99, but bin_out remains completely frozen at 720. This confirms that our integrated clock gating cell successfully halts register toggling without any errors."*

---

<!-- slide -->

## Slide 16: Performance Results & Comparative Analysis

### Visual Layout
- Embed `figures/fig7_hardware_comparison.png` and `figures/fig8_energy_kernels.png`.
- Highlight the 71.43% delay reduction and 77.10% ADP improvement in bold green badges.

---

### Slide Content

### Quantitative Results: Conventional FCC vs. Proposed Carry-Save FCU

#### 1. Hardware Complexity & Delay Comparison (Paper Table II)
| Architectural Metric | Conventional FCC (Existing) | Proposed Carry-Save FCU | Quantitative Improvement |
| :--- | :---: | :---: | :---: |
| **Intermediate CPAs** | **3 CPAs** | **0 CPAs** | **All intermediate CPAs eliminated** |
| **Critical Path Delay ($T_g$)** | **$140.0 \, T_g$** | **$40.0 \, T_g$** | **71.43% Delay Reduction (3.5× Faster!)** |
| **Clock Period @ 65nm ($T_{\text{crit}}$)** | **$1.68 \, \text{ns}$** | **$1.13 \, \text{ns}$** | **32.74% Higher Operating Frequency** |
| **Gate-Equivalent Area ($A_g$)** | **$3274.0 \, A_g$** | **$2624.0 \, A_g$** | **19.85% Area Reduction** |
| **Area-Delay Product (ADP)** | **$458,360 \, A_g \cdot T_g$** | **$104,960 \, A_g \cdot T_g$** | **77.10% Overall Efficiency Gain** |

#### 2. Kernel-Level Energy Consumption @ 65nm (Paper Table III)
- **16-Tap FIR Filter (`FIR16`):** Reduced from $1038.04\,\text{pJ} \rightarrow \mathbf{754.05\,\text{pJ}}$ (**27.36% Energy Reduction**)
- **6th-Order Elliptic Filter (`ELLIPTIC`):** Reduced from $261.04\,\text{pJ} \rightarrow \mathbf{167.18\,\text{pJ}}$ (**35.95% Energy Reduction**)
- **2nd-Order Volterra Filter (`VOLTERRA`):** Reduced from $391.30\,\text{pJ} \rightarrow \mathbf{243.18\,\text{pJ}}$ (**37.85% Energy Reduction**)

#### 3. Dynamic Power Savings with Clock Gating (Paper Table IV)
- In the proposed FCU, dual-rail ICG reduces dynamic power from $0.5478\,\text{mW} \rightarrow \mathbf{0.5156\,\text{mW}}$ (**5.88% dynamic power saved**).

---

### Speaker Presenter Notes
> *"Slide 16 presents our experimental results. Compared to the conventional FCC baseline, our proposed FCU cuts the critical path delay by 71.43%, reducing gate delay from 140 Tg to 40 Tg. In 65nm CMOS, the clock period drops from 1.68ns to 1.13ns. Even though Carry-Save representation doubles register bits, our gate area decreases by 19.85% because we eliminated two 16-bit CPAs and absorbed the accumulator into the multiplier tree. This achieves a 77.10% improvement in Area-Delay Product and delivers up to 37.85% energy savings across real DSP filters."*

---

<!-- slide -->

## Slide 17: Advantages & Real-World Applications

### Visual Layout
- Left Column: Technical advantages over conventional VLSI architectures.
- Right Column: Targeted real-world industry applications.

---

### Slide Content

### Core Technical Advantages
- **Constant-Time Pre-Addition ($4\,T_g$):** Adding or subtracting operands prior to multiplication takes constant time regardless of whether bit-width is 16, 32, or 64 bits.
- **Zero Intermediate Carry Propagation:** By eliminating intermediate CPAs, high-frequency operation is sustained even in deeply scaled sub-micron CMOS nodes.
- **Glitch-Free Dynamic Power Suppression:** Dual-rail ICG stops clock distribution to both carry and sum register rails with zero rail skew.
- **Reconfigurable Template Support:** Executes symmetrical FIR, differential FIR, MAC, and scaling on a single unified datapath.

### Real-World Industry Applications
```
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ 1. Wireless Communications      │   │ 2. Edge AI & TinyML Inference   │
│ • 5G OFDM Channel Estimation    │   │ • 1D/2D CNN Convolution Layers  │
│ • FFT / IFFT Butterfly Stages   │   │ • Quantized INT8/INT16 Multiply-│
│ • Digital Down-Converters (DDC) │   │   Accumulate (MAC) Engines      │
└─────────────────────────────────┘   └─────────────────────────────────┘
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ 3. Biomedical Signal Processing │   │ 4. Multimedia & Video Codecs    │
│ • Real-time ECG/EEG Filtering   │   │ • 2-D Discrete Cosine Transform │
│ • Low-power Wearable Sensors    │   │ • High-Efficiency Motion        │
│ • Adaptive Noise Cancellation   │   │   Compensation Filters          │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

---

### Speaker Presenter Notes
> *"Slide 17 outlines the practical engineering advantages and applications. Because our pre-addition stage operates in constant time, this architecture scales exceptionally well to 32-bit and 64-bit precision. Furthermore, the combination of high computational throughput and clock gating makes this accelerator ideal for battery-powered wearable biomedical devices like ECG monitors, 5G wireless baseband filters, and real-time Edge AI convolutional neural network acceleration."*

---

<!-- slide -->

## Slide 18: Limitations, Future Scope & Conclusion

### Visual Layout
- Two-column layout: Left = Limitations & Future Improvements, Right = Final Concluding Summary.

---

### Slide Content

### Implementation Limitations & Future Scope
- **Current Limitations:**
  - **Register Width:** Carry-Save representation requires storing two 16-bit rails per operand, doubling scratchpad register width and interconnection routing wires.
  - **Peak Instantaneous Power:** Due to wider dual-rail datapaths, peak instantaneous power is higher, though total energy per kernel is substantially lower.
- **Planned Future Extensions:**
  - **FPGA On-Board Validation:** Synthesizing the design onto a Xilinx Artix-7 / Zynq-7000 FPGA development board with hardware I/O verification.
  - **Multi-Precision Reconfigurability:** Enabling dynamic splitting of the 16-bit FCU into two parallel 8-bit FCUs for quantized Edge AI inference.
  - **Data-Dependent Operand Isolation:** Shutting down multiplier Booth logic when multiplier inputs are zero.

### Final Conclusion
1. **Problem Solved:** Overcame the fundamental carry-propagate adder bottleneck that degrades speed and energy in conventional flexible DSP accelerators.
2. **Architecture Delivered:** Successfully designed and verified a synthesizable Carry-Save Flexible Computational Unit (FCU) supporting templates T1–T5 with dual-rail ICG.
3. **Validated Gains:** Demonstrated a **71.43% reduction in critical path delay**, a **77.10% improvement in Area-Delay Product**, and up to **37.85% energy savings** across benchmark DSP kernels.

---

### Speaker Presenter Notes
> *"In conclusion, our project demonstrates that by replacing conventional binary arithmetic with pervasive carry-save computation, we can fundamentally break the carry-propagation bottleneck in DSP accelerators. We successfully verified all five operation templates and proved glitch-free clock gating in Verilog RTL. While carry-save arithmetic increases register wiring width, the 71.4% delay cut and 77% ADP improvement far outweigh the routing cost. Thank you for your time, and we are now ready for your questions."*

---

<!-- slide -->

## Slide 19: References & Question and Answer Session

### Visual Layout
- Formal academic reference listing following IEEE citation standards, followed by a professional Q&A closing banner.

---

### Slide Content

### Academic References
1. **[1] K. Tsoumanis, S. Xydis, G. Zervakis, and K. Pekmestzi**, *"Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic,"* **IEEE Transactions on Very Large Scale Integration (VLSI) Systems**, Vol. 24, No. 1, pp. 368–372, Jan. 2016. *(Base Paper)*
2. **[2] M. D. Galanis, G. Theodoridis, S. Tragoudas, and C. E. Goutis**, *"A High-Performance Data Path for Synthesizing DSP Kernels,"* **IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems**, Vol. 25, No. 6, pp. 1154–1162, Jun. 2006. *(FCC Baseline)*
3. **[3] S. Xydis, G. Economakos, D. Soudris, and K. Pekmestzi**, *"High Performance and Area Efficient Flexible DSP Datapath Synthesis,"* **IEEE Transactions on VLSI Systems**, Vol. 19, No. 3, pp. 429–442, Mar. 2011.
4. **[4] T. Kim and J. Um**, *"A Practical Approach to the Synthesis of Arithmetic Circuits Using Carry-Save-Adders,"* **IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems**, Vol. 19, No. 5, pp. 615–624, May 2000.
5. **[5] A. K. Verma, P. Brisk, and P. Ienne**, *"Data-Flow Transformations to Maximize the Use of Carry-Save Representation in Arithmetic Circuits,"* **IEEE Transactions on CAD**, Vol. 27, No. 10, pp. 1761–1774, Oct. 2008.
6. **[6] K. Tsoumanis, S. Xydis, C. Efstathiou, N. Moschopoulos, and K. Pekmestzi**, *"An Optimized Modified Booth Recoder for Efficient Design of the Add-Multiply Operator,"* **IEEE Transactions on Circuits and Systems I: Regular Papers**, Vol. 61, No. 4, pp. 1133–1143, Apr. 2014.
7. **[7] B. Parhami**, *Computer Arithmetic: Algorithms and Hardware Designs*, Oxford University Press, 2000.
8. **[8] N. H. E. Weste and D. M. Harris**, *CMOS VLSI Design: A Circuits and Systems Perspective*, 4th ed., Addison-Wesley, 2010.

---

### Thank You!
#### Questions & Discussion Welcome.

---

### Speaker Presenter Notes
> *"Here are our primary research references, including the 2016 IEEE TVLSI base paper and foundational VLSI textbooks. We thank our internal project guide and the department faculty for their continuous support throughout our major project. We welcome your feedback, critiques, and questions."*

---

# External Examiner Viva Voce Defense Guide
### 10 Critical Technical Questions & High-Scoring Model Answers

---

#### Q1: What exactly is Carry-Save representation, and why does it save time?
**Examiner's Intent:** To test if the student understands the underlying arithmetic theory.  
**High-Scoring Answer:**  
> *"In standard binary, a number is represented by a single vector, meaning whenever an addition takes place, every bit must wait for the carry generated by the previous bit slice, causing $O(N)$ delay. In Carry-Save representation, a number is stored as two independent vectors: a Sum vector $X_S$ and a Carry vector $X_C$, where $\text{Value} = X_C + X_S$. When two carry-save numbers are added using a 4:2 compressor, carries are passed only to the immediately adjacent bit slice horizontally—they never propagate across the entire word width. Therefore, addition is performed in constant $O(1)$ delay ($4\,T_g$), completely independent of whether the operand is 16, 32, or 64 bits wide."*

---

#### Q2: How does a 4:2 compressor achieve a constant delay of $4\,T_g$?
**Examiner's Intent:** To check if the student knows the circuit-level composition of the compressor.  
**High-Scoring Answer:**  
> *"A 4:2 compressor bit-slice is constructed from two cascaded Full Adders. The first Full Adder takes three inputs ($X_S, Y_S, Y_C$) and generates an intermediate sum $sum_1$ and a horizontal carry $cout_1$. Crucially, $cout_1$ is routed directly to the second Full Adder of the next bit slice ($i+1$)—it does not propagate further. The second Full Adder takes $sum_1$, $X_C$, and the horizontal carry from bit slice $i-1$, producing the final sum bit and carry bit. Because there are exactly two XOR gate delays in FA1 and two XOR gate delays in FA2, the total critical path delay is strictly $2 + 2 = 4\,T_g$, regardless of word width."*

---

#### Q3: Why couldn't you use standard Radix-4 Booth recoding on a Carry-Save number?
**Examiner's Intent:** To test why the direct CS-to-MB recoder is an essential innovation.  
**High-Scoring Answer:**  
> *"Standard Radix-4 Modified Booth recoding inspects 3-bit overlapping windows of a single binary integer ($b_{2i+1}, b_{2i}, b_{2i-1}$). If an operand is in Carry-Save form $\{P_C, P_S\}$, it consists of two separate bit vectors. Conventional architectures were forced to insert a 16-bit Carry-Propagate Adder to convert $\{P_C, P_S\}$ into a single binary integer before feeding it to the Booth encoder, which re-introduced the very CPA delay we wanted to eliminate. Our direct CS-to-MB recoder uses the arithmetic formulation of Tsoumanis et al. to compute the local weighted sum $val_i = 2(P_{C,2i+1} + P_{S,2i+1}) + (P_{C,2i} + P_{S,2i}) + c_{\text{transfer}}$ and generates Booth digits in $8\,T_g$ delay with zero prior carry-propagation."*

---

#### Q4: How is subtraction handled in Carry-Save arithmetic? Why is a $+2$ carry-in needed?
**Examiner's Intent:** To see if the student caught the dual-rail mathematical subtlety.  
**High-Scoring Answer:**  
> *"In conventional two's-complement binary, negation is formed by inverting all bits and adding $+1$ ($\sim Y + 1$). In Carry-Save format, $Y^*$ consists of two vectors: $Y_C$ and $Y_S$. Inverting both vectors bitwise produces:
> $$\sim Y_C + \sim Y_S = (2^N - 1 - Y_C) + (2^N - 1 - Y_S) = 2 \cdot 2^N - 2 - (Y_C + Y_S) \equiv -(Y_C + Y_S) - 2 \pmod{2^N}$$
> Because there are two ones'-complements, the result is off by $-2$. Therefore, exact two's-complement negation of a Carry-Save pair requires adding $+2$. In our RTL, this is handled elegantly by injecting $cin_1 = 1$ into the horizontal carry chain of the 4:2 compressor, and $cin_2 = 1$ into bit 0 of the output carry vector."*

---

#### Q5: If Carry-Save arithmetic is so fast, why isn't it used everywhere in microprocessors?
**Examiner's Intent:** To test if the student understands architectural trade-offs.  
**High-Scoring Answer:**  
> *"Carry-Save arithmetic is ideal for deep arithmetic pipelines with chained additions and multiplications, such as DSP accelerators and GPU shader cores. However, it is not used for general-purpose CPU register files because it doubles the number of flip-flops (each value requires a Carry rail and a Sum rail) and doubles internal routing bus widths. Furthermore, control flow operations like conditional branching ($A > B$) or zero-checking require a full CPA conversion to determine magnitude. Thus, Carry-Save arithmetic represents a targeted trade-off: higher wiring complexity in exchange for over 70% reduction in arithmetic delay."*

---

#### Q6: Why did you use an Integrated Clock Gating (ICG) cell instead of a simple AND gate?
**Examiner's Intent:** To evaluate the student's VLSI timing and clock-domain knowledge.  
**High-Scoring Answer:**  
> *"Using a simple two-input AND gate with a clock and enable signal is unacceptable in professional VLSI design because if the enable signal changes while the clock is high, it chops the clock pulse, generating a runt pulse or clock glitch that violates register hold times. Our ICG cell uses a negative-level-sensitive D-latch followed by an AND gate. The latch samples `clk_gate_en` strictly while the clock is low and holds it stable during the clock's high phase. This guarantees 100% glitch-free clock gating and suppresses dynamic power without timing hazards."*

---

#### Q7: How did you calculate the delay in $T_g$ and area in $A_g$?
**Examiner's Intent:** To check familiarity with the Unit Gate Model.  
**High-Scoring Answer:**  
> *"We utilized the standard Unit Gate Model widely adopted in VLSI literature (Weste & Harris). Under this model, an inverter has unit delay $1\,T_g$ and unit area $1\,A_g$. Two-input NAND and NOR gates count as $1\,A_g$ and $1\,T_g$. Two-input XOR and XNOR gates count as $2\,A_g$ and $2\,T_g$. A Full Adder has an area of $7\,A_g$ with a carry delay of $2\,T_g$ and sum delay of $4\,T_g$. This provides a technology-independent metric that translates directly to $\approx 28\,\text{ps}$ per $T_g$ in a standard 65nm TSMC CMOS process."*

---

#### Q8: Why is your gate area ($2624\,A_g$) smaller than the baseline FCC ($3274\,A_g$) if Carry-Save registers require double the bits?
**Examiner's Intent:** A classic examiner trap—testing if the student actually checked the area breakdown.  
**High-Scoring Answer:**  
> *"That is an insightful question. Although our scratch registers store 32 bits instead of 16 bits (adding roughly $160\,A_g$ of flip-flop overhead), we eliminated two complete 16-bit Carry-Propagate Adders (saving $2 \times 112 = 224\,A_g$), eliminated the multiplier's internal CPA (saving another $112\,A_g$), and merged the post-accumulation adder directly into the CSA multiplier tree. The massive logic savings from removing three separate 16-bit carry-propagate adders easily outweighs the extra storage bits, yielding an overall 19.85% net reduction in total silicon gate area."*

---

#### Q9: How did you verify that your proposed RTL produces mathematically identical results?
**Examiner's Intent:** To verify simulation rigor and functional equivalence.  
**High-Scoring Answer:**  
> *"We designed a two-tier verification suite. First, we wrote a golden cycle-accurate simulator in Python that calculates the exact two's-complement arithmetic formulas. Second, we built a self-checking SystemVerilog testbench (`testbench.sv`) with automatic assertions. We simulated 535 randomized input vectors across all five operation templates (T1 through T5) and executed three full DSP benchmark filters—a 16-tap FIR filter, a 6th-order Elliptic filter, and a 2nd-order Volterra filter. Every single output sequence from our Carry-Save FCU matched the conventional FCC bit-for-bit with 100% mathematical equivalence."*

---

#### Q10: What are your key project conclusions in one sentence?
**Examiner's Intent:** To test if the student can summarize the core contribution concisely.  
**High-Scoring Answer:**  
> *"Our project proves that by enforcing pervasive Carry-Save arithmetic throughout the datapath and gating inactive dual-rail registers with latch-based ICG, we achieve a **71.43% reduction in critical path delay**, a **77.10% improvement in Area-Delay Product**, and up to **37.85% energy savings** across real DSP filtering benchmarks compared to conventional flexible accelerators."*

