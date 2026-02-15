[ ! -e "${PWD}/envsetup.local.sh" ] || . "${PWD}/envsetup.local.sh"

XILINX_VIVADO="${XILINX_VIVADO-/opt/Xilinx/2025.2/Vivado}"
XILINX_VITIS="${XILINX_VITIS-/opt/Xilinx/2025.2/Vitis}"
export XILINX_VIVADO XILINX_VITIS
. "${XILINX_VIVADO}/settings64.sh"
. "${XILINX_VITIS}/settings64.sh"

case ":${PWD}/common/artiq:" in *":${PYTHONPATH-}:"*) ;; *)
  PYTHONPATH="${PWD}/common/artiq${PYTHONPATH:+":${PYTHONPATH}"}"
  ;; esac
case ":${PWD}/common/migen:" in *":${PYTHONPATH-}:"*) ;; *)
  PYTHONPATH="${PWD}/common/migen${PYTHONPATH:+":${PYTHONPATH}"}"
  ;; esac
case ":${XILINX_VITIS}/cli:" in *":${PYTHONPATH-}:"*) ;; *)
  PYTHONPATH="${XILINX_VITIS}/cli${PYTHONPATH:+":${PYTHONPATH}"}"
  ;; esac
export PYTHONPATH
