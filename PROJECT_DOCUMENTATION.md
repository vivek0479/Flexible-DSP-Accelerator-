# Complete Project Documentation: Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating

---

## Document Control & Metadata

| Attribute | Details |
| :--- | :--- |
| **Project Title** | Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating |
| **Domain** | Digital VLSI Design / Computer Arithmetic / Hardware Accelerator Architectures |
| **Academic Program** | Bachelor of Technology (B.Tech) in Electronics and Communication Engineering (ECE) |
| **Academic Year** | 2026 – 2027 |
| **Base Reference Paper** | K. Tsoumanis, S. Xydis, G. Zervakis, and K. Pekmestzi, *"Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic,"* **IEEE Transactions on Very Large Scale Integration (VLSI) Systems**, Vol. 24, No. 1, pp. 368–372, January 2016. |
| **Primary Authors / Team** | A. Vaishnavi, A. Rishikeshwar, B. Vivekananda |
| **Institution** | Department of Electronics and Communication Engineering, CMR Institute of Technology, Hyderabad, Telangana, India |
| **Implementation Deliverables** | Synthesizable Verilog HDL RTL (`rtl/`), EDA Playground Test Suites (`design.sv`, `testbench.sv`), Golden Python Architectural Simulator & Verification Suite (`run_all.py`), Xilinx Vivado Synthesis & Timing/Power Reports (`.rpx`), and Master Presentation Deck. |
| **Verification Status** | **100% Pass** across 535 Python template vectors, 3 DSP kernels (FIR16, Elliptic, Volterra), and 112 Vivado/ModelSim RTL test vectors with **0 functional errors**. |

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [Project Objectives](#4-project-objectives)
5. [Existing System vs Proposed System](#5-existing-system-vs-proposed-system)
6. [System Architecture](#6-system-architecture)
7. [Technology Stack](#7-technology-stack)
8. [System Modules](#8-system-modules)
9. [Detailed Working Methodology](#9-detailed-working-methodology)
10. [Algorithms and Technical Implementation](#10-algorithms-and-technical-implementation)
11. [Hardware Storage & Register Architecture](#11-hardware-storage--register-architecture)
12. [Hardware Port & Interface Specifications](#12-hardware-port--interface-specifications)
13. [User Interface and Simulation Waveforms](#13-user-interface-and-simulation-waveforms)
14. [Installation and Execution Guide](#14-installation-and-execution-guide)
15. [Testing and Validation](#15-testing-and-validation)
16. [Experimental Results and Verification Analysis](#16-experimental-results-and-verification-analysis)
17. [Technical Advantages](#17-technical-advantages)
18. [Real-World Applications](#18-real-world-applications)
19. [Implementation Limitations](#19-implementation-limitations)
20. [Future Enhancements](#20-future-enhancements)
21. [Reliability and Glitch Immunity](#21-reliability-and-glitch-immunity)
22. [Development Challenges Faced and Engineering Solutions](#22-development-challenges-faced-and-engineering-solutions)
23. [Conclusion](#23-conclusion)
24. [References](#24-references)
25. [Project File Structure](#25-project-file-structure)
26. [Comprehensive Viva & Technical Interview Preparation](#26-comprehensive-viva--technical-interview-preparation)

---

## 1. Project Overview

### 1.1 Introduction
In modern embedded computing, Internet-of-Things (IoT) edge processors, mobile graphics, wireless communications (5G/6G), radar signal processing, and biomedical signal conditioning, computational workloads are overwhelmingly dominated by Digital Signal Processing (DSP) algorithms. These algorithms—including Finite Impulse Response (FIR) filtering, Infinite Impulse Response (IIR) filtering, Fast Fourier Transforms (FFT), Discrete Cosine Transforms (DCT), and non-linear polynomial filters (Volterra series)—are characterized by recurring patterns of chained arithmetic operations:

$$W = A \times (X \pm Y) + K$$

These composite operations, termed **Add-Multiply-Accumulate (AMA)** or **Multiply-Accumulate (MAC)** chains, constitute up to 80% of the total execution cycles and dynamic energy expenditure in signal processing processors.

### 1.2 What is this Project?
This project is an advanced, synthesizable, hardware-efficient **Flexible Computational Unit (FCU)** accelerator architecture. It operates pervasively in the **redundant Carry-Save (CS)** arithmetic domain, completely bypassing the conventional need for multi-bit Carry-Propagate Adders (CPA) between cascaded arithmetic stages. To eliminate clock-distribution waste during idle cycles, the architecture integrates a **Dual-Rail Negative-Level Latch-Based Integrated Clock Gating (ICG)** cell that gates both redundant register rails ($W_C$ and $W_S$) concurrently without hazards or skew.

### 1.3 Why Was It Developed?
Traditional reconfigurable DSP engines (such as the Flexible Computational Component - FCC) rely on standard two's-complement binary representations. Consequently, whenever an operation chain combines an addition, a multiplication, and an accumulation, three sequential carry-propagate additions are executed in series. Carry propagation is inherently an $O(N)$ serial process where carry bits ripple horizontally across the entire 16-bit word length ($32\,T_g$ delay per adder). This creates a severe **$140\,T_g$ critical path delay bottleneck**, increases parasitic switching activity, and inflates dynamic power dissipation. This project was developed to break this bottleneck at the arithmetic level.

### 1.4 Target Users & Domain
- **Target Users:** VLSI design engineers, DSP hardware architects, embedded systems developers, and researchers designing energy-constrained edge AI and DSP accelerator SoCs.
- **Project Domain:** Digital VLSI Systems, Computer Arithmetic, Low-Power Digital Design, Synthesizable Verilog HDL, and FPGA/ASIC Implementation.

### 1.5 Real-World Applications
1. **Edge AI & TinyML Audio/Vision:** Matrix-vector multiplications in quantized neural network inference.
2. **5G/6G Baseband Processing:** High-speed channel equalization, match filtering, and Massive-MIMO digital beamforming.
3. **Biomedical Implants:** Wearable ECG/EEG noise-cancellation filters requiring microwatt-level power envelopes.
4. **Autonomous Robotics:** High-rate Kalman filtering, inertial measurement unit (IMU) fusion, and LiDAR point-cloud decimation.

### 1.6 Project Scope
The design encompasses:
- A parameterizable 16-bit FCU datapath supporting 5 operational templates (T1–T5).
- A 16-bit constant-time 4:2 Carry-Save Compressor for pre-addition/subtraction ($4\,T_g$).
- A Direct Carry-Save to Modified Booth (CS-to-MB) Radix-4 Recoder ($8\,T_g$) operating with zero CPAs.
- A structural 3-level 4:2 compressor Wallace/Dadda CSA reduction tree that compresses 8 Booth partial products and fuses an external carry-save addend ($K^*$ or $N^*$) directly into Level 3.
- Dual-rail latch-based Integrated Clock Gating (ICG) for dynamic power preservation.
- Full verification through Python architectural models, automated 535-vector equivalence suites, and 112 synthesizable Verilog test vectors on EDA Playground and Xilinx Vivado.

---

## 2. Problem Statement

### 2.1 The Carry Propagation Dilemma in Conventional Accelerators
In non-redundant two's-complement arithmetic, every number is represented uniquely by a single binary vector:

$$X = -x_{N-1} 2^{N-1} + \sum_{i=0}^{N-2} x_i 2^i$$

When two such numbers are summed, each bit position $i$ produces a sum $s_i = x_i \oplus y_i \oplus c_i$ and a carry bit $c_{i+1} = (x_i y_i) + c_i(x_i \oplus y_i)$. Because $c_{i+1}$ depends strictly on $c_i$, carry information must ripple sequentially from bit 0 to bit $N-1$. Even with accelerated prefix topologies (Kogge-Stone, Brent-Kung), carry propagation incurs substantial silicon area, routing congestion, and dynamic power overhead.

### 2.2 The Conventional FCC Bottleneck
In the conventional Flexible Computational Component (FCC) baseline (Galanis et al., IEEE TCAD 2006):
1. **Stage 1 (Pre-Adder):** Computes $X \pm Y$ using CPA 1 $\rightarrow$ **$32\,T_g$ delay**.
2. **Stage 2 (Multiplier):** Modified Booth encoding ($8\,T_g$), Wallace tree compression ($36\,T_g$), followed immediately by an internal CPA to convert carry-save partial products back into binary $\rightarrow$ **$32\,T_g$ internal CPA delay** (Total Multiplier = **$76\,T_g$**).
3. **Stage 3 (Post-Accumulation):** The binary product is accumulated with external operand $K$ using CPA 2 $\rightarrow$ **$32\,T_g$ delay**.

$$\text{Critical Delay}_{\text{FCC}} = T_{\text{CPA1}} + T_{\text{Mult}} + T_{\text{CPA2}} = 32\,T_g + 76\,T_g + 32\,T_g = \mathbf{140\,T_g} \quad (1.68\,\text{ns at 65 nm})$$

### 2.3 Power and Switching Consequences
Whenever a long carry ripple propagates across 16 bit slices, spurious logic glitches (dynamic hazards) occur before the signals settle. These dynamic hazards propagate through cascading logic levels, consuming charging/discharging energy across parasitic capacitances ($P_{\text{dyn}} = \alpha C_L V_{DD}^2 f$). In high-sample-rate DSP pipelines, intermediate CPAs account for more than 45% of total datapath switching power.

---

## 3. Proposed Solution

The proposed **Flexible Computational Unit (FCU)** resolves the carry-propagation dilemma by maintaining all operands and intermediate results in **redundant Carry-Save (CS) form** throughout the entire computational lifecycle:

$$X^* = \{X_C, X_S\} \implies \text{Value}(X^*) = (X_C + X_S) \bmod 2^{16}$$

```mermaid
flowchart LR
    A["Two's Complement Inputs"] --> B["Boundary Split"]
    B --> C["4:2 Compressor Pre-Adder (4 Tg)"]
    C --> D["Direct CS-to-MB Recoder (8 Tg)"]
    D --> E["CSA Multiplier Tree + Operand Fusion (24 Tg)"]
    E --> F["Dual-Rail Clock-Gated Regs (WC, WS)"]
    F --> G["Boundary CStoBin Converter (CPA)"]
    G --> H["Final Output Result"]
    
    style C fill:#d4edda,stroke:#28a745,stroke-width:2px;
    style D fill:#d4edda,stroke:#28a745,stroke-width:2px;
    style E fill:#d4edda,stroke:#28a745,stroke-width:2px;
    style F fill:#cce5ff,stroke:#004085,stroke-width:2px;
```

### Key Pillars of the Proposed Solution:
1. **Constant-Time Pre-Addition ($4\,T_g$):** Replaces the $32\,T_g$ pre-adder with a 16-bit 4:2 Carry-Save Compressor. Carries do not propagate horizontally; they are passed between adjacent full adders within the slice, guaranteeing a fixed delay of $4\,T_g$ regardless of bit width.
2. **Direct CS-to-Modified Booth (CS-to-MB) Recoding ($8\,T_g$):** Generates 8 Radix-4 Booth digits directly from the dual-rail inputs $\{P_C, P_S\}$ without an intermediate CPA, bounding carry transfers strictly between adjacent 2-bit slices.
3. **Operand Fusion in the Multiplier Reduction Tree ($24\,T_g$):** Eliminates the post-accumulation CPA entirely. The external addend $\{ext\_c, ext\_s\}$ is injected as an additional operand vector directly into Level 3 of the structural Wallace reduction tree.
4. **Dual-Rail Integrated Clock Gating (ICG):** Simultaneously gates clock propagation to both the carry rail register ($W_C$) and sum rail register ($W_S$) via a single glitch-free negative-level latch cell, achieving 5.88% dynamic power savings during idle cycles.
5. **Single Boundary CPA:** Carry-propagate conversion is isolated strictly to the accelerator boundary where data exits to memory or standard binary peripherals.

$$\text{Critical Delay}_{\text{FCU}} = T_{\text{MUX}} + T_{4:2} + T_{\text{CS-MB}} + T_{\text{CSA-Tree}} = 4\,T_g + 4\,T_g + 8\,T_g + 24\,T_g = \mathbf{40\,T_g} \quad (1.13\,\text{ns at 65 nm})$$

---

## 4. Project Objectives

### Primary Objectives
1. **Eliminate Intermediate CPAs:** Design an FCU datapath executing composite DSP operations with zero intermediate carry-propagate conversions.
2. **Minimize Critical Path Delay:** Reduce the critical path from $140\,T_g$ down to $40\,T_g$, realizing a theoretical speedup of **71.43%**.
3. **Design a True Structural 3-Level 4:2 CSA Reduction Tree:** Implement four structural 4:2 compressors in Verilog HDL to compress 8 Booth partial products and fuse dual-rail external operands without behavioral `+` addition chains.
4. **Implement Dual-Rail Integrated Clock Gating (ICG):** Prevent clock glitches and eliminate dynamic register switching during idle clock periods.
5. **Synthesizability & Device Verification:** Validate the hardware on Xilinx 7-Series FPGA hardware using Xilinx Vivado, ensuring 0 combinational loops, 0 latch loops, and complete timing closure.

### Secondary Objectives
1. **Automated Mathematical Equivalence:** Construct an exhaustive Python verification environment comparing the existing FCC and proposed FCU against 535 template test vectors and 3 benchmark DSP kernels (FIR16, Elliptic, Volterra).
2. **FPGA Resource Minimization:** Keep FPGA logic utilization under 400 LUTs on modern Xilinx Artix-7 devices.
3. **Comprehensive Testbench Engineering:** Provide self-checking Verilog testbenches verifying directed positive, signed negative, boundary, clock-gating, and 100+ randomized vectors.

---

## 5. Existing System vs Proposed System

| Dimension | Existing System: Conventional FCC | Proposed System: Carry-Save FCU | Architectural Significance |
| :--- | :--- | :--- | :--- |
| **Number Representation** | Two's-complement binary ($X$) | Redundant Carry-Save ($X^* = \{X_C, X_S\}$) | Eliminates carry propagation delay during cascading. |
| **Pre-Adder Structure** | 16-bit Carry-Propagate Adder (Ripple Carry) | 16-bit 4:2 Carry-Save Compressor | Replaces $O(N)$ ripple delay ($32\,T_g$) with constant $4\,T_g$ delay. |
| **Booth Recoding Method** | Standard Radix-4 Booth (Requires binary input) | Direct Carry-Save to Modified Booth (CS-to-MB) | Recodes dual-rail data directly with local transfer carries ($8\,T_g$). |
| **Multiplier Output Stage** | Internal CPA converts PPs to binary | Preserves Carry and Sum output vectors ($W_C, W_S$) | Avoids $32\,T_g$ intermediate CPA bottleneck. |
| **Post-Accumulation** | Dedicated CPA 2 adder | Direct injection into Level 3 of CSA tree | Fuses post-addition into reduction tree at **zero extra delay**. |
| **Number of CPAs in Chain** | **3 CPAs** (Pre-adder, Multiplier CPA, Post-adder) | **0 Intermediate CPAs** (Single CPA at boundary) | Eliminates $3 \times 32 = 96\,T_g$ of carry-rippling overhead. |
| **Theoretical Delay ($T_g$)** | **$140 \, T_g$** | **$40 \, T_g$** | **71.43% Delay Reduction** |
| **65 nm Clock Period** | **1.68 ns** | **1.13 ns** | **32.74% Clock Period Improvement** |
| **Gate-Equivalent Area ($A_g$)**| **$3274 \, A_g$** | **$2624 \, A_g$** | **19.85% Silicon Area Reduction** |
| **Area-Delay Product (ADP)** | **$458,360 \, A_g \cdot T_g$** | **$104,960 \, A_g \cdot T_g$** | **77.10% Overall Metric Improvement** |
| **Clock Gating Technique** | Single-Rail Latch-Based ICG | Synchronized Dual-Rail Latch-Based ICG | Protects both $W_C$ and $W_S$ registers from skew and hazards. |
| **FIR16 Energy Consumption** | 1038.04 pJ | 711.88 pJ | **31.42% Energy Savings** |
| **Volterra Filter Energy** | 391.30 pJ | 229.92 pJ | **41.24% Energy Savings** |
| **Vivado Synthesis (Artix-7)** | $> 500$ LUTs (estimated with 3 CPAs) | **368 LUTs, 31 FFs, 166 I/O Pins** | Compact footprint with 0 timing loops. |

---

## 6. System Architecture

### 6.1 Top-Level Architecture
The top-level accelerator architecture consists of an interconnected array of FCU datapaths, a dual-rail scratchpad register bank, an interconnection crossbar, a boundary ripple-carry Carry-Save-to-Binary (CStoBin) converter, and an FSM control unit.

```mermaid
flowchart TD
    subgraph DataPort["Data Port & Control"]
        DP["I/O Data Buffer"]
        CU["Control Unit\n(FSM Scheduler, CL0-CL3, clk_gate_en)"]
    end

    subgraph Storage["Dual-Rail Scratchpad Register Bank"]
        RB["Dual-Rail Register Storage\nStores {X_C, X_S}, {Y_C, Y_S}, {K_C, K_S}"]
    end

    subgraph Interconnect["Reconfigurable Interconnection Network"]
        XBAR["Non-blocking Crossbar Routing Matrix"]
    end

    subgraph FCUArray["Flexible Computational Units (FCUs)"]
        FCU1["FCU Datapath 0\n(T1 - T5 Configurable)"]
        FCU2["FCU Datapath 1\n(T1 - T5 Configurable)"]
        FCUN["FCU Datapath N-1\n(T1 - T5 Configurable)"]
    end

    subgraph Boundary["Accelerator Boundary Conversion"]
        CSTOBIN["Boundary CStoBin Converter\n(16-bit Ripple Carry CPA)"]
        BOUT["Final 16-bit Two's Complement Output"]
    end

    DP <--> RB
    CU --> XBAR
    CU --> FCUArray
    RB <--> XBAR
    XBAR --> FCU1
    XBAR --> FCU2
    XBAR --> FCUN
    FCU1 --> XBAR
    FCU2 --> XBAR
    FCUN --> CSTOBIN
    CSTOBIN --> BOUT
```

### 6.2 Detailed FCU Microarchitecture
Within each FCU instance, multiplexers `MUX0` through `MUX3` dynamically steer signals based on configuration bits `CL0` through `CL3`:

```mermaid
flowchart TD
    subgraph FCU_Inputs["FCU Primary Inputs"]
        X["X* = {XC, XS} [15:0]"]
        Y["Y* = {YC, YS} [15:0]"]
        K["K* = {KC, KS} [15:0]"]
        A["A [15:0] (Signed Multiplicand)"]
    end

    subgraph PreCompStage["Pre-Addition / Subtraction"]
        MUX0["MUX0 (CL0)\nSelects Y* or ~Y*"]
        C42["16-bit 4:2 Compressor\ncin1=CL0, cin2=CL0\nDelay = 4 Tg"]
        N["N* = {NC, NS}"]
    end

    subgraph MultiplexerRouting["Dynamic Operand Steering"]
        MUX1["MUX1 (CL1)\nSelects Multiplier P* = N* (0) or K* (1)"]
        MUX2["MUX2 (CL2)\nSelects Addend ext* = K* (0) or N* (1)"]
        MUX3["MUX3 (CL3)\nControls Subtraction of Ext Addend"]
    end

    subgraph MultiplierCore["Carry-Save Multiplier with Tree Fusion"]
        RECODER["Direct CS-to-MB Recoder\n(8 Radix-4 Booth Digits, Delay = 8 Tg)"]
        PPG["Partial Product Generation\n(8 Shifted Rows PP0 - PP7)"]
        
        subgraph CSATree["Structural 3-Level 4:2 CSA Reduction Tree"]
            L1A["4:2 Comp L1_A\n(PP0, PP1, PP2, PP3)"]
            L1B["4:2 Comp L1_B\n(PP4, PP5, PP6, PP7)"]
            L2["4:2 Comp L2\n(Reduces to Pure Mult Product)"]
            L3["4:2 Comp L3 (Fusion)\n(Fuses ext_c, ext_s with ZERO CPA!)"]
        end
    end

    subgraph GatedOutputs["Clock Gated Output Registers"]
        ICG_CELL["Integrated Clock Gating (ICG)\nNegative-Level Latch"]
        REG_WC["WC Output Register [15:0]"]
        REG_WS["WS Output Register [15:0]"]
    end

    subgraph PostBoundary["Output Interface"]
        CPA_BOUND["Boundary CStoBin Adder\n(bin_out = wc + ws)"]
    end

    Y --> MUX0
    X --> C42
    MUX0 --> C42
    C42 --> N
    
    N --> MUX1
    K --> MUX1
    K --> MUX2
    N --> MUX2
    
    MUX1 --> RECODER
    RECODER --> PPG
    A --> PPG
    
    PPG --> L1A
    PPG --> L1B
    L1A --> L2
    L1B --> L2
    
    MUX2 --> MUX3
    L2 --> L3
    MUX3 --> L3
    
    ICG_CELL -.->|Gated Clock| REG_WC
    ICG_CELL -.->|Gated Clock| REG_WS
    L3 --> REG_WC
    L3 --> REG_WS
    
    REG_WC --> CPA_BOUND
    REG_WS --> CPA_BOUND
```

---

## 7. Technology Stack

| Layer / Tool | Technology / Version | Purpose in Project | Implementation Location |
| :--- | :--- | :--- | :--- |
| **Hardware Description** | Verilog-2001 / SystemVerilog | Synthesizable RTL design of the FCU datapath, sub-modules, and top-level architecture. | `rtl/*.v`, `rtl/design.sv` |
| **FPGA Synthesis Tool** | Xilinx Vivado Design Suite 2024.x | RTL synthesis, elaboration, logic optimization, technology mapping, LUT/FF resource utilization analysis. | `fcu_top.v` synthesized on Artix-7 |
| **RTL Simulator 1** | Vivado Simulator (XSim) | Cycle-accurate behavioral simulation, timing verification, and interactive waveform debugging. | `fcu_tb_behav.wcfg` |
| **RTL Simulator 2** | Aldec Riviera-PRO / Icarus Verilog (`iverilog -g2012`) | Fast cloud simulation, VCD waveform dumping, and automated test execution. | EDA Playground online platform |
| **Waveform Viewer** | EPWave (EDA Playground) & Vivado Logic Waveform Viewer | Visual waveform inspection across buses, control signals, and dual-rail carry/sum rails. | `dump.vcd`, `fcu_tb_behav.wcfg` |
| **Architectural Modeling**| Python 3.10+ | Golden high-level reference simulator, algorithmic bit-accurate arithmetic verification, and PPA analysis. | `existing_system/`, `proposed_system/` |
| **Scientific Computing** | NumPy / SciPy | Vectorized calculation of DSP kernel outputs (FIR16, Elliptic, Volterra) for golden comparison. | `benchmarks/` |
| **Data Visualization** | Matplotlib 3.8+ | Generation of 9 publication-grade IEEE vector figures (PDF/PNG) showing schematics, charts, and dataflow. | `generate_all_paper_figures.py` |
| **PDF Processing** | PyPDF 5.x | Automated extraction and technical verification of base paper and audit manuscripts. | Audit parsing scripts |

---

## 8. System Modules

### 8.1 Module: `icg_cell.v` (Integrated Clock Gating Cell)
- **Source File:** `rtl/icg_cell.v`
- **Purpose:** Prevents illegal clock glitches and dynamic power consumption in output registers during idle execution states.
- **Circuit Schematic:**
  ```
  clk_gate_en ──► [ D   Latch ] ── Q (latch_en) ──┐
                    [ G_N       ]                 ├──► [ AND Gate ] ──► gated_clk
  clk ────────────► [ (Active L) ] ────────────────┘
  ```
- **Inputs:** `clk` (System clock), `clk_gate_en` (Active-high enable).
- **Outputs:** `gated_clk` (Cleanly gated clock signal).
- **Working Mechanism:** Operates via a negative-level sensitive D-latch. When `clk = 0`, the latch is transparent and captures `clk_gate_en`. When `clk = 1`, the latch enters hold mode, locking `latch_en`. The downstream AND gate combines `clk` and `latch_en`. Any transition on `clk_gate_en` while `clk` is high is blocked, guaranteeing that no truncated "runt" pulses appear on `gated_clk`.

### 8.2 Module: `compressor_4_2.v` (16-bit 4:2 Carry-Save Compressor)
- **Source File:** `rtl/compressor_4_2.v`
- **Purpose:** Fuses two carry-save operands ($X^* \pm Y^*$) into a single carry-save operand ($N^* = \{N_C, N_S\}$) prior to multiplication in constant $4\,T_g$ delay.
- **Inputs:** `xc[15:0]`, `xs[15:0]`, `yc[15:0]`, `ys[15:0]`, `cin1` (Horizontal carry-in), `cin2` (Carry-in to bit 0 of carry output).
- **Outputs:** `nc[15:0]`, `ns[15:0]`, `cout` (Horizontal carry-out).
- **Logic Equations per Bit Slice $i$:**
  $$\begin{aligned}
  sum_{1,i} &= xs_i \oplus ys_i \oplus yc_i \\
  cout_{1,i} &= (xs_i \cdot ys_i) + (ys_i \cdot yc_i) + (xs_i \cdot yc_i) \\
  final\_s_i &= sum_{1,i} \oplus xc_i \oplus c_{\text{horiz},i} \\
  final\_c_i &= (sum_{1,i} \cdot xc_i) + (c_{\text{horiz},i} \cdot (sum_{1,i} \oplus xc_i)) \\
  c_{\text{horiz},i+1} &= cout_{1,i}
  \end{aligned}$$
- **Vector Output Alignment:**
  $$ns = final\_s, \quad nc = \{final\_c[14:0], cin_2\}$$

### 8.3 Module: `cs_to_mb_recoder.v` (Direct CS-to-MB Recoder)
- **Source File:** `rtl/cs_to_mb_recoder.v`
- **Purpose:** Directly translates 16-bit redundant carry-save inputs $\{P_C, P_S\}$ into 8 Radix-4 Modified Booth digits without an intermediate CPA.
- **Inputs:** `pc[15:0]`, `ps[15:0]`.
- **Outputs:** 8-bit one-hot control vectors: `digit_one[7:0]`, `digit_two[7:0]`, `digit_neg[7:0]`, `digit_zero[7:0]`.
- **Working Mechanism:** For each digit index $i \in [0, 7]$, the recoder samples bit positions $2i$ and $2i+1$ from sign-extended inputs:
  $$val_i = 2 \times (pc_{2i+1} + ps_{2i+1}) + (pc_{2i} + ps_{2i}) + c_{\text{transfer},i}$$
  Transfer carry $c_{\text{transfer},i} \in \{0, 1, 2\}$ propagates strictly to stage $i+1$, eliminating word-length carry propagation ($8\,T_g$ constant delay).

### 8.4 Module: `csa_tree_multiplier.v` (Structural 3-Level Wallace CSA Multiplier)
- **Source File:** `rtl/csa_tree_multiplier.v`
- **Purpose:** Multiplies 16-bit signed multiplicand $A$ by recoded Booth digits, and fuses the external carry-save addend directly into Level 3 of the CSA reduction tree.
- **Inputs:** `a_in[15:0]`, `pc[15:0]`, `ps[15:0]`, `ext_c[15:0]`, `ext_s[15:0]`, `has_ext`, `sub_ext`.
- **Outputs:** `wc[15:0]`, `ws[15:0]` (Authentic redundant Carry-Save outputs).
- **Internal Structural Hierarchy:**
  - `u_recoder`: Instantiates `cs_to_mb_recoder`.
  - `gen_pp`: Function generating 8 partial products ($PP_0 \dots PP_7$) shifted by $2i$ bits modulo $2^{16}$.
  - `u_comp_tree_l1_a`: Compresses $PP_0, PP_1, PP_2, PP_3 \rightarrow \{l1\_c\_a, l1\_s\_a\}$.
  - `u_comp_tree_l1_b`: Compresses $PP_4, PP_5, PP_6, PP_7 \rightarrow \{l1\_c\_b, l1\_s\_b\}$.
  - `u_comp_tree_l2`: Compresses $\{l1\_c\_a, l1\_s\_a, l1\_c\_b, l1\_s\_b\} \rightarrow \{l2\_c, l2\_s\}$ (pure multiplication result).
  - `u_comp_tree_l3_fusion`: Compresses $\{l2\_c, l2\_s, ext\_c\_mux, ext\_s\_mux\} \rightarrow \{wc, ws\}$ with **zero intermediate CPA delay**!

### 8.5 Module: `cs_to_bin.v` (Boundary CPA Converter)
- **Source File:** `rtl/cs_to_bin.v`
- **Purpose:** Converts the final redundant carry-save pair $\{W_C, W_S\}$ into a two's-complement binary word.
- **Inputs:** `wc[15:0]`, `ws[15:0]`.
- **Outputs:** `bin_out[15:0] = $signed(wc + ws)`.
- **Placement:** Positioned strictly at the output boundary of the accelerator.

### 8.6 Module: `fcu_top.v` (Top-Level Datapath)
- **Source File:** `rtl/fcu_top.v`
- **Purpose:** Connects all arithmetic sub-modules, control multiplexers, and clock-gating registers to support dynamic template execution (T1–T5).

---

## 9. Detailed Working Methodology

### 9.1 Step-by-Step Data Processing Pipeline
1. **Reset Phase:** When `rst_n = 0`, output registers `wc_out` and `ws_out` are synchronously cleared to `0x0000`.
2. **Template Decode:** The 3-bit `template_sel` is decoded into control bits `CL0` through `CL3` and `has_ext`.
3. **Pre-Addition / Subtraction:** If executing templates T1, T2, T3, or T4, inputs $X^*$ and $Y^*$ are compressed by `u_comp42` in $4\,T_g$ to produce $N^*$.
4. **Multiplier Operand Steering:** Multiplexer `MUX1` routes $N^*$ (for T1, T2) or $K^*$ (for T3, T4, T5) to the multiplier.
5. **CS-to-MB Recoding:** `u_recoder` converts the selected CS multiplier into 8 signed Radix-4 Booth digits in $8\,T_g$.
6. **Partial Product Generation:** Eight partial product vectors ($PP_0 \dots PP_7$) are computed in parallel.
7. **Tree Reduction & Operand Fusion:**
   - Level 1 reduces 8 PPs to 4 vectors.
   - Level 2 reduces 4 vectors to 2 vectors (pure multiplication product).
   - Level 3 fuses external addend $\{ext\_c, ext\_s\}$ directly into the tree without CPA.
8. **Clock-Gated Register Capture:** On the rising edge of `gated_clk`, the redundant outputs are captured into registers `wc_out` and `ws_out`.
9. **Boundary Conversion:** `u_csto_bin` computes the binary result `bin_out = wc_out + ws_out`.

```mermaid
sequenceDiagram
    autonumber
    participant TB as Testbench / Controller
    participant FCU as Top-Level FCU
    participant C42 as 4:2 Pre-Compressor
    participant REC as CS-to-MB Recoder
    participant TREE as 3-Level CSA Tree
    participant REG as Clock-Gated Regs
    participant CPA as Boundary CStoBin

    TB->>FCU: Apply template_sel, a_in, X*, Y*, K*, clk_gate_en=1
    FCU->>C42: Compute N* = X* ± Y* (Constant 4 Tg)
    C42-->>FCU: Return N* = {NC, NS}
    FCU->>REC: Route P* to Recoder
    REC-->>TREE: 8 Radix-4 Digits (d0 - d7)
    FCU->>TREE: Multiplicand A + External Addend (ext_c, ext_s)
    TREE->>TREE: Level 1 (8 -> 4 PPs)
    TREE->>TREE: Level 2 (4 -> 2 Vectors)
    TREE->>TREE: Level 3 (Fuse ext_c, ext_s without CPA!)
    TREE-->>REG: Present mult_wc, mult_ws
    Note over REG: At posedge gated_clk:
    REG->>CPA: wc_out, ws_out
    CPA-->>TB: bin_out = wc_out + ws_out
```

---

## 10. Algorithms and Technical Implementation

### 10.1 Radix-4 Modified Booth Recoding
Modified Booth recoding reduces the number of partial products by half (from $N$ to $N/2$). For 16-bit operands, exactly 8 partial products are generated.

Each digit $d_i \in \{-2, -1, 0, +1, +2\}$ corresponds to an operation on multiplicand $A$:
- $d_i = 0 \implies PP_i = 0$
- $d_i = +1 \implies PP_i = A \ll 2i$
- $d_i = +2 \implies PP_i = (A \ll 1) \ll 2i$
- $d_i = -1 \implies PP_i = (-A) \ll 2i$
- $d_i = -2 \implies PP_i = (-(A \ll 1)) \ll 2i$

### 10.2 Modulo-$2^{16}$ Two's-Complement Arithmetic
The accelerator implements **16-bit two's-complement modulo-$2^{16}$ fixed-point arithmetic**:
- Input range for multiplicand $A$: $[-32768, +32767]$.
- Redundant inputs: $X_C + X_S \equiv X \pmod{2^{16}}$.
- Any higher-order bits beyond bit 15 naturally wrap around according to standard integer modular arithmetic:

$$\text{Result} = (A \times P^* + ext^*) \bmod 2^{16}$$

This ensures full consistency across chained DSP operations, matching standard 16-bit DSP architectures.

### 10.3 Structural Wallace Reduction Tree
In conventional RTL, students often write:
```verilog
// Behavioral addition chain (AVOIDED - flags carry propagation):
wire signed [31:0] total = pp0 + pp1 + pp2 + pp3 + pp4 + pp5 + pp6 + pp7 + ext;
```
This causes synthesizers to construct an 8-adder carry ripple chain! 

In our structural implementation, four `compressor_4_2` instances are explicitly wired:
```verilog
// Genuine Structural CSA Tree Implementation:
compressor_4_2 u_comp_tree_l1_a (.xc(pp0), .xs(pp1), .yc(pp2), .ys(pp3), .nc(l1_c_a), .ns(l1_s_a));
compressor_4_2 u_comp_tree_l1_b (.xc(pp4), .xs(pp5), .yc(pp6), .ys(pp7), .nc(l1_c_b), .ns(l1_s_b));
compressor_4_2 u_comp_tree_l2   (.xc(l1_c_a), .xs(l1_s_a), .yc(l1_c_b), .ys(l1_s_b), .nc(l2_c), .ns(l2_s));
compressor_4_2 u_comp_tree_l3_fusion (.xc(l2_c), .xs(l2_s), .yc(ext_c_mux), .ys(ext_s_mux), .nc(wc), .ns(ws));
```
This guarantees an authentic $O(\log N)$ compressor tree with no behavioral shortcuts.

---

## 11. Hardware Storage & Register Architecture

In digital VLSI accelerators, data storage is implemented via on-chip **Dual-Rail Register Banks**:
- **Dual-Rail Representation:** Each 16-bit virtual variable occupies 32 physical flip-flop bits (16 bits for Carry rail, 16 bits for Sum rail).
- **Output Holding Registers:**
  - `wc_out[15:0]`: Holds the 16-bit carry vector.
  - `ws_out[15:0]`: Holds the 16-bit sum vector.
- **Clock Control:** Both registers are driven strictly by `gated_clk` from the negative-level latch ICG cell.

---

## 12. Hardware Port & Interface Specifications

### Module: `fcu_top` Port List

| Pin Name | Direction | Width | Type | Functional Description |
| :--- | :---: | :---: | :---: | :--- |
| `clk` | Input | 1 | Wire | Master system clock (100 MHz, 10 ns period). |
| `rst_n` | Input | 1 | Wire | Active-low asynchronous master reset. |
| `clk_gate_en` | Input | 1 | Wire | Integrated Clock Gating active-high enable. |
| `template_sel`| Input | 3 | Wire | Template opcode: `3'd1` (T1) to `3'd5` (T5). |
| `a_in` | Input | 16 | Signed Wire | 16-bit two's-complement multiplicand $A$. |
| `xc_in` | Input | 16 | Wire | Carry vector of operand $X^*$. |
| `xs_in` | Input | 16 | Wire | Sum vector of operand $X^*$. |
| `yc_in` | Input | 16 | Wire | Carry vector of operand $Y^*$. |
| `ys_in` | Input | 16 | Wire | Sum vector of operand $Y^*$. |
| `kc_in` | Input | 16 | Wire | Carry vector of operand $K^*$. |
| `ks_in` | Input | 16 | Wire | Sum vector of operand $K^*$. |
| `wc_out` | Output| 16 | Reg | Dual-rail output Carry vector. |
| `ws_out` | Output| 16 | Reg | Dual-rail output Sum vector. |
| `bin_out` | Output| 16 | Signed Wire | Final binary result from boundary CPA ($W_C + W_S$). |

---

## 13. User Interface and Simulation Waveforms

### 13.1 Vivado XSim Waveform Analysis
The simulation was verified in **Xilinx Vivado (XSim)** under waveform configuration `fcu_tb_behav.wcfg`:

```text
Time (ns):       20ns        40ns        60ns        80ns        100ns       120ns       140ns
                  |           |           |           |           |           |           |
clk          _/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_/~~\_
clk_gate_en  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\___________/~~~~~~~~~~~~~~
template_sel X   1 (T1)   X   2 (T2)   X   3 (T3)   X   4 (T4)   X   5 (T5)   X  Gated (Held)
a_in         X     25     X     15     X     30     X     20     X     45     X      999     
wc_out (Hex) X   0x0004   X   0x4100   X   0x10A0   X   0x0214   X   0x0000   X (Holds 0x0000)
ws_out (Hex) X   0x0EAC   X   0xC60D   X   0xF12C   X   0xFEF0   X   0x02D0   X (Holds 0x02D0)
bin_out(Dec) X    3760    X    1805    X    460     X    260     X    720     X (Holds 720)   
errors[31:0] X                        00000000 (ZERO ERRORS!)
                  ▲                       ▲                       ▲                 ▲
               T1 Pass                 T3 Pass                 T5 Pass        Clock Gated
```

### 13.2 EPWave Waveform Viewer (EDA Playground)
- **Radix Settings:**
  - `bin_out[15:0]` set to **Signed Decimal**.
  - `a_in[15:0]` set to **Signed Decimal**.
  - `template_sel[2:0]` set to **Unsigned Decimal**.
  - `wc_out[15:0]` and `ws_out[15:0]` set to **Hexadecimal**.
- **Zoom Window:** Set time range `0ps` to `140000ps` (0–140 ns) for clear template transition viewing.

---

## 14. Installation and Execution Guide

### 14.1 Running the Python Architectural Verification Suite
From PowerShell or Command Prompt:

```powershell
# Navigate to the project root directory:
cd "c:\Users\LENOVO\OneDrive\Documents\majar_project\1.Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic"

# Run master verification suite:
python run_all.py
```

### 14.2 Running RTL on EDA Playground
1. Open [EDA Playground](https://www.edaplayground.com).
2. Set **Language:** `SystemVerilog/Verilog`.
3. Set **Simulator:** `Aldec Riviera Pro` or `Icarus Verilog 0.10.0`.
4. Check **Open EPWave after run**.
5. Copy contents of `rtl/design.sv` into the left editor pane.
6. Copy contents of `rtl/testbench.sv` into the right editor pane.
7. Click **Run**.

### 14.3 Running RTL on Xilinx Vivado
1. Open Vivado and create an **RTL Project** named `fcu_dsp_accelerator`.
2. Target part: Any Xilinx 7-Series FPGA (e.g., `xc7a200tfbg676-2` or `xc7a35tcpg236-1`).
3. Add **Design Sources:**
   - `rtl/fcu_top.v`
   - `rtl/csa_tree_multiplier.v`
   - `rtl/compressor_4_2.v`
   - `rtl/cs_to_mb_recoder.v`
   - `rtl/cs_to_bin.v`
   - `rtl/icg_cell.v`
4. Add **Simulation Source:** `rtl/fcu_tb.v`.
5. Under **Simulation**, click **Run Simulation** $\rightarrow$ **Run Behavioral Simulation**.
6. Under **RTL Analysis**, click **Open Elaborated Design** $\rightarrow$ **Schematic** to view the hardware gates.
7. Click **Run Synthesis** $\rightarrow$ Open Synthesized Design $\rightarrow$ **Report Utilization**.

---

## 15. Testing and Validation

### 15.1 Verification Test Suite Summary

| Section | Test Type | Test Vectors | Description & Mathematical Formula | Expected Result | Actual Result | Status |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: |
| **Sec 1** | Directed Positive | Vector 1 (T1) | $25 \times (100 + 50) + 10$ | `3760` | `3760` (`wc=0x0004, ws=0x0eac`) | **PASS** |
| | | Vector 2 (T2) | $15 \times (150 - 30) + 5$ | `1805` | `1805` (`wc=0x4100, ws=0xc60d`) | **PASS** |
| | | Vector 3 (T3) | $30 \times 12 + (60 + 40)$ | `460` | `460` (`wc=0x10a0, ws=0xf12c`) | **PASS** |
| | | Vector 4 (T4) | $20 \times 10 + (100 - 40)$ | `260` | `260` (`wc=0x0214, ws=0xfef0`) | **PASS** |
| | | Vector 5 (T5) | $45 \times 16$ | `720` | `720` (`wc=0x0000, ws=0x02d0`) | **PASS** |
| **Sec 2** | Signed & Negative | Vector 6 (T1) | $-25 \times 50 + 50$ (Negative Multiplicand) | `-1200` | `-1200` (`wc=0x0024, ws=0xfb2c`) | **PASS** |
| | | Vector 7 (T2) | $10 \times (20 - 50) + 100$ (Negative Diff) | `-200` | `-200` (`wc=0x0088, ws=0xfeb0`) | **PASS** |
| | | Vector 8 (T5) | $30 \times (-15)$ (Negative Multiplier) | `-450` | `-450` (`wc=0x0000, ws=0xfe3e`) | **PASS** |
| **Sec 3** | Boundary Cases | Vector 9 (T1) | $0 \times X + 77$ (Zero Multiplicand) | `77` | `77` (`wc=0x0000, ws=0x004d`) | **PASS** |
| | | Vector 10 (T5)| $1234 \times 0$ (Zero Multiplier) | `0` | `0` (`wc=0x0000, ws=0x0000`) | **PASS** |
| **Sec 4** | Clock Gating | Vector 11 | `clk_gate_en = 0` over 4 clock cycles | Holds previous state | `wc` & `ws` held frozen at 0 | **PASS** |
| | | Vector 12 | `clk_gate_en = 1` resume cycle ($12 \times 10$) | `120` | `120` (`wc=0x0000, ws=0x0078`) | **PASS** |
| **Sec 5** | Randomized Tests | Vectors 13–112| 100 random signed trials across T1–T5 | Auto-Assertion | 100/100 matches | **PASS** |
| **Total**| **All Suites** | **112 Vectors**| **Comprehensive Synthesizable RTL Test**| **Zero Errors** | **Zero Errors (`errors=0`)** | **100% PASS**|

---

## 16. Experimental Results and Verification Analysis

### 16.1 Hardware Complexity & Delay Comparison (Theoretical & 65 nm)

| Evaluation Metric | Baseline FCC [Galanis 2006] | Proposed FCU [Tsoumanis 2016 + ICG] | Relative Improvement |
| :--- | :---: | :---: | :---: |
| **Intermediate CPAs** | 3 | **0** | **100% Elimination** |
| **Critical Delay ($T_g$)** | $140 \, T_g$ | **$40 \, T_g$** | **71.43% Reduction** |
| **Clock Period @ 65 nm** | 1.68 ns | **1.13 ns** | **32.74% Improvement** |
| **Gate-Equivalent Area ($A_g$)** | $3274 \, A_g$ | **$2624 \, A_g$** | **19.85% Area Reduction** |
| **Area-Delay Product (ADP)** | $458,360 \, A_g \cdot T_g$ | **$104,960 \, A_g \cdot T_g$** | **77.10% ADP Improvement** |

### 16.2 Real-World DSP Benchmark Energy Results (65 nm CMOS)

| Benchmark Kernel | Algorithm Type | Execution Cycles | Baseline FCC Energy | Proposed FCU Energy | Energy Savings (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **FIR16** | 16-tap Symmetric Filter | 272 | 1038.04 pJ | **711.88 pJ** | **31.42%** |
| **ELLIPTIC** | 6th-Order Wave Filter | 64 | 261.04 pJ | **160.36 pJ** | **38.57%** |
| **VOLTERRA** | 2nd-Order Polynomial Filter | 96 | 391.30 pJ | **229.92 pJ** | **41.24%** |
| **Arithmetic Mean**| — | — | — | — | **37.08% Energy Reduction** |

### 16.3 Vivado FPGA Synthesis Resource Utilization (Artix-7 `xc7a200tfbg676-2`)
Synthesized directly from `fcu_top.v`:
- **Lookup Tables (LUTs):** **368** out of 134,600 (**0.27%**).
- **Flip-Flops (FFs):** **31** out of 269,200 (**0.01%**).
- **I/O Pin Count:** **166** out of 400 (**41.50%**).
- **Combinational Loops:** **0** (Verified by Vivado Design Rules Check).
- **Latch Loops:** **0** (Verified by Vivado Timing Engine).

---

## 17. Technical Advantages

1. **Ultra-Fast Operation Chaining:** Constant-delay 4:2 compressor ($4\,T_g$) and CS-to-MB recoder ($8\,T_g$) decouple critical timing from word length.
2. **True Carry-Free Operand Fusion:** Accumulation addends enter the multiplier tree directly, avoiding dedicated accumulator adder circuits.
3. **Glitch-Free Power Suppression:** Negative-latch ICG isolates output registers during idle intervals without runt pulses.
4. **Negligible FPGA Overhead:** Requires only 368 LUTs, making it suitable for multi-core accelerator arrays.

---

## 18. Real-World Applications

1. **Telecommunication Base Stations:** Channel estimation and FFT butterflies in 5G NR OFDM demodulation.
2. **Automotive Radar:** High-throughput 2D-FFT processing for Doppler velocity mapping.
3. **Consumer Audio DSP:** Ultra-low-power graphic equalizers and acoustic echo cancellation.
4. **Hearing Aids & Medical Wearables:** Battery-powered digital filtering operating at low milliwatt budgets.

---

## 19. Implementation Limitations

1. **Wiring Overhead:** Carry-save representation doubles the interconnect wire count between storage registers and computational units.
2. **Modulo-$2^{16}$ Wrap-around:** Multiplication results are maintained modulo $2^{16}$ without saturation clipping; applications requiring full 32-bit products must widen the tree.
3. **Boundary Conversion Overhead:** A standard CPA is still mandatory at the final accelerator exit port to convert carry-save data to binary.

---

## 20. Future Enhancements

1. **Saturation & Overflow Detection:** Incorporating carry-save overflow prediction logic.
2. **Configurable Word Lengths (8/16/32-bit SIMD):** Sub-word parallelism for deep learning inference.
3. **ASIC Standard-Cell Physical Layout:** Tape-out ready GDSII generation using commercial 28 nm / 16 nm FinFET process design kits.

---

## 21. Reliability and Glitch Immunity

- **Hazard Elimination:** By removing carry ripple propagation, internal dynamic hazards are reduced by over 60%.
- **Clock Tree Integrity:** Negative-level latch gating eliminates hazards caused by asynchronous enable transitions during high clock phases.
- **Race Condition Prevention:** Verified zero combinational loops and zero latch loops across all multiplexer paths.

---

## 22. Development Challenges Faced and Engineering Solutions

### Challenge 1: The Behavioral Adder Shortcut (The "Twin Split" Flaw)
* **Problem:** An early draft used behavioral additions `pp0 + pp1 + ...` and split the output using integer division `wc = total >> 1; ws = total - wc;`. This generated twin outputs (`0x0758, 0x0758`) that external examiners would immediately reject as non-hardware behavior.
* **Solution:** Re-engineered `csa_tree_multiplier.v` with a structural 3-level 4:2 compressor tree (`u_comp_tree_l1_a`, `u_comp_tree_l1_b`, `u_comp_tree_l2`, `u_comp_tree_l3_fusion`). Outputs are now genuine hardware compressor signals (`wc = 0x0004, ws = 0x0eac`).

### Challenge 2: Dual-Rail Subtraction Inversion Offset
* **Problem:** Negating a carry-save number $\sim(Y_C + Y_S)$ results in $-(Y_C + Y_S) - 2$.
* **Solution:** Configured the 4:2 compressor to accept dual carry-in inputs: $cin_1 = 1$ to the horizontal carry chain and $cin_2 = 1$ into bit 0 of the carry output vector, providing the exact $+2$ correction.

---

## 23. Conclusion

This project successfully designed, implemented, and verified an **Energy-Efficient Flexible DSP Accelerator Architecture Utilizing Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating**. By eliminating all intermediate carry-propagate adders, the architecture reduces the critical path delay by **71.43%** ($140\,T_g \rightarrow 40\,T_g$), shrinks gate-equivalent area by **19.85%**, and improves the area-delay product by **77.10%**. Dual-rail ICG contributes an additional **5.88%** dynamic power reduction. With 100% equivalence demonstrated across 535 template vectors, 3 DSP kernels, and 112 Vivado RTL test vectors utilizing only 368 LUTs, the project delivers a publication-grade, hardware-verified arithmetic accelerator for next-generation low-power DSP systems.

---

## 24. References

1. **K. Tsoumanis, S. Xydis, G. Zervakis, and K. Pekmestzi**, *"Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic,"* **IEEE Transactions on Very Large Scale Integration (VLSI) Systems**, Vol. 24, No. 1, pp. 368–372, Jan. 2016.
2. **M. D. Galanis, G. Theodoridis, S. Tragoudas, and C. E. Goutis**, *"A high-performance data path for synthesizing DSP kernels,"* **IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems**, Vol. 25, No. 6, pp. 1154–1162, Jun. 2006.
3. **S. Xydis, G. Economakos, D. Soudris, and K. Pekmestzi**, *"High performance and area efficient flexible DSP datapath synthesis,"* **IEEE Transactions on VLSI Systems**, Vol. 19, No. 3, pp. 429–442, Mar. 2011.
4. **K. Tsoumanis, S. Xydis, C. Efstathiou, N. Moschopoulos, and K. Pekmestzi**, *"An optimized modified Booth recoder for efficient design of the add-multiply operator,"* **IEEE Transactions on Circuits and Systems I: Regular Papers**, Vol. 61, No. 4, pp. 1133–1143, Apr. 2014.
5. **N. H. E. Weste and D. M. Harris**, *CMOS VLSI Design: A Circuits and Systems Perspective*, 4th ed., Addison-Wesley, 2010.

---

## 25. Project File Structure

```
1.Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic/
├── 1.Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic.pdf # IEEE base paper
├── PROJECT_DOCUMENTATION.md            # Comprehensive Master Documentation (This Document)
├── README.md                           # Quick-Start Summary
├── run_all.py                          # Master verification suite runner
├── generate_rtl.py                     # Synthesizable RTL generator script
├── generate_all_paper_figures.py       # Publication figure generation script
│
├── rtl/                                # Synthesizable Verilog & Testbench Files
│   ├── icg_cell.v                      # Latch-based Integrated Clock Gating cell
│   ├── compressor_4_2.v                # 16-bit 4:2 Carry-Save Compressor
│   ├── cs_to_mb_recoder.v              # Direct CS-to-MB Radix-4 recoder
│   ├── csa_tree_multiplier.v           # 3-level structural 4:2 CSA Wallace reduction tree
│   ├── cs_to_bin.v                     # Boundary ripple-carry CPA converter
│   ├── fcu_top.v                       # Top-Level FCU Datapath (Templates T1 - T5)
│   ├── fcu_tb.v                        # 112-vector self-checking testbench (Vivado)
│   ├── design.sv                       # All-in-one RTL file for EDA Playground
│   └── testbench.sv                    # All-in-one testbench for EDA Playground
│
├── existing_system/                    # Conventional Two's-Complement Baseline (FCC)
│   ├── clock_gating.py                 # Single-rail ICG simulation
│   ├── arithmetic_units.py             # 16-bit CPA and Radix-4 Booth Multiplier
│   ├── fcc_datapath.py                 # FCC Datapath model
│   └── dsp_kernels.py                  # FIR16, Elliptic, Volterra mappings
│
├── proposed_system/                    # Proposed Carry-Save FCU Datapath
│   ├── clock_gating.py                 # Dual-rail ICG simulation
│   ├── cs_arithmetic.py                # CarrySaveNumber class & compressor logic
│   ├── cs_to_mb_recoder.py             # Direct CS-to-MB recoder model
│   ├── csa_tree_multiplier.py          # Structural 4:2 reduction tree model
│   └── fcu_datapath.py                 # FCU Datapath model
│
└── figures/                            # 10 High-Resolution Vector Figures (PNG & PDF)
    ├── fig1_top_level_architecture.png
    ├── fig2_fcu_microarchitecture.png
    ├── fig3_chaining_comparison.png
    ├── fig4_templates_dataflow.png
    ├── fig5_clock_gating_schematic.png
    └── fig6_rtl_simulation_waveform.png
```

---

## 26. Comprehensive Viva & Technical Interview Preparation

### 26.1 20 Basic Project Questions & Answers

1. **What is the title of your project?**  
   *Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating.*
2. **What is the base reference paper for this work?**  
   *IEEE TVLSI 2016 paper by Kostas Tsoumanis, Sotirios Xydis, Georgios Zervakis, and Kiamal Pekmestzi.*
3. **What is an FCU?**  
   *Flexible Computational Unit—a reconfigurable arithmetic engine executing fused DSP templates.*
4. **What is Carry-Save representation?**  
   *Representing a number as two redundant bit-vectors (Carry and Sum) such that $\text{Value} = C + S$.*
5. **Why use Carry-Save arithmetic?**  
   *It eliminates the horizontal propagation of carries, enabling constant-time additions independent of word length.*
6. **What is a 4:2 compressor?**  
   *An arithmetic block compressing four inputs of equal weight down to two outputs (carry and sum) with fixed delay.*
7. **What is the critical path delay of your FCU?**  
   *$40\,T_g$ (equivalent to 1.13 ns at 65 nm).*
8. **What was the critical path delay of the conventional FCC?**  
   *$140\,T_g$ (1.68 ns at 65 nm).*
9. **What percentage reduction in critical path delay did you achieve?**  
   *71.43% reduction.*
10. **How many operational templates does the FCU support?**  
    *Five templates: T1, T2, T3, T4, and T5.*
11. **What formula does Template T1 implement?**  
    *$W^* = A \times (X^* + Y^*) + K^*$.*
12. **What formula does Template T2 implement?**  
    *$W^* = A \times (X^* - Y^*) + K^*$.*
13. **What formula does Template T5 implement?**  
    *$W^* = A \times K^*$.*
14. **What is Integrated Clock Gating (ICG)?**  
    *Disabling the clock distribution network to idle registers to save dynamic power.*
15. **Why is dual-rail ICG necessary here?**  
    *Because each carry-save operand occupies two register rails ($W_C$ and $W_S$); both must be gated simultaneously.*
16. **What FPGA resources does your design consume on Xilinx Artix-7?**  
    *368 LUTs, 31 Flip-Flops, and 166 I/O pins.*
17. **How many test vectors did your testbench execute?**  
    *112 test vectors with 0 assertion errors.*
18. **What does the boundary CStoBin module do?**  
    *It converts the redundant $\{W_C, W_S\}$ vectors into a two's-complement binary number using a CPA.*
19. **What is the Unit Gate Model?**  
    *A technology-independent delay model where an inverter delay is $1\,T_g$ and area is $1\,A_g$.*
20. **What are the real-world applications of your project?**  
    *Edge AI processors, 5G baseband filters, biomedical signal processing, and automotive radar.*

### 26.2 20 Advanced Technical Questions & Answers

21. **Why does conventional Booth recoding require a binary input?**  
    *Standard Booth groups 3 contiguous bits ($x_{2i+1}, x_{2i}, x_{2i-1}$). Redundant CS data has two bits per position, so standard recoding cannot group them without prior addition.*
22. **How does the Direct CS-to-MB recoder work without a CPA?**  
    *It sums 2 bits from $P_C$ and 2 bits from $P_S$ plus an incoming transfer carry, bounding carry propagation strictly between adjacent digit stages ($8\,T_g$ delay).*
23. **What is the maximum value of $val_i$ in the CS-to-MB recoder?**  
    *8. ($2 \times (1 + 1) + (1 + 1) + 2 = 8$).*
24. **How is subtraction handled in carry-save form ($X^* - Y^*$)?**  
    *By inverting both rails ($\sim Y_C, \sim Y_S$) and adding $+2$ through compressor inputs $cin_1 = 1$ and $cin_2 = 1$.*
25. **How does operand fusion work in the CSA tree?**  
    *The external addend $\{ext\_c, ext\_s\}$ is injected as an additional vector into Level 3 of the 4:2 compressor tree.*
26. **Why is there no CPA inside the multiplier?**  
    *Because the outputs remain in carry-save format ($W_C, W_S$) for direct reuse in subsequent FCUs.*
27. **What is the structure of the CSA reduction tree?**  
    *A 3-level tree: Level 1 (two 4:2 compressors), Level 2 (one 4:2 compressor), Level 3 (one 4:2 compressor for operand fusion).*
28. **Why does Vivado report 0 combinational loops?**  
    *Because the 4:2 compressors and MUX networks are purely feed-forward.*
29. **Why does Vivado report 0 latch loops?**  
    *Because the negative-level latch in the ICG cell is purely open-loop and gated by the clock.*
30. **What is the function of the negative-level latch in the ICG cell?**  
    *It captures the enable signal while `clk = 0`, ensuring that enable transitions when `clk = 1` do not produce glitches.*
31. **What is the Area-Delay Product (ADP) improvement?**  
    *77.10% improvement ($458,360 \rightarrow 104,960 \, A_g \cdot T_g$).*
32. **Why does FCU instantaneous dynamic power exceed FCC instantaneous power?**  
    *Because FCU clocks twice as many register bits and maintains wider dual-rail datapath wiring.*
33. **If FCU instantaneous power is higher, why is kernel energy lower?**  
    *Because FCU executes operations in fewer clock cycles and eliminates the energy wasted in CPAs ($E = P \times t$).*
34. **What was the energy saving on the 16-tap FIR filter?**  
    *31.42% reduction (1038.04 pJ down to 711.88 pJ).*
35. **What was the energy saving on the Volterra filter?**  
    *41.24% reduction (391.30 pJ down to 229.92 pJ).*
36. **What is the delay of a single Full Adder in the unit gate model?**  
    *$4\,T_g$ critical delay (area is $7\,A_g$).*
37. **Why does a 4:2 compressor have a delay of $4\,T_g$ rather than $8\,T_g$?**  
    *Because the internal horizontal carry $cout_1$ is generated by FA1 and fed to FA2 of the next bit, keeping the path length to 2 XOR gates.*
38. **What word-length wrap-around convention is used?**  
    *Two's-complement modulo-$2^{16}$ wrap-around arithmetic.*
39. **Why is only 31 Flip-Flops utilized on FPGA?**  
    *32 physical output bits are registered ($W_C, W_S$), with 1 bit optimized out by clock-gating mapping.*
40. **How many top-level I/O pins does `fcu_top` have?**  
    *166 pins (118 inputs, 48 outputs).*

### 26.3 10 Challenging / Viva In-Depth Questions

41. **"In your waveform, `wc_out` is `0x2800` and `ws_out` is `0x419C`. Why aren't they identical?"**  
    *Because in real Carry-Save arithmetic, carries and sums are independent bit patterns generated by XOR and majority functions. Identical halves only occur in behavioral integer division (`>> 1`), which our structural tree avoids.*
42. **"Does carry rippling occur inside the 4:2 compressor horizontal carry line?"**  
    *No. $cout_1$ depends only on $xs, ys, yc$; it does not depend on the horizontal carry-in from the previous bit.*
43. **"What happens if an enable glitch occurs while the clock is high in your ICG cell?"**  
    *The negative-level latch is opaque when `clk = 1`, so the glitch is blocked from reaching the AND gate.*
44. **"Why don't you place a CStoBin converter after every FCU?"**  
    *That would reintroduce the $32\,T_g$ CPA bottleneck. Data is kept in carry-save form and converted only at the accelerator boundary.*
45. **"How does the direct CS-to-MB recoder avoid sign-extension overhead?"**  
    *Inputs are sign-extended by 2 bits, and digits are generated modulo $2^{16}$ across the 8 radix-4 stages.*
46. **"Can this architecture support floating-point arithmetic?"**  
    *Currently it is fixed-point integer. Supporting floating point would require separate exponent alignment and normalization logic.*
47. **"Why does the baseline FCC occupy $3274\,A_g$ while FCU occupies $2624\,A_g$ despite having twice as many register bits?"**  
    *The savings from eliminating two 16-bit CPAs ($2 \times 112\,A_g$) and the multiplier's internal CPA ($112\,A_g$) and post-adder outweigh the cost of 16 extra register bits.*
48. **"How do you prove your design is glitch-free in simulation?"**  
    *By deasserting `clk_gate_en` while applying varying inputs; outputs remain strictly held without toggle events.*
49. **"What are the Worst Negative Slack (WNS) and setup timing requirements?"**  
    *With a 10 ns clock constraint (100 MHz), WNS is positive ($> 0$), indicating zero setup violations on FPGA.*
50. **"What is the mathematical proof of 4:2 compressor carry weighting?"**  
    *Sum output has weight $2^i$; carry output $final\_c$ has weight $2^{i+1}$. Wiring $nc = \{final\_c[14:0], cin_2\}$ ensures all carry bits are properly shifted by 1 bit position.*

### 26.4 2-Minute Elevator Pitch Script for Interviews & Viva
> *"Good morning, respected examiners. My major project is the design, verification, and implementation of a **Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating**, based on the IEEE TVLSI 2016 base paper by Tsoumanis et al.*
>
> *In conventional DSP datapaths, chained Add-Multiply-Accumulate operations require three consecutive Carry-Propagate Adders, creating a $140\,T_g$ delay bottleneck due to horizontal carry rippling.*
>
> *Our architecture solves this by enforcing pervasive Carry-Save arithmetic: pre-additions are executed in constant $4\,T_g$ delay using a 4:2 compressor; Booth recoding is executed directly on carry-save inputs in $8\,T_g$; and post-accumulation is fused directly into Level 3 of a structural Wallace CSA reduction tree with zero extra CPA delay. This reduces the critical path from $140\,T_g$ to $40\,T_g$—a **71.43% speedup**—and improves the Area-Delay Product by **77.10%**.*
>
> *Additionally, we integrated a Dual-Rail Integrated Clock Gating cell that simultaneously gates both carry and sum registers from a negative-level latch, achieving **5.88% dynamic power savings** during idle cycles.*
>
> *The design has been verified across 535 Python golden vectors, 3 DSP kernels (FIR16, Elliptic, Volterra), and 112 synthesizable Verilog test vectors in Vivado with **zero errors**, consuming just **368 LUTs** on a Xilinx Artix-7 FPGA."*
