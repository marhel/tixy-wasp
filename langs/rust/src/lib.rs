#[no_mangle]
pub extern fn tixy(t: f32, i: i32, x: i32, y: i32) -> f32 {
    y as f32 - t
}
