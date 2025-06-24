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

int main(void)
{
    struct rpmsg_virtio_device rvdev = {};
    struct metal_io_region rsc_vdev_io = {};
    struct metal_io_region shm_io = {};
    metal_phys_addr_t rsc_vdev_pa;
    metal_phys_addr_t shm_io_pa;
    struct virtio_device * vdev;
    int r;

    rsc_vdev_pa = (metal_phys_addr_t) (&(this_resource_table.vdev));
    metal_io_init(&(rsc_vdev_io), (void *) (&(this_resource_table.vdev)),
        &(rsc_vdev_pa), sizeof this_resource_table.vdev, (unsigned) -1, 0U,
        NULL);

    shm_io_pa = (metal_phys_addr_t) this_resource_table.carveout.pa;
    metal_io_init(&(shm_io), (void *) this_resource_table.carveout.da,
        &(shm_io_pa), (size_t) this_resource_table.carveout.len, (unsigned) -1,
        0U, NULL);

    vdev = rproc_virtio_create_vdev(VIRTIO_DEV_DEVICE, 0U,
        metal_io_virt(&(rsc_vdev_io), 0LU), &(rsc_vdev_io), NULL, notify,
        rst_cb);
    if (vdev == NULL) {
        goto finally;
    }

    r = rpmsg_init_vdev(&(rvdev), vdev, ns_bind_cb, &(shm_io), NULL);
    if (r != 0) {
        goto finally;
    }

finally:
    extern noreturn void rust_main(void);
    rust_main();
}
