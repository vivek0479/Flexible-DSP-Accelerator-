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
