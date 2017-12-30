#[macro_use] extern crate cpython;
#[macro_use] extern crate lazy_static;
#[macro_use] extern crate assert_approx_eq;
extern crate spade;
extern crate cgmath;

use cpython::{PyResult, Python, PyList, PyObject, PyString, PyFloat, ObjectProtocol, PythonObject};
use spade::rtree::RTree;
use spade::primitives::SimpleEdge;

use std::sync::Mutex;
use std::collections::HashMap;

use cgmath::{Point3, Vector3, InnerSpace, Quaternion, Rotation};

use std::f64::consts::PI;

mod vertex;
use vertex::{Vertex};

struct PathQuery {
    steer: Vector3<f64>
}

impl PathQuery {
    fn new(steer_vec: Vector3<f64>) -> PathQuery {
        PathQuery {
            steer: steer_vec
        }
    }
    fn clone(&self) -> PathQuery {
        PathQuery {
            steer: self.steer.clone()
        }
    }
}

struct Path {
    vertices: Vec<Vertex>,
    rtree: RTree<SimpleEdge<Vertex>>,
    result_cache: HashMap<String, Option<PathQuery>>
}

impl Path {
    fn new() -> Path {
        Path {
            vertices: Vec::new(),
            rtree: RTree::new(),
            result_cache: HashMap::new()
        }
    }
    fn new_frame(&mut self) {
        self.result_cache.clear();
    }
}

struct PathState {
    paths: HashMap<String, Path>,
}

impl PathState {
    fn new() -> PathState {
        PathState {
            paths: HashMap::new(),
        }
    }
    fn clear(&mut self) {
        self.paths.clear();
    }
    fn new_frame(&mut self) {
        for path in self.paths.values_mut() {
            path.new_frame();
        }
    }
}

lazy_static! {
    static ref PATHSTATE: Mutex<Option<PathState>> = Mutex::new(Some(PathState::new()));
}

py_module_initializer!(channel_sound, initchannel_sound, PyInit_channel_sound, |py, m| {
    try!(m.add(py, "__doc__", "This is the CrowdMaster channel_path module (implemented in Rust)."));
    try!(m.add(py, "add_path", py_fn!(py, add_path_py(py_obj_data: PyObject, py_path_name: PyString))));
    try!(m.add(py, "clear_state", py_fn!(py, clear_state_py())));
    try!(m.add(py, "rx", py_fn!(py, rx_py(py_path_name: PyString, py_agent_name: PyString, py_agent_location: PyObject, py_agent_rotation: PyObject, py_agent_speed: PyFloat))));
    try!(m.add(py, "rz", py_fn!(py, rz_py(py_path_name: PyString, py_agent_name: PyString, py_agent_location: PyObject, py_agent_rotation: PyObject, py_agent_speed: PyFloat))));
    Ok(())
});

fn clear_state_py(py: Python) -> PyResult<PyObject> {
    clear_state();
    Ok(py.None())
}

fn clear_state() {
    let mut opt = PATHSTATE.lock().unwrap();
    let path_state = opt.as_mut().unwrap();
    path_state.clear();
}

fn add_path_py(py: Python, py_obj_data: PyObject, py_path_name: PyString) -> PyResult<PyObject> {
    let path_name = py_path_name.to_string_lossy(py).to_string();
    let mut size: usize = 0;
    {
        let mut opt = PATHSTATE.lock().unwrap();
        let path_state = opt.as_mut().unwrap();
        if path_state.paths.contains_key(&path_name) {
            size = path_state.paths.get_mut(&path_name).unwrap().vertices.len();
        }
    }

    let mut vertices = Vec::new();
    let py_vertices = py_obj_data.getattr(py, "vertices").unwrap().cast_into::<PyList>(py).unwrap();
    let mut py_vert_iter = py_vertices.iter(py);
    let mut next = py_vert_iter.next();
    while next.is_some() {
        let py_vert = next.unwrap();
        let py_co = py_vert.getattr(py, "co").unwrap();
        let x = py_co.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
        let y = py_co.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
        let z = py_co.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
        let index: usize = py_vert.getattr(py, "index").unwrap().extract(py).unwrap();
        let vertex = Vertex::new(x, y, z, index + size);
        vertices.push(vertex);
        next = py_vert_iter.next();
    }
    let mut edges = Vec::new();
    let py_edges = py_obj_data.getattr(py, "edges").unwrap().cast_into::<PyList>(py).unwrap();
    let mut py_edge_iter = py_edges.iter(py);
    let mut next = py_edge_iter.next();
    while next.is_some() {
        let py_edge = next.unwrap();
        let py_ends = py_edge.getattr(py, "vertices").unwrap();
        let from_vert: usize = py_ends.getattr(py, 0).unwrap().extract(py).unwrap();
        let to_vert: usize = py_ends.getattr(py, 1).unwrap().extract(py).unwrap();
        let edge = SimpleEdge::new(vertices[from_vert].clone(),
                                   vertices[to_vert].clone());
        edges.push(edge);
        next = py_edge_iter.next();
    }
    add_path(vertices, edges, path_name);
    Ok(py.None())
}

