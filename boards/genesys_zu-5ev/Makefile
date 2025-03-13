I := .
O := build

override I := $(abspath $(I))
override O := $(abspath $(O))

CONFIG := debug

PLATFORM := 0_platform
GATEWARE := 1_gateware
FIRMWARE := 2_firmware
BOOTABLE := 3_bootable

I_PLATFORM := $(I)/$(PLATFORM)
I_GATEWARE := $(I)/$(GATEWARE)
I_FIRMWARE := $(I)/$(FIRMWARE)
I_BOOTABLE := $(I)/$(BOOTABLE)

I_FIRMWARE_SRC := $(I_FIRMWARE)/src

O_MIGEN_BUILD := $(O)/migen-build
O_CARGO_BUILD := $(O)/cargo-build
O_RUST_FW_DIR := $(O_CARGO_BUILD)/aarch64-unknown-none/$(CONFIG)
O_VITIS_WS := $(O)/vitis-ws

I_VIVADO_SCRIPT_TCL := $(I_PLATFORM)/vivado_script.tcl
I_PLATFORM_wildcard_TCL := $(wildcard $(I_PLATFORM)/*.tcl)
I_MAIN_C := $(I_FIRMWARE_SRC)/main.c
I_GATEWARE_PY := $(I_GATEWARE)/gateware.py
I_GATEWARE_wildcard_PY := $(wildcard $(I_GATEWARE)/*.py)
I_VITIS_SCRIPT_PY := $(I_BOOTABLE)/vitis_script.py
I_XFSBL_DDR_INIT_C := $(I_BOOTABLE)/xfsbl_ddr_init.c

O_ZYNQ_ULTRA_PS_E_0 := $(O)/zynq_ultra_ps_e_0
O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI := $(O)/platform_zynq_ultra_ps_e_0_0.xci
O_PLATFORM_XSA := $(O)/platform.xsa
O_TOP_BIT := $(O_MIGEN_BUILD)/top.bit
O_LIBRUST_FIRMWARE_A := $(O_RUST_FW_DIR)/librust_firmware.a
O_LIBRUST_FIRMWARE_D := $(O_RUST_FW_DIR)/librust_firmware.d
O_FSBL_ELF := $(O_VITIS_WS)/hw_pf/zynqmp_fsbl/build/fsbl.elf
O_APP_ELF := $(O_VITIS_WS)/app/build/app.elf
O_BOOT_BIF := $(O)/boot.bif
O_BOOT_BIN := $(O)/boot.bin

.PHONY: all $(PLATFORM) $(GATEWARE) $(FIRMWARE) $(BOOTABLE)
all: $(PLATFORM) $(GATEWARE) $(FIRMWARE) $(BOOTABLE)
$(PLATFORM): $(O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI) $(O_PLATFORM_XSA)
$(GATEWARE): $(O_TOP_BIT)
$(FIRMWARE): $(O_LIBRUST_FIRMWARE_A)
$(BOOTABLE): $(O_FSBL_ELF) $(O_APP_ELF) $(O_BOOT_BIF) $(O_BOOT_BIN)

$(O):
	mkdir -- "$(O)"

$(O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI) $(O_PLATFORM_XSA)&: \
 $(I_VIVADO_SCRIPT_TCL) $(I_PLATFORM_wildcard_TCL) | $(O)
	env -C "$(O)" -- vivado -mode batch \
	  -script "$(I_VIVADO_SCRIPT_TCL)"

$(O_TOP_BIT): $(O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI) $(I_GATEWARE_PY) \
 $(I_GATEWARE_wildcard_PY)
	env -C "$(O)" -- "$(I_GATEWARE_PY)" -B $(O_MIGEN_BUILD) \
	  -I "$(O_PLATFORM_ZYNQ_ULTRA_PS_E_0_0_XCI)" -Z "$(O_ZYNQ_ULTRA_PS_E_0)"

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
