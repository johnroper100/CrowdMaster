#[macro_use] extern crate cpython;

use cpython::{PyResult, Python};

// add bindings to the generated python module
// N.B: names: "libcpython_lib" must be the name of the `.so` or `.pyd` file
py_module_initializer!(cm_gen, initcm_gen, PyInit_cm_gen, |py, m| {
    try!(m.add(py, "__doc__", "This is the CrowdMaster cm_gen module (implemented in Rust)."));
    try!(m.add(py, "template_random_positioning", py_fn!(py, template_random_positioning_py(locationType: String, MaxX: f64, MaxY: f64, noToPlace: u64, radius: f64, relax: u8, relaxIterations: u8, relaxRadius: f64, direc: f32, angle: f64))));
    Ok(())
});

static mut NUM : u32 = 0;

// logic implemented as a normal rust function
fn template_random_positioning(locationType: String, MaxX: f64, MaxY: f64, noToPlace: u64, radius: f64, relax: u8, relaxIterations: u8, relaxRadius: f64, direc: f32, angle: f64) -> String {
    println!("It works! {}, {}", MaxX, MaxY);
}

// rust-cpython aware function. All of our python interface could be
// declared in a separate module.
// Note that the py_fn!() macro automatically converts the arguments from
// Python objects to Rust values; and the Rust return value back into a Python object.
fn template_random_positioning_py(_: Python, locationType: String, MaxX: f64, MaxY: f64, noToPlace: u64, radius: f64, relax: u8, relaxIterations: u8, relaxRadius: f64, direc: f32, angle: f64) -> PyResult<String> {
    let out = template_random_positioning(locationType, MaxX, MaxY, noToPlace, radius, relax, relaxIterations, relaxRadius, direc, angle);
    Ok(out)
}
