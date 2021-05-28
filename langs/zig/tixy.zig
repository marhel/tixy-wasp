export fn tixy(t: f64, i: i64, x: i64, y: i64) f64 {
  return @cos(t + @intToFloat(f64, i) + @intToFloat(f64, x * y));
}
