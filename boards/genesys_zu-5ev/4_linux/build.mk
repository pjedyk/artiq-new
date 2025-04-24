LINUX := $(THIS)

BITBAKE_IMAGE := artiqlinux-image-default

I_LINUX := $(I)/$(LINUX)
I_BBLAYERS_CONF_IN := $(I_LINUX)/bblayers.conf.in
I_LOCAL_CONF_IN := $(I_LINUX)/local.conf.in
I_ZYNQMP_ARTIQ_CONF_IN := $(I_LINUX)/zynqmp-artiq.conf.in
I_YOCTO := $(abspath ../../common/yocto/rel-v2024.2)
I_SETUPSDK := $(I_YOCTO)/setupsdk

O_LINUX := $(O)/linux
O_LINUX_CONF := $(O_LINUX)/conf
O_LINUX_CONF_MACHINE := $(O_LINUX_CONF)/machine
O_BBLAYERS_CONF := $(O_LINUX_CONF)/bblayers.conf
O_LOCAL_CONF := $(O_LINUX_CONF)/local.conf
O_ZYNQMP_ARTIQ_CONF := $(O_LINUX_CONF_MACHINE)/zynqmp-artiq.conf
O_all_CONF := $(O_BBLAYERS_CONF) $(O_LOCAL_CONF) $(O_ZYNQMP_ARTIQ_CONF)
O_SETUPSDK := $(O_LINUX)/setupsdk
O_SDT_TOP_BIT := $(O_VITIS_WS)/hw_pf/hw/sdt/top.bit
O_IMAGES := $(O_LINUX)/tmp/deploy/images/xlnx-zynqmp
O_IMAGE_WIC := $(O_IMAGES)/$(BITBAKE_IMAGE)-xlnx-zynqmp.wic

.PHONY: $(LINUX)
all: $(LINUX)
$(LINUX): $(O_IMAGE_WIC)

$(O_LINUX_CONF): | $(O_LINUX)
$(O_LINUX_CONF_MACHINE): | $(O_LINUX_CONF)
$(O_LINUX) $(O_LINUX_CONF) $(O_LINUX_CONF_MACHINE):
	mkdir -- "$(@)"

$(O_BBLAYERS_CONF): $(I_BBLAYERS_CONF_IN) | $(O_LINUX_CONF)
$(O_LOCAL_CONF): $(I_LOCAL_CONF_IN) | $(O_LINUX_CONF)
$(O_ZYNQMP_ARTIQ_CONF): $(I_ZYNQMP_ARTIQ_CONF_IN) | $(O_LINUX_CONF_MACHINE)
$(O_all_CONF):
	m4 -D_YOCTO_="$(I_YOCTO)" -D_LINUX_="$(I_LINUX)" -D_BUILD_="$(O)" \
	  -D_FSBL_FILE_="$(basename $(O_FSBL_ELF))" -- "$(^)" >"$(@)"

$(O_SETUPSDK):
	printf -- 'source -- %q %q\n' "$(I_SETUPSDK)" "$(O_LINUX)" >"$(O_SETUPSDK)"

$(O_SDT_TOP_BIT): $(O_TOP_BIT) $(O_FSBL_ELF)
	cp -fT -- $(O_TOP_BIT) $(O_SDT_TOP_BIT)

$(O_IMAGE_WIC): $(O_all_CONF) $(O_SETUPSDK) $(O_SDT_TOP_BIT)
	source -- "$(O_SETUPSDK)" && \
	gen-machineconf \
	  --add-config='CONFIG_YOCTO_BBMC_CORTEXA53_FSBL=n' \
	  --add-config='CONFIG_YOCTO_INCLUDE_MACHINE_NAME="zynqmp-artiq"' \
	  --hw-description="$(dir $(O_SDT_TOP_BIT))" \
	  parse-sdt -l "$(O_LOCAL_CONF)" && \
	bitbake -- $(BITBAKE_IMAGE)
