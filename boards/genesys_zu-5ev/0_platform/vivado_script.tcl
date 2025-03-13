create_project -force -part xczu5ev-sfvc784-1-e platform vivado-proj
create_bd_design platform

create_bd_cell -vlnv xilinx.com:ip:zynq_ultra_ps_e zynq_ultra_ps_e_0
source [file dirname [info script]]/zynq_ultra_ps_e_0.properties.tcl
file mkdir zynq_ultra_ps_e_0
report_property -all -file zynq_ultra_ps_e_0/properties.txt [get_bd_cells zynq_ultra_ps_e_0]

set fp [open zynq_ultra_ps_e_0/pins.txt w]
foreach pin [get_bd_pins zynq_ultra_ps_e_0/*] {
    set pin_name [get_property NAME $pin]
    set pin_intf [get_property INTF $pin]
    puts $fp $pin_name
    report_property -all -file zynq_ultra_ps_e_0/pins.$pin_name.txt $pin
    if !$pin_intf {
        make_bd_pins_external $pin
    }
}
close $fp

set fp [open zynq_ultra_ps_e_0/intf_pins.txt w]
foreach intf_pin [get_bd_intf_pins zynq_ultra_ps_e_0/*] {
    set intf_pin_name [get_property NAME $intf_pin]
    puts $fp $intf_pin_name
    report_property -all -file zynq_ultra_ps_e_0/intf_pins.$intf_pin_name.txt $intf_pin
    make_bd_intf_pins_external $intf_pin
}
close $fp

assign_bd_address
set fp [open zynq_ultra_ps_e_0/addr_segs.txt w]
foreach addr_seg [get_bd_addr_segs zynq_ultra_ps_e_0/*] {
    set addr_seg_name [get_property NAME $addr_seg]
    puts $fp $addr_seg_name
    report_property -all -file zynq_ultra_ps_e_0/addr_segs.$addr_seg_name.txt $addr_seg
}
close $fp

save_bd_design
generate_target all [get_files platform.bd]
make_wrapper -top -import [get_files platform.bd]
file copy -force -- [get_files platform_zynq_ultra_ps_e_0_0.xci] .
write_hw_platform -fixed -force platform.xsa
