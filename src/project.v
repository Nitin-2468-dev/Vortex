
`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,
    output reg  [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    // Full-width operands stored inside the ASIC.
    reg signed [15:0] a_reg;
    reg signed [15:0] b_reg;

    wire signed [31:0] product;

    // The bidirectional pins are inputs for this first version.
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // Your Amaranth-generated multiplier.
    Clocked_FixedMult mult (
        .a       (a_reg),
        .b       (b_reg),
        .product (product),
        .clk     (clk),
        .rst     (~rst_n)
    );

    // Load operand bytes.
    always @(posedge clk) begin
        if (!rst_n) begin
            a_reg <= 16'sd0;
            b_reg <= 16'sd0;
        end else begin
            case (ui_in)
                8'h10: a_reg[7:0]  <= uio_in;
                8'h11: a_reg[15:8] <= uio_in;

                8'h20: b_reg[7:0]  <= uio_in;
                8'h21: b_reg[15:8] <= uio_in;

                default: begin
                    // No operand change.
                end
            endcase
        end
    end

    // Select which byte of the 32-bit result to read.
    always @* begin
        case (ui_in)
            8'h40: uo_out = product[7:0];
            8'h41: uo_out = product[15:8];
            8'h42: uo_out = product[23:16];
            8'h43: uo_out = product[31:24];
            default: uo_out = 8'h00;
        endcase
    end

    wire _unused = &{ena, 1'b0};

endmodule

`default_nettype wire
