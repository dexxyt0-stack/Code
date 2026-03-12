"""
Conway's Game of Life - Terminal Edition

A clean, colorful terminal implementation of Conway's Game of Life.
Run it and watch complexity emerge from simplicity.

Usage:
    python life.py                 # Random soup
    python life.py --pattern glider
    python life.py --pattern pulsar
    python life.py --pattern gosper # Gosper glider gun
    python life.py --pattern rpentomino
    python life.py -w 60 -h 30     # Custom grid size
    python life.py --speed 5       # Generations per second
"""

import argparse
import os
import sys
import time
from copy import deepcopy

# ── ANSI helpers ──────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_SCREEN = "\033[2J\033[H"

COLORS = [
    "\033[38;5;34m",   # green
    "\033[38;5;70m",   # light-green
    "\033[38;5;106m",  # yellow-green
    "\033[38;5;142m",  # olive
    "\033[38;5;178m",  # gold
    "\033[38;5;214m",  # orange
    "\033[38;5;208m",  # dark-orange
    "\033[38;5;196m",  # red (old cells)
]

ALIVE_CHAR = "\u2588\u2588"  # Full block x2 for square-ish cells
DEAD_CHAR = "  "


# ── Grid / simulation ────────────────────────────────────────────────────

def make_grid(width, height):
    return [[0] * width for _ in range(height)]


def neighbor_count(grid, x, y, width, height):
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = (x + dx) % width, (y + dy) % height
            if grid[ny][nx] > 0:
                count += 1
    return count


def step(grid, width, height):
    """Advance one generation. Cell values track age (0 = dead, 1+ = alive)."""
    new = make_grid(width, height)
    for y in range(height):
        for x in range(width):
            n = neighbor_count(grid, x, y, width, height)
            if grid[y][x] > 0:
                if n in (2, 3):
                    new[y][x] = min(grid[y][x] + 1, len(COLORS))
                # else dies (stays 0)
            else:
                if n == 3:
                    new[y][x] = 1
    return new


def population(grid):
    return sum(cell > 0 for row in grid for cell in row)


# ── Patterns ──────────────────────────────────────────────────────────────

PATTERNS = {}


def _register(name, cells):
    """Register a pattern as a list of (x, y) offsets."""
    PATTERNS[name] = cells


_register("glider", [
    (0, 1), (1, 2), (2, 0), (2, 1), (2, 2),
])

_register("lwss", [  # Lightweight spaceship
    (0, 1), (0, 3), (1, 4), (2, 0), (2, 4), (3, 1), (3, 2), (3, 3), (3, 4),
])

_register("rpentomino", [
    (1, 0), (2, 0), (0, 1), (1, 1), (1, 2),
])

_register("diehard", [
    (6, 0), (0, 1), (1, 1), (1, 2), (5, 2), (6, 2), (7, 2),
])

_register("acorn", [
    (1, 0), (3, 1), (0, 2), (1, 2), (4, 2), (5, 2), (6, 2),
])

_register("pulsar", [
    # Quarter pattern, mirrored 4 ways
    *[(x, y) for x, y in [
        (2, 0), (3, 0), (4, 0), (0, 2), (0, 3), (0, 4),
        (5, 2), (5, 3), (5, 4), (2, 5), (3, 5), (4, 5),
    ]],
    *[(x + 7, y) for x, y in [
        (0, 0), (1, 0), (2, 0), (-1, 2), (-1, 3), (-1, 4),
        (3, 2), (3, 3), (3, 4), (0, 5), (1, 5), (2, 5),
    ]],
    *[(x, y + 7) for x, y in [
        (2, -1), (3, -1), (4, -1), (0, 0), (0, 1), (0, 2),
        (5, 0), (5, 1), (5, 2), (2, 3), (3, 3), (4, 3),
    ]],
    *[(x + 7, y + 7) for x, y in [
        (0, -1), (1, -1), (2, -1), (-1, 0), (-1, 1), (-1, 2),
        (3, 0), (3, 1), (3, 2), (0, 3), (1, 3), (2, 3),
    ]],
])

