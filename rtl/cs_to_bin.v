// ==============================================================================
// 5. Boundary CStoBin Converter
// Placed strictly at the boundary of the accelerator to convert
// final Carry-Save representation W* = {WC, WS} into Two's Complement binary.
// ==============================================================================
`timescale 1ns / 1ps

module cs_to_bin #(
    parameter WIDTH = 16
)(
    input  wire [WIDTH-1:0] wc,
    input  wire [WIDTH-1:0] ws,
    output wire signed [WIDTH-1:0] bin_out
);
    // Standard Ripple-Carry / Carry-Propagate Addition at accelerator boundary
    assign bin_out = $signed(wc + ws);

endmodule
