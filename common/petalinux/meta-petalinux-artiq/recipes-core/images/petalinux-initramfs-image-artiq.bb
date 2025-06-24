require recipes-core/images/petalinux-initramfs-image.bb
export IMAGE_BASENAME = "petalinux-initramfs-image-artiq"

INITRAMFS_PACKAGES = ""

INITRAMFS_SCRIPTS = " \
    petalinux-initramfs-framework-artiq \
"
