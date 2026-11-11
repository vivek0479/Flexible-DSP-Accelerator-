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
