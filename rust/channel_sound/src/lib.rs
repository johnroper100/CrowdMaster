#[macro_use] extern crate cpython;

use cpython::{PyResult, Python};

// add bindings to the generated python module
// N.B: names: "libcpython_lib" must be the name of the `.so` or `.pyd` file
py_module_initializer!(channel_sound, initchannel_sound, PyInit_channel_sound, |py, m| {
    try!(m.add(py, "__doc__", "This module is implemented in Rust."));
    try!(m.add(py, "sum_as_string", py_fn!(py, sum_as_string_py(a: i64, b:i64))));
    Ok(())
});

static mut NUM : u32 = 0;

// logic implemented as a normal rust function
fn sum_as_string(a:i64, b:i64) -> String {
    unsafe {
        NUM += 1;
	format!("{}_{}", a + b, NUM).to_string()
    }
}

// rust-cpython aware function. All of our python interface could be
// declared in a separate module.
// Note that the py_fn!() macro automatically converts the arguments from
// Python objects to Rust values; and the Rust return value back into a Python object.
fn sum_as_string_py(_: Python, a:i64, b:i64) -> PyResult<String> {
    let out = sum_as_string(a, b);
    Ok(out)
}
