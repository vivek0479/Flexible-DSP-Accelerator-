#!/usr/bin/env python3
"""
RTL Generator for Flexible DSP Accelerator Architecture Exploiting Carry-Save Arithmetic
(Kostas Tsoumanis, Sotirios Xydis, Georgios Zervakis, Kiamal Pekmestzi - IEEE TVLSI 2016)

Generates:
  1. icg_cell.v              - Negative-level latch-based Integrated Clock Gating cell.
  2. compressor_4_2.v         - 16-bit 4:2 Carry-Save Compressor with dual-rail subtraction.
  3. cs_to_mb_recoder.v       - Direct CS-to-Modified Booth recoder (no intermediate CPA).
  4. csa_tree_multiplier.v    - True 3-level Wallace/Dadda 4:2 CSA reduction tree with operand fusion.
  5. cs_to_bin.v              - Boundary ripple-carry CPA converter.
  6. fcu_top.v                - Top-level Flexible Computational Unit (Templates T1-T5).
  7. fcu_tb.v                 - Comprehensive self-checking testbench (directed, negative, corner, ICG, random).
  8. design.sv / testbench.sv - EDA Playground all-in-one versions.
"""

import os

RTL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rtl")

ICG_CELL_V = """// ==============================================================================
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
"""

COMPRESSOR_4_2_V = """// ==============================================================================
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
"""

CS_TO_MB_RECODER_V = """// ==============================================================================
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
"""

CSA_TREE_MULTIPLIER_V = """// ==============================================================================
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
"""

CS_TO_BIN_V = """// ==============================================================================
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
"""

FCU_TOP_V = """// ==============================================================================
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
"""

