require recipes-core/images/petalinux-initramfs-image.bb
export IMAGE_BASENAME = "artiqlinux-initramfs-image"

INITRAMFS_SCRIPTS = " \
    artiqlinux-initramfs-framework \
"
