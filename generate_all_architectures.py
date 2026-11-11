#!/usr/bin/env python3
"""
Comprehensive Architecture Image Generator for Flexible DSP Accelerator
Generates publication-quality (300 DPI PNG & Vector PDF) diagrams for:
  Architecture 1: Conventional FCC Datapath (Baseline Existing System, 140 Tg)
  Architecture 2: Proposed Carry-Save FCU Datapath (Proposed System, 40 Tg)
  Architecture 3: Top-Level Flexible DSP Accelerator SoC System
  Architecture 4: 16-bit 4:2 Carry-Save Compressor & Subtraction Slice
  Architecture 5: Direct Carry-Save to Modified Booth (CS-to-MB) Recoder
  Architecture 6: Structural 3-Level 4:2 CSA Multiplier Reduction Tree with Operand Fusion
  Architecture 7: Dual-Rail Integrated Clock Gating (ICG) Cell & Timing
  Architecture 8: FCU Operation Templates Dataflow Graphs (T1 - T5)
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color Palette (IEEE Standard Compliant)
C_NAVY   = "#1f497d"
C_BLUE   = "#2e75b6"
C_LBLUE  = "#d9e1f2"
C_RED    = "#c00000"
C_LRED   = "#fce4d6"
C_GREEN  = "#385723"
C_LGREEN = "#e2efda"
C_ORANGE = "#c65911"
C_LORANGE= "#fff2cc"
C_PURPLE = "#7030a0"
C_LPURPLE= "#f2e8f9"
C_DARK   = "#262626"
C_GRAY   = "#595959"
C_LGRAY  = "#f2f2f2"


# ==============================================================================
# ARCHITECTURE 1: Conventional Flexible Computational Component (FCC) Baseline
# ==============================================================================
def generate_arch1():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Title
    ax.text(55, 96, "Architecture 1: Conventional Flexible Computational Component (FCC) Baseline", 
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.text(55, 92, "Standard Two's-Complement Datapath with 3 Serial Carry-Propagate Adders (Total Delay = 140 Tg)", 
            ha="center", va="center", fontsize=9.5, fontstyle="italic", color=C_RED)

    # Inputs Box
    p_in = patches.FancyBboxPatch((15, 80), 80, 8, boxstyle="round,pad=0.5", fc=C_LBLUE, ec=C_BLUE, lw=1.5)
    ax.add_patch(p_in)
    ax.text(55, 84, "Input Operands: X [15:0], Y [15:0], A [15:0] (Multiplicand), K [15:0] (Addend) [All Two's Complement]", 
            ha="center", va="center", fontsize=9, fontweight="bold", color=C_NAVY)

    # CPA 1 (Pre-Adder)
    p_cpa1 = patches.FancyBboxPatch((15, 62), 35, 12, boxstyle="round,pad=0.5", fc=C_LRED, ec=C_RED, lw=1.8)
    ax.add_patch(p_cpa1)
    ax.text(32.5, 70, "Carry-Propagate Adder 1 (CPA 1)\nPre-Adder: (X ± Y)", ha="center", va="center", fontsize=9, fontweight="bold", color=C_RED)
    ax.text(32.5, 64.5, "Delay = 16 x 2 Tg = 32 Tg [Ripple Carry]", ha="center", va="center", fontsize=8, color="#800000")

    # MUX1 & MUX2
    p_mux = patches.FancyBboxPatch((15, 46), 80, 10, boxstyle="round,pad=0.5", fc=C_LGRAY, ec=C_GRAY, lw=1.2)
    ax.add_patch(p_mux)
    ax.text(55, 51, "Multiplexers MUX1 & MUX2 (Operand Routing: N = X ± Y, or K)", ha="center", va="center", fontsize=9, fontweight="bold")

    # Multiplier Block (with Internal CPA!)
    p_mult = patches.FancyBboxPatch((15, 24), 80, 16, boxstyle="round,pad=0.8", fc="#fff5e6", ec=C_ORANGE, lw=1.8)
    ax.add_patch(p_mult)
    ax.text(55, 37, "Conventional Two's-Complement Multiplier (Total Multiplier Delay = 76 Tg)", ha="center", va="center", fontsize=9.5, fontweight="bold", color=C_ORANGE)
    
    # Inside multiplier sub-blocks
    ax.text(28, 30, "Radix-4 Booth Encoder\n(T_Booth = 8 Tg)", ha="center", va="center", fontsize=8, bbox=dict(boxstyle="square,pad=0.3", fc="white", ec=C_GRAY))
    ax.text(55, 30, "Wallace CSA Reduction Tree\n(T_Tree = 36 Tg)", ha="center", va="center", fontsize=8, bbox=dict(boxstyle="square,pad=0.3", fc="white", ec=C_GRAY))
    ax.text(82, 30, "INTERNAL CPA (CS to Binary)\n(T_CPA = 32 Tg) [BOTTLENECK!]", ha="center", va="center", fontsize=7.5, fontweight="bold", color=C_RED, bbox=dict(boxstyle="square,pad=0.3", fc=C_LRED, ec=C_RED))

    # CPA 2 (Post-Adder)
    p_cpa2 = patches.FancyBboxPatch((35, 8), 40, 11, boxstyle="round,pad=0.5", fc=C_LRED, ec=C_RED, lw=1.8)
    ax.add_patch(p_cpa2)
    ax.text(55, 15, "Carry-Propagate Adder 2 (CPA 2)\nPost-Accumulator (+ K)", ha="center", va="center", fontsize=9, fontweight="bold", color=C_RED)
    ax.text(55, 10.5, "Delay = 16 x 2 Tg = 32 Tg [Ripple Carry]", ha="center", va="center", fontsize=8, color="#800000")

    # Connective arrows
    ax.annotate("", xy=(32.5, 74), xytext=(32.5, 80), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_RED))
    ax.annotate("", xy=(32.5, 56), xytext=(32.5, 62), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_RED))
    ax.annotate("", xy=(55, 40), xytext=(55, 46), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_NAVY))
    ax.annotate("", xy=(55, 19), xytext=(55, 24), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_RED))

    # Summary callout
    p_box = patches.FancyBboxPatch((70, 60), 36, 16, boxstyle="round,pad=0.5", fc="#ffebe6", ec=C_RED, lw=1.2)
    ax.add_patch(p_box)
    ax.text(88, 71, "CRITICAL PATH BOTTLENECK:", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_RED)
    ax.text(88, 64, "T_crit = T_CPA1 + T_Mult + T_CPA2\n= 32 Tg + 76 Tg + 32 Tg\n= 140 Tg (1.68 ns @ 65nm)", ha="center", va="center", fontsize=8, color="#800000")

    plt.tight_layout()
    fpng = os.path.join(OUTPUT_DIR, "arch1_existing_fcc_datapath.png")
    fpdf = os.path.join(OUTPUT_DIR, "arch1_existing_fcc_datapath.pdf")
    plt.savefig(fpng, dpi=300)
    plt.savefig(fpdf)
    plt.close()
    print(f" [+] Generated: {fpng}")


# ==============================================================================
# ARCHITECTURE 2: Proposed Carry-Save Flexible Computational Unit (FCU)
# ==============================================================================
def generate_arch2():
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 110)
    ax.axis("off")

    ax.text(55, 106, "Architecture 2: Proposed Carry-Save Flexible Computational Unit (FCU)", 
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_GREEN)
    ax.text(55, 102, "Zero Intermediate CPAs | Constant-Time 4:2 Pre-Compressor | CSA Multiplier with Operand Fusion", 
            ha="center", va="center", fontsize=9.5, fontstyle="italic", color=C_NAVY)

    # Inputs
    p_in = patches.FancyBboxPatch((10, 91), 90, 8, boxstyle="round,pad=0.5", fc=C_LGREEN, ec=C_GREEN, lw=1.5)
    ax.add_patch(p_in)
    ax.text(55, 95, "Redundant Inputs: X*={XC, XS}, Y*={YC, YS}, K*={KC, KS} [16-bit CS Pairs], Multiplicand A [Signed 16-bit]", 
            ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_GREEN)

    # 4:2 Compressor Pre-Adder
    p_comp = patches.FancyBboxPatch((10, 75), 42, 11, boxstyle="round,pad=0.5", fc=C_LBLUE, ec=C_BLUE, lw=1.5)
    ax.add_patch(p_comp)
    ax.text(31, 82, "16-bit 4:2 Carry-Save Compressor\nPre-Adder: N* = X* ± Y*", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax.text(31, 77.5, "Delay = 4 Tg (Constant, Independent of Width!)", ha="center", va="center", fontsize=7.5, color=C_GREEN)

    # MUX Routing
    p_mux = patches.FancyBboxPatch((10, 60), 90, 9, boxstyle="round,pad=0.5", fc=C_LGRAY, ec=C_GRAY, lw=1.2)
    ax.add_patch(p_mux)
    ax.text(55, 64.5, "Multiplexers MUX0, MUX1, MUX2, MUX3 (Select P* = N* or K*, and Ext Addend = K* or N*)", 
            ha="center", va="center", fontsize=8.5, fontweight="bold")

    # CS-to-MB Recoder
    p_rec = patches.FancyBboxPatch((10, 44), 42, 11, boxstyle="round,pad=0.5", fc=C_LORANGE, ec=C_ORANGE, lw=1.5)
    ax.add_patch(p_rec)
    ax.text(31, 51, "Direct CS-to-MB Recoder\nRadix-4 Booth Digits d_i in {-2,-1,0,1,2}", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_ORANGE)
    ax.text(31, 46.5, "Delay = 8 Tg (Zero CPA Conversion!)", ha="center", va="center", fontsize=7.5, color=C_RED)

    # CSA Tree Multiplier with Operand Fusion
    p_tree = patches.FancyBboxPatch((56, 44), 44, 11, boxstyle="round,pad=0.5", fc=C_LBLUE, ec=C_BLUE, lw=1.5)
    ax.add_patch(p_tree)
    ax.text(78, 51, "CSA Tree Multiplier + Operand Fusion\nCompresses 8 PPs + Fused Ext Addend", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax.text(78, 46.5, "Delay = 24 Tg (No Post-Accumulator CPA!)", ha="center", va="center", fontsize=7.5, color=C_GREEN)

    # Clock Gated Output Registers
    p_icg = patches.FancyBboxPatch((10, 24), 90, 14, boxstyle="round,pad=0.6", fc="#e6f2ff", ec=C_BLUE, lw=1.5)
    ax.add_patch(p_icg)
    ax.text(55, 33, "Dual-Rail Gated Output Registers: W* = {WC_OUT, WS_OUT} [16-bit x 2]", ha="center", va="center", fontsize=9, fontweight="bold", color=C_NAVY)
    ax.text(55, 27.5, "Clocked by Glitch-Free Negative-Level Latch ICG Cell (clk_gate_en) | Saves 5.88% Dynamic Power", ha="center", va="center", fontsize=8, color=C_GREEN)

    # Boundary CPA
    p_cpa = patches.FancyBboxPatch((25, 6), 60, 12, boxstyle="round,pad=0.5", fc=C_LPURPLE, ec=C_PURPLE, lw=1.5)
    ax.add_patch(p_cpa)
    ax.text(55, 14, "Single Boundary CStoBin Ripple-Carry Converter", ha="center", va="center", fontsize=9, fontweight="bold", color=C_PURPLE)
    ax.text(55, 9.5, "Placed strictly at Accelerator Boundary (Off the inter-FCU critical path!) -> bin_out = wc + ws", ha="center", va="center", fontsize=7.5, color=C_DARK)

    # Callout Comparison
    p_call = patches.FancyBboxPatch((60, 75), 40, 11, boxstyle="round,pad=0.5", fc=C_LGREEN, ec=C_GREEN, lw=1.4)
    ax.add_patch(p_call)
    ax.text(80, 82, "PROPOSED SPEEDUP & ADP GAIN:", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_GREEN)
    ax.text(80, 77.5, "T_crit = 4 + 4 + 8 + 24 = 40 Tg\nDelay Reduction: 71.43% | ADP Gain: 77.10%", ha="center", va="center", fontsize=8, color=C_NAVY)

    # Connectors
    ax.annotate("", xy=(31, 86), xytext=(31, 91), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_GREEN))
    ax.annotate("", xy=(31, 69), xytext=(31, 75), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_GREEN))
    ax.annotate("", xy=(31, 55), xytext=(31, 60), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_NAVY))
    ax.annotate("", xy=(56, 49.5), xytext=(52, 49.5), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_ORANGE))
    ax.annotate("", xy=(78, 38), xytext=(78, 44), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_GREEN))
    ax.annotate("", xy=(55, 18), xytext=(55, 24), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_PURPLE))

    plt.tight_layout()
    fpng = os.path.join(OUTPUT_DIR, "arch2_proposed_fcu_microarchitecture.png")
    fpdf = os.path.join(OUTPUT_DIR, "arch2_proposed_fcu_microarchitecture.pdf")
    plt.savefig(fpng, dpi=300)
    plt.savefig(fpdf)
    plt.close()
    print(f" [+] Generated: {fpng}")


# ==============================================================================
# ARCHITECTURE 3: Top-Level Flexible DSP Accelerator SoC System
# ==============================================================================
def generate_arch3():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(55, 96, "Architecture 3: Top-Level Multi-FCU Flexible DSP Accelerator Architecture", 
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.text(55, 92, "Coarse-Grained Reconfigurable Datapath with Direct Carry-Save Chaining Across FCUs", 
            ha="center", va="center", fontsize=9.5, fontstyle="italic", color=C_GRAY)

    # Data Port
    p_dp = patches.FancyBboxPatch((8, 68), 24, 18, boxstyle="round,pad=0.5", fc=C_LBLUE, ec=C_BLUE, lw=1.4)
    ax.add_patch(p_dp)
    ax.text(20, 80, "I/O Data Port\n(External DMA / Host)", ha="center", va="center", fontsize=9, fontweight="bold", color=C_NAVY)
    ax.text(20, 72, "16-bit Parallel Streams\nInput/Output Buffers", ha="center", va="center", fontsize=7.5)

    # Scratch Register Bank
    p_rb = patches.FancyBboxPatch((38, 68), 64, 18, boxstyle="round,pad=0.5", fc=C_LGREEN, ec=C_GREEN, lw=1.4)
    ax.add_patch(p_rb)
    ax.text(70, 80, "Dual-Rail Carry-Save Scratchpad Register Bank", ha="center", va="center", fontsize=10, fontweight="bold", color=C_GREEN)
    ax.text(70, 72, "Stores Operands as Redundant Pairs {XC, XS}, {YC, YS}, {KC, KS}\nEnables Zero-Conversion Chaining Between Cascaded Execution Steps", ha="center", va="center", fontsize=8)

    # Crossbar Network
    p_xbar = patches.FancyBboxPatch((8, 48), 94, 12, boxstyle="round,pad=0.5", fc=C_LORANGE, ec=C_ORANGE, lw=1.4)
    ax.add_patch(p_xbar)
    ax.text(55, 54, "Reconfigurable Interconnection Network (Non-Blocking Crossbar Routing Matrix)", 
            ha="center", va="center", fontsize=9.5, fontweight="bold", color=C_ORANGE)

    # Array of FCUs
    fcu_names = ["FCU Datapath 0\n(T1 - T5)", "FCU Datapath 1\n(T1 - T5)", "FCU Datapath 2\n(T1 - T5)", "FCU Datapath N-1\n(T1 - T5)"]
    for i, name in enumerate(fcu_names):
        x_pos = 8 + i * 24.5
        p_fcu = patches.FancyBboxPatch((x_pos, 22), 21, 18, boxstyle="round,pad=0.4", fc="#e8f4f8", ec=C_BLUE, lw=1.3)
        ax.add_patch(p_fcu)
        ax.text(x_pos + 10.5, 33, name, ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
        ax.text(x_pos + 10.5, 26, "40 Tg Delay\nPervasive CS", ha="center", va="center", fontsize=7.5, color=C_GREEN)

    # Control Unit & FSM Scheduler
    p_cu = patches.FancyBboxPatch((8, 4), 58, 12, boxstyle="round,pad=0.5", fc=C_LGRAY, ec=C_GRAY, lw=1.2)
    ax.add_patch(p_cu)
    ax.text(37, 10, "Control Unit & FSM Mobility-Based Scheduler\n(Drives Template Words CL0-CL3, Routing Crossbar, and Clock Gating)", ha="center", va="center", fontsize=8.5, fontweight="bold")

    # Boundary CStoBin
    p_bound = patches.FancyBboxPatch((70, 4), 32, 12, boxstyle="round,pad=0.5", fc=C_LPURPLE, ec=C_PURPLE, lw=1.4)
    ax.add_patch(p_bound)
    ax.text(86, 11, "Boundary CStoBin\nRipple Carry CPA", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_PURPLE)
    ax.text(86, 6.5, "Final 16-bit Binary Out", ha="center", va="center", fontsize=7.5)

    # Connections
    ax.annotate("", xy=(38, 77), xytext=(32, 77), arrowprops=dict(arrowstyle="<->", lw=1.5, color=C_NAVY))
    ax.annotate("", xy=(55, 60), xytext=(55, 68), arrowprops=dict(arrowstyle="<->", lw=1.5, color=C_GREEN))
    for i in range(4):
        x_c = 18.5 + i * 24.5
        ax.annotate("", xy=(x_c, 40), xytext=(x_c, 48), arrowprops=dict(arrowstyle="<->", lw=1.3, color=C_ORANGE))
    ax.annotate("", xy=(86, 16), xytext=(86, 22), arrowprops=dict(arrowstyle="->", lw=1.5, color=C_PURPLE))

    plt.tight_layout()
    fpng = os.path.join(OUTPUT_DIR, "arch3_top_level_accelerator_system.png")
    fpdf = os.path.join(OUTPUT_DIR, "arch3_top_level_accelerator_system.pdf")
    plt.savefig(fpng, dpi=300)
    plt.savefig(fpdf)
    plt.close()
    print(f" [+] Generated: {fpng}")


# ==============================================================================
# ARCHITECTURE 4: 16-bit 4:2 Carry-Save Compressor with Subtraction Slice
# ==============================================================================
def generate_arch4():
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 96, "Architecture 4: 16-bit 4:2 Carry-Save Compressor & Subtraction Slice", 
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.text(50, 92, "Constant 4 Tg Critical Delay | 2 Cascaded Full Adders per Bit | Dual Carry-In (+2) for Subtraction", 
            ha="center", va="center", fontsize=9, fontstyle="italic", color=C_GRAY)

    # Outer Slice Border
    p_slice = patches.FancyBboxPatch((10, 10), 80, 78, boxstyle="round,pad=1.0", fc="#fafafa", ec=C_BLUE, lw=1.5, ls="--")
    ax.add_patch(p_slice)
    ax.text(14, 85, "Bit Slice i (i = 0, 1, ..., 15)", fontsize=9, fontweight="bold", color=C_NAVY)

    # FA 1
    p_fa1 = patches.FancyBboxPatch((20, 52), 26, 26, boxstyle="round,pad=0.5", fc=C_LBLUE, ec=C_BLUE, lw=1.5)
    ax.add_patch(p_fa1)
    ax.text(33, 68, "Full Adder 1\n(FA 1)", ha="center", va="center", fontsize=9.5, fontweight="bold", color=C_NAVY)
    ax.text(33, 58, "Delay: 2 Tg\nsum1 = xs ^ ys ^ yc\ncout1 = maj(xs,ys,yc)", ha="center", va="center", fontsize=7.5)

    # FA 2
    p_fa2 = patches.FancyBboxPatch((58, 52), 26, 26, boxstyle="round,pad=0.5", fc=C_LGREEN, ec=C_GREEN, lw=1.5)
    ax.add_patch(p_fa2)
    ax.text(71, 68, "Full Adder 2\n(FA 2)", ha="center", va="center", fontsize=9.5, fontweight="bold", color=C_GREEN)
    ax.text(71, 58, "Delay: 2 Tg\nfinal_s = sum1 ^ xc ^ c_in\nfinal_c = maj(sum1,xc,c_in)", ha="center", va="center", fontsize=7.5)

    # Inputs to FA1
    ax.annotate("xs[i]", xy=(24, 78), xytext=(24, 88), arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5, fontweight="bold")
    ax.annotate("ys[i]", xy=(33, 78), xytext=(33, 88), arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5, fontweight="bold")
    ax.annotate("yc[i]", xy=(42, 78), xytext=(42, 88), arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5, fontweight="bold")

    # Inputs to FA2
    ax.annotate("xc[i]", xy=(71, 78), xytext=(71, 88), arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=8.5, fontweight="bold")
    ax.annotate("", xy=(58, 65), xytext=(46, 65), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_NAVY))
    ax.text(52, 67, "sum1", ha="center", va="bottom", fontsize=8, fontweight="bold", color=C_NAVY)

    # Horizontal Carries
    ax.annotate("", xy=(58, 56), xytext=(48, 56), arrowprops=dict(arrowstyle="<-", lw=1.3, color=C_RED))
    ax.text(53, 52, "c_horiz[i]", ha="center", va="top", fontsize=7.5, color=C_RED)
    ax.annotate("", xy=(12, 60), xytext=(20, 60), arrowprops=dict(arrowstyle="<-", lw=1.3, color=C_RED))
    ax.text(16, 62, "cout1 -> [i+1]", ha="center", va="bottom", fontsize=7.5, color=C_RED)

    # Outputs
    ax.annotate("", xy=(71, 38), xytext=(71, 52), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_GREEN))
    ax.text(71, 34, "final_s[i] (Weight 2^i)\n-> ns[i]", ha="center", va="center", fontsize=8, fontweight="bold", color=C_GREEN)
    ax.annotate("", xy=(62, 38), xytext=(62, 52), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_NAVY))
    ax.text(58, 26, "final_c[i] (Weight 2^{i+1})\n-> nc[i+1] (Shifted by 1!)", ha="center", va="center", fontsize=8, fontweight="bold", color=C_NAVY)

    # Subtraction Formula Box
    p_sub = patches.FancyBboxPatch((15, 13), 50, 11, boxstyle="round,pad=0.4", fc=C_LORANGE, ec=C_ORANGE, lw=1.2)
    ax.add_patch(p_sub)
    ax.text(40, 20, "Exact Two's-Complement Subtraction (X* - Y*):", fontsize=8, fontweight="bold", color=C_ORANGE)
    ax.text(40, 16, "~(Y_C + Y_S) = -(Y_C + Y_S) - 2. Inversion requires adding +2:\ncin1 = 1 (to bit 0 horizontal chain) | cin2 = 1 (to nc[0])", fontsize=7.5)

    plt.tight_layout()
    fpng = os.path.join(OUTPUT_DIR, "arch4_compressor_4_2_slice.png")
    fpdf = os.path.join(OUTPUT_DIR, "arch4_compressor_4_2_slice.pdf")
    plt.savefig(fpng, dpi=300)
    plt.savefig(fpdf)
    plt.close()
    print(f" [+] Generated: {fpng}")


# ==============================================================================
# ARCHITECTURE 5: Direct CS-to-Modified Booth (CS-to-MB) Recoder
# ==============================================================================
def generate_arch5():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(55, 96, "Architecture 5: Direct Carry-Save to Modified Booth (CS-to-MB) Recoder", 
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_ORANGE)
    ax.text(55, 92, "Constant 8 Tg Delay | Zero Intermediate CPA | Translates Redundant CS Multiplier to 8 Radix-4 Digits", 
            ha="center", va="center", fontsize=9, fontstyle="italic", color=C_GRAY)

    # Digits blocks (stages 0 to 7)
    for i in range(4):
        x = 10 + i * 24
        p_st = patches.FancyBboxPatch((x, 48), 21, 36, boxstyle="round,pad=0.5", fc=C_LORANGE, ec=C_ORANGE, lw=1.4)
        ax.add_patch(p_st)
        ax.text(x + 10.5, 78, f"Digit Slice {i}\n(Bits {2*i+1}, {2*i})", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_ORANGE)
        ax.text(x + 10.5, 66, f"val_{i} = 2(pc_{{2i+1}}+ps_{{2i+1}})\n+ (pc_{{2i}}+ps_{{2i}})\n+ c_transfer_{i}", ha="center", va="center", fontsize=7.2)
        ax.text(x + 10.5, 54, f"Booth Digit d_{i}\nin {{-2,-1,0,1,2}}", ha="center", va="center", fontsize=8, fontweight="bold", color=C_NAVY)

        # Input arrows
        ax.annotate(f"P*[{2*i+1}:{2*i}]", xy=(x + 10.5, 84), xytext=(x + 10.5, 90), arrowprops=dict(arrowstyle="->", lw=1.2), fontsize=7.5)
        # Output arrows
        ax.annotate(f"d_{i} (one,two,neg,zero)", xy=(x + 10.5, 38), xytext=(x + 10.5, 48), arrowprops=dict(arrowstyle="<-", lw=1.2, color=C_NAVY), fontsize=7)

        # Transfer carries
        if i < 3:
            ax.annotate("", xy=(x + 21, 62), xytext=(x + 24, 62), arrowprops=dict(arrowstyle="<-", lw=1.4, color=C_RED))
            ax.text(x + 22.5, 64, f"c_tr\nin {{0,1,2}}", ha="center", va="bottom", fontsize=6.5, color=C_RED)

    # Truth Table Box
    p_tbl = patches.FancyBboxPatch((10, 6), 90, 26, boxstyle="round,pad=0.5", fc="#fafafa", ec=C_GRAY, lw=1.2)
    ax.add_patch(p_tbl)
    ax.text(55, 28, "Direct CS-to-MB Recoding Truth Table (val_i in [0, 8] -> Booth Digit d_i & Next Carry):", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
    
    table_text = (
        "val_i = 0  ->  d_i =  0, c_next = 0 (zero=1)      |      val_i = 5  ->  d_i = +1, c_next = 1 (one=1)\n"
        "val_i = 1  ->  d_i = +1, c_next = 0 (one=1)       |      val_i = 6  ->  d_i = +2, c_next = 1 (two=1)\n"
        "val_i = 2  ->  d_i = +2, c_next = 0 (two=1)       |      val_i = 7  ->  d_i = -1, c_next = 2 (neg=1, one=1)\n"
        "val_i = 3  ->  d_i = -1, c_next = 1 (neg=1, one=1)|      val_i = 8  ->  d_i =  0, c_next = 2 (zero=1)\n"
        "val_i = 4  ->  d_i =  0, c_next = 1 (zero=1)      |      Transfer carry is bounded strictly to adjacent digits (Delay = 8 Tg!)"
    )
    ax.text(55, 17, table_text, ha="center", va="center", fontsize=7.8, family="monospace", color=C_DARK)

    plt.tight_layout()
    fpng = os.path.join(OUTPUT_DIR, "arch5_cs_to_mb_recoder_stages.png")
    fpdf = os.path.join(OUTPUT_DIR, "arch5_cs_to_mb_recoder_stages.pdf")
    plt.savefig(fpng, dpi=300)
    plt.savefig(fpdf)
    plt.close()
    print(f" [+] Generated: {fpng}")


# ==============================================================================
# ARCHITECTURE 6: Structural 3-Level 4:2 CSA Multiplier Reduction Tree
# ==============================================================================
def generate_arch6():
    fig, ax = plt.subplots(figsize=(11, 8), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(55, 96, "Architecture 6: Structural 3-Level 4:2 CSA Wallace Reduction Tree", 
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.text(55, 92, "Compresses 8 Booth Partial Products + Directly Fuses Dual-Rail External Addend with Zero CPA", 
            ha="center", va="center", fontsize=9, fontstyle="italic", color=C_GREEN)

    # 8 Partial Products at top
    for i in range(8):
        x = 8 + i * 12
        p_pp = patches.FancyBboxPatch((x, 80), 10, 7, boxstyle="round,pad=0.3", fc=C_LORANGE, ec=C_ORANGE, lw=1.2)
        ax.add_patch(p_pp)
        ax.text(x + 5, 83.5, f"PP{i}", ha="center", va="center", fontsize=8, fontweight="bold", color=C_ORANGE)

    # Level 1 Compressors (Two 4:2 Compressors)
    p_l1a = patches.FancyBboxPatch((14, 60), 36, 12, boxstyle="round,pad=0.4", fc=C_LBLUE, ec=C_BLUE, lw=1.4)
    ax.add_patch(p_l1a)
    ax.text(32, 67, "4:2 Compressor L1_A", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax.text(32, 62.5, "Compresses PP0, PP1, PP2, PP3", ha="center", va="center", fontsize=7.5)

    p_l1b = patches.FancyBboxPatch((60, 60), 36, 12, boxstyle="round,pad=0.4", fc=C_LBLUE, ec=C_BLUE, lw=1.4)
    ax.add_patch(p_l1b)
    ax.text(78, 67, "4:2 Compressor L1_B", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax.text(78, 62.5, "Compresses PP4, PP5, PP6, PP7", ha="center", va="center", fontsize=7.5)

    # Connections to L1
    for i in range(4):
        ax.annotate("", xy=(32, 72), xytext=(13 + i * 12, 80), arrowprops=dict(arrowstyle="->", lw=1.1, color=C_ORANGE))
    for i in range(4, 8):
        ax.annotate("", xy=(78, 72), xytext=(13 + i * 12, 80), arrowprops=dict(arrowstyle="->", lw=1.1, color=C_ORANGE))

    # Level 2 Compressor
    p_l2 = patches.FancyBboxPatch((32, 38), 46, 13, boxstyle="round,pad=0.4", fc=C_LGREEN, ec=C_GREEN, lw=1.4)
    ax.add_patch(p_l2)
    ax.text(55, 46, "4:2 Compressor L2 (Multiplication Core)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_GREEN)
    ax.text(55, 41, "Reduces 4 vectors to 2 vectors: {l2_c, l2_s}\n(Pure Multiplication Product in Carry-Save Form)", ha="center", va="center", fontsize=7.5)

    ax.annotate("{l1_c_a, l1_s_a}", xy=(42, 51), xytext=(32, 60), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY), fontsize=7)
    ax.annotate("{l1_c_b, l1_s_b}", xy=(68, 51), xytext=(78, 60), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY), fontsize=7)

    # Level 3 Operand Fusion Compressor
    p_l3 = patches.FancyBboxPatch((25, 14), 60, 15, boxstyle="round,pad=0.5", fc=C_LPURPLE, ec=C_PURPLE, lw=1.6)
    ax.add_patch(p_l3)
    ax.text(55, 23, "Level 3: 4:2 Compressor L3 (OPERAND FUSION CORE)", ha="center", va="center", fontsize=9, fontweight="bold", color=C_PURPLE)
    ax.text(55, 17, "Fuses {l2_c, l2_s} + External Addend {ext_c, ext_s} with ZERO Intermediate CPA!\nProduces Final Dual-Rail Outputs: W* = {wc_out, ws_out}", ha="center", va="center", fontsize=7.5)

    ax.annotate("{l2_c, l2_s}", xy=(55, 29), xytext=(55, 38), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_GREEN), fontsize=7.5, fontweight="bold")
    ax.annotate("External Addend: {ext_c, ext_s} (from MUX3)", xy=(75, 29), xytext=(85, 38), arrowprops=dict(arrowstyle="->", lw=1.4, color=C_PURPLE), fontsize=7.5, fontweight="bold")

    # Outputs
    ax.annotate("", xy=(45, 5), xytext=(45, 14), arrowprops=dict(arrowstyle="->", lw=1.5, color=C_NAVY))
    ax.text(45, 3, "wc_out [15:0] (Carry Rail)", ha="center", va="top", fontsize=8, fontweight="bold", color=C_NAVY)
    ax.annotate("", xy=(65, 5), xytext=(65, 14), arrowprops=dict(arrowstyle="->", lw=1.5, color=C_GREEN))
    ax.text(65, 3, "ws_out [15:0] (Sum Rail)", ha="center", va="top", fontsize=8, fontweight="bold", color=C_GREEN)

    plt.tight_layout()
    fpng = os.path.join(OUTPUT_DIR, "arch6_csa_multiplier_tree_reduction.png")
    fpdf = os.path.join(OUTPUT_DIR, "arch6_csa_multiplier_tree_reduction.pdf")
    plt.savefig(fpng, dpi=300)
    plt.savefig(fpdf)
    plt.close()
    print(f" [+] Generated: {fpng}")


# ==============================================================================
# ARCHITECTURE 7: Dual-Rail Integrated Clock Gating (ICG) Architecture
# ==============================================================================
def generate_arch7():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)
    
    # Left: Schematic
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 80)
    ax1.axis("off")
    ax1.set_title("(a) Negative-Level Latch Dual-Rail ICG Schematic", fontweight="bold", fontsize=10, pad=10)

    p_latch = patches.FancyBboxPatch((20, 30), 22, 28, boxstyle="round,pad=0.3", fc=C_LBLUE, ec=C_BLUE, lw=1.4)
    ax1.add_patch(p_latch)
    ax1.text(31, 46, "D Latch\n(Negative Lvl\nTransparent)", ha="center", va="center", fontsize=8, fontweight="bold", color=C_NAVY)

    p_and = patches.FancyBboxPatch((58, 32), 18, 24, boxstyle="round,pad=0.3", fc=C_LGREEN, ec=C_GREEN, lw=1.4)
    ax1.add_patch(p_and)
    ax1.text(67, 44, "AND", ha="center", va="center", fontsize=9, fontweight="bold", color=C_GREEN)

    # Connections
    ax1.annotate("clk_gate_en", xy=(20, 48), xytext=(4, 48), arrowprops=dict(arrowstyle="->", lw=1.3), fontsize=8, fontweight="bold")
    ax1.annotate("clk", xy=(31, 22), xytext=(31, 10), arrowprops=dict(arrowstyle="->", lw=1.3), fontsize=8, fontweight="bold")
    ax1.annotate("", xy=(58, 48), xytext=(42, 48), arrowprops=dict(arrowstyle="->", lw=1.3, color=C_NAVY))
    ax1.text(50, 51, "latch_en", ha="center", va="bottom", fontsize=7.5, color=C_NAVY)
    ax1.annotate("", xy=(58, 38), xytext=(31, 16), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax1.annotate("gated_clk\n(Clocks both\nWC & WS Regs)", xy=(94, 44), xytext=(76, 44), arrowprops=dict(arrowstyle="<-", lw=1.4, color=C_GREEN), fontsize=8, fontweight="bold", color=C_GREEN)

    # Right: Timing Waveform
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 80)
    ax2.axis("off")
    ax2.set_title("(b) Glitch-Free Clock Gating Waveform", fontweight="bold", fontsize=10, pad=10)

    t = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    # clk
    ax2.text(2, 65, "clk", fontsize=8.5, fontweight="bold")
    ax2.step([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], [60, 68, 60, 68, 60, 68, 60, 68, 60, 68, 60], where="post", color="#333", lw=1.4)
    # enable
    ax2.text(2, 47, "enable", fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax2.step([0, 15, 65, 100], [45, 52, 45, 45], where="post", color=C_NAVY, lw=1.5)
    # latch_en
    ax2.text(2, 31, "latch_en", fontsize=8.5, fontweight="bold", color=C_ORANGE)
    ax2.step([0, 20, 70, 100], [29, 36, 29, 29], where="post", color=C_ORANGE, lw=1.5)
    # gated_clk
    ax2.text(2, 14, "gated_clk", fontsize=8.5, fontweight="bold", color=C_GREEN)
    ax2.step([0, 20, 30, 40, 50, 60, 70, 100], [10, 18, 10, 18, 10, 18, 10, 10], where="post", color=C_GREEN, lw=1.8)

    ax2.axvspan(65, 100, color="#ffebee", alpha=0.6)
    ax2.text(82, 5, "Clock Distribution Gated\n(Dynamic Power = 0)", ha="center", fontsize=7.5, fontweight="bold", color=C_RED)

    plt.tight_layout()
    fpng = os.path.join(OUTPUT_DIR, "arch7_dual_rail_icg_clock_gating.png")
    fpdf = os.path.join(OUTPUT_DIR, "arch7_dual_rail_icg_clock_gating.pdf")
    plt.savefig(fpng, dpi=300)
    plt.savefig(fpdf)
    plt.close()
    print(f" [+] Generated: {fpng}")


# ==============================================================================
# ARCHITECTURE 8: FCU Operation Templates Dataflow Graphs (T1 - T5)
# ==============================================================================
def generate_arch8():
    fig, axes = plt.subplots(1, 5, figsize=(12, 4.2), dpi=300)
    
    templates = [
        ("T1", "W* = A * (X* + Y*) + K*", "add_mult_add", "+", "+"),
        ("T2", "W* = A * (X* - Y*) + K*", "sub_mult_add", "-", "+"),
        ("T3", "W* = A * K* + (X* + Y*)", "mult_add_add", "*", "+"),
        ("T4", "W* = A * K* + (X* - Y*)", "mult_add_sub", "*", "-"),
        ("T5", "W* = A * K*", "mult_only", "*", "")
    ]

    for ax, (tname, formula, kind, op1, op2) in zip(axes, templates):
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
        ax.set_title(tname, fontweight="bold", fontsize=10, pad=6, color=C_NAVY)
        ax.text(50, 92, formula, ha="center", va="center", fontsize=7.2, fontweight="bold", color=C_GREEN)

        # Draw dataflow nodes
        if kind in ["add_mult_add", "sub_mult_add"]:
            # Pre-add node
            ax.add_patch(plt.Circle((50, 68), 9, color=C_LBLUE, ec=C_BLUE, lw=1.2))
            ax.text(50, 68, op1, ha="center", va="center", fontsize=11, fontweight="bold", color=C_NAVY)
            ax.text(28, 78, "X*", fontsize=8, fontweight="bold")
            ax.text(72, 78, "Y*", fontsize=8, fontweight="bold")
            ax.annotate("", xy=(44, 72), xytext=(32, 78), arrowprops=dict(arrowstyle="->", lw=1.1))
            ax.annotate("", xy=(56, 72), xytext=(68, 78), arrowprops=dict(arrowstyle="->", lw=1.1))

            # Mult node
            ax.add_patch(plt.Circle((50, 44), 9, color=C_LORANGE, ec=C_ORANGE, lw=1.2))
            ax.text(50, 44, "x", ha="center", va="center", fontsize=10, fontweight="bold", color=C_ORANGE)
            ax.annotate("", xy=(50, 53), xytext=(50, 59), arrowprops=dict(arrowstyle="->", lw=1.2))
            ax.text(28, 44, "A", fontsize=8, fontweight="bold")
            ax.annotate("", xy=(41, 44), xytext=(32, 44), arrowprops=dict(arrowstyle="->", lw=1.1))

            # Post-add node
            ax.add_patch(plt.Circle((50, 20), 9, color=C_LGREEN, ec=C_GREEN, lw=1.2))
            ax.text(50, 20, op2, ha="center", va="center", fontsize=11, fontweight="bold", color=C_GREEN)
            ax.annotate("", xy=(50, 29), xytext=(50, 35), arrowprops=dict(arrowstyle="->", lw=1.2))
            ax.text(72, 20, "K*", fontsize=8, fontweight="bold")
            ax.annotate("", xy=(59, 20), xytext=(68, 20), arrowprops=dict(arrowstyle="->", lw=1.1))

            ax.annotate("", xy=(50, 4), xytext=(50, 11), arrowprops=dict(arrowstyle="->", lw=1.3, color=C_PURPLE))
            ax.text(50, 0, "W*", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_PURPLE)

        elif kind in ["mult_add_add", "mult_add_sub"]:
            # Mult node
            ax.add_patch(plt.Circle((36, 60), 9, color=C_LORANGE, ec=C_ORANGE, lw=1.2))
            ax.text(36, 60, "x", ha="center", va="center", fontsize=10, fontweight="bold", color=C_ORANGE)
            ax.text(20, 72, "A", fontsize=8, fontweight="bold")
            ax.text(42, 72, "K*", fontsize=8, fontweight="bold")
            ax.annotate("", xy=(32, 66), xytext=(24, 72), arrowprops=dict(arrowstyle="->", lw=1.1))
            ax.annotate("", xy=(40, 66), xytext=(44, 72), arrowprops=dict(arrowstyle="->", lw=1.1))

            # Pre-add node
            ax.add_patch(plt.Circle((72, 60), 9, color=C_LBLUE, ec=C_BLUE, lw=1.2))
            ax.text(72, 60, op2, ha="center", va="center", fontsize=11, fontweight="bold", color=C_NAVY)
            ax.text(60, 72, "X*", fontsize=8, fontweight="bold")
            ax.text(84, 72, "Y*", fontsize=8, fontweight="bold")
            ax.annotate("", xy=(68, 66), xytext=(62, 72), arrowprops=dict(arrowstyle="->", lw=1.1))
            ax.annotate("", xy=(76, 66), xytext=(82, 72), arrowprops=dict(arrowstyle="->", lw=1.1))

            # Post-add node
            ax.add_patch(plt.Circle((54, 25), 9, color=C_LGREEN, ec=C_GREEN, lw=1.2))
            ax.text(54, 25, "+", ha="center", va="center", fontsize=11, fontweight="bold", color=C_GREEN)
            ax.annotate("", xy=(49, 32), xytext=(40, 52), arrowprops=dict(arrowstyle="->", lw=1.2))
            ax.annotate("", xy=(59, 32), xytext=(68, 52), arrowprops=dict(arrowstyle="->", lw=1.2))

            ax.annotate("", xy=(54, 8), xytext=(54, 16), arrowprops=dict(arrowstyle="->", lw=1.3, color=C_PURPLE))
            ax.text(54, 4, "W*", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_PURPLE)

        else: # T5: mult only
            ax.add_patch(plt.Circle((50, 48), 11, color=C_LORANGE, ec=C_ORANGE, lw=1.3))
            ax.text(50, 48, "x", ha="center", va="center", fontsize=12, fontweight="bold", color=C_ORANGE)
            ax.text(30, 68, "A", fontsize=9, fontweight="bold")
            ax.text(70, 68, "K*", fontsize=9, fontweight="bold")
            ax.annotate("", xy=(43, 54), xytext=(34, 65), arrowprops=dict(arrowstyle="->", lw=1.2))
            ax.annotate("", xy=(57, 54), xytext=(66, 65), arrowprops=dict(arrowstyle="->", lw=1.2))

            ax.annotate("", xy=(50, 24), xytext=(50, 37), arrowprops=dict(arrowstyle="->", lw=1.3, color=C_PURPLE))
            ax.text(50, 18, "W*", ha="center", va="center", fontsize=9, fontweight="bold", color=C_PURPLE)

    plt.tight_layout()
    fpng = os.path.join(OUTPUT_DIR, "arch8_fcu_templates_t1_t5_dataflow.png")
    fpdf = os.path.join(OUTPUT_DIR, "arch8_fcu_templates_t1_t5_dataflow.pdf")
    plt.savefig(fpng, dpi=300)
    plt.savefig(fpdf)
    plt.close()
    print(f" [+] Generated: {fpng}")


def main():
    print("=" * 75)
    print(" GENERATING ALL 8 ESSENTIAL ARCHITECTURE IMAGES (300 DPI PNG & VECTOR PDF)")
    print("=" * 75)
    generate_arch1()
    generate_arch2()
    generate_arch3()
    generate_arch4()
    generate_arch5()
    generate_arch6()
    generate_arch7()
    generate_arch8()
    print("=" * 75)
    print(f" ALL ARCHITECTURE IMAGES SUCCESSFULLY GENERATED IN: {OUTPUT_DIR}")
    print("=" * 75)


if __name__ == "__main__":
    main()

