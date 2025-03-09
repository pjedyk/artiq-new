set_param board.repoPaths vivado-boards/new/board_files
create_project -force -part xczu5ev-sfvc784-1-e design vivado-proj
set_property BOARD_PART digilentinc.com:gzu_5ev:part0:1.1 [current_project]
create_bd_design system

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
make_wrapper -top -import [get_files system.bd]
ipx::package_project -import_files
write_hw_platform -fixed -force system.xsa
