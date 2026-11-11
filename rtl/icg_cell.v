// ==============================================================================
// 1. Integrated Clock Gating (ICG) Cell
// Negative-level latch prevents clock glitches on the output gated_clk.
// When clk_gate_en is low, the clock is cleanly gated to save dynamic power.
// ==============================================================================
`timescale 1ns / 1ps

module icg_cell (
    input  wire clk,
    input  wire clk_gate_en,
    output wire gated_clk
);
    reg latch_en;

    // Negative-level latch captures enable during low clock phase
    always @(clk or clk_gate_en) begin
        if (!clk) begin
            latch_en <= clk_gate_en;
        end
    end

    assign gated_clk = clk & latch_en;

endmodule
