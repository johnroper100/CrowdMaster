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

use std::sync::Mutex;
use std::collections::HashMap;

enum EventOption {
    Control,
    Duration,
    Elapsed
}

enum Event {
    Time((i32, i32)),
    Volume(String)  // index for EventGroup.volume_map
}

struct EventGroup {
    events: Vec<Event>,
    volume_map: HashMap<String, (Box<Shape3<f64>>, Isometry3<f64>)>,
    bvt: Option<BVT<String, bounding_volume::AABB<Point3<f64>>>>
}

impl EventGroup {
    fn new() -> EventGroup {
        EventGroup { events: Vec::new(),
                     volume_map: HashMap::new(),
                     bvt: None }
    }
}

struct EventState {
    event_groups: HashMap<String, EventGroup>,
    time: i32
}

impl EventState {
    fn new() -> EventState {
        EventState { event_groups: HashMap::new(),
                     time: 1 }
    }
}

lazy_static! {
    static ref EVENTSTATE: Mutex<Option<EventState>> = Mutex::new(Some(EventState::new()));
}

// add bindings to the generated python module
py_module_initializer!(channel_world, initchannel_world, PyInit_channel_world, |py, m| {
    try!(m.add(py, "__doc__", "This is the CrowdMaster channel_world module (implemented in Rust)."));
    try!(m.add(py, "event_set_time", py_fn!(py, event_set_time_py(time: i32))));
    try!(m.add(py, "event_time_create", py_fn!(py, event_time_create_py(event_name: String, lower: i32, upper: i32))));
    try!(m.add(py, "event_volume_create", py_fn!(py, event_volume_create_py(event_name: String, object_name: String,
                                                                            py_loc: PyObject, py_rot: PyObject, py_scale: PyObject))));
    try!(m.add(py, "event_volume_update", py_fn!(py, event_volume_update_py(event_name: String, object_name: String, py_loc: PyObject,
                                                                            py_rot: PyObject, py_scale: PyObject))));
    try!(m.add(py, "event_construct_bvt", py_fn!(py, event_construct_bvt_py())));
    try!(m.add(py, "event_query", py_fn!(py, event_query_py(event_name: String, point_py: PyObject, output: String))));
    try!(m.add(py, "event_clear", py_fn!(py, event_clear_py())));
    Ok(())
});

fn event_set_time(time: i32) {
    let mut opt = EVENTSTATE.lock().unwrap();
    let event_state = opt.as_mut().unwrap();

    event_state.time = time;
}

fn event_set_time_py(py: Python, time: i32) -> PyResult<PyObject> {
    event_set_time(time);
    Ok(py.None())
}

fn event_time_create(event_name: String, lower: i32, upper: i32) {
    let mut opt = EVENTSTATE.lock().unwrap();
    let event_state = opt.as_mut().unwrap();

    let e: Event = Event::Time((lower, upper));

    if !event_state.event_groups.contains_key(&event_name) {
        let event_group = EventGroup::new();
        event_state.event_groups.insert(event_name.clone(), event_group);
    }

    event_state.event_groups.get_mut(&event_name).unwrap().events.push(e);
}

fn event_time_create_py(py: Python, event_name: String, lower: i32, upper: i32) -> PyResult<PyObject> {
    event_time_create(event_name, lower, upper);
    Ok(py.None())
}

fn event_volume_create(event_name: String, object_name: String, loc: Vector3<f64>, rot: Rotation3<f64>, scale: Vector3<f64>) {
    let mut opt = EVENTSTATE.lock().unwrap();
    let event_state = opt.as_mut().unwrap();

    let e: Event = Event::Volume(object_name.clone());

    {
        if !event_state.event_groups.contains_key(&event_name) {
            let event_group = EventGroup::new();
            event_state.event_groups.insert(event_name.clone(), event_group);
        }

        let event_group = event_state.event_groups.get_mut(&event_name).unwrap();
        event_group.volume_map.insert(object_name.clone(), (Box::new(Cuboid3::new(scale)), Isometry3::new(loc, rot.scaled_axis())));
    }

    event_state.event_groups.get_mut(&event_name).unwrap().events.push(e);
}

fn event_volume_create_py(py: Python, event_name: String, object_name: String, py_loc: PyObject, py_rot: PyObject, py_scale: PyObject) -> PyResult<PyObject> {
    let loc_x: f64 = py_loc.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let loc_y: f64 = py_loc.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let loc_z: f64 = py_loc.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);

    let rot_x: f64 = py_rot.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_y: f64 = py_rot.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_z: f64 = py_rot.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);

    let scale_x: f64 = py_scale.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let scale_y: f64 = py_scale.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let scale_z: f64 = py_scale.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);

    let loc = Vector3::new(loc_x, loc_y, loc_z);
    let rot = Rotation3::from_euler_angles(rot_x, rot_y, rot_z);
    let scale = Vector3::new(scale_x, scale_y, scale_z);
    event_volume_create(event_name, object_name, loc, rot, scale);
    Ok(py.None())
}

fn event_volume_update(event_name: String, object_name: String, loc: Vector3<f64>, rot: Rotation3<f64>, scale: Vector3<f64>) {
    let mut opt = EVENTSTATE.lock().unwrap();
    let event_state = opt.as_mut().unwrap();

    if let Some(event_group) = event_state.event_groups.get_mut(&event_name) {
        if let Some(x) = event_group.volume_map.get_mut(&object_name) {
            *x = (Box::new(Cuboid3::new(scale)), Isometry3::new(loc, rot.scaled_axis()));
        }
    }
}

fn event_volume_update_py(py: Python, event_name: String, object_name: String, py_loc: PyObject, py_rot: PyObject, py_scale: PyObject) -> PyResult<PyObject> {
    let loc_x: f64 = py_loc.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let loc_y: f64 = py_loc.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let loc_z: f64 = py_loc.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);

    let rot_x: f64 = py_rot.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_y: f64 = py_rot.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_z: f64 = py_rot.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);

    let scale_x: f64 = py_scale.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let scale_y: f64 = py_scale.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let scale_z: f64 = py_scale.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);

    let loc = Vector3::new(loc_x, loc_y, loc_z);
    let rot = Rotation3::from_euler_angles(rot_x, rot_y, rot_z);
    let scale = Vector3::new(scale_x, scale_y, scale_z);
    event_volume_update(event_name, object_name, loc, rot, scale);
    Ok(py.None())
}

fn event_construct_bvt() {
    let mut opt = EVENTSTATE.lock().unwrap();
    let event_state = opt.as_mut().unwrap();

    for (_, event_group) in event_state.event_groups.iter_mut() {
        let mut ids_and_aabb: Vec<(String, bounding_volume::AABB<Point3<f64>>)> = vec!();
        for (name, vol) in event_group.volume_map.iter() {
            let &(ref shape, iso) = vol;
            ids_and_aabb.push((name.clone(), shape.aabb(&iso)));
        }
        let bvt = BVT::new_balanced(ids_and_aabb);
        event_group.bvt = Some(bvt);
    }
}

fn event_construct_bvt_py(py: Python) -> PyResult<PyObject> {
    event_construct_bvt();
    Ok(py.None())
}

fn event_query(event_name: String, point: Point3<f64>, output: EventOption) -> f64 {
    let mut opt = EVENTSTATE.lock().unwrap();
    let event_state = opt.as_mut().unwrap();

    if !event_state.event_groups.contains_key(&event_name) {
        return 0.0
    }
    let event_group = event_state.event_groups.get_mut(&event_name).unwrap();

    let mut narrow_phase = Vec::new();
    if let Some(ref bvt) = event_group.bvt {
        let mut broad_phase = Vec::new();
        {
            let mut visitor = PointInterferencesCollector::new(&point, &mut broad_phase);
            bvt.visit(&mut visitor);
        }
        for p in broad_phase {
            let &(ref shape, iso) = event_group.volume_map.get(&p).unwrap();
            let d = shape.distance_to_point(&iso, &point, false);
            if d <= 0.0 {
                narrow_phase.push(p);
            }
        }
    }

    for event in &event_group.events {
        match event {
            &Event::Time((lower, upper)) => {
                if lower <= event_state.time && event_state.time <= upper {
                    match output {
                        EventOption::Control => {
                            return 1.0
                        },
                        EventOption::Duration => {
                            return (upper - lower) as f64
                        },
                        EventOption::Elapsed => {
                            return (event_state.time - lower) as f64
                        }
                    }
                }
            },
            &Event::Volume(ref vol) => {
                if narrow_phase.contains(&vol) {
                    match output {
                        EventOption::Control => {
                            return 1.0
                        },
                        EventOption::Duration => {
                            return 0.0
                        },
                        EventOption::Elapsed => {
                            return 0.0
                        }
                    }
                }
            }
        }
    }
    0.0
}

fn event_query_py(py: Python, event_name: String, point_py: PyObject, output: String) -> PyResult<f64> {
    let x: f64 = point_py.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let y: f64 = point_py.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let z: f64 = point_py.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let mut output_type = EventOption::Control;
    match output.as_ref() {
        "control" => output_type = EventOption::Control,
        "duration" => output_type = EventOption::Duration,
        "elapsed" => output_type = EventOption::Elapsed,
        _ => ()
    }
    Ok(event_query(event_name, Point3::new(x, y, z), output_type))
}

fn event_clear() {
    let mut opt = EVENTSTATE.lock().unwrap();
    let event_state = opt.as_mut().unwrap();
    event_state.event_groups.clear();
}

