#!/usr/bin/env python3
"""
Generates the Architectural Diagram for the Existing System (Base Paper Architecture - FCC)
Saves as 300 DPI PNG and vector PDF in figures/
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.linewidth"] = 1.2

C_NAVY = "#1f497d"
C_RED  = "#c0392b"
C_GRAY = "#555555"

def generate_existing_fcc_diagram():
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Title
    ax.text(50, 97, "Base Paper Architecture: Conventional Flexible Computational Component (FCC)", 
            ha="center", va="center", fontsize=12, fontweight="bold", color="#111")
    ax.text(50, 93.5, "Based on Galanis et al. & Section IV Fig. 4(a) of IEEE TVLSI 2016", 
            ha="center", va="center", fontsize=9, fontstyle="italic", color="#555")

    # Outer border
    outer = patches.FancyBboxPatch((4, 4), 92, 86, boxstyle="round,pad=1.2", fc="#fafafa", ec="#777", lw=1.5)
    ax.add_patch(outer)
    ax.text(6, 87, "Conventional Two's Complement Datapath (FCC)", fontsize=9.5, fontweight="bold", color=C_NAVY)

    # Inputs at top
    ax.text(18, 82, "X [15:0]\n(2's Compl.)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax.text(38, 82, "Y [15:0]\n(2's Compl.)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax.text(58, 82, "A [15:0]\n(Multiplicand)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#803300")
    ax.text(78, 82, "K [15:0]\n(Addend)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)

    # Input MUX (select Y or ~Y)
    mux_in = patches.Polygon([[32, 76], [44, 76], [41, 71], [35, 71]], closed=True, fc="#fff2cc", ec="#d6b656", lw=1.2)
    ax.add_patch(mux_in)
    ax.text(38, 73.5, "MUX\n(Add/Sub)", ha="center", va="center", fontsize=7.5, fontweight="bold")
    ax.annotate("", xy=(38, 76), xytext=(38, 79), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY))

    # CPA 1 Box
    cpa1_box = patches.FancyBboxPatch((12, 57), 36, 10, boxstyle="round,pad=0.4", fc="#fadbd8", ec=C_RED, lw=1.4)
    ax.add_patch(cpa1_box)
    ax.text(30, 62, "Carry-Propagate Adder 1 (CPA 1)\n16-bit Ripple-Carry Adder: (X ± Y)\n[Critical Delay: 32 Tg | Long Carry Ripple!]", 
            ha="center", va="center", fontsize=8, fontweight="bold", color="#78281f")

    ax.annotate("", xy=(18, 67), xytext=(18, 79), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY))
    ax.annotate("", xy=(38, 67), xytext=(38, 71), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY))

    # MUX1 & MUX2 for FCC templates
    m1 = patches.Polygon([[24, 51], [36, 51], [33, 46], [27, 46]], closed=True, fc="#fff2cc", ec="#d6b656", lw=1.2)
    ax.add_patch(m1)
    ax.text(30, 48.5, "MUX1", ha="center", va="center", fontsize=7.5, fontweight="bold")

    m2 = patches.Polygon([[68, 51], [80, 51], [77, 46], [71, 46]], closed=True, fc="#fff2cc", ec="#d6b656", lw=1.2)
    ax.add_patch(m2)
    ax.text(74, 48.5, "MUX2", ha="center", va="center", fontsize=7.5, fontweight="bold")

    ax.annotate("", xy=(30, 51), xytext=(30, 57), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_RED))
    ax.annotate("", xy=(72, 51), xytext=(34, 57), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_RED))
    ax.annotate("", xy=(76, 51), xytext=(78, 79), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY))
    ax.annotate("", xy=(33, 51), xytext=(76, 79), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY))

    # Multiplier Subsystem
    mult_box = patches.FancyBboxPatch((12, 25), 44, 18, boxstyle="round,pad=0.5", fc="#dae8fc", ec="#4a7ebb", lw=1.4)
    ax.add_patch(mult_box)
    ax.text(34, 39, "Conventional Radix-4 Booth Multiplier\n(16-bit × 16-bit Two's Complement)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_NAVY)

    # Sub-blocks inside multiplier
    b_enc = patches.Rectangle((15, 27.5), 11, 8, fc="white", ec="#4a7ebb", lw=1)
    ax.add_patch(b_enc)
    ax.text(20.5, 31.5, "Booth\nEncoder", ha="center", va="center", fontsize=7, fontweight="bold")

    b_tree = patches.Rectangle((28, 27.5), 13, 8, fc="white", ec="#4a7ebb", lw=1)
    ax.add_patch(b_tree)
    ax.text(34.5, 31.5, "PPG +\nCSA Tree", ha="center", va="center", fontsize=7, fontweight="bold")

    b_cpa = patches.Rectangle((43, 27.5), 11, 8, fc="#fadbd8", ec=C_RED, lw=1)
    ax.add_patch(b_cpa)
    ax.text(48.5, 31.5, "Internal\nCPA Adder\n(32 Tg)", ha="center", va="center", fontsize=6.5, fontweight="bold", color="#78281f")

    ax.annotate("", xy=(26, 31.5), xytext=(28, 31.5), arrowprops=dict(arrowstyle="<-", lw=1))
    ax.annotate("", xy=(41, 31.5), xytext=(43, 31.5), arrowprops=dict(arrowstyle="<-", lw=1))

    ax.annotate("", xy=(21, 35.5), xytext=(30, 46), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY))
    ax.annotate("", xy=(34, 35.5), xytext=(58, 79), arrowprops=dict(arrowstyle="->", lw=1.2, color="#803300"))

    # CPA 2 Box (Post-Addition)
    cpa2_box = patches.FancyBboxPatch((30, 11), 40, 10, boxstyle="round,pad=0.4", fc="#fadbd8", ec=C_RED, lw=1.4)
    ax.add_patch(cpa2_box)
    ax.text(50, 16, "Carry-Propagate Adder 2 (CPA 2)\nPost-Multiplier Accumulation: Product + K\n[Critical Delay: 32 Tg | Ripple Carry Bottleneck!]", 
            ha="center", va="center", fontsize=8, fontweight="bold", color="#78281f")

    ax.annotate("", xy=(44, 21), xytext=(34, 25), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY))
    ax.annotate("", xy=(56, 21), xytext=(74, 46), arrowprops=dict(arrowstyle="->", lw=1.2, color=C_NAVY))

    # Single-Rail Clock Gating
    icg = patches.FancyBboxPatch((74, 18), 20, 14, boxstyle="round,pad=0.3", fc="#e2efda", ec="#385723", lw=1.2)
    ax.add_patch(icg)
    ax.text(84, 25, "Single-Rail ICG Cell\n(clk_gate_en)\nGates Binary Regs", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#274e13")

    # Output Arrow
    ax.annotate("Final Output: W [15:0] (Two's Complement Binary)", xy=(50, 5), xytext=(50, 11),
                ha="center", va="top", fontsize=9, fontweight="bold", color=C_NAVY,
                arrowprops=dict(arrowstyle="<-", lw=1.5, color=C_NAVY))

    # Critical path banner on right side
    c_banner = patches.FancyBboxPatch((60, 64), 34, 15, boxstyle="round,pad=0.4", fc="#fff", ec=C_RED, lw=1.5, ls="--")
    ax.add_patch(c_banner)
    ax.text(77, 74, "CRITICAL PATH BOTTLENECK", ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_RED)
    ax.text(77, 68, "T_crit = T_CPA1 + T_Mult + T_CPA2\n= 32 Tg + 76 Tg + 32 Tg\n≈ 140 Tg (High Delay!)", 
            ha="center", va="center", fontsize=7.5, fontweight="bold", color="#333")

    plt.tight_layout()
    fpath_png = os.path.join(OUTPUT_DIR, "fig_base_paper_existing_fcc.png")
    fpath_pdf = os.path.join(OUTPUT_DIR, "fig_base_paper_existing_fcc.pdf")
    plt.savefig(fpath_png, dpi=300)
    plt.savefig(fpath_pdf)
    plt.close()
    print(f" [+] Generated: {fpath_png}")

if __name__ == "__main__":
    generate_existing_fcc_diagram()

