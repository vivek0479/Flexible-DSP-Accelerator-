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

// ==============================================================================
// 3. Direct Carry-Save to Modified Booth (CS-to-MB) Recoder
// Directly recodes Carry-Save operand P* = {PC, PS} into 8 Radix-4 Modified Booth digits
// without any prior Carry-Propagate Addition (CPA).
// Output digits: {-2, -1, 0, +1, +2} represented as one-hot controls.
// ==============================================================================
`timescale 1ns / 1ps

module cs_to_mb_recoder #(
    parameter WIDTH = 16,
    parameter NUM_DIGITS = 8
)(
    input  wire [WIDTH-1:0] pc,
    input  wire [WIDTH-1:0] ps,
    output wire [NUM_DIGITS-1:0] digit_one,
    output wire [NUM_DIGITS-1:0] digit_two,
    output wire [NUM_DIGITS-1:0] digit_neg,
    output wire [NUM_DIGITS-1:0] digit_zero
);
    // Sign-extended inputs for 2's complement arithmetic
    wire [WIDTH+1:0] pc_ext = {{2{pc[WIDTH-1]}}, pc};
    wire [WIDTH+1:0] ps_ext = {{2{ps[WIDTH-1]}}, ps};

    // Carry transfers between radix-4 digit stages
    wire [3*(NUM_DIGITS+1)-1:0] c_transfer;
    assign c_transfer[2:0] = 3'b000;

    genvar i;
    generate
        for (i = 0; i < NUM_DIGITS; i = i + 1) begin : digit_gen
            wire pc_0 = pc_ext[2*i];
            wire ps_0 = ps_ext[2*i];
            wire pc_1 = pc_ext[2*i+1];
            wire ps_1 = ps_ext[2*i+1];
            wire [2:0] c_in_i = c_transfer[3*i +: 3];

            wire [3:0] val_i = (2 * (pc_1 + ps_1)) + (pc_0 + ps_0) + c_in_i;

            reg [2:0] cout_next;
            reg one_r, two_r, neg_r, zero_r;

            always @(*) begin
                case (val_i)
                    4'd0: begin one_r = 1'b0; two_r = 1'b0; neg_r = 1'b0; zero_r = 1'b1; cout_next = 3'd0; end
                    4'd1: begin one_r = 1'b1; two_r = 1'b0; neg_r = 1'b0; zero_r = 1'b0; cout_next = 3'd0; end
                    4'd2: begin one_r = 1'b0; two_r = 1'b1; neg_r = 1'b0; zero_r = 1'b0; cout_next = 3'd0; end
                    4'd3: begin one_r = 1'b1; two_r = 1'b0; neg_r = 1'b1; zero_r = 1'b0; cout_next = 3'd1; end
                    4'd4: begin one_r = 1'b0; two_r = 1'b0; neg_r = 1'b0; zero_r = 1'b1; cout_next = 3'd1; end
                    4'd5: begin one_r = 1'b1; two_r = 1'b0; neg_r = 1'b0; zero_r = 1'b0; cout_next = 3'd1; end
                    4'd6: begin one_r = 1'b0; two_r = 1'b1; neg_r = 1'b0; zero_r = 1'b0; cout_next = 3'd1; end
                    4'd7: begin one_r = 1'b1; two_r = 1'b0; neg_r = 1'b1; zero_r = 1'b0; cout_next = 3'd2; end
                    4'd8: begin one_r = 1'b0; two_r = 1'b0; neg_r = 1'b0; zero_r = 1'b1; cout_next = 3'd2; end
                    default: begin one_r = 1'b0; two_r = 1'b0; neg_r = 1'b0; zero_r = 1'b1; cout_next = 3'd0; end
                endcase
            end

            assign c_transfer[3*(i+1) +: 3] = cout_next;
            assign digit_one[i]  = one_r;
            assign digit_two[i]  = two_r;
            assign digit_neg[i]  = neg_r;
            assign digit_zero[i] = zero_r;
        end
    endgenerate

endmodule

// ==============================================================================
// 4. CSA Tree Multiplier with Structural Wallace/Dadda Reduction & Operand Fusion
// Multiplies signed multiplicand A by CS operand P*, fusing external CS addend
// ext_addend* = {ext_c, ext_s} directly into the Carry-Save tree with ZERO CPA!
//
// Reduction Tree Structure:
//   Level 1: Two 4:2 compressors reduce 8 Booth partial products (PP0-PP7) to 4 vectors.
//   Level 2: One 4:2 compressor reduces the 4 vectors to 2 vectors (pure multiplication product).
//   Level 3: One 4:2 compressor fuses {ext_c, ext_s} directly into the tree to produce
//            genuine dual-rail Carry-Save outputs W* = {wc, ws}.
// ==============================================================================
`timescale 1ns / 1ps

