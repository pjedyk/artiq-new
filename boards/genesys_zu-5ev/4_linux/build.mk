LINUX := $(THIS)

MACHINE := genesys_zu-5ev
BITBAKE_IMAGE := petalinux-image-artiq
MENUCONFIG :=

I_LINUX := $(I)/$(LINUX)
I_YOCTO := $(abspath ../../common/petalinux/rel-v2025.2)
I_SETUPSDK := $(I_YOCTO)/setupsdk
I_YOCTOSHELL := $(I_LINUX)/yoctoshell.bash

O_LINUX := $(O)/linux
O_SETUPSDK := $(O_LINUX)/setupsdk
O_YOCTOSHELL := $(O_LINUX)/yoctoshell.bash
O_SDT_TOP_BIT := $(O_VITIS_WS)/hw_pf/hw/sdt/top.bit
O_GEN_MACHINECONF_CONF := $(O_LINUX)/conf/gen-machineconf.conf
O_GEN_MACHINECONF_FLAG := $(O_LINUX)/gen-machineconf.flag
O_BITBAKE_FLAG := $(O_LINUX)/bitbake.flag

.PHONY: $(LINUX)
all: $(LINUX)
$(LINUX): $(O_BITBAKE_FLAG)

$(O_LINUX):
	mkdir -- "$(@)"

$(O_SETUPSDK): $(I_SETUPSDK) | $(O_LINUX)
	printf -- 'source -- %q %q\n' "$(I_SETUPSDK)" "$(O_LINUX)" >"$(O_SETUPSDK)"

$(O_YOCTOSHELL): $(I_YOCTOSHELL) $(O_SETUPSDK)
	printf -- '#! /usr/bin/env bash\nSETUPSDK=%q %q "$${@}"\n' "$(O_SETUPSDK)" "$(I_YOCTOSHELL)" \
	  >"$(O_YOCTOSHELL)~"
	chmod -- +x "$(O_YOCTOSHELL)~"
	mv -fT -- "$(O_YOCTOSHELL)~" "$(O_YOCTOSHELL)"

$(O_SDT_TOP_BIT): $(O_TOP_BIT) $(O_FSBL_ELF)
	cp -fT -- "$(O_TOP_BIT)" "$(O_SDT_TOP_BIT)"

$(O_GEN_MACHINECONF_FLAG): $(O_YOCTOSHELL) $(O_SDT_TOP_BIT)
	$(O_YOCTOSHELL) gen-machineconf $(if $(MENUCONFIG),--menuconfig=project) \
	  --add-config='CONFIG_SUBSYSTEM_COMPONENT_FSBL_FROM_LOCAL_PATH=y' \
	  --add-config='CONFIG_SUBSYSTEM_COMPONENT_FSBL_ELF_PATH="$(O_FSBL_ELF)"' \
	  --add-config='CONFIG_YOCTO_INCLUDE_MACHINE_NAME="zynqmp-artiq"' \
	  --hw-description="$(dir $(O_SDT_TOP_BIT))" --machine-name="$(MACHINE)" \
	  parse-sdt -l "$(O_GEN_MACHINECONF_CONF)"
	touch -- "$(O_GEN_MACHINECONF_FLAG)"

$(O_BITBAKE_FLAG): $(O_GEN_MACHINECONF_FLAG)
	$(O_YOCTOSHELL) bitbake -- "$(BITBAKE_IMAGE)"
	touch -- "$(O_BITBAKE_FLAG)"
