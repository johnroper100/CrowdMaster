#[macro_use] extern crate cpython;
extern crate nalgebra;
extern crate spade;

use cpython::{PyResult, Python};
use nalgebra::geometry::Point3;
use spade::rtree::RTree;
use spade::primitives::SimpleEdge;

py_module_initializer!(channel_sound, initchannel_sound, PyInit_channel_sound, |py, m| {
    try!(m.add(py, "__doc__", "This is the CrowdMaster channel_sound module (implemented in Rust)."));
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

fn sum_as_string_py(_: Python, a:i64, b:i64) -> PyResult<String> {
    let out = sum_as_string(a, b);
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_r_tree() {
        let e = SimpleEdge::new(Point3::new(0.0, 1.0, 0.0), Point3::new(1.0, 0.0, 0.0));
        let outside_range = Point3::new(-0.5, 1.5, 0.0);
        let fac = e.project_point(&outside_range);
        println!("{}", fac);
        assert!(false);
        let mut rtree = RTree::new();
        rtree.insert(SimpleEdge::new(Point3::new(0.0, 1.0, 0.0), Point3::new(1.0, 0.0, 0.0)));
        let query_point = Point3::new(0.0, 0.0, 0.0);
        let edge = rtree.nearest_neighbor(&query_point).unwrap();
    }
}