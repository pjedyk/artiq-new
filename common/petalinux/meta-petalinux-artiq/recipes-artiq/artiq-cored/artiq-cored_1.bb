LICENSE = "LGPL-3.0-only"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/LGPL-3.0-only;md5=bfccfe952269fff2b407dd11f2f3083b"

inherit setuptools3
inherit systemd

FILESPATH:prepend = "${THISDIR}:"
SRC_URI = "file://${BPN}"
S = "${WORKDIR}/${BPN}"

do_install:append() {
    install -D -m0644 -t"${D}${systemd_system_unitdir}" -- "${S}/artiq_cored.service"
}

FILES:${PN} += " \
  ${bindir}/artiq_cored \
  ${PYTHON_SITEPACKAGES_DIR}/artiq_cored \
  ${PYTHON_SITEPACKAGES_DIR}/artiq_cored-*.dist-info \
  ${systemd_system_unitdir}/artiq_cored.service \
"

SYSTEMD_PACKAGES = "${PN}"
SYSTEMD_SERVICE:${PN} = "artiq_cored.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"
