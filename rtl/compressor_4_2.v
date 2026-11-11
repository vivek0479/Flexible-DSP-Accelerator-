// ==============================================================================
// 2. 16-bit 4:2 Carry-Save Compressor / Adder
// Fuses additions and subtractions prior to multiplication in constant 4 Tg delay.
// Uses two cascaded Full Adders per bit slice; carries do NOT propagate horizontally.
// cin1: Carry-in to horizontal carry chain
// cin2: Carry-in into bit 0 of the carry output vector (+2 total for dual-rail ~Y)
// ==============================================================================
`timescale 1ns / 1ps

module compressor_4_2 #(
    parameter WIDTH = 16
)(
    input  wire [WIDTH-1:0] xc,
    input  wire [WIDTH-1:0] xs,
    input  wire [WIDTH-1:0] yc,
    input  wire [WIDTH-1:0] ys,
    input  wire             cin1, // Carry-in to FA1 horizontal chain
    input  wire             cin2, // Carry-in into FA2 carry vector bit 0
    output wire [WIDTH-1:0] nc,
    output wire [WIDTH-1:0] ns,
    output wire             cout
);
    wire [WIDTH:0] c_horiz;
    assign c_horiz[0] = cin1;

    wire [WIDTH-1:0] final_s;
    wire [WIDTH-1:0] final_c;

    genvar i;
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin : bit_slice
            wire sum1;
            wire cout1;

            // FA1: compresses xs, ys, yc
            assign sum1  = xs[i] ^ ys[i] ^ yc[i];
            assign cout1 = (xs[i] & ys[i]) | (ys[i] & yc[i]) | (xs[i] & yc[i]);

            // FA2: compresses sum1, xc, and horizontal carry from lower bit
            assign final_s[i] = sum1 ^ xc[i] ^ c_horiz[i];
            assign final_c[i] = (sum1 & xc[i]) | (c_horiz[i] & (sum1 ^ xc[i]));

            assign c_horiz[i+1] = cout1;
        end
    endgenerate

    assign cout = c_horiz[WIDTH];

    // ns has weight 2^i
    assign ns = final_s;

    // final_c[i] has weight 2^{i+1}. In nc:
    // nc[0] gets cin2 (weight 2^0)
    // nc[i] gets final_c[i-1] (weight 2^i)
    assign nc = {final_c[WIDTH-2:0], cin2};

endmodule
