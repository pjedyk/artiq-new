FILESEXTRAPATHS:prepend := "${THISDIR}:"
SRC_URI:append = " file://petalinux-artiq-kmeta;type=kmeta;name=petalinux-artiq-kmeta;destsuffix=petalinux-artiq-kmeta"
KERNEL_FEATURES:append = " cfg/debug-kernel.cfg"
