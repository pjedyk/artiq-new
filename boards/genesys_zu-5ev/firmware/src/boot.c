#include <stdnoreturn.h>

//#include <xil_hal.h>

int main(void)
{
#if 0
    u32 volatile addr;
    u32 volatile value;

    addr = 0x80000000U;

    for (;;) {
        value = Xil_In32(addr);
        continue;
    }
#endif

    extern noreturn void rust_main(void);
    rust_main();
}

#if 0
noreturn void _exit(int _status)
{
    for (;;) {
    }

    (void) _status;
}
#endif
