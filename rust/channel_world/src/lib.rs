#[macro_use] extern crate cpython;
#[macro_use] extern crate lazy_static;
extern crate ncollide;
extern crate nalgebra as na;

use cpython::{PyResult, Python, PyObject, ObjectProtocol, PyFloat};

use na::{Vector3, Isometry3, Point3};
use na::geometry::Rotation3;

use ncollide::partitioning::BVT;
use ncollide::shape::{Cuboid3, Shape3};
use ncollide::bounding_volume;
use ncollide::query::{PointInterferencesCollector, PointQuery};

use std::f64::consts::PI;
use std::sync::Mutex;
use std::collections::HashMap;

struct Event {
    shape: Box<Shape3<f64>>,
    isometry: Isometry3<f64>
}

struct EventState {
    volumes: HashMap<String, Event>,
    bvt: Option<BVT<String, bounding_volume::AABB<Point3<f64>>>>
}

impl EventState {
    fn new() -> EventState {
        EventState { volumes: HashMap::new(),
                     bvt: None }
    }
}

lazy_static! {
    static ref EVENTSTATE: Mutex<Option<EventState>> = Mutex::new(Some(EventState::new()));
}

// add bindings to the generated python module
// N.B: names: "channel_world" must be the name of the `.so` or `.pyd` file
py_module_initializer!(channel_world, initchannel_world, PyInit_channel_world, |py, m| {
    try!(m.add(py, "__doc__", "This module is implemented in Rust."));
    try!(m.add(py, "event_new", py_fn!(py, event_new_py(name: String,
                                                        loc_x: f64, loc_y: f64, loc_z: f64,
                                                        rot_x: f64, rot_y: f64, rot_z: f64,
                                                        scale_x: f64, scale_y: f64, scale_z: f64))));
    try!(m.add(py, "event_construct_bvt", py_fn!(py, event_construct_bvt_py())));
    try!(m.add(py, "event_query_point", py_fn!(py, event_query_point_py(vector: PyObject))));
    Ok(())
});

fn event_new(name: String, loc: Vector3<f64>, rot: Rotation3<f64>, scale: Vector3<f64>) {
    let e = Event { shape: Box::new(Cuboid3::new(scale)),
                    isometry: Isometry3::new(loc, rot.scaled_axis())};
    EVENTSTATE.lock().unwrap().as_mut().unwrap().volumes.insert(name, e);
}

fn event_new_py(py: Python, name: String, loc_x: f64, loc_y: f64, loc_z: f64,
                rot_x: f64, rot_y: f64, rot_z: f64, scale_x: f64, scale_y: f64, scale_z: f64) -> PyResult<PyObject> {
    let loc = Vector3::new(loc_x, loc_y, loc_z);
    let rot = Rotation3::from_euler_angles(PI * rot_x / 180.0,
                                           PI * rot_y / 180.0,
                                           PI * rot_z / 180.0);
    let scale = Vector3::new(scale_x, scale_y, scale_z);
    event_new(name, loc, rot, scale);
    Ok(py.None())
}

fn event_construct_bvt() {
    let mut opt = EVENTSTATE.lock().unwrap();
    let mut event_state = opt.as_mut().unwrap();
    let mut ids_and_aabb: Vec<(String, bounding_volume::AABB<Point3<f64>>)> = vec!();
    for (key, event) in &event_state.volumes {
        ids_and_aabb.push((key.clone(), event.shape.aabb(&event.isometry)));
    }
    let bvt = BVT::new_balanced(ids_and_aabb);
    event_state.bvt = Some(bvt);
}

fn event_construct_bvt_py(py: Python) -> PyResult<PyObject> {
    event_construct_bvt();
    Ok(py.None())
}

fn event_query_point(point: Point3<f64>) -> Vec<String> {
    let mut opt = EVENTSTATE.lock().unwrap();
    let mut event_state = opt.as_mut().unwrap();

    let mut broad_phase = Vec::new();
    {
        let mut visitor = PointInterferencesCollector::new(&point, &mut broad_phase);
        event_state.bvt.as_mut().unwrap().visit(&mut visitor);
    }
    let mut narrow_phase = Vec::new();
    for p in broad_phase {
        let event = &event_state.volumes[&p];
        let d = event.shape.distance_to_point(&event.isometry, &point, false);
        if d <= 0.0 {
            narrow_phase.push(p);
        }
    }
    narrow_phase
}

fn event_query_point_py(py: Python, vector: PyObject) -> PyResult<Vec<String>> {
    let x: f64 = vector.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let y: f64 = vector.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let z: f64 = vector.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    Ok(event_query_point(Point3::new(x, y, z)))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_event_bvt () {
        let rot1 = Rotation3::from_euler_angles(PI * 75.222 / 180.0,
                                                PI * -3.574 / 180.0,
                                                PI * -69.214 / 180.0);
        event_new(String::from("1"), Vector3::new(0.0, 0.0, -0.3), rot1, Vector3::new(0.5, 0.25, 0.25));

        let rot2 = Rotation3::from_euler_angles(PI * -40.903 / 180.0,
                                                PI * 32.16 / 180.0,
                                                PI * 50.156 / 180.0);
        event_new(String::from("2"), Vector3::new(0.0, 0.66454, 0.0), rot2, Vector3::new(0.5, 0.25, 0.5));

        let rot3 = Rotation3::from_euler_angles(PI * 0.0 / 180.0,
                                                PI * 0.0 / 180.0,
                                                PI * 0.0 / 180.0);
        event_new(String::from("3"), Vector3::new(0.0, 0.0, 0.0), rot3, Vector3::new(0.5, 0.25, 0.5));
        event_construct_bvt();
        let mut r = event_query_point(Point3::new(0.0, 0.0, 0.0));
        r.sort();
        assert_eq!(r, ["2", "3"]);
        let mut r = event_query_point(Point3::new(0.04573, 0.53356, -0.19536));
        r.sort();
        assert_eq!(r, ["1", "2"]);
        event_new(String::from("4"), Vector3::new(0.0, 0.0, 0.0), Rotation3::from_euler_angles(0.0, 0.0, 0.0), Vector3::new(0.5, 0.5, 0.5));
        event_construct_bvt();
        let mut r = event_query_point(Point3::new(0.0, 0.0, 0.0));
        r.sort();
        assert_eq!(r, ["2", "3", "4"]);
    }

    #[test]
    fn test_event_empty () {
        event_construct_bvt();
        let r = event_query_point(Point3::new(0.0, 0.0, 0.0));
        assert_eq!(r, Vec::<String>::new());
    }
}