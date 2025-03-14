# System Configuration
set_property -dict [list \
    CONFIG.PSU__USE__IRQ0 {1} \
    CONFIG.PSU__TTC0__PERIPHERAL__ENABLE {1} \
    CONFIG.PSU_BANK_1_IO_STANDARD {LVCMOS18} \
    CONFIG.PSU_BANK_2_IO_STANDARD {LVCMOS18} \
] [get_bd_cells zynq_ultra_ps_e_0]

# Clock Configuration
set_property -dict [list \
    CONFIG.PSU__PSS_REF_CLK__FREQMHZ {30} \
    CONFIG.PSU__CRF_APB__DDR_CTRL__FREQMHZ {1066} \
    CONFIG.PSU__CRF_APB__GDMA_REF_CTRL__SRCSEL {APLL} \
    CONFIG.PSU__CRF_APB__GPU_REF_CTRL__SRCSEL {IOPLL} \
    CONFIG.PSU__CRF_APB__TOPSW_MAIN_CTRL__SRCSEL {DPLL} \
    CONFIG.PSU__CRL_APB__PL0_REF_CTRL__SRCSEL {IOPLL} \
    CONFIG.PSU__CRL_APB__QSPI_REF_CTRL__FREQMHZ {250} \
    CONFIG.PSU__DLL__ISUSED {1} \
] [get_bd_cells zynq_ultra_ps_e_0]

# DDR Configuration
set_property -dict [list \
    CONFIG.PSU_DYNAMIC_DDR_CONFIG_EN {1} \
    CONFIG.PSU__DDR__INTERFACE__FREQMHZ {533.000} \
    CONFIG.PSU__DDRC__COMPONENTS {UDIMM} \
    CONFIG.PSU__DDRC__DEVICE_CAPACITY {4096 MBits} \
    CONFIG.PSU__DDRC__SPEED_BIN {DDR4_2133P} \
    CONFIG.PSU__DDRC__DDR4_ADDR_MAPPING {0} \
    CONFIG.PSU__DDRC__DDR4_T_REF_MODE {1} \
    CONFIG.PSU__DDRC__ROW_ADDR_COUNT {15} \
] [get_bd_cells zynq_ultra_ps_e_0]

# Peripheral - UART
set_property -dict [list \
    CONFIG.PSU__UART0__BAUD_RATE {115200} \
    CONFIG.PSU__UART0__PERIPHERAL__ENABLE {1} \
    CONFIG.PSU__UART0__PERIPHERAL__IO {MIO 18 .. 19} \
] [get_bd_cells zynq_ultra_ps_e_0]

# Peripheral - I2C
set_property -dict [list \
    CONFIG.PSU__I2C0__PERIPHERAL__IO {MIO 22 .. 23} \
    CONFIG.PSU__I2C0__PERIPHERAL__ENABLE {1} \
    CONFIG.PSU__I2C1__PERIPHERAL__IO {MIO 8 .. 9} \
    CONFIG.PSU__I2C1__PERIPHERAL__ENABLE {1} \
] [get_bd_cells zynq_ultra_ps_e_0]

# Peripheral - QSPI
set_property -dict [list \
    CONFIG.PSU__QSPI__PERIPHERAL__ENABLE {1} \
    CONFIG.PSU__QSPI__PERIPHERAL__IO {MIO 0 .. 5} \
    CONFIG.PSU__QSPI__PERIPHERAL__MODE {Single} \
    CONFIG.PSU__QSPI__PERIPHERAL__DATA_MODE {x4} \
    CONFIG.PSU__QSPI__GRP_FBCLK__ENABLE {1} \
    CONFIG.PSU__QSPI__GRP_FBCLK__IO {MIO 6} \
] [get_bd_cells zynq_ultra_ps_e_0]
