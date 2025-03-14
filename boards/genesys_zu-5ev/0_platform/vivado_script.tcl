source [file dirname [info script]]/migen_integration.tcl

create_project -force -part xczu5ev-sfvc784-1-e platform vivado-proj

create_bd_design platform
create_migen_bd_cell xilinx.com:ip:zynq_ultra_ps_e zynq_ultra_ps_e_0
save_bd_design

generate_target all [get_files platform.bd]
make_wrapper -top -import [get_files platform.bd]
export_migen_conf
write_hw_platform -fixed -force platform.xsa
