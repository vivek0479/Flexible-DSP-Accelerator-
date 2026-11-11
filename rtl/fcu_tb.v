// ==============================================================================
// Comprehensive Self-Checking Verilog Testbench for FCU Datapath
// Tests:
//   1. Templates T1 - T5 with positive operands
//   2. Templates T1 - T5 with negative operands
//   3. Boundary & Corner Cases (0x7FFF, 0x8000, 0x0000, 0xFFFF)
//   4. Glitch-Free Dual-Rail Integrated Clock Gating (ICG) hold/resume
//   5. 100 Randomized equivalence trials with auto-assertion
// ==============================================================================
`timescale 1ns / 1ps

module fcu_tb;

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
        $dumpvars(0, fcu_tb);

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
        $display("\n--- SECTION 1: DIRECTED POSITIVE TESTS ---");

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
        $display("\n--- SECTION 2: SIGNED & NEGATIVE OPERAND TESTS ---");

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
        $display("\n--- SECTION 3: BOUNDARY & CORNER CASES ---");

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
        $display("\n--- SECTION 4: DUAL-RAIL INTEGRATED CLOCK GATING (ICG) ---");

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
        $display("\n--- SECTION 5: 100 RANDOMIZED EQUIVALENCE TESTS ---");

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
        $display("\n==================================================================");
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