fn add_path(vertices: Vec<Vertex>, edges: Vec<SimpleEdge<Vertex>>, path_name: String) {
    let mut opt = PATHSTATE.lock().unwrap();
    let path_state = opt.as_mut().unwrap();
    if !path_state.paths.contains_key(&path_name) {
        let path = Path::new();
        path_state.paths.insert(path_name.clone(), path);
    }
    let path = path_state.paths.get_mut(&path_name).unwrap();

    for vert in vertices {
        path.vertices.push(vert);
    }
    for edge in edges {
        path.rtree.insert(edge);
    }
}

fn point_on_path(path_name: String, point: Point3<f64>) -> Option<(Point3<f64>, Vector3<f64>)> {
    let lookup = Vertex::new(point.x, point.y, point.z, 0);
    let mut opt = PATHSTATE.lock().unwrap();
    let path_state = opt.as_mut().unwrap();
    if !path_state.paths.contains_key(&path_name) {
        return None
    }
    let path = path_state.paths.get_mut(&path_name).unwrap();
    let edge = path.rtree.nearest_neighbor(&lookup).unwrap();
    let nearest = edge.nearest_point(&lookup);
    let direction = Vector3::new(edge.to.point.x - edge.from.point.x,
                                 edge.to.point.y - edge.from.point.y,
                                 edge.to.point.z - edge.from.point.z);
    Some((nearest.point, direction))
}

fn calc_target(path_name: String, agent_name: String, agent_location: Point3<f64>, agent_rotation: Quaternion<f64>, agent_speed: f64) -> Option<PathQuery> {
    let norm_velocity = agent_rotation.rotate_vector(Vector3::new(0.0, 1.0, 0.0));

    let mut opt = PATHSTATE.lock().unwrap();
    let path_state = opt.as_mut().unwrap();
    if !path_state.paths.contains_key(&path_name) {
        return None
    }
    let path = path_state.paths.get_mut(&path_name).unwrap();
    if path.result_cache.contains_key(&agent_name) {
        match path.result_cache.get(&agent_name).unwrap() {
            &None => {
                return None
            },
            &Some(ref pq) => {
                return Some(pq.clone())
            }
        }
    }
    if path.rtree.size() == 0 {
        return None
    }
    let lookup = Vertex::new(agent_location.x, agent_location.y, agent_location.z, 0);
    let edge = path.rtree.nearest_neighbor(&lookup).unwrap();
    let project_fac = edge.project_point(&lookup);
    let nearest = edge.from.point + project_fac * (edge.to.point - edge.from.point);
    let start_radius = {
        if project_fac <= 0.0 {
            edge.from.radius
        } else if project_fac >= 1.0 {
            edge.to.radius
        } else {
            edge.from.radius * (1.0 - project_fac) + edge.to.radius * project_fac
        }
    };
    let mut offset = agent_location - nearest;
    let mut remaining = f64::sqrt(edge.length2()) * agent_speed;
    remaining -= (nearest - edge.to.point).magnitude();
    let mut last_vert: usize = edge.from.vertex_id;
    let mut next_vert: usize = edge.to.vertex_id;
    while remaining > 0.0 {
        // TODO assuming vert is DIRECTIONAL
        match path.vertices[next_vert].to_verts.len() {
            0 => {
                remaining = 0.0;
            }, // TODO search for new unconnected path?
            1 => {
                last_vert = next_vert;
                next_vert = path.vertices[next_vert].to_verts[0];
                remaining -= (path.vertices[next_vert].point - path.vertices[last_vert].point).magnitude();
            },
            _ => {
                let mut best_score: f64 = -2.0;
                let mut best_vert: usize = path.vertices[next_vert].to_verts[0];
                for vert in &path.vertices[next_vert].to_verts {
                    let score = norm_velocity.dot((path.vertices[*vert].point - path.vertices[next_vert].point).normalize());
                    if score > best_score {
                        best_vert = path.vertices[next_vert].vertex_id;
                        best_score = score;
                    }
                }
                last_vert = next_vert;
                next_vert = best_vert;
                remaining -= (path.vertices[next_vert].point - path.vertices[last_vert].point).magnitude();
            }
        };
    }
    let last_edge_vec = path.vertices[next_vert].point - path.vertices[last_vert].point;
    let last_edge_len = last_edge_vec.magnitude();
    let last_edge_fac = remaining / last_edge_len;
    let last_radius = path.vertices[last_vert].radius * (1.0 - last_edge_fac) + path.vertices[last_vert].radius * last_edge_fac;
    let offset_scale = {
        let mag = offset.magnitude();
        if mag == 0.0 || start_radius == 0.0 {
            0.0
        } else if mag > start_radius {
            last_radius / mag
        } else {
            last_radius / start_radius
        }
    };
    offset = offset * offset_scale;
    let target = path.vertices[next_vert].point + remaining * (path.vertices[next_vert].point - path.vertices[last_vert].point).normalize() + offset;
    let target_vec = agent_rotation.invert().rotate_vector(target - agent_location);

    path.result_cache.insert(agent_name, Some(PathQuery::new(target_vec)));
    Some(PathQuery::new(target_vec))
}

fn rx(path_name: String, agent_name: String, agent_location: Point3<f64>, agent_rotation: Quaternion<f64>, agent_speed: f64) -> Option<f64> {
    let pq_opt = calc_target(path_name, agent_name, agent_location, agent_rotation, agent_speed);
    match pq_opt {
        Some(ref pq) => Some(f64::atan2(pq.steer.z, pq.steer.y) / PI),
        None => None
    }
}

fn rx_py(py: Python, py_path_name: PyString, py_agent_name: PyString, py_agent_location: PyObject, py_agent_rotation: PyObject, py_agent_speed: PyFloat) -> PyResult<PyObject> {
    let path_name = py_path_name.to_string_lossy(py).to_string();
    let agent_name = py_agent_name.to_string_lossy(py).to_string();
    let loc_x = py_agent_location.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let loc_y = py_agent_location.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let loc_z = py_agent_location.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let agent_location = Point3::new(loc_x, loc_y, loc_z);
    let rot_w = py_agent_rotation.getattr(py, "w").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_x = py_agent_rotation.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_y = py_agent_rotation.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_z = py_agent_rotation.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let agent_rotation = Quaternion::new(rot_w, rot_x, rot_y, rot_z);
    let agent_speed = py_agent_speed.value(py);
    match rx(path_name, agent_name, agent_location, agent_rotation, agent_speed) {
        Some(r) => Ok(PyFloat::new(py, r).into_object()),
        None => Ok(py.None())
    }
}

fn rz(path_name: String, agent_name: String, agent_location: Point3<f64>, agent_rotation: Quaternion<f64>, agent_speed: f64) -> Option<f64> {
    let pq_opt = calc_target(path_name, agent_name, agent_location, agent_rotation, agent_speed);
    match pq_opt {
        Some(ref pq) => Some(f64::atan2(pq.steer.x, pq.steer.y) / PI),
        None => None
    }
}

fn rz_py(py: Python, py_path_name: PyString, py_agent_name: PyString, py_agent_location: PyObject, py_agent_rotation: PyObject, py_agent_speed: PyFloat) -> PyResult<PyObject> {
    let path_name = py_path_name.to_string_lossy(py).to_string();
    let agent_name = py_agent_name.to_string_lossy(py).to_string();
    let loc_x = py_agent_location.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let loc_y = py_agent_location.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let loc_z = py_agent_location.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let agent_location = Point3::new(loc_x, loc_y, loc_z);
    let rot_w = py_agent_rotation.getattr(py, "w").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_x = py_agent_rotation.getattr(py, "x").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_y = py_agent_rotation.getattr(py, "y").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let rot_z = py_agent_rotation.getattr(py, "z").unwrap().cast_into::<PyFloat>(py).unwrap().value(py);
    let agent_rotation = Quaternion::new(rot_w, rot_x, rot_y, rot_z);
    let agent_speed = py_agent_speed.value(py);
    match rz(path_name, agent_name, agent_location, agent_rotation, agent_speed) {
        Some(r) => Ok(PyFloat::new(py, r).into_object()),
        None => Ok(py.None())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_point_on_path_empty() {
        clear_state();
        assert_eq!(point_on_path(String::from("path name"), Point3::new(0.0, 0.0, 0.0)), None);
    }

    #[test]
    fn test_point_on_path() {
        clear_state();

        let mut vertices = Vec::new();
        let mut vert = Vertex::new(1.0, 4.0, 0.0, 0);
        vert.to_verts.push(1);
        vertices.push(vert);

        let mut vert = Vertex::new(2.0, 5.0, 0.0, 1);
        vert.from_verts.push(0);
        vert.to_verts.push(2);
        vertices.push(vert);

        let mut vert = Vertex::new(3.0, 6.0, 0.0, 2);
        vert.from_verts.push(1);
        vertices.push(vert);

        let mut vert = Vertex::new(3.0, 2.0, 0.0, 3);
        vert.to_verts.push(4);
        vertices.push(vert);

        let mut vert = Vertex::new(4.0, 2.0, 0.0, 4);
        vert.from_verts.push(3);
        vert.to_verts.push(5);
        vertices.push(vert);

        let mut vert = Vertex::new(5.0, 2.0, 0.0, 5);
        vert.from_verts.push(4);
        vert.to_verts.push(6);
        vertices.push(vert);

        let mut vert = Vertex::new(6.0, 3.0, 0.0, 6);
        vert.from_verts.push(5);
        vertices.push(vert);

        let mut edges = Vec::new();
        edges.push(SimpleEdge::new(vertices[0].clone(), vertices[1].clone()));
        edges.push(SimpleEdge::new(vertices[1].clone(), vertices[2].clone()));
        edges.push(SimpleEdge::new(vertices[3].clone(), vertices[4].clone()));
        edges.push(SimpleEdge::new(vertices[4].clone(), vertices[5].clone()));
        edges.push(SimpleEdge::new(vertices[5].clone(), vertices[6].clone()));

        add_path(vertices, edges, String::from("path name"));
        let result = point_on_path(String::from("path name"), Point3::new(1.0, 5.0, 0.0));
        match result {
            Some((point, vector)) => {
                assert_eq!(point.x, 1.5);
                assert_eq!(point.y, 4.5);
                assert_eq!(point.z, 0.0);
                assert!(vector.dot(Vector3::new(1.0, 1.0, 0.0)) > 0.99);
            },
            None => assert!(false),
        }
    }

    #[test]
    fn test_r_tree() {
        clear_state();
        
        let v1 = Vertex::new(0.0, 1.0, 0.0, 0);
        let v2 = Vertex::new(1.0, 0.0, 0.0, 1);
        let e = SimpleEdge::new(v1, v2);
        let outside_range = Vertex::new(-0.5, 1.5, 0.0, 0);
        let fac = e.project_point(&outside_range);
        assert_eq!(fac, -0.5);

        let mut rtree = RTree::new();
        rtree.insert(e);
        let query_point = Vertex::new(0.0, 0.0, 0.0, 0);
        let edge = rtree.nearest_neighbor(&query_point).unwrap();
        let fac = edge.project_point(&query_point);
        assert_eq!(fac, 0.5);
        assert_eq!(edge.from.vertex_id, 0);
        assert_eq!(edge.to.vertex_id, 1);
    }

    #[test]
    fn test_calc_target() {
        clear_state();

        let mut vertices = Vec::new();
        let mut vert = Vertex::new_radius(1.0, 4.0, 0.0, 0, 1.0);
        vert.to_verts.push(1);
        vertices.push(vert);

        let mut vert = Vertex::new_radius(2.0, 5.0, 0.0, 1, 1.0);
        vert.from_verts.push(0);
        vert.to_verts.push(2);
        vertices.push(vert);

        let mut vert = Vertex::new_radius(3.0, 6.0, 0.0, 2, 1.0);
        vert.from_verts.push(1);
        vertices.push(vert);

        let mut vert = Vertex::new_radius(3.0, 2.0, 0.0, 3, 1.0);
        vert.to_verts.push(4);
        vertices.push(vert);

        let mut vert = Vertex::new_radius(4.0, 2.0, 0.0, 4, 1.0);
        vert.from_verts.push(3);
        vert.to_verts.push(5);
        vertices.push(vert);

        let mut vert = Vertex::new_radius(5.0, 2.0, 0.0, 5, 1.0);
        vert.from_verts.push(4);
        vert.to_verts.push(6);
        vertices.push(vert);

        let mut vert = Vertex::new_radius(6.0, 3.0, 0.0, 6, 1.0);
        vert.from_verts.push(5);
        vertices.push(vert);

        let mut edges = Vec::new();
        edges.push(SimpleEdge::new(vertices[0].clone(), vertices[1].clone()));
        edges.push(SimpleEdge::new(vertices[1].clone(), vertices[2].clone()));
        edges.push(SimpleEdge::new(vertices[3].clone(), vertices[4].clone()));
        edges.push(SimpleEdge::new(vertices[4].clone(), vertices[5].clone()));
        edges.push(SimpleEdge::new(vertices[5].clone(), vertices[6].clone()));

        add_path(vertices, edges, String::from("path_name"));

        let pq_opt = calc_target(String::from("path_name"),
                                 String::from("agent_name"),
                                 Point3::new(3.0, 1.0, 0.0),
                                 Quaternion::new(0.707, 0.0, 0.0, -0.707),
                                 2.0);
        match pq_opt {
            Some(pq) => {
                assert_approx_eq!(pq.steer.x, 0.0, 1e-3f64);
                assert_approx_eq!(pq.steer.y, 2.0, 1e-3f64);
                assert_approx_eq!(pq.steer.z, 0.0, 1e-3f64);
            },
            None => {
                assert!(false);
            }
        }
    }

    #[test]
    fn test_new_frame() {
        let mut opt = PATHSTATE.lock().unwrap();
        let path_state = opt.as_mut().unwrap();
        path_state.new_frame();
        // TODO check for success?
    }

    #[test]
    fn test_rx_rz() {
        clear_state();

        let mut vertices = Vec::new();
        let mut vert = Vertex::new_radius(3.0, 2.0, 0.0, 0, 1.0);
        vert.to_verts.push(1);
        vertices.push(vert);

        let mut vert = Vertex::new_radius(6.0, 2.0, 0.0, 1, 1.0);
        vert.from_verts.push(0);
        vertices.push(vert);

        let mut edges = Vec::new();
        edges.push(SimpleEdge::new(vertices[0].clone(), vertices[1].clone()));

        add_path(vertices, edges, String::from("path_name"));

        let path_name = String::from("path_name");
        let agent_name = String::from("agent_name");
        let agent_location = Point3::new(3.0, 1.0, 0.0);
        let agent_rotation = Quaternion::new(0.707, 0.0, 0.0, -0.707);
        let agent_speed = 1.0;

        let result_opt = rx(path_name.clone(),
                            agent_name.clone(),
                            agent_location.clone(),
                            agent_rotation.clone(),
                            agent_speed.clone());
        match result_opt {
            None => assert!(false),
            Some(rot_x) => assert_approx_eq!(rot_x, 0.0, 1e-3f64),
        }
        let result_opt = rz(path_name.clone(),
                            agent_name.clone(),
                            agent_location.clone(),
                            agent_rotation.clone(),
                            agent_speed.clone());
        match result_opt {
            None => assert!(false),
            Some(rot_z) => assert_approx_eq!(rot_z, 0.0, 1e-3f64),
        }
    }
}