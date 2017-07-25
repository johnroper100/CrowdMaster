use std::panic;
use std::ffi::CStr;
use std::os::raw::{c_uint, c_char};


fn silent_panic_handler(_pi: &panic::PanicInfo) {
    // don't do anything here.  This disables the default printing of
    // panics to stderr which we really don't care about here.
}


#[no_mangle]
pub unsafe extern "C" fn libcm_init() {
    panic::set_hook(Box::new(silent_panic_handler));
}


#[no_mangle]
pub unsafe extern "C" fn sum(a: c_uint, b: c_uint) -> c_uint {
    println!("{}, {}", a, b);
    a + b
}


#[no_mangle]
pub unsafe extern "C" fn onbytes(bytes: *const c_char) {
    let b = CStr::from_ptr(bytes);
    println!("{}", b.to_str().unwrap())

}
