#! /bin/false --

[[ ! -e "${PWD}/envsetup.local.bash" ]] \
  || source -- "${PWD}/envsetup.local.bash"

XILINX_VIVADO="${XILINX_VIVADO-/opt/Xilinx/2025.1/Vivado}"
XILINX_VITIS="${XILINX_VITIS-/opt/Xilinx/2025.1/Vitis}"

source -- "${XILINX_VIVADO}/settings64.sh"
source -- "${XILINX_VITIS}/settings64.sh"

_IFS="${IFS}" IFS=:
_OFS="${OFS}" OFS=:

_PYTHONPATH=(
    "${PWD}/common/migen"
    "${XILINX_VITIS}/cli"
    ${PYTHONPATH}
)
export -- PYTHONPATH="${_PYTHONPATH[*]}"
unset -- _PYTHONPATH

IFS="${_IFS}"
OFS="${_OFS}"
unset -- _IFS _OFS
