#![no_std]

use core::panic::PanicInfo;
use core::ptr::read_volatile;

#[no_mangle]
extern "C" fn rust_main() -> ! {
    let mut _x: u32 = 0;
    let addr: u32 = 0x80000000;

    loop {
        unsafe {
            _x = read_volatile(addr as *const u32);
        }
    }
}


#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
   loop {}
}
