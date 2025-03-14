#![no_std]

use core::panic::PanicInfo;

#[no_mangle]
extern "C" fn rust_main() -> ! {
    let mut _x: u32 = 0;

    loop {
        _x += 1;
        _x -=1;
    }
}


#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
   loop {}
}
