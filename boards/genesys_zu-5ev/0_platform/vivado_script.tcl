create_project -force -part xczu5ev-sfvc784-1-e platform vivado-proj
create_bd_design platform

create_bd_cell -vlnv xilinx.com:ip:zynq_ultra_ps_e zynq_ultra_ps_e_0
source [file dirname [info script]]/zynq_ultra_ps_e_0.properties.tcl
report_property -all -file zynq_ultra_ps_e_0.properties.txt [get_bd_cells zynq_ultra_ps_e_0]

set fp [open "zynq_ultra_ps_e_0.pins.txt" w]
foreach pin [get_bd_pins zynq_ultra_ps_e_0/*] {
    make_bd_pins_external $pin
    puts $fp [format "%-20s %s" [get_property NAME $pin] [get_property DIR $pin]]
}
close $fp

save_bd_design
generate_target all [get_files platform.bd]
make_wrapper -top -import [get_files platform.bd]
file copy -force -- vivado-proj/platform.srcs/sources_1/bd/platform/ip/platform_zynq_ultra_ps_e_0_0/platform_zynq_ultra_ps_e_0_0.xci .
write_hw_platform -fixed -force platform.xsa