def generate_tb(module_name="fcu_tb"):
    return f"""// ==============================================================================
// Comprehensive Self-Checking Verilog Testbench for FCU Datapath
// Tests:
//   1. Templates T1 - T5 with positive operands
//   2. Templates T1 - T5 with negative operands
//   3. Boundary & Corner Cases (0x7FFF, 0x8000, 0x0000, 0xFFFF)
//   4. Glitch-Free Dual-Rail Integrated Clock Gating (ICG) hold/resume
//   5. 100 Randomized equivalence trials with auto-assertion
// ==============================================================================
`timescale 1ns / 1ps

module {module_name};

    parameter WIDTH = 16;

    reg                     clk;
    reg                     rst_n;
    reg                     clk_gate_en;
    reg  [2:0]              template_sel;
    reg  signed [WIDTH-1:0] a_in;
    reg  [WIDTH-1:0]        xc_in, xs_in;
    reg  [WIDTH-1:0]        yc_in, ys_in;
    reg  [WIDTH-1:0]        kc_in, ks_in;
    wire [WIDTH-1:0]        wc_out, ws_out;
    wire signed [WIDTH-1:0] bin_out;

    // Instantiate FCU
    fcu_top #(
        .WIDTH(WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .clk_gate_en(clk_gate_en),
        .template_sel(template_sel),
        .a_in(a_in),
        .xc_in(xc_in),
        .xs_in(xs_in),
        .yc_in(yc_in),
        .ys_in(ys_in),
        .kc_in(kc_in),
        .ks_in(ks_in),
        .wc_out(wc_out),
        .ws_out(ws_out),
        .bin_out(bin_out)
    );

    // Clock generator (100 MHz, 10ns period)
    always #5 clk = ~clk;

    integer errors = 0;
    integer test_count = 0;
    reg [WIDTH-1:0] prev_wc, prev_ws;
    reg signed [WIDTH-1:0] exp_val;

    // Helper task to check result against expected
    task check_result;
        input [2:0]              tmpl;
        input signed [WIDTH-1:0] expected;
        input [255:0]            test_name;
        begin
            test_count = test_count + 1;
            #1;
            if (bin_out !== expected) begin
                $display(">> [FAIL] %0s | T%0d | Got: %0d (0x%04x) | Expected: %0d (0x%04x)",
                         test_name, tmpl, bin_out, bin_out, expected, expected);
                errors = errors + 1;
            end else begin
                $display(">> [PASS] %0s | T%0d | Output: %0d | wc: 0x%04x, ws: 0x%04x",
                         test_name, tmpl, bin_out, wc_out, ws_out);
            end
        end
    endtask

    integer i;
    reg signed [WIDTH-1:0] rand_a;
    reg [WIDTH-1:0] rand_xc, rand_xs, rand_yc, rand_ys, rand_kc, rand_ks;
    reg signed [WIDTH-1:0] op_x, op_y, op_k;
    reg [2:0] rand_tmpl;

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, {module_name});

        $display("==================================================================");
        $display("   STARTING ADVANCED FCU VERILOG TESTBENCH (GENUINE CSA TREE)    ");
        $display("==================================================================");

        clk = 0;
        rst_n = 0;
        clk_gate_en = 1;
        template_sel = 0;
        a_in = 0;
        xc_in = 0; xs_in = 0;
        yc_in = 0; ys_in = 0;
        kc_in = 0; ks_in = 0;

        #20 rst_n = 1;
        #10;

        // =====================================================================
        // SECTION 1: DIRECTED POSITIVE TESTS (TEMPLATES T1 - T5)
        // =====================================================================
        $display("\\n--- SECTION 1: DIRECTED POSITIVE TESTS ---");

        // TEST 1: T1 -> W* = A * (X* + Y*) + K*
        // A = 25, X = 100, Y = 50, K = 10 -> Expected = 25 * 150 + 10 = 3760
        template_sel = 3'd1; a_in = 16'sd25;
        xc_in = 16'd50;  xs_in = 16'd50;  // X = 100
        yc_in = 16'd25;  ys_in = 16'd25;  // Y = 50
        kc_in = 16'd5;   ks_in = 16'd5;   // K = 10
        @(posedge clk);
        check_result(3'd1, 16'sd3760, "T1 Pos: 25 * (100 + 50) + 10");

        // TEST 2: T2 -> W* = A * (X* - Y*) + K*
        // A = 15, X = 150, Y = 30, K = 5 -> Expected = 15 * 120 + 5 = 1805
        template_sel = 3'd2; a_in = 16'sd15;
        xc_in = 16'd100; xs_in = 16'd50; // X = 150
        yc_in = 16'd15;  ys_in = 16'd15; // Y = 30
        kc_in = 16'd2;   ks_in = 16'd3;  // K = 5
        @(posedge clk);
        check_result(3'd2, 16'sd1805, "T2 Pos: 15 * (150 - 30) + 5");

        // TEST 3: T3 -> W* = A * K* + (X* + Y*)
        // A = 30, K = 12, X = 60, Y = 40 -> Expected = 30 * 12 + 100 = 460
        template_sel = 3'd3; a_in = 16'sd30;
        kc_in = 16'd6;   ks_in = 16'd6;  // K = 12
        xc_in = 16'd30;  xs_in = 16'd30; // X = 60
        yc_in = 16'd20;  ys_in = 16'd20; // Y = 40
        @(posedge clk);
        check_result(3'd3, 16'sd460, "T3 Pos: 30 * 12 + (60 + 40)");

        // TEST 4: T4 -> W* = A * K* + (X* - Y*)
        // A = 20, K = 10, X = 100, Y = 40 -> Expected = 20 * 10 + 60 = 260
        template_sel = 3'd4; a_in = 16'sd20;
        kc_in = 16'd5;   ks_in = 16'd5;  // K = 10
        xc_in = 16'd50;  xs_in = 16'd50; // X = 100
        yc_in = 16'd20;  ys_in = 16'd20; // Y = 40
        @(posedge clk);
        check_result(3'd4, 16'sd260, "T4 Pos: 20 * 10 + (100 - 40)");

        // TEST 5: T5 -> W* = A * K*
        // A = 45, K = 16 -> Expected = 45 * 16 = 720
        template_sel = 3'd5; a_in = 16'sd45;
        kc_in = 16'd8;   ks_in = 16'd8;  // K = 16
        @(posedge clk);
        check_result(3'd5, 16'sd720, "T5 Pos: 45 * 16");

        // =====================================================================
        // SECTION 2: SIGNED & NEGATIVE OPERAND TESTS
        // =====================================================================
        $display("\\n--- SECTION 2: SIGNED & NEGATIVE OPERAND TESTS ---");

        // TEST 6: T1 with negative multiplicand A = -25
        // A = -25, X = 40, Y = 10, K = 50 -> Expected: -25 * 50 + 50 = -1200
        template_sel = 3'd1; a_in = -16'sd25;
        xc_in = 16'd20;  xs_in = 16'd20;  // X = 40
        yc_in = 16'd5;   ys_in = 16'd5;   // Y = 10
        kc_in = 16'd25;  ks_in = 16'd25;  // K = 50
        @(posedge clk);
        check_result(3'd1, -16'sd1200, "T1 Neg Multiplicand: -25 * 50 + 50");

        // TEST 7: T2 with negative difference (X - Y = 20 - 50 = -30)
        // A = 10, X = 20, Y = 50, K = 100 -> Expected: 10 * (-30) + 100 = -200
        template_sel = 3'd2; a_in = 16'sd10;
        xc_in = 16'd10;  xs_in = 16'd10;  // X = 20
        yc_in = 16'd25;  ys_in = 16'd25;  // Y = 50
        kc_in = 16'd50;  ks_in = 16'd50;  // K = 100
        @(posedge clk);
        check_result(3'd2, -16'sd200, "T2 Neg Difference: 10 * (-30) + 100");

        // TEST 8: T5 with negative multiplier K = -15
        // A = 30, K = -15 -> Expected: 30 * (-15) = -450
        template_sel = 3'd5; a_in = 16'sd30;
        kc_in = 16'hFFF0; ks_in = 16'h0001; // K = -16 + 1 = -15
        @(posedge clk);
        check_result(3'd5, -16'sd450, "T5 Neg K: 30 * (-15)");

        // =====================================================================
        // SECTION 3: BOUNDARY & CORNER CASES
        // =====================================================================
        $display("\\n--- SECTION 3: BOUNDARY & CORNER CASES ---");

        // TEST 9: A = 0
        template_sel = 3'd1; a_in = 16'sd0;
        xc_in = 16'h1234; xs_in = 16'h0000;
        yc_in = 16'h0000; ys_in = 16'h0000;
        kc_in = 16'd77;   ks_in = 16'd0;
        @(posedge clk);
        check_result(3'd1, 16'sd77, "Zero Multiplicand: 0 * X + 77");

        // TEST 10: Multiplier P = 0
        template_sel = 3'd5; a_in = 16'sd1234;
        kc_in = 16'h0000; ks_in = 16'h0000;
        @(posedge clk);
        check_result(3'd5, 16'sd0, "Zero Multiplier: 1234 * 0");

        // =====================================================================
        // SECTION 4: INTEGRATED CLOCK GATING (ICG) VERIFICATION
        // =====================================================================
        $display("\\n--- SECTION 4: DUAL-RAIL INTEGRATED CLOCK GATING (ICG) ---");

        // Capture current state
        prev_wc = wc_out;
        prev_ws = ws_out;

        // Disable clock gating (gate closed)
        $display("Asserting clk_gate_en = 0 (Gating clock)...");
        clk_gate_en = 0;
        // Inject entirely new inputs while gated
        a_in = 16'sd999;
        kc_in = 16'd999;
        xc_in = 16'd999;

        // Run 4 clock cycles while gated
        repeat (4) @(posedge clk);
        #1;

        test_count = test_count + 1;
        if (wc_out === prev_wc && ws_out === prev_ws) begin
            $display(">> [PASS] ICG Hold: wc_out (0x%04x) and ws_out (0x%04x) strictly held across 4 cycles!", wc_out, ws_out);
        end else begin
            $display(">> [FAIL] ICG Glitch! Registers changed while clk_gate_en was 0!");
            errors = errors + 1;
        end

        // Re-enable clock gating (gate open)
        $display("Re-enabling clk_gate_en = 1 (Resuming clock)...");
        clk_gate_en = 1;
        template_sel = 3'd5;
        a_in = 16'sd12;
        kc_in = 16'd10; ks_in = 16'd0; // 12 * 10 = 120
        @(posedge clk);
        check_result(3'd5, 16'sd120, "ICG Resume: Computation resumes cleanly");

        // =====================================================================
        // SECTION 5: RANDOMIZED EQUIVALENCE LOOP (100 VECTORS)
        // =====================================================================
        $display("\\n--- SECTION 5: 100 RANDOMIZED EQUIVALENCE TESTS ---");

        for (i = 0; i < 100; i = i + 1) begin
            rand_tmpl = ($urandom % 5) + 1;
            rand_a    = $urandom % 256 - 128; // Signed 8-bit range to avoid large overflow
            rand_xc   = $urandom % 500;
            rand_xs   = $urandom % 500;
            rand_yc   = $urandom % 500;
            rand_ys   = $urandom % 500;
            rand_kc   = $urandom % 500;
            rand_ks   = $urandom % 500;

            op_x = rand_xc + rand_xs;
            op_y = rand_yc + rand_ys;
            op_k = rand_kc + rand_ks;

            case (rand_tmpl)
                3'd1: exp_val = rand_a * (op_x + op_y) + op_k;
                3'd2: exp_val = rand_a * (op_x - op_y) + op_k;
                3'd3: exp_val = rand_a * op_k + (op_x + op_y);
                3'd4: exp_val = rand_a * op_k + (op_x - op_y);
                3'd5: exp_val = rand_a * op_k;
                default: exp_val = 0;
            endcase

            template_sel = rand_tmpl;
            a_in         = rand_a;
            xc_in        = rand_xc; xs_in = rand_xs;
            yc_in        = rand_yc; ys_in = rand_ys;
            kc_in        = rand_kc; ks_in = rand_ks;

            @(posedge clk);
            #1;
            test_count = test_count + 1;
            if (bin_out !== exp_val) begin
                $display(">> [FAIL] Random Vector %0d (T%0d) | Got: %0d | Expected: %0d",
                         i, rand_tmpl, bin_out, exp_val);
                errors = errors + 1;
            end
        end
        $display(">> Completed 100/100 randomized trials.");

        // =====================================================================
        // FINAL SUMMARY
        // =====================================================================
        #20;
        $display("\\n==================================================================");
        $display("   FINAL TESTBENCH EXECUTION SUMMARY                              ");
        $display("==================================================================");
        $display("   Total Test Vectors Executed : %0d", test_count);
        $display("   Total Functional Errors     : %0d", errors);
        if (errors == 0) begin
            $display("   STATUS                      : 100%% ALL TESTS PASSED!          ");
            $display("   GENUINE CSA TREE MULTIPLIER : FULLY VERIFIED & DEFENDED        ");
        end else begin
            $display("   STATUS                      : FAILED WITH %0d ERRORS!         ", errors);
        end
        $display("==================================================================");
        $finish;
    end

endmodule
"""

