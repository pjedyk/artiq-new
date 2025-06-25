#include <stdnoreturn.h>

#include "resource_table.h"

static int notify(void * priv, uint32_t id)
{
    return 0;

    (void) priv;
    (void) id;
}

static void rst_cb(struct virtio_device * vdev)
{
    (void) vdev;
}

static void ns_bind_cb(
    struct rpmsg_device * rdev, char const * name, uint32_t dest)
{
    (void) rdev;
    (void) name;
    (void) dest;
}

int ept_cb(struct rpmsg_endpoint * ept, void * data, size_t len, uint32_t src,
    void * priv)
{
    return 0;

    (void) ept;
    (void) data;
    (void) len;
    (void) src;
    (void) priv;
}

void ns_unbind_cb(struct rpmsg_endpoint * ept)
{
    (void) ept;
}

int main(void)
{
    struct rpmsg_virtio_device rvdev = {};
    struct metal_io_region rsc_vdev_io = {};
    struct metal_io_region shm_io = {};
    struct rpmsg_endpoint ept = {};
    metal_phys_addr_t rsc_vdev_pa;
    metal_phys_addr_t shm_io_pa;
    struct virtio_device * vdev;
    struct rpmsg_device * rdev;
    int r;

    int volatile x = 0;
    while (!x) {
        asm volatile ("nop");
    }

    rsc_vdev_pa = (metal_phys_addr_t) (&(this_resource_table.vdev));
    metal_io_init(&(rsc_vdev_io), (void *) (&(this_resource_table.vdev)),
        &(rsc_vdev_pa), sizeof this_resource_table.vdev, (unsigned) -1, 0U,
        NULL);

    shm_io_pa = (metal_phys_addr_t) this_resource_table.vring[0].da;
    metal_io_init(&(shm_io), (void *) this_resource_table.vring[0].da,
        &(shm_io_pa), 0x108000U, (unsigned) -1, 0U, NULL);

    vdev = rproc_virtio_create_vdev(VIRTIO_DEV_DEVICE, 0U,
        metal_io_virt(&(rsc_vdev_io), 0U), &(rsc_vdev_io), NULL, notify,
        rst_cb);
    if (vdev == NULL) {
        goto finally;
    }

    r = rpmsg_init_vdev(&(rvdev), vdev, ns_bind_cb, &(shm_io), NULL);
    if (r != 0) {
        goto finally;
    }

    rdev = rpmsg_virtio_get_rpmsg_device(&(rvdev));
    if (rdev == NULL) {
        goto finally;
    }

    r = rpmsg_create_ept(&(ept), rdev, "artiq", RPMSG_ADDR_ANY, RPMSG_ADDR_ANY,
        ept_cb, ns_unbind_cb);
    if (r != 0) {
        goto finally;
    }

finally:
    extern noreturn void rust_main(void);
    rust_main();
}
