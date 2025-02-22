cd [file dirname [info script]]
set_param board.repoPaths [list [pwd]/vivado-boards/new/board_files]

if {[catch {open_project [pwd]/vivado-proj/artiq_zynqmp.xpr}]} {
    create_project -part xczu5ev-sfvc784-1-e artiq_zynqmp [pwd]/vivado-proj
    set_property BOARD_PART digilentinc.com:gzu_5ev:part0:1.1 [current_project]
}
if {[catch {open_bd_design [get_files system.bd]}]} {
    create_bd_design system
}

foreach net [get_bd_nets] {
    delete_bd_objs $net
}
foreach port [get_bd_ports] {
    delete_bd_objs $port
}
foreach cell [get_bd_cells] {
    delete_bd_objs $cell
}

create_bd_port -dir I dp_aux_din
create_bd_port -dir O -from 0 -to 0 dp_aux_doe
create_bd_port -dir O dp_aux_dout
create_bd_port -dir I dp_aux_hotplug_detect

create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic util_vector_logic_0
set_property -dict [list \
    CONFIG.C_OPERATION {not} \
    CONFIG.C_SIZE {1} \
] [get_bd_cell util_vector_logic_0]

create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e zynq_ultra_ps_e_0
source [pwd]/zynq_ultra_ps_e_0_properties.tcl

connect_bd_net -net dp_aux_data_in_0_1 [get_bd_ports dp_aux_din] [get_bd_pins zynq_ultra_ps_e_0/dp_aux_data_in]
connect_bd_net -net dp_hot_plug_detect_0_1 [get_bd_ports dp_aux_hotplug_detect] [get_bd_pins zynq_ultra_ps_e_0/dp_hot_plug_detect]
connect_bd_net -net util_vector_logic_0_Res [get_bd_pins util_vector_logic_0/Res] [get_bd_ports dp_aux_doe]
connect_bd_net -net zynq_ultra_ps_e_0_dp_aux_data_oe_n [get_bd_pins zynq_ultra_ps_e_0/dp_aux_data_oe_n] [get_bd_pins util_vector_logic_0/Op1]
connect_bd_net -net zynq_ultra_ps_e_0_dp_aux_data_out [get_bd_pins zynq_ultra_ps_e_0/dp_aux_data_out] [get_bd_ports dp_aux_dout]
connect_bd_net -net zynq_ultra_ps_e_0_pl_clk0 [get_bd_pins zynq_ultra_ps_e_0/pl_clk0] [get_bd_pins zynq_ultra_ps_e_0/maxihpm0_lpd_aclk] [get_bd_pins zynq_ultra_ps_e_0/saxihpc0_fpd_aclk]

add_files [pwd]/simple_axi_slave.v
create_bd_cell -type module -reference simple_axi_slave simple_axi_0
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { \
   Clk_master {/zynq_ultra_ps_e_0/pl_clk0} \
   Clk_slave {Auto} \
   Clk_xbar {Auto} \
   Master {/zynq_ultra_ps_e_0/M_AXI_HPM0_LPD} \
   Slave {/simple_axi_0/S_AXI} \
   intc_ip {New AXI Interconnect} \
   master_apm {0} \
} [get_bd_intf_pins simple_axi_0/S_AXI]

validate_bd_design
save_bd_design

add_files -fileset [current_fileset -constrset] [pwd]/Genesys_ZU_revC.xdc
add_files [make_wrapper -files [get_files system.bd] -top]
update_compile_order -fileset [current_fileset]

reset_run [current_run -synthesis]
launch_runs [current_run -synthesis] -jobs 3
wait_on_run [current_run -synthesis]
reset_run [current_run]
launch_runs [current_run] -to_step write_bitstream -jobs 3
wait_on_run [current_run]

#write_hw_platform -fixed -include_bit -force -file [pwd]/system_wrapper.xsa

#add_files [pwd]/simple_axi_slave.v
#create_bd_cell -type module -reference simple_axi_slave simple_axi_0
#apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { \
#    Clk_master {/zynq_ultra_ps_e_0/pl_clk0} \
#    Clk_slave {Auto} \
#    Clk_xbar {Auto} \
#    Master {/zynq_ultra_ps_e_0/M_AXI_HPM0_LPD} \
#    Slave {/simple_axi_0/S_AXI} \
#    intc_ip {New AXI Interconnect} \
#    master_apm {0} \
#} [get_bd_intf_pins simple_axi_0/S_AXI]


#generate target ???


#generate_target all [get_files system.bd]
#write_hw_platform -fixed -force [pwd]/system.xsa
