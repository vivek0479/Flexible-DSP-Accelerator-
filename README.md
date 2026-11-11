# Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic with Dual-Rail Integrated Clock Gating

This repository contains the complete academic research implementation, cycle-accurate simulation, synthesizable Verilog RTL, publication figures, and verification suite for:

> **"Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic"**  
> **Authors**: Kostas Tsoumanis, Sotirios Xydis, Georgios Zervakis, and Kiamal Pekmestzi  
> **Journal**: *IEEE Transactions on Very Large Scale Integration (VLSI) Systems*, Vol. 24, No. 1, January 2016  
> **Extended With**: Dual-Rail Integrated Clock Gating (ICG) Architecture and Open-Source Synthesizable RTL.

---

## 📁 Repository Structure & Directory Organization

```
1.Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic/
│
├── 📄 1. DOCUMENTATION & MANUSCRIPTS
│   ├── PROJECT_DOCUMENTATION.md        # Comprehensive master documentation & Viva Guide
│   ├── BASE_PAPER_EXISTING_SYSTEM.md   # Base paper analysis & Existing System (FCC) breakdown
│   ├── README.md                       # Quick-start directory overview (this file)
│   └── 1.Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic.pdf
│
├── ⚙️ 2. MASTER RUNNERS & CODE GENERATORS
│   ├── run_all.py                      # Master execution & verification pipeline
│   ├── generate_rtl.py                 # Synthesizable Verilog RTL generator
│   ├── generate_all_paper_figures.py   # Generates Figures 1 to 6 (Architectural Diagrams & Waveforms)
│   ├── generate_paper_charts.py        # Generates Figures 7 to 9 (Quantitative Comparison Charts)
│   └── generate_base_paper_figure.py   # Generates Existing System (FCC) Architecture Diagram
│
├── 🧠 3. PROPOSED SYSTEM (CARRY-SAVE FCU DATAPATH)
│   ├── proposed_system/
│   │   ├── cs_arithmetic.py            # CarrySaveNumber class & 4:2 Compressor (Delay = 4 Tg)
│   │   ├── cs_to_mb_recoder.py         # Direct CS-to-Modified-Booth recoder (Delay = 8 Tg, NO CPA)
│   │   ├── csa_tree_multiplier.py      # CSA Tree Multiplier with operand fusion (Delay = 24 Tg)
│   │   ├── fcu_datapath.py             # Top-Level FCU Datapath (Templates T1-T5) & CStoBin
│   │   ├── clock_gating.py             # Dual-rail Carry-Save ICG cell & power tracker
│   │   ├── dsp_kernels.py              # FIR16, ELLIPTIC, and VOLTERRA benchmark mappings
│   │   ├── simulator.py                # Standalone cycle-accurate simulation runner
│   │   └── README.md
│
├── 🏛️ 4. EXISTING SYSTEM (CONVENTIONAL FCC BASELINE)
│   ├── existing_system/
│   │   ├── arithmetic_units.py         # 16-bit CPA and Conventional Radix-4 Booth Multiplier
│   │   ├── fcc_datapath.py             # FCC Datapath with 3 intermediate CPAs (Delay = 140 Tg)
│   │   ├── clock_gating.py             # Single-rail ICG cell & power tracker
│   │   ├── dsp_kernels.py              # FIR16, ELLIPTIC, and VOLTERRA mappings on FCC
│   │   ├── simulator.py                # Standalone simulation & power runner
│   │   └── README.md
│
├── 🧪 5. VERIFICATION & COMPARATIVE BENCHMARKS
│   ├── benchmarks/
│   │   ├── verify_equivalence.py       # 100% bit-accurate mathematical equivalence checker
│   │   └── compare_metrics.py          # Area, delay, ADP, energy, and power comparisons
│
├── 💻 6. SYNTHESIZABLE VERILOG RTL (EDA PLAYGROUND / VIVADO)
│   ├── rtl/
│   │   ├── design.sv                   # All-in-one synthesizable design for EDA Playground
│   │   ├── testbench.sv                # All-in-one self-checking testbench for EDA Playground
│   │   ├── icg_cell.v                  # Integrated Clock Gating (ICG) cell
│   │   ├── compressor_4_2.v            # Constant-time 16-bit 4:2 Carry-Save Compressor
│   │   ├── cs_to_mb_recoder.v          # Direct CS-to-Modified Booth Recoder (No CPA)
│   │   ├── csa_tree_multiplier.v       # CSA Multiplier Tree with inlined operand fusion
│   │   ├── cs_to_bin.v                 # Boundary CStoBin Ripple-Carry Converter
│   │   ├── fcu_top.v                   # Top-level FCU datapath (Templates T1 - T5)
│   │   └── fcu_tb.v                    # Standalone self-checking testbench
│
└── 📊 7. PUBLICATION-QUALITY FIGURES (300 DPI PNG & VECTOR PDF)
    ├── figures/
    │   ├── fig1_top_level_architecture.png / .pdf    # Top-Level Accelerator Core
    │   ├── fig2_fcu_microarchitecture.png / .pdf     # Detailed FCU Datapath
    │   ├── fig3_chaining_comparison.png / .pdf       # Critical Path Chaining: 140 Tg vs 40 Tg
    │   ├── fig4_templates_dataflow.png / .pdf        # Operation Templates (T1 - T5 DFGs)
    │   ├── fig5_clock_gating_schematic.png / .pdf    # Latch-Based ICG Cell & Waveform
    │   ├── fig6_rtl_simulation_waveform.png / .pdf   # Behavioral Simulation Waveform
    │   ├── fig7_hardware_comparison.png / .pdf       # Delay, Area, and ADP Comparison Charts
    │   ├── fig8_energy_kernels.png / .pdf            # Energy Savings across DSP Filters
    │   ├── fig9_clock_gating_power.png / .pdf        # Dynamic Power Reduction with ICG
    │   └── fig_base_paper_existing_fcc.png / .pdf    # Existing Base Paper FCC Architecture
```

