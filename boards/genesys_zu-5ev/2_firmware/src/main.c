#include <stdnoreturn.h>

extern noreturn void rust_main(void);

int main(void)
{
    rust_main();
}