module csa_tree_multiplier #(
    parameter WIDTH = 16,
    parameter NUM_DIGITS = 8
)(
    input  wire signed [WIDTH-1:0] a_in,
    input  wire        [WIDTH-1:0] pc,
    input  wire        [WIDTH-1:0] ps,
    input  wire        [WIDTH-1:0] ext_c,
    input  wire        [WIDTH-1:0] ext_s,
    input  wire                    has_ext,
    input  wire                    sub_ext,
    output wire        [WIDTH-1:0] wc,
    output wire        [WIDTH-1:0] ws
);
    wire [NUM_DIGITS-1:0] d_one, d_two, d_neg, d_zero;

    // Radix-4 CS-to-MB recoder
    cs_to_mb_recoder #(
        .WIDTH(WIDTH),
        .NUM_DIGITS(NUM_DIGITS)
    ) u_recoder (
        .pc(pc),
        .ps(ps),
        .digit_one(d_one),
        .digit_two(d_two),
        .digit_neg(d_neg),
        .digit_zero(d_zero)
    );

    // Generation of 16-bit partial products
    function [WIDTH-1:0] gen_pp;
        input signed [WIDTH-1:0] a;
        input zero_b, one_b, two_b, neg_b;
        input integer shift_b;
        reg signed [WIDTH-1:0] cand;
        begin
            if (zero_b)
                cand = {WIDTH{1'b0}};
            else if (two_b)
                cand = neg_b ? -(a <<< 1) : (a <<< 1);
            else if (one_b)
                cand = neg_b ? -a : a;
            else
                cand = {WIDTH{1'b0}};
            gen_pp = cand <<< shift_b;
        end
    endfunction

    wire [WIDTH-1:0] pp0 = gen_pp(a_in, d_zero[0], d_one[0], d_two[0], d_neg[0], 0);
    wire [WIDTH-1:0] pp1 = gen_pp(a_in, d_zero[1], d_one[1], d_two[1], d_neg[1], 2);
    wire [WIDTH-1:0] pp2 = gen_pp(a_in, d_zero[2], d_one[2], d_two[2], d_neg[2], 4);
    wire [WIDTH-1:0] pp3 = gen_pp(a_in, d_zero[3], d_one[3], d_two[3], d_neg[3], 6);
    wire [WIDTH-1:0] pp4 = gen_pp(a_in, d_zero[4], d_one[4], d_two[4], d_neg[4], 8);
    wire [WIDTH-1:0] pp5 = gen_pp(a_in, d_zero[5], d_one[5], d_two[5], d_neg[5], 10);
    wire [WIDTH-1:0] pp6 = gen_pp(a_in, d_zero[6], d_one[6], d_two[6], d_neg[6], 12);
    wire [WIDTH-1:0] pp7 = gen_pp(a_in, d_zero[7], d_one[7], d_two[7], d_neg[7], 14);

    // -------------------------------------------------------------------------
    // Level 1: Compress 8 Booth partial products to 4 vectors
    // -------------------------------------------------------------------------
    wire [WIDTH-1:0] l1_c_a, l1_s_a;
    wire [WIDTH-1:0] l1_c_b, l1_s_b;
    wire             cout_l1_a, cout_l1_b;

    compressor_4_2 #(.WIDTH(WIDTH)) u_comp_tree_l1_a (
        .xc(pp0), .xs(pp1), .yc(pp2), .ys(pp3),
        .cin1(1'b0), .cin2(1'b0),
        .nc(l1_c_a), .ns(l1_s_a), .cout(cout_l1_a)
    );

    compressor_4_2 #(.WIDTH(WIDTH)) u_comp_tree_l1_b (
        .xc(pp4), .xs(pp5), .yc(pp6), .ys(pp7),
        .cin1(1'b0), .cin2(1'b0),
        .nc(l1_c_b), .ns(l1_s_b), .cout(cout_l1_b)
    );

    // -------------------------------------------------------------------------
    // Level 2: Compress 4 vectors to 2 vectors (Multiplication Product in CS form)
    // -------------------------------------------------------------------------
    wire [WIDTH-1:0] l2_c, l2_s;
    wire             cout_l2;

    compressor_4_2 #(.WIDTH(WIDTH)) u_comp_tree_l2 (
        .xc(l1_c_a), .xs(l1_s_a), .yc(l1_c_b), .ys(l1_s_b),
        .cin1(1'b0), .cin2(1'b0),
        .nc(l2_c), .ns(l2_s), .cout(cout_l2)
    );

    // -------------------------------------------------------------------------
    // Level 3: External Operand Fusion (fusing {ext_c, ext_s} without CPA)
    // -------------------------------------------------------------------------
    wire [WIDTH-1:0] ext_c_mux = !has_ext ? {WIDTH{1'b0}} : (sub_ext ? ~ext_c : ext_c);
    wire [WIDTH-1:0] ext_s_mux = !has_ext ? {WIDTH{1'b0}} : (sub_ext ? ~ext_s : ext_s);
    wire             ext_cin1  = has_ext & sub_ext;
    wire             ext_cin2  = has_ext & sub_ext;
    wire             cout_l3;

    compressor_4_2 #(.WIDTH(WIDTH)) u_comp_tree_l3_fusion (
        .xc(l2_c), .xs(l2_s),
        .yc(ext_c_mux), .ys(ext_s_mux),
        .cin1(ext_cin1), .cin2(ext_cin2),
        .nc(wc), .ns(ws), .cout(cout_l3)
    );

endmodule

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

// ==============================================================================
// 6. Top-Level Flexible Computational Unit (FCU)
// Implements Templates T1 - T5 from IEEE TVLSI 2016:
//   T1: W* = A * (X* + Y*) + K*
//   T2: W* = A * (X* - Y*) + K*
//   T3: W* = A * K* + (X* + Y*)
//   T4: W* = A * K* + (X* - Y*)
//   T5: W* = A * K*
// Features: Integrated Clock Gating (ICG), 4:2 Compressor, CS-to-MB Recoder,
//           CSA Tree Multiplier with operand fusion, and boundary CStoBin.
// ==============================================================================
`timescale 1ns / 1ps

module fcu_top #(
    parameter WIDTH = 16
)(
    input  wire                    clk,
    input  wire                    rst_n,
    input  wire                    clk_gate_en,  // Integrated Clock Gating Enable
    input  wire [2:0]              template_sel, // 3'd1: T1, 3'd2: T2, 3'd3: T3, 3'd4: T4, 3'd5: T5
    input  wire signed [WIDTH-1:0] a_in,         // 16-bit 2's complement multiplicand
    input  wire [WIDTH-1:0]        xc_in,        // Carry vector of X*
    input  wire [WIDTH-1:0]        xs_in,        // Sum vector of X*
    input  wire [WIDTH-1:0]        yc_in,        // Carry vector of Y*
    input  wire [WIDTH-1:0]        ys_in,        // Sum vector of Y*
    input  wire [WIDTH-1:0]        kc_in,        // Carry vector of K*
    input  wire [WIDTH-1:0]        ks_in,        // Sum vector of K*
    output reg  [WIDTH-1:0]        wc_out,       // Output Carry vector
    output reg  [WIDTH-1:0]        ws_out,       // Output Sum vector
    output wire signed [WIDTH-1:0] bin_out       // Final binary output from CStoBin
);

    // Clock Gating Cell
    wire gated_clk;
    icg_cell u_icg (
        .clk(clk),
        .clk_gate_en(clk_gate_en),
        .gated_clk(gated_clk)
    );

    // Control signals decoded from template
    reg cl0, cl1, cl2, cl3, has_ext;

    always @(*) begin
        case (template_sel)
            3'd1: begin cl0 = 1'b0; cl1 = 1'b0; cl2 = 1'b0; cl3 = 1'b0; has_ext = 1'b1; end // T1
            3'd2: begin cl0 = 1'b1; cl1 = 1'b0; cl2 = 1'b0; cl3 = 1'b0; has_ext = 1'b1; end // T2
            3'd3: begin cl0 = 1'b0; cl1 = 1'b1; cl2 = 1'b1; cl3 = 1'b0; has_ext = 1'b1; end // T3
            3'd4: begin cl0 = 1'b1; cl1 = 1'b1; cl2 = 1'b1; cl3 = 1'b0; has_ext = 1'b1; end // T4
            3'd5: begin cl0 = 1'b0; cl1 = 1'b1; cl2 = 1'b0; cl3 = 1'b0; has_ext = 1'b0; end // T5
            default: begin cl0 = 1'b0; cl1 = 1'b0; cl2 = 1'b0; cl3 = 1'b0; has_ext = 1'b0; end
        endcase
    end

    // MUX0: select Y* or ~Y* (for subtraction)
    wire [WIDTH-1:0] yc_mux = cl0 ? ~yc_in : yc_in;
    wire [WIDTH-1:0] ys_mux = cl0 ? ~ys_in : ys_in;
    wire cin1_42 = cl0; // Carry-in to FA1 chain
    wire cin2_42 = cl0; // Carry-in into FA2 carry output bit 0 (+2 total for dual-rail ~Y*)

    // 4:2 Carry-Save Compressor / Adder
    wire [WIDTH-1:0] nc, ns;
    wire cout_42;
    compressor_4_2 #(
        .WIDTH(WIDTH)
    ) u_comp42 (
        .xc(xc_in),
        .xs(xs_in),
        .yc(yc_mux),
        .ys(ys_mux),
        .cin1(cin1_42),
        .cin2(cin2_42),
        .nc(nc),
        .ns(ns),
        .cout(cout_42)
    );

    // MUX1: Select multiplier operand P* (0 -> N*, 1 -> K*)
    wire [WIDTH-1:0] pc = cl1 ? kc_in : nc;
    wire [WIDTH-1:0] ps = cl1 ? ks_in : ns;

    // MUX2: Select external addend fused into CSA Tree (0 -> K*, 1 -> N*)
    wire [WIDTH-1:0] ext_c = cl2 ? nc : kc_in;
    wire [WIDTH-1:0] ext_s = cl2 ? ns : ks_in;

    // CSA Tree Multiplier with Operand Fusion
    wire [WIDTH-1:0] mult_wc, mult_ws;
    csa_tree_multiplier #(
        .WIDTH(WIDTH)
    ) u_csa_mult (
        .a_in(a_in),
        .pc(pc),
        .ps(ps),
        .ext_c(ext_c),
        .ext_s(ext_s),
        .has_ext(has_ext),
        .sub_ext(cl3),
        .wc(mult_wc),
        .ws(mult_ws)
    );

    // Registered Carry-Save outputs (clock gated)
    always @(posedge gated_clk or negedge rst_n) begin
        if (!rst_n) begin
            wc_out <= {WIDTH{1'b0}};
            ws_out <= {WIDTH{1'b0}};
        end else begin
            wc_out <= mult_wc;
            ws_out <= mult_ws;
        end
    end

    // Boundary CPA: Converts final CS pair {wc_out, ws_out} to binary Two's Complement
    cs_to_bin #(
        .WIDTH(WIDTH)
    ) u_csto_bin (
        .wc(wc_out),
        .ws(ws_out),
        .bin_out(bin_out)
    );

endmodule
