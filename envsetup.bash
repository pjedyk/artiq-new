#! /bin/false --

XILINX_VIVADO="${XILINX_VIVADO-/opt/Xlx/Vivado_Vitis2024.2/Vivado/2024.2}"
XILINX_VITIS="${XILINX_VITIS-/opt/Xlx/Vivado_Vitis2024.2/Vitis/2024.2}"

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
