set_property -dict [list \
    CONFIG.PSU__USE__M_AXI_GP0 0 \
    CONFIG.PSU__USE__M_AXI_GP1 0 \
    CONFIG.PSU__USE__M_AXI_GP2 1 \
] [get_bd_cells zynq_ultra_ps_e_0]
