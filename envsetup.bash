export -- ARTIQ_TOP="${ARTIQ_TOP:-"${PWD}"}"
[[ ! -e "${ARTIQ_TOP}/envsetup.local.bash" ]] || source -- "${ARTIQ_TOP}/envsetup.local.bash"

export -- XILINX_VIVADO="${XILINX_VIVADO:-"/opt/Xilinx/2025.2/Vivado"}"
export -- XILINX_VITIS="${XILINX_VIVADO//Vivado/Vitis}"
source -- "${XILINX_VIVADO}/settings64.sh"
source -- "${XILINX_VITIS}/settings64.sh"

case ":${PYTHONPATH-}:" in *":${ARTIQ_TOP}/common/artiq:"*) ;; *)
  PYTHONPATH="${ARTIQ_TOP}/common/artiq${PYTHONPATH:+":${PYTHONPATH}"}"
  ;; esac
case ":${PYTHONPATH-}:" in *":${ARTIQ_TOP}/common/migen:"*) ;; *)
  PYTHONPATH="${ARTIQ_TOP}/common/migen${PYTHONPATH:+":${PYTHONPATH}"}"
  ;; esac
case ":${PYTHONPATH-}:" in *":${XILINX_VITIS}/cli:"*) ;; *)
  PYTHONPATH="${XILINX_VITIS}/cli${PYTHONPATH:+":${PYTHONPATH}"}"
  ;; esac
export PYTHONPATH

case ":${PATH}:" in *":${ARTIQ_TOP}/common/artiq/artiq/frontend:"*) ;; *)
  PATH="${ARTIQ_TOP}/common/artiq/artiq/frontend:${PATH}"
  ;; esac
export PATH
