# TIXY-WASP: Tixy WebAssembly demo in Python

from wasmer import engine, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler
import sys, pygame
import random, time


def nice_random_color() -> pygame.Color:
    angle = random.randrange(0, 360)
    sat = random.randrange(50, 100)
    val = 80
    col = pygame.Color(0, 0, 0)
    col.hsva = (angle, sat, val, 100)
    return col


GRID_SIZE = 32
CIRC_SIZE = 48
TIMING_RUNS = 64
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


def calculate_average(delta_nanos, nanos):
    l = len(nanos)
    nanos.append(delta_nanos)
    if l >= TIMING_RUNS: nanos.pop(0)
    if l == TIMING_RUNS:
        avg_nanos = sum(nanos) / len(nanos)
        return avg_nanos
    return 0


def render_average_timing(delta_nanos, nanos, iterations):
    avg_nanos = calculate_average(delta_nanos, nanos)
    cells = GRID_SIZE * GRID_SIZE
    if avg_nanos:
        delta_text = font.render(
            "%4.2f µs  %.1fM calls" % (avg_nanos / (GRID_SIZE * GRID_SIZE) / 1000.0, iterations * cells / 1000000.0),
            False, white)
        screen.blit(delta_text, dest=(4, 4))


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


def get_wasm_exports(fileName):
    # Let's define the store, that holds the engine, that holds the compiler.
    store = Store(engine.JIT(Compiler))

    # get bytes from wasm module
    wasm_bytes = open(fileName, 'rb').read()

    # Let's compile the module to be able to execute it!
    module = Module(store, wasm_bytes)

    # Now the module is compiled, we can instantiate it.
    instance = Instance(module)

    # return the dict of exported functions
    return instance.exports


def generate_grid_values(tixy):
    time_seconds = (pygame.time.get_ticks() - base_ticks) / 1000.0
    index = 0
    values = []
    for x in range(0, GRID_SIZE):
        for y in range(0, GRID_SIZE):
            values.append((x, y, tixy(time_seconds, index, x, y)))
            index += 1
    return values


if __name__ == '__main__':
    kou_tixy = get_wasm_exports(
        'langs/kou/tixy.wasm'
    ).tixy
    rust_tixy = get_wasm_exports(
        'langs/rust/target/wasm32-unknown-unknown/release/tixy.wasm'
    ).tixy

    pygame.init()
    font = pygame.font.Font(None, 24)
    base_ticks = pygame.time.get_ticks()
    size = (GRID_SIZE + 2) * CIRC_SIZE, (GRID_SIZE + 2) * CIRC_SIZE
    background = 0x2b, 0x2b, 0x2b
    screen = pygame.display.set_mode(size)

    iterations = 0
    delta_nanos = 0
    nanos = []
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

        start_nanos = time.perf_counter_ns()
        if iterations % 100 > 50:
            values = generate_grid_values(rust_tixy)
        else:
            values = generate_grid_values(kou_tixy)
        delta_nanos = time.perf_counter_ns() - start_nanos

        screen.fill(background)
        render_average_timing(delta_nanos, nanos, iterations)
        render_grid(screen, values)

        pygame.display.flip()
