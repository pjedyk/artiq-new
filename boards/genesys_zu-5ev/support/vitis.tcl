cd [file dirname [info script]]
setws [pwd]/vitis-ws

if {[catch {platform active hw_pf}]} {
    repo -set [pwd]/embeddedsw
    platform create -name hw_pf -hw [pwd]/system_wrapper.xsa -proc psu_cortexa53_0 -os standalone
}

if {[catch {app report app}]} {
    app create -name app -platform hw_pf -domain standalone_domain -template "Empty Application(C)"
    app config -name app -add compiler-misc "-g -Og -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Wfatal-errors"
    app config -name app -add library-search-path "[pwd]/target/aarch64-unknown-none/debug"
    app config -name app -add libraries rust_firmware
}

importsources -name app -path [pwd]/src
app build -all
