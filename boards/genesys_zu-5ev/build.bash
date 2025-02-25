#! /usr/bin/env bash

set -e || exit

T="/${0}" T="${T%/*}" T="${T#/}" T="${T:-.}"
T="$( cd -- "${T}" && pwd -- )"

[[ "${#}" -eq 0 ]] || declare -x -- "${@}"

env -C"${T}/firmware" -- cargo build --

BUILD_DIR="${BUILD_DIR:-"${T}/build"}"
XILINX_VIVADO="${XILINX_VIVADO:-"/opt/Xilinx/Vivado/2024.2"}"
XILINX_VITIS="${XILINX_VITIS:-"/opt/Xilinx/Vitis/2024.2"}"

mkdir -p -- "${BUILD_DIR}/src"
ln -fns -t"${BUILD_DIR}" -- \
    "${T}/vivado-boards" \
    "${T}/embeddedsw" \
    "${T}/firmware/target"
cp -f -t"${BUILD_DIR}" -- \
    "${T}/support/vivado.tcl" \
    "${T}/support/zynq_ultra_ps_e_0_properties.tcl" \
    "${T}/support/simple_axi_slave.v" \
    "${T}/support/led_blinker.v" \
    "${T}/support/Genesys_ZU_revC.xdc" \
    "${T}/support/vitis.tcl" \
    "${T}/support/system_wrapper.xsa" \
    "${T}/support/boot.bif"
cp -f -t"${BUILD_DIR}/src" -- \
    "${T}/firmware/src/boot.c"

(   source -- "${XILINX_VIVADO}/settings64.sh"
    env -C"${BUILD_DIR}" -- vivado -mode batch -script vivado.tcl
)

(   source -- "${XILINX_VITIS}/settings64.sh"
    env -C"${BUILD_DIR}" -- xsct vitis.tcl
    env -C"${BUILD_DIR}" -- bootgen -arch zynqmp -image boot.bif -w -o boot.bin
)
