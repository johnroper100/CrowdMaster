use spade::PointN;
use cgmath::Point3;

#[derive(Debug, Clone, PartialEq)]
pub enum DirectionType { DIRECTIONAL }

#[derive(Debug, Clone, PartialEq)]
pub struct Vertex {
    pub point: Point3<f64>,
    pub vertex_id: usize,
    pub direction_type: DirectionType,
    pub to_verts: Vec<usize>,
    pub from_verts: Vec<usize>,
    pub radius: f64,
}

impl Vertex {
    pub fn new(x: f64, y: f64, z: f64, vertex_id: usize) -> Vertex {
        Vertex {
            point: Point3::new(x, y, z),
            vertex_id,
            direction_type: DirectionType::DIRECTIONAL,
            to_verts: Vec::new(),
            from_verts: Vec::new(),
            radius: 0.0,
        }
    }
    pub fn new_radius(x: f64, y: f64, z: f64, vertex_id: usize, radius: f64) -> Vertex {
        Vertex {
            point: Point3::new(x, y, z),
            vertex_id,
            direction_type: DirectionType::DIRECTIONAL,
            to_verts: Vec::new(),
            from_verts: Vec::new(),
            radius,
        }
    }
}

impl PointN for Vertex {
    type Scalar = f64;
    fn dimensions() -> usize { 3 }
    fn from_value(value: f64) -> Self {
        Vertex {
            point: Point3::new(value, value, value),
            vertex_id: 0,
            direction_type: DirectionType::DIRECTIONAL,
            to_verts: Vec::new(),
            from_verts: Vec::new(),
            radius: 0.0,
        }
    }
    fn nth(&self, index: usize) -> &f64 {
        match index {
            0 => &self.point.x,
            1 => &self.point.y,
            _ => &self.point.z,
        }
    }
    fn nth_mut(&mut self, index: usize) -> &mut f64 {
        match index {
            0 => &mut self.point.x,
            1 => &mut self.point.y,
            _ => &mut self.point.z,
        }
    }
}