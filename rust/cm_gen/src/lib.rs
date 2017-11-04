#[macro_use] extern crate cpython;
extern crate nalgebra as na;

use cpython::{PyResult, Python};
use na::Vector3;
use std::collections::HashMap;

// add bindings to the generated python module
// N.B: names: "libcpython_lib" must be the name of the `.so` or `.pyd` file
py_module_initializer!(cm_gen, initcm_gen, PyInit_cm_gen, |py, m| {
    try!(m.add(py, "__doc__", "This is the CrowdMaster cm_gen module (implemented in Rust)."));
    try!(m.add(py, "template_random_positioning", py_fn!(py, template_random_positioning_py(locationType: String, MaxX: f64, MaxY: f64, noToPlace: u64, radius: f64, relax: u8, relaxIterations: u8, relaxRadius: f64, direc: f32, angle: f64))));
    Ok(())
});

struct TemplateRequest {
    position: Vector3<f64>,
    rotation: Vector3<f64>,
    scale: Vector3<f64>,
    tags: HashMap<String, f64>,
    group: String,
    materials: HashMap<String, String>
}

struct TemplateRequestComplete {
    request: TemplateRequest,
    target: String //TODO node rather than string
}

trait TemplateNode {
    fn build(&self, tr: TemplateRequest) -> Vec<TemplateRequestComplete>;
}

struct TemplateNodeExample {
    settings: String, //TODO struct?
    inputs: Vec<Box<TemplateNode>>
}

impl TemplateNode for TemplateNodeExample {
    fn build(&self, tr: TemplateRequest) -> Vec<TemplateRequestComplete> {
        Vec::new()
    }
}

/*
Press generate
node tree compiled
template request added to the head of the tree
Spin up many work stealing threads

--------------------
- Each owns a branch of the graph, which may be the same nodes but being called with a different TemplateRequest.
- Each node returns ownership of complete template requests and the Template node they are meant for
- Blender API is NEVER touched.
- Template requests can be created and modified but NO GLOBAL DATA.
--------------------

Synchronise so that all template requests are finalised.
If template requests are returned to Blender then finish here.
Else spin up many work stealing threads (compare to single thread as this stage may become slower with multithreading)

--------------------
- Each thread processes a template request at a time and processes the geo nodes.
- Accesses the bpy module (protected by Mutex).
--------------------

Synchronise threads and return control to Blender UI
*/

// logic implemented as a normal rust function
fn template_random_positioning(location_type: String, MaxX: f64, MaxY: f64, noToPlace: u64, radius: f64, relax: u8, relaxIterations: u8, relaxRadius: f64, direc: f32, angle: f64) -> String {
    println!("It works! {}, {}", MaxX, MaxY);
    String::from("return value")
}

// rust-cpython aware function. All of our python interface could be
// declared in a separate module.
// Note that the py_fn!() macro automatically converts the arguments from
// Python objects to Rust values; and the Rust return value back into a Python object.
fn template_random_positioning_py(_: Python, location_type: String, MaxX: f64, MaxY: f64, noToPlace: u64, radius: f64, relax: u8, relaxIterations: u8, relaxRadius: f64, direc: f32, angle: f64) -> PyResult<String> {
    let out = template_random_positioning(locationType, MaxX, MaxY, noToPlace, radius, relax, relaxIterations, relaxRadius, direc, angle);
    Ok(out)
}
