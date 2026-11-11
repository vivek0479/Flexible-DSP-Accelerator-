#!/usr/bin/env python3
"""
Publication-Quality Figure Generator for IEEE Paper
Generates Figs 7, 8, and 9 as 300-DPI PNGs and vector SVGs.
"""

import os
import sys

# Destination directory for publication figures
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_with_matplotlib():
    import matplotlib.pyplot as plt
    import numpy as np

    # Set publication styling
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.linewidth"] = 1.2
    plt.rcParams["grid.alpha"] = 0.35
    plt.rcParams["grid.linestyle"] = "--"

    # Color palette (IEEE compliant)
    c_existing = "#2b5c8f"   # Deep Navy
    c_proposed = "#d95f02"   # High-contrast Ochre / Orange
    c_gain     = "#1b9e77"   # Forest Green

    # ==============================================================================
    # FIGURE 7: Hardware Metric Comparison (Area, Delay, ADP)
    # ==============================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

    # Subplot A: Delay and Area
    metrics = ["Critical Delay\n(Tg)", "Delay @ 65nm\n(ns x 10)", "Gate Area\n(Ag / 100)"]
    fcc_vals = [140.0, 1.68 * 10, 3274.0 / 100]
    fcu_vals = [40.0,  1.13 * 10, 2624.0 / 100]

    x = np.arange(len(metrics))
    width = 0.32

    rects1 = ax1.bar(x - width/2, fcc_vals, width, label="Existing (FCC)", color=c_existing, edgecolor="black", linewidth=0.8)
    rects2 = ax1.bar(x + width/2, fcu_vals, width, label="Proposed (FCU)", color=c_proposed, edgecolor="black", linewidth=0.8)

    ax1.set_ylabel("Normalized Metric Value", fontweight="bold")
    ax1.set_title("(a) Speed & Area Complexity", fontweight="bold", pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend(loc="upper right", framealpha=0.9)
    ax1.grid(True, axis="y")

    # Add reduction percentage annotations
    gains = ["-71.4%", "-32.7%", "-19.8%"]
    for i, g in enumerate(gains):
        y_pos = max(fcc_vals[i], fcu_vals[i]) + 4
        ax1.annotate(g, xy=(x[i] + width/2, fcu_vals[i]),
                     xytext=(x[i] + width/2, fcu_vals[i] + 4),
                     ha="center", va="bottom", fontsize=9, fontweight="bold", color=c_gain,
                     arrowprops=dict(arrowstyle="->", color=c_gain, lw=1))
    ax1.set_ylim(0, 165)

    # Subplot B: Area-Delay Product (ADP)
    adp_labels = ["Area-Delay Product\n(x 10³ Ag·Tg)"]
    fcc_adp = [458.36]
    fcu_adp = [104.96]

    x_b = np.arange(len(adp_labels))
    b1 = ax2.bar(x_b - width/2, fcc_adp, width, label="Existing (FCC)", color=c_existing, edgecolor="black", linewidth=0.8)
    b2 = ax2.bar(x_b + width/2, fcu_adp, width, label="Proposed (FCU)", color=c_proposed, edgecolor="black", linewidth=0.8)

    ax2.set_ylabel("ADP (10³ Ag·Tg)", fontweight="bold")
    ax2.set_title("(b) Area-Delay Product (ADP)", fontweight="bold", pad=12)
    ax2.set_xticks(x_b)
    ax2.set_xticklabels(adp_labels)
    ax2.legend(loc="upper right", framealpha=0.9)
    ax2.grid(True, axis="y")

    ax2.annotate("77.10% ADP\nImprovement", xy=(x_b[0] + width/2, fcu_adp[0]),
                 xytext=(x_b[0] + width/2 + 0.05, fcu_adp[0] + 100),
                 ha="center", va="bottom", fontsize=10, fontweight="bold", color=c_gain,
                 arrowprops=dict(arrowstyle="->", color=c_gain, lw=1.2))
    ax2.set_ylim(0, 520)

    # Bar value labels
    for bar in list(b1) + list(b2):
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f"{yval:.1f}k", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    f7_png = os.path.join(OUTPUT_DIR, "fig7_hardware_comparison.png")
    f7_pdf = os.path.join(OUTPUT_DIR, "fig7_hardware_comparison.pdf")
    plt.savefig(f7_png, dpi=300)
    plt.savefig(f7_pdf)
    plt.close()
    print(f" [+] Generated: {f7_png}")

    # ==============================================================================
    # FIGURE 8: Energy Consumption per DSP Benchmark Kernel
    # ==============================================================================
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)

    kernels = ["16-tap FIR Filter\n(FIR16)", "6th-Order Elliptic\nFilter (ELLIPTIC)", "2nd-Order Volterra\nFilter (VOLTERRA)"]
    fcc_energy = [1038.04, 261.04, 391.30]
    fcu_energy = [754.05,  167.18, 243.18]
    energy_gains = ["27.36% Less", "35.95% Less", "37.85% Less"]

    x = np.arange(len(kernels))
    width = 0.32

    r1 = ax.bar(x - width/2, fcc_energy, width, label="Existing (FCC Datapath)", color=c_existing, edgecolor="black", linewidth=0.8)
    r2 = ax.bar(x + width/2, fcu_energy, width, label="Proposed (Carry-Save FCU)", color=c_proposed, edgecolor="black", linewidth=0.8)

    ax.set_ylabel("Total Energy Consumption (pJ)", fontweight="bold")
    ax.set_title("Energy Consumption across Benchmark DSP Kernels (65nm CMOS)", fontweight="bold", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(kernels, fontweight="medium")
    ax.legend(loc="upper right", framealpha=0.95)
    ax.grid(True, axis="y")
    ax.set_ylim(0, 1200)

    # Values and badges on bars
    for i, bar in enumerate(r1):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 18, f"{yval:.1f} pJ", ha="center", va="bottom", fontsize=9)

    for i, bar in enumerate(r2):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 18, f"{yval:.1f} pJ", ha="center", va="bottom", fontsize=9, fontweight="bold")
        # Callout banner for energy saved
        ax.text(bar.get_x() + bar.get_width()/2.0, yval / 2.0, energy_gains[i], ha="center", va="center", color="white", fontsize=8.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", facecolor=c_gain, edgecolor="none"))

    plt.tight_layout()
    f8_png = os.path.join(OUTPUT_DIR, "fig8_energy_kernels.png")
    f8_pdf = os.path.join(OUTPUT_DIR, "fig8_energy_kernels.pdf")
    plt.savefig(f8_png, dpi=300)
    plt.savefig(f8_pdf)
    plt.close()
    print(f" [+] Generated: {f8_png}")

    # ==============================================================================
    # FIGURE 9: Clock Gating Dynamic Power Savings Analysis
    # ==============================================================================
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)

    archs = ["Existing System (FCC)", "Proposed System (FCU)"]
    ungated_power = [0.2510, 0.5478]
    gated_power   = [0.2270, 0.5156]
    savings_pct   = ["9.58% Saved", "5.88% Saved"]

    x = np.arange(len(archs))
    width = 0.3

    p1 = ax.bar(x - width/2, ungated_power, width, label="Continuous Clock (Un-gated)", color="#7570b3", edgecolor="black", linewidth=0.8)
    p2 = ax.bar(x + width/2, gated_power, width, label="With Integrated Clock Gating (ICG)", color=c_gain, edgecolor="black", linewidth=0.8)

    ax.set_ylabel("Dynamic Power Consumption (mW)", fontweight="bold")
    ax.set_title("Impact of Integrated Clock Gating (ICG) on Dynamic Power", fontweight="bold", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(archs, fontweight="medium")
    ax.legend(loc="upper left", framealpha=0.95)
    ax.grid(True, axis="y")
    ax.set_ylim(0, 0.65)

    for i, bar in enumerate(p1):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.015, f"{yval:.4f} mW", ha="center", va="bottom", fontsize=9)

    for i, bar in enumerate(p2):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.015, f"{yval:.4f} mW", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.annotate(savings_pct[i], xy=(bar.get_x() + bar.get_width()/2.0, yval),
                    xytext=(bar.get_x() + bar.get_width()/2.0, yval + 0.05),
                    ha="center", va="bottom", fontsize=9, fontweight="bold", color=c_gain,
                    arrowprops=dict(arrowstyle="->", color=c_gain, lw=1))

    plt.tight_layout()
    f9_png = os.path.join(OUTPUT_DIR, "fig9_clock_gating_power.png")
    f9_pdf = os.path.join(OUTPUT_DIR, "fig9_clock_gating_power.pdf")
    plt.savefig(f9_png, dpi=300)
    plt.savefig(f9_pdf)
    plt.close()
    print(f" [+] Generated: {f9_png}")


def main():
    print("=" * 70)
    print(" GENERATING PUBLICATION-QUALITY PAPER FIGURES (FIGS 7, 8, 9)")
    print("=" * 70)
    try:
        plot_with_matplotlib()
        print("=" * 70)
        print(f" ALL FIGURES GENERATED SUCCESSFULLY IN: {OUTPUT_DIR}")
        print("=" * 70)
    except ImportError:
        print(" [!] matplotlib not found. Please install with: pip install matplotlib")
        sys.exit(1)


if __name__ == "__main__":
    main()

