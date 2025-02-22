module simple_axi_slave #(
    parameter C_S_AXI_DATA_WIDTH = 32,
    parameter C_S_AXI_ADDR_WIDTH = 4
) (
    input wire S_AXI_ACLK,
    input wire S_AXI_ARESETN,

    input wire [C_S_AXI_ADDR_WIDTH-1:0] S_AXI_ARADDR,
    input wire S_AXI_ARVALID,
    output wire S_AXI_ARREADY,

    output wire [C_S_AXI_DATA_WIDTH-1:0] S_AXI_RDATA,
    output wire [1:0] S_AXI_RRESP,
    output wire S_AXI_RVALID,
    input wire S_AXI_RREADY,

    input wire [C_S_AXI_ADDR_WIDTH-1:0] S_AXI_AWADDR,
    input wire S_AXI_AWVALID,
    output wire S_AXI_AWREADY,

    input wire [C_S_AXI_DATA_WIDTH-1:0] S_AXI_WDATA,
    input wire [(C_S_AXI_DATA_WIDTH/8)-1:0] S_AXI_WSTRB,
    input wire S_AXI_WVALID,
    output wire S_AXI_WREADY,

    output wire [1:0] S_AXI_BRESP,
    output wire S_AXI_BVALID,
    input wire S_AXI_BREADY
);

    localparam CONSTANT_VALUE = 32'hDCBA4321;

    reg axi_rvalid;
    reg [C_S_AXI_DATA_WIDTH-1:0] axi_rdata;

    assign S_AXI_ARREADY = 1'b1;
    assign S_AXI_RRESP = 2'b00;

    assign S_AXI_RVALID = axi_rvalid;
    assign S_AXI_RDATA = axi_rdata;

    always @(posedge S_AXI_ACLK) begin
        if (S_AXI_ARESETN == 1'b0) begin
            axi_rvalid <= 1'b0;
            axi_rdata <= 32'b0;
        end else begin
            if (S_AXI_ARVALID && S_AXI_ARREADY && !axi_rvalid) begin
                axi_rvalid <= 1'b1;
                axi_rdata <= CONSTANT_VALUE;
            end else if (S_AXI_RREADY && axi_rvalid) begin
                axi_rvalid <= 1'b0;
            end
        end
    end

    assign S_AXI_AWREADY = 1'b1;
    assign S_AXI_WREADY = 1'b1;
    assign S_AXI_BRESP = 2'b00;
    assign S_AXI_BVALID = S_AXI_WVALID && S_AXI_WREADY;

endmodule
