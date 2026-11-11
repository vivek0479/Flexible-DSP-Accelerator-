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