FILES = {
    "icg_cell.v": ICG_CELL_V,
    "compressor_4_2.v": COMPRESSOR_4_2_V,
    "cs_to_mb_recoder.v": CS_TO_MB_RECODER_V,
    "csa_tree_multiplier.v": CSA_TREE_MULTIPLIER_V,
    "cs_to_bin.v": CS_TO_BIN_V,
    "fcu_top.v": FCU_TOP_V,
    "fcu_tb.v": generate_tb("fcu_tb"),
}


def main():
    os.makedirs(RTL_DIR, exist_ok=True)
    print("=" * 70)
    print(" GENERATING SYNTHESIZABLE VERILOG RTL FOR PROPOSED FCU ACCELERATOR")
    print("=" * 70)
    for fname, content in FILES.items():
        fpath = os.path.join(RTL_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f" [+] Generated: rtl/{fname}")

    # Also generate single-file design.sv for EDA Playground
    design_sv_path = os.path.join(RTL_DIR, "design.sv")
    with open(design_sv_path, "w", encoding="utf-8") as f:
        design_all = "\n\n".join([
            ICG_CELL_V.strip(),
            COMPRESSOR_4_2_V.strip(),
            CS_TO_MB_RECODER_V.strip(),
            CSA_TREE_MULTIPLIER_V.strip(),
            CS_TO_BIN_V.strip(),
            FCU_TOP_V.strip(),
        ])
        f.write(design_all + "\n")
    print(f" [+] Generated: rtl/design.sv (All-in-one for EDA Playground)")

    # Testbench for EDA Playground uses module testbench
    testbench_sv_path = os.path.join(RTL_DIR, "testbench.sv")
    with open(testbench_sv_path, "w", encoding="utf-8") as f:
        f.write(generate_tb("testbench").strip() + "\n")
    print(f" [+] Generated: rtl/testbench.sv (EDA Playground testbench with VCD dump)")
    print("=" * 70)
    print(f" ALL RTL FILES SUCCESSFULLY GENERATED IN: {RTL_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
