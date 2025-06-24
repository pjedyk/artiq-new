#pragma once

#include <openamp/open_amp.h>

METAL_PACKED_BEGIN
struct this_resource_table
{
    struct resource_table tab;
    uint32_t offset[3];
    struct fw_rsc_carveout carveout;
    struct fw_rsc_vdev vdev;
    struct fw_rsc_vdev_vring vring[2];
    struct fw_rsc_trace trace;
} METAL_PACKED_END;

extern struct this_resource_table const this_resource_table;
