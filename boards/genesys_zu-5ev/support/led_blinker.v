module led_blinker (
    input wire clk,
    output reg [3:0] leds
);
    parameter COUNT_MAX = 50000000;

    reg [31:0] counter;
    reg [1:0] pattern;

    always @(posedge clk) begin
        if (counter == COUNT_MAX - 1) begin
            counter <= 32'b0;
            pattern <= pattern + 1'b1;
        end else begin
            counter <= counter + 1'b1;
        end
    end

    always @(*) begin
        case (pattern)
            2'b00: leds = 4'b0001;
            2'b01: leds = 4'b0010;
            2'b10: leds = 4'b0100;
            2'b11: leds = 4'b1000;
            default: leds = 4'b0000;
        endcase
    end

endmodule
