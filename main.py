# TIXY-WASP: Tixy WebAssembly demo in Python
# Heavily inspired by https://tixy.land/ by Martin Kleppe (@aemkei)

from wasmer import engine, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler
import sys, pygame
import random, time
from os.path import exists
from os import getcwd

def nice_random_color() -> pygame.Color:
    angle = random.randrange(0, 360)
    sat = random.randrange(50, 100)
    val = 80
    col = pygame.Color(0, 0, 0)
    col.hsva = (angle, sat, val, 100)
    return col


GRID_SIZE = 16
CIRC_SIZE = 32
X_GRIDS = 3
Y_GRIDS = 2
TIMING_RUNS = 16
primary = nice_random_color()
white = pygame.Color(255, 255, 255)


def twist_color(color):
    v = list(color.hsva)
    v[0] = (v[0] + 1) % 360
    color.hsva = tuple(v)


def turn_color(color, num):
    v = list(color.hsva)
    l = 60 + int(num) % 80
    if l > 100: l = 200 - l
    v[2] = l
    color.hsva = tuple(v)


def render_average_timing(surface, name, avg_nanos, iterations):
    cells = GRID_SIZE * GRID_SIZE
    if avg_nanos:
        delta_text = font.render(
            "%.1f µs  %.1fM calls [%s]" % (
                avg_nanos / (GRID_SIZE * GRID_SIZE) / 1000.0,
                iterations * cells / 1000000.0,
                name
            ),
            False, white)
        surface.blit(delta_text, dest=(CIRC_SIZE, 2))


def render_grid(surface, values):
    for (x, y, value) in values:
        turn_color(white, (x + y) * 4 + iterations / 3.0)
        xpos = (1 + x) * CIRC_SIZE + CIRC_SIZE / 2
        ypos = (1 + y) * CIRC_SIZE + CIRC_SIZE / 2

        if value > 0:
            color = primary
        else:
            color = white
        size = abs(value * CIRC_SIZE)
        if size > CIRC_SIZE:
            size = CIRC_SIZE
        pygame.draw.circle(surface, color, [xpos, ypos], size / 2 - 1)


def render(tixyhandler):
    surface = pygame.Surface(size)
    render_grid(surface, tixyhandler.generate_with_timing())
    render_average_timing(surface, tixyhandler.lang, tixyhandler.avg_nanos,
                          iterations)
    return surface


def get_wasm_exports(filename):
    print("Loading WASM from " + filename, end=" ")
    # Let's define the store, that holds the engine, that holds the compiler.
    store = Store(engine.JIT(Compiler))

    # get bytes from wasm module
    wasm_bytes = open(filename, 'rb').read()
    print("[%d bytes]" % len(wasm_bytes))
    # Let's compile the module to be able to execute it!
    module = Module(store, wasm_bytes)

    # Now the module is compiled, we can instantiate it.
    instance = Instance(module)

    # return the dict of exported functions
    return instance.exports


def calculate_squares():
    for y in range(0, Y_GRIDS):
        for x in range(0, X_GRIDS):
            corner = (GRID_SIZE + 1) * CIRC_SIZE
            square.append([x * corner, y * corner])


class TixyHandler:
    def __init__(self, lang, filename):
        self.tixy = get_wasm_exports(filename).tixy
        self.nanos = []
        self.avg_nanos = 0
        self.lang = lang

    def generate_grid_values(self):
        time_seconds = (pygame.time.get_ticks() - base_ticks) / 1000.0
        index = 0
        values = []
        for x in range(0, GRID_SIZE):
            for y in range(0, GRID_SIZE):
                values.append((x, y, self.tixy(time_seconds, index, x, y)))
                index += 1
        return values

    def generate_with_timing(self):
        start_nanos = time.perf_counter_ns()
        values = self.generate_grid_values()
        delta_nanos = time.perf_counter_ns() - start_nanos
        self.calculate_average(delta_nanos, self.nanos)
        return values

    def calculate_average(self, delta_nanos, nanos):
        runs = len(nanos)
        nanos.append(delta_nanos)
        if runs >= TIMING_RUNS: nanos.pop(0)
        if runs == TIMING_RUNS:
            self.avg_nanos = sum(nanos) / len(nanos)


if __name__ == '__main__':
    kou = TixyHandler('kou', 'langs/kou/tixy.wasm')
    rust = TixyHandler('rust', 'langs/rust/tixy.wasm')
    assemblyscript = TixyHandler('assemblyscript', 'langs/assemblyscript/build/tixy.wasm')
    zig = TixyHandler('zig', 'langs/zig/tixy.wasm')

    pygame.init()
    # use None fo pygame default font
    # if your system doesn't find the font, try replacing path with output of :
    # print(pygame.font.match_font('Courier'))
    print("Creating font")
    font = pygame.font.Font("font/SourceCodePro/SourceCodePro-Regular.ttf", 24)
    base_ticks = pygame.time.get_ticks()
    size = (GRID_SIZE + 2) * CIRC_SIZE, (GRID_SIZE + 2) * CIRC_SIZE

    full_size = (X_GRIDS * GRID_SIZE + X_GRIDS+1) * CIRC_SIZE, (
            Y_GRIDS * GRID_SIZE + Y_GRIDS+1) * CIRC_SIZE
    background = 0x2b, 0x2b, 0x2b
    screen = pygame.display.set_mode(full_size)
    pygame.display.set_caption("TIXY WASP")
    square = []
    calculate_squares()

    iterations = 0
    while 1:
        iterations += 1
        if iterations % 3 == 0:
            twist_color(primary)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: sys.exit()
                if event.key == pygame.K_SPACE: primary = nice_random_color()
                if event.key == pygame.K_RETURN: base_ticks = pygame.time.get_ticks()

        if event.type == pygame.QUIT: sys.exit()

        screen.fill(background)

        corner = (GRID_SIZE + 1) * CIRC_SIZE
        screen.blit(render(rust), square[0])
        screen.blit(render(kou), square[1])
        screen.blit(render(assemblyscript), square[2])
        screen.blit(render(zig), square[3])
        # screen.blit(render(some_lang1), square[2])
        # screen.blit(render(some_lang2), square[3])
        # screen.blit(render(some_lang3), square[4])
        # screen.blit(render(some_lang4), square[5])

        pygame.display.flip()