---

## ⚡ Key Results Summary

| Architectural Metric | Existing System (FCC) | Proposed System (FCU) | Improvement |
| :--- | :---: | :---: | :---: |
| **Critical Path Delay ($T_g$)** | **$140.0 \, T_g$** | **$40.0 \, T_g$** | **71.43% Delay Cut** |
| **Clock Period @ 65nm ($T_{\text{crit}}$)** | **$1.68 \, \text{ns}$** | **$1.13 \, \text{ns}$** | **32.74% Clock Frequency Gain** |
| **Gate Equivalent Area ($A_g$)** | **$3274.0 \, A_g$** | **$2624.0 \, A_g$** | **19.85% Area Reduction** |
| **Area-Delay Product (ADP)** | **$458,360 \, A_g \cdot T_g$** | **$104,960 \, A_g \cdot T_g$** | **77.10% Efficiency Improvement** |
| **FIR16 Energy Consumption** | **$1038.04 \, \text{pJ}$** | **$754.05 \, \text{pJ}$** | **27.36% Less Energy** |
| **Elliptic Filter Energy** | **$261.04 \, \text{pJ}$** | **$167.18 \, \text{pJ}$** | **35.95% Less Energy** |
| **Volterra Filter Energy** | **$391.30 \, \text{pJ}$** | **$243.18 \, \text{pJ}$** | **37.85% Less Energy** |
| **Clock Gating Power Savings** | **$9.58\%$** | **$5.88\%$** | **Idle Dynamic Power Suppressed** |

---

## 🚀 Execution & Simulation Guide

### 1. Master Simulation (Python)
Run the full verification and comparison pipeline:
```powershell
python run_all.py
```

### 2. Regenerate Synthesizable Verilog RTL
```powershell
python generate_rtl.py
```

### 3. Regenerate Publication Figures
```powershell
python generate_all_paper_figures.py
python generate_paper_charts.py
python generate_base_paper_figure.py
```

### 4. Run RTL in EDA Playground (Online)
1. Go to **[edaplayground.com](https://www.edaplayground.com)**.
2. Select **Icarus Verilog 0.10.0** (or **Aldec Riviera Pro**).
3. Paste `rtl/design.sv` into the **`design.sv`** pane.
4. Paste `rtl/testbench.sv` into the **`testbench.sv`** pane.
5. Check **Open EPWave after run** and click **Run**.
