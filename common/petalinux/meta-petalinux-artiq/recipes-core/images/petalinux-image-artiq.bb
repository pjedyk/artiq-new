require recipes-core/images/petalinux-image-common.inc

# SEE: https://docs.yoctoproject.org/5.0.8/ref-manual/features.html#ref-features-image
# SEE: poky/meta/classes-recipe/core-image.bbclass
IMAGE_FEATURES += " \
    allow-empty-password \
    stateless-rootfs \
"

# SEE: meta-petalinux/classes/plnx-image.bbclass
IMAGE_FEATURES += " \
    petalinux-networking-stack \
    petalinux-lmsensors \
    petalinux-openamp \
"

IMAGE_INSTALL += " \
    networkmanager-daemon networkmanager-nmcli \
    avahi-daemon avahi-utils avahi-dnsconfd \
    tmux vim rsync \
    packagegroup-artiq \
"

IMAGE_LINGUAS = "c"
