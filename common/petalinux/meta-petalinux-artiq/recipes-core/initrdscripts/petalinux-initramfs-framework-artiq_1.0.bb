LICENSE = "LGPL-3.0-only"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/LGPL-3.0-only;md5=bfccfe952269fff2b407dd11f2f3083b"
RDEPENDS:${PN} += "busybox"

inherit allarch

SRC_URI = "file://init"

S = "${WORKDIR}"

do_install() {
    install -m0755 -- "${WORKDIR}/init" "${D}/init"
}

PACKAGES = "${PN}"
FILES:${PN} = "/init"
