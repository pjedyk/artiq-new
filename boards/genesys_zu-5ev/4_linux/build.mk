LINUX := $(THIS)

MACHINE := genesys_zu-5ev
BITBAKE_IMAGE := petalinux-image-artiq
MENUCONFIG :=

I_LINUX := $(I)/$(LINUX)
I_YOCTO := $(abspath ../../common/petalinux/rel-v2025.1)
I_SETUPSDK := $(I_YOCTO)/setupsdk

O_LINUX := $(O)/linux
O_SETUPSDK := $(O_LINUX)/setupsdk
O_SDT_TOP_BIT := $(O_VITIS_WS)/hw_pf/hw/sdt/top.bit
O_GEN_MACHINECONF_CONF := $(O_LINUX)/conf/gen-machineconf.conf
O_GEN_MACHINECONF_FLAG := $(O_LINUX)/gen-machineconf.flag
O_BITBAKE_FLAG := $(O_LINUX)/bitbake.flag

.PHONY: $(LINUX)
all: $(LINUX)
$(LINUX): $(O_BITBAKE_FLAG)

$(O_LINUX):
	mkdir -- "$(@)"

$(O_SETUPSDK): | $(O_LINUX)
	printf -- 'source -- %q %q\n' "$(I_SETUPSDK)" "$(O_LINUX)" \
	  >"$(O_SETUPSDK)"

$(O_SDT_TOP_BIT): $(O_TOP_BIT) $(O_FSBL_ELF)
	cp -fT -- "$(O_TOP_BIT)" "$(O_SDT_TOP_BIT)"

$(O_GEN_MACHINECONF_FLAG): $(O_all_CONF) $(O_SETUPSDK) $(O_SDT_TOP_BIT)
	source -- "$(O_SETUPSDK)" && gen-machineconf \
	  $(if $(MENUCONFIG),--menuconfig) \
	  --add-config='CONFIG_SUBSYSTEM_COMPONENT_FSBL_FROM_LOCAL_PATH=y' \
	  --add-config='CONFIG_SUBSYSTEM_COMPONENT_FSBL_ELF_PATH="$(O_FSBL_ELF)"' \
	  --add-config='CONFIG_YOCTO_INCLUDE_MACHINE_NAME="zynqmp-artiq"' \
	  --hw-description="$(dir $(O_SDT_TOP_BIT))" \
	  --machine-name="$(MACHINE)" \
	  parse-sdt -l "$(O_GEN_MACHINECONF_CONF)"
	touch -- "$(O_GEN_MACHINECONF_FLAG)"

$(O_BITBAKE_FLAG): $(O_GEN_MACHINECONF_FLAG)
	source -- "$(O_SETUPSDK)" && bitbake -- "$(BITBAKE_IMAGE)"
	touch -- "$(O_BITBAKE_FLAG)"
