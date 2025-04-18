BOOTABLE := $(THIS)

I_BOOTABLE := $(I)/$(BOOTABLE)
I_VITIS_SCRIPT_PY := $(I_BOOTABLE)/vitis_script.py
I_XFSBL_DDR_INIT_C := $(I_BOOTABLE)/xfsbl_ddr_init.c
I_BOOTABLE_SRC := $(I_BOOTABLE)/src
I_BOOTABLE_SRC_wildcard_CHS := $(wildcard $(I_BOOTABLE_SRC)/*.[chS])

O_VITIS_WS := $(O)/vitis-ws
O_FSBL_ELF := $(O_VITIS_WS)/hw_pf/zynqmp_fsbl/build/fsbl.elf
O_APP_ELF := $(O_VITIS_WS)/app/build/app.elf

.PHONY: $(BOOTABLE)
all: $(BOOTABLE)
$(BOOTABLE): $(O_FSBL_ELF) $(O_APP_ELF)

$(O_FSBL_ELF) $(O_APP_ELF)&: $(O_PLATFORM_XSA) $(O_LIBRUST_FIRMWARE_A) \
 $(I_VITIS_SCRIPT_PY) $(I_XFSBL_DDR_INIT_C) $(I_BOOTABLE_SRC_wildcard_CHS)
	env -C "$(O)" -- vitis -s "$(I_VITIS_SCRIPT_PY)" \
	  -W "$(O_VITIS_WS)" -H "$(O_PLATFORM_XSA)" \
	  -S "$(I_BOOTABLE_SRC)" -R "$(O_RUST_FW_DIR)"