fn event_clear_py(py: Python) -> PyResult<PyObject> {
    event_clear();
    Ok(py.None())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::f64::consts::PI;

    #[test]
    fn test_event_volumes() {
        let rot1 = Rotation3::from_euler_angles(PI * 75.222 / 180.0,
                                                PI * -3.574 / 180.0,
                                                PI * -69.214 / 180.0);
        event_volume_create(String::from("1"), String::from("Obj1"), Vector3::new(0.0, 0.0, -0.3), rot1, Vector3::new(0.5, 0.25, 0.25));

        let rot2 = Rotation3::from_euler_angles(PI * -40.903 / 180.0,
                                                PI * 32.16 / 180.0,
                                                PI * 50.156 / 180.0);
        event_volume_create(String::from("1"), String::from("Obj2"), Vector3::new(0.0, 0.66454, 0.0), rot2, Vector3::new(0.5, 0.25, 0.5));

        let rot3 = Rotation3::from_euler_angles(PI * 0.0 / 180.0,
                                                PI * 0.0 / 180.0,
                                                PI * 0.0 / 180.0);
        event_volume_create(String::from("2"), String::from("Obj3"), Vector3::new(0.0, 0.0, 0.0), rot3, Vector3::new(0.5, 0.25, 0.5));
        event_construct_bvt();
        let ev1 = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        let ev2 = event_query(String::from("2"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(ev1, 1.0);
        assert_eq!(ev2, 1.0);
        let ev1 = event_query(String::from("1"), Point3::new(0.04573, 0.53356, -0.19536), EventOption::Control);
        let ev2 = event_query(String::from("2"), Point3::new(0.04573, 0.53356, -0.19536), EventOption::Control);
        assert_eq!(ev1, 1.0);
        assert_eq!(ev2, 0.0);
        let ev1 = event_query(String::from("1"), Point3::new(0.04169, 1.19358, 0.00399), EventOption::Control);
        let ev2 = event_query(String::from("2"), Point3::new(0.04169, 1.19358, 0.00399), EventOption::Control);
        assert_eq!(ev1, 1.0);
        assert_eq!(ev2, 0.0);
        let ev1 = event_query(String::from("1"), Point3::new(1.0, 0.0, 0.0), EventOption::Control);
        let ev2 = event_query(String::from("2"), Point3::new(1.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(ev1, 0.0);
        assert_eq!(ev2, 0.0);
        event_volume_update(String::from("2"), String::from("Obj3"), Vector3::new(1.0, 0.0, 0.0), Rotation3::from_euler_angles(0.0, 0.0, 0.0), Vector3::new(0.5, 0.5, 0.5));
        event_construct_bvt();
        let ev1 = event_query(String::from("1"), Point3::new(1.0, 0.0, 0.0), EventOption::Control);
        let ev2 = event_query(String::from("2"), Point3::new(1.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(ev1, 0.0);
        assert_eq!(ev2, 1.0);
        event_construct_bvt();
        let ev1 = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        let ev2 = event_query(String::from("2"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(ev1, 1.0);
        assert_eq!(ev2, 0.0);

        event_clear();
    }

    #[test]
    fn test_event_time() {
        event_time_create(String::from("1"), 0, 10);
        event_time_create(String::from("1"), 15, 20);
        event_construct_bvt();

        event_set_time(1);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 1.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 10.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 1.0);

        event_set_time(2);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 1.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 10.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 2.0);

        event_set_time(12);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 0.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 0.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 0.0);

        event_set_time(15);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 1.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 5.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 0.0);

        event_clear();
    }

    #[test]
    fn test_event_empty() {
        event_construct_bvt();
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 0.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 0.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 0.0);

        event_clear();
    }

    #[test]
    fn test_event_mixed() {
        event_time_create(String::from("1"), 0, 10);

        let rot = Rotation3::from_euler_angles(PI * 0.0 / 180.0,
                                               PI * 0.0 / 180.0,
                                               PI * 0.0 / 180.0);
        event_volume_create(String::from("1"), String::from("Obj1"), Vector3::new(0.0, 0.0, 0.0), rot, Vector3::new(0.5, 0.25, 0.5));

        event_time_create(String::from("1"), 15, 20);

        event_construct_bvt();
        event_set_time(1);

        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 1.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 10.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 1.0);

        event_set_time(12);

        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 1.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 0.0);
        let r = event_query(String::from("1"), Point3::new(0.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 0.0);

        let r = event_query(String::from("1"), Point3::new(1.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 0.0);
        let r = event_query(String::from("1"), Point3::new(1.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 0.0);
        let r = event_query(String::from("1"), Point3::new(1.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 0.0);

        event_set_time(15);

        let r = event_query(String::from("1"), Point3::new(1.0, 0.0, 0.0), EventOption::Control);
        assert_eq!(r, 1.0);
        let r = event_query(String::from("1"), Point3::new(1.0, 0.0, 0.0), EventOption::Duration);
        assert_eq!(r, 5.0);
        let r = event_query(String::from("1"), Point3::new(1.0, 0.0, 0.0), EventOption::Elapsed);
        assert_eq!(r, 0.0);

        event_clear();
    }
}