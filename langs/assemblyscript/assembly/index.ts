// The entry file of your WebAssembly module.

export function tixy(t: f32, i: i32, x: i32, y: i32): f64 {
  return (x-y) - Math.sin(t) * 16;
}
