 // TIXY-WASP: Tixy WebAssembly demo in JavaScript
 // Heavily inspired by https://tixy.land/ by Martin Kleppe (@aemkei)

function nice_random_color() {
    angle = random.randrange(0, 360);
    sat = random.randrange(50, 100);
    val = 80;
    col = pygame.Color(0, 0, 0);
    col.hsva = (angle, sat, val, 100);
    return col
}

 const GRID_SIZE = 16;
 const CIRC_SIZE = 16;
 const X_GRIDS = 3;
 const Y_GRIDS = 2;
 const TIMING_RUNS = 16;
 var primary = "blue" // nice_random_color();
 var white = "#FFFFFF";
 const twoPI = Math.PI * 2;

 function twist_color(color) {
     let v = list(color.hsva)
     v[0] = (v[0] + 1) % 360
     color.hsva = tuple(v)
 }


 function turn_color(color, num) {
    let v = list(color.hsva)
    let l = 60 + int(num) % 80
    if (l > 100)
    {
        l = 200 - l
    }
    v[2] = l
    color.hsva = tuple(v)
}


function render_average_timing(gridCtx, name) {
    gridCtx.font = "16px SourceCodePro";
    gridCtx.fillStyle = white
    gridCtx.fillText(name, CIRC_SIZE / 2, CIRC_SIZE);
}

function render_grid(gridCtx, values) {
    for (let [x, y, value] of values) {
        // turn_color(white, (x + y) * 4 + iterations / 3.0)
        let xpos = (1 + x) * CIRC_SIZE //+ CIRC_SIZE
        let ypos = (1 + y) * CIRC_SIZE + CIRC_SIZE

        let color = value > 0 ? primary : white
        let size = Math.abs(value * (CIRC_SIZE));
        if(size > CIRC_SIZE - 2) {
            size = CIRC_SIZE - 2;
        }
        var radius = size / 2 - 1
        gridCtx.fillStyle = color;
        gridCtx.fillRect(xpos - radius, ypos - radius, size, size);
    }
}

function render(tixyhandler) {
    let surface = document.createElement('canvas');
    surface.width = (GRID_SIZE + 2) * CIRC_SIZE
    surface.height = (GRID_SIZE + 2) * CIRC_SIZE
    var gridCtx = surface.getContext("2d");
    gridCtx.fillStyle = "#2b2b2b";
    gridCtx.fillRect(0, 0, surface.height, surface.width);
    render_grid(gridCtx, tixyhandler.generate_grid_values())
    render_average_timing(gridCtx, tixyhandler.lang)
    return surface
}

async function get_wasm_exports(filename) {
    console.log("Loading WASM from " + filename)
    // This is our recommended way of loading WebAssembly.
    const fetchPromise = fetch(filename);
    const { instance } = await WebAssembly.instantiateStreaming(fetchPromise);
    // return the dict of exported functions
    return instance.exports
}


function calculate_squares() {
    square = []
    for (let y = 0; y < Y_GRIDS; y++) {
        for (let x = 0; x < X_GRIDS; x++) {
            let corner = (GRID_SIZE + 1) * CIRC_SIZE
            square.push([x * corner, y * corner + CIRC_SIZE * y])
        }
    }
    return square;
}

async function CreateTixyHandler(lang, filename, small = true) {
    var exports = await get_wasm_exports(filename)
    if(small) {
        tixy = exports.tixy
    } else {
        tixy = (t, i, x, y) => exports.tixy(t, BigInt(i), BigInt(x), BigInt(y))
    }
    return new TixyHandler(lang, tixy);
}

class TixyHandler {
    constructor(lang, tixy) {
        this.tixy = tixy
        this.base_ticks = performance.now()
        this.nanos = []
        this.avg_nanos = 0
        this.lang = lang
    }

    generate_grid_values() {
        let time_seconds = (performance.now() - this.base_ticks) / 1000.0
        let index = 0
        let values = []
        for (let x = 0; x < GRID_SIZE; x++) {
            for (let y = 0; y < GRID_SIZE; y++) {
                let value = this.tixy(time_seconds, index, x, y)
                values.push([x, y, value])
                index += 1
            }
        }
        return values
    }

    generate_with_timing() {
        let start_nanos = time.perf_counter_ns()
        let values = this.generate_grid_values()
        let delta_nanos = time.perf_counter_ns() - start_nanos
        this.calculate_average(delta_nanos, self.nanos)
        return values
    }

    calculate_average(self, delta_nanos, nanos) {
        runs = len(nanos)
        nanos.append(delta_nanos)
        if (runs >= TIMING_RUNS) {
            nanos.pop(0)
        }
        if (runs == TIMING_RUNS) {
            self.avg_nanos = sum(nanos) / len(nanos)
        }
    }
}

// var size = [(GRID_SIZE + 2) * CIRC_SIZE, (GRID_SIZE + 2) * CIRC_SIZE]

var full_size = [(X_GRIDS * GRID_SIZE + X_GRIDS+1) * CIRC_SIZE, (
      Y_GRIDS * GRID_SIZE + Y_GRIDS+1) * CIRC_SIZE]
console.log(full_size)
var background = 0x2b2b2b
var square = calculate_squares()

async function renderGrids() {
    var kou = await CreateTixyHandler('kou', 'langs/kou/tixy.wasm')
    var rust = await CreateTixyHandler('rust', 'langs/rust/tixy.wasm')
    var assemblyscript = await CreateTixyHandler('assemblyscript', 'langs/assemblyscript/tixy.wasm')
    var zig = await CreateTixyHandler('zig', 'langs/zig/tixy.wasm', false)
    var c = await CreateTixyHandler('c', 'langs/c/tixy.wasm')
    var base_ticks = performance.now()
    console.log("rendering...")
    var canvas = document.getElementById("gameCanvas");
    var ctx = canvas.getContext("2d");

    var iterations = 0
    function animate() {
        iterations += 1
        if(iterations % 3 == 0)
        {
            // twist_color(primary)
        }

        /*for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE: sys.exit()
        if event.key == pygame.K_SPACE: primary = nice_random_color()
        if event.key == pygame.K_RETURN: base_ticks = pygame.time.get_ticks()

        if event.type == pygame.QUIT: sys.exit()
        */

       ctx.drawImage(render(rust), ... square[0])
       ctx.drawImage(render(kou), ... square[1])
       ctx.drawImage(render(assemblyscript), ... square[2])
       ctx.drawImage(render(zig), ... square[3])
       ctx.drawImage(render(c), ... square[4])
       // ctx.drawImage(render(some_lang3), square[4])
       // ctx.drawImage(render(some_lang4), square[5])
       window.requestAnimationFrame(animate);
    }

    window.requestAnimationFrame(animate);
}
