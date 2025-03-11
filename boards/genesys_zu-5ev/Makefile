I := .
O := build

override I := $(abspath $(I))
override O := $(abspath $(O))

CONFIG := debug

I_PLATFORM := $(I)/0_platform
I_GATEWARE := $(I)/1_gateware
I_FIRMWARE := $(I)/2_firmware
I_BOOTABLE := $(I)/3_bootable

I_FIRMWARE_SRC := $(I_FIRMWARE)/src

O_MIGEN_BUILD := $(O)/migen-build
O_CARGO_BUILD := $(O)/cargo-build
O_RUST_FW_DIR := $(O_CARGO_BUILD)/aarch64-unknown-none/$(CONFIG)
O_VITIS_WS := $(O)/vitis-ws

I_VIVADO_SCRIPT_TCL := $(I_PLATFORM)/vivado_script.tcl
I_ZYNQ_ULTRA_PS_E_0_PROPERTIES_TCL := $(I_PLATFORM)/zynq_ultra_ps_e_0.properties.tcl
I_MAIN_C := $(I_FIRMWARE_SRC)/main.c
I_GATEWARE_PY := $(I_GATEWARE)/gateware.py
I_VITIS_SCRIPT_PY := $(I_BOOTABLE)/vitis_script.py
I_XFSBL_DDR_INIT_C := $(I_BOOTABLE)/xfsbl_ddr_init.c

O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI := $(O)/platform_zynq_ultra_ps_e_0_0.xci
O_PLATFORM_XSA := $(O)/platform.xsa
O_TOP_BIT := $(O_MIGEN_BUILD)/top.bit
O_LIBRUST_FIRMWARE_A := $(O_RUST_FW_DIR)/librust_firmware.a
O_LIBRUST_FIRMWARE_D := $(O_RUST_FW_DIR)/librust_firmware.d
O_FSBL_ELF := $(O_VITIS_WS)/hw_pf/zynqmp_fsbl/build/fsbl.elf
O_APP_ELF := $(O_VITIS_WS)/app/build/app.elf
O_BOOT_BIF := $(O)/boot.bif
O_BOOT_BIN := $(O)/boot.bin

.PHONY: all
all: $(O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI) $(O_PLATFORM_XSA) $(O_TOP_BIT) \
 $(O_LIBRUST_FIRMWARE_A) $(O_FSBL_ELF) $(O_APP_ELF) $(O_BOOT_BIF) $(O_BOOT_BIN)

$(O):
	mkdir -- "$(O)"

$(O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI) $(O_PLATFORM_XSA)&: \
 $(I_VIVADO_SCRIPT_TCL) $(I_ZYNQ_ULTRA_PS_E_0_PROPERTIES_TCL) | $(O)
	env -C "$(O)" -- vivado -mode batch \
	  -script "$(I_VIVADO_SCRIPT_TCL)"

$(O_TOP_BIT): $(O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI) $(I_GATEWARE_PY)
	env -C "$(O)" -- "$(I_GATEWARE_PY)" \
	  -I "$(O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI)"

$(O_LIBRUST_FIRMWARE_A):
	env -C "$(I_FIRMWARE)" -- cargo build \
	  --target-dir="$(O_CARGO_BUILD)" \
	  --profile="$(subst debug,dev,$(CONFIG))"
-include $(O_LIBRUST_FIRMWARE_D)

$(O_FSBL_ELF) $(O_APP_ELF)&: $(O_PLATFORM_XSA) $(I_MAIN_C) \
 $(O_LIBRUST_FIRMWARE_A) $(I_VITIS_SCRIPT_PY) $(I_XFSBL_DDR_INIT_C)
	env -C "$(O)" -- vitis -s "$(I_VITIS_SCRIPT_PY)" \
	  -W "$(O_VITIS_WS)" -H "$(O_PLATFORM_XSA)" \
	  -S "$(I_FIRMWARE_SRC)" -R "$(O_RUST_FW_DIR)"

.ONESHELL: $(O_BOOT_BIF)
$(O_BOOT_BIF): | $(O)
	cat <<"EOF" >"$(O_BOOT_BIF)"
	the_ROM_image:
	{
	  [bootloader, destination_cpu=a53-0] $(O_FSBL_ELF)
	  [destination_device=pl] $(O_TOP_BIT)
	  [destination_cpu=a53-0, exception_level=el-3] $(O_APP_ELF)
	}
	EOF

$(O_BOOT_BIN): $(O_TOP_BIT) $(O_FSBL_ELF) $(O_APP_ELF) $(O_BOOT_BIF)
	bootgen -arch zynqmp -image "$(O_BOOT_BIF)" -o "$(O_BOOT_BIN)" -w