_register("gosper", [
    # Gosper glider gun
    (24, 0),
    (22, 1), (24, 1),
    (12, 2), (13, 2), (20, 2), (21, 2), (34, 2), (35, 2),
    (11, 3), (15, 3), (20, 3), (21, 3), (34, 3), (35, 3),
    (0, 4), (1, 4), (10, 4), (16, 4), (20, 4), (21, 4),
    (0, 5), (1, 5), (10, 5), (14, 5), (16, 5), (17, 5), (22, 5), (24, 5),
    (10, 6), (16, 6), (24, 6),
    (11, 7), (15, 7),
    (12, 8), (13, 8),
])

_register("pentadecathlon", [
    (1, 0), (2, 0), (3, 0),
    (0, 1), (4, 1),
    (0, 2), (4, 2),
    (1, 3), (2, 3), (3, 3),
    (1, 5), (2, 5), (3, 5),
    (0, 6), (4, 6),
    (0, 7), (4, 7),
    (1, 8), (2, 8), (3, 8),
])


def place_pattern(grid, name, width, height):
    cells = PATTERNS[name]
    max_x = max(c[0] for c in cells)
    max_y = max(c[1] for c in cells)
    ox = (width - max_x) // 2
    oy = (height - max_y) // 2
    for x, y in cells:
        px, py = (ox + x) % width, (oy + y) % height
        grid[py][px] = 1


def random_soup(grid, width, height, density=0.3):
    import random
    for y in range(height):
        for x in range(width):
            grid[y][x] = 1 if random.random() < density else 0


# ── Rendering ─────────────────────────────────────────────────────────────

def render(grid, width, height, gen, pop):
    lines = [CLEAR_SCREEN]
    top_bar = f"  {BOLD}Conway's Game of Life{RESET}  |  Gen: {gen}  |  Pop: {pop}  |  {DIM}Ctrl+C to quit{RESET}"
    lines.append(top_bar)
    lines.append("  " + "\u2500" * (width * 2))
    for row in grid:
        parts = []
        for cell in row:
            if cell > 0:
                color_idx = min(cell - 1, len(COLORS) - 1)
                parts.append(f"{COLORS[color_idx]}{ALIVE_CHAR}{RESET}")
            else:
                parts.append(DEAD_CHAR)
        lines.append("  " + "".join(parts))
    lines.append("  " + "\u2500" * (width * 2))
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Conway's Game of Life in the terminal")
    parser.add_argument("-W", "--width", type=int, default=40, help="Grid width (default: 40)")
    parser.add_argument("-H", "--height", type=int, default=20, help="Grid height (default: 20)")
    parser.add_argument("-p", "--pattern", choices=list(PATTERNS.keys()),
                        help="Starting pattern (default: random soup)")
    parser.add_argument("-s", "--speed", type=float, default=10,
                        help="Generations per second (default: 10)")
    parser.add_argument("-d", "--density", type=float, default=0.3,
                        help="Random soup density 0-1 (default: 0.3)")
    args = parser.parse_args()

    # Auto-fit to terminal if it's big enough
    try:
        term = os.get_terminal_size()
        max_w = (term.columns - 4) // 2
        max_h = term.lines - 5
        if args.width > max_w:
            args.width = max_w
        if args.height > max_h:
            args.height = max_h
    except OSError:
        pass

    grid = make_grid(args.width, args.height)

    if args.pattern:
        place_pattern(grid, args.pattern, args.width, args.height)
    else:
        random_soup(grid, args.width, args.height, args.density)

    delay = 1.0 / args.speed
    gen = 0

    sys.stdout.write(HIDE_CURSOR)
    try:
        while True:
            pop = population(grid)
            render(grid, args.width, args.height, gen, pop)
            time.sleep(delay)
            grid = step(grid, args.width, args.height)
            gen += 1
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR + "\n")
        print(f"\nSimulation ended after {gen} generations.")


if __name__ == "__main__":
    main()
