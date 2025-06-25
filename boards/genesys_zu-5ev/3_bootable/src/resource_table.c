#include "resource_table.h"

/* SEE: system-user.dtsi */

__attribute__((section(".resource_table")))
struct this_resource_table const this_resource_table = {
    .tab = {
        .ver = 1U,
        .num = 2U,
    },
    .offset = {
        offsetof(struct this_resource_table, vdev),
        offsetof(struct this_resource_table, trace),
    },
    .vdev = {
        .type = RSC_VDEV,
        .id = 7U,
        .notifyid = 0U,
        .dfeatures = (1U << VIRTIO_RPMSG_F_NS),
        .num_of_vrings = 2U,
    },
    .vring = {
        {
            .da = 0x3ED40000U,
            .align = 0x1000U,
            .num = 256U,
            .notifyid = 1U,
        },
        {
            .da = 0x3ED44000U,
            .align = 0x1000U,
            .num = 256U,
            .notifyid = 2U,
        },
    },
    .trace = {
        .type = RSC_TRACE,
        .da = 0x3EE48000U,
        .len = 0x10000U,
        .name = "trace:r5f0",
    },
};
