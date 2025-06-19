proc create_migen_bd_cell {vlnv name} {
    create_bd_cell -vlnv $vlnv $name
    source [file dirname [info script]]/$name.properties.tcl
    file mkdir $name
    report_property -all -file $name/properties.txt [get_bd_cells $name]

    set fp [open $name/pins.txt w]
    foreach pin [get_bd_pins $name/*] {
        set pin_name [get_property NAME $pin]
        set pin_intf [get_property INTF $pin]
        puts $fp $pin_name
        report_property -all -file $name/pins.$pin_name.txt $pin
        if !$pin_intf {
            make_bd_pins_external $pin
        }
    }
    close $fp

    set fp [open $name/intf_pins.txt w]
    foreach intf_pin [get_bd_intf_pins $name/*] {
        set intf_pin_name [get_property NAME $intf_pin]
        puts $fp $intf_pin_name
        report_property -all -file $name/intf_pins.$intf_pin_name.txt $intf_pin
        make_bd_intf_pins_external $intf_pin
    }
    close $fp

    assign_bd_address
    set fp [open $name/addr_segs.txt w]
    foreach addr_seg [get_bd_addr_segs $name/*] {
        set addr_seg_name [get_property NAME $addr_seg]
        puts $fp $addr_seg_name
        report_property -all -file $name/addr_segs.$addr_seg_name.txt $addr_seg
    }
    close $fp
}

proc export_migen_conf {} {
    set fp [open mi_part.txt w]
        puts $fp [get_property PART [current_project]]
    close $fp

    set fp [open mi_bd_cells.txt w]
    foreach bd_cell [get_bd_cells] {
        set bd_cell_name [get_property NAME $bd_cell]
        puts $fp $bd_cell_name
    }
    close $fp

    ipx::package_project -import_files
    set fp [open mi_xci_files.txt w]
    foreach xci_file [glob -directory [get_property ROOT_DIRECTORY [ipx::current_core]] */*/*.xci] {
        puts $fp $xci_file
    }
    close $fp
}
