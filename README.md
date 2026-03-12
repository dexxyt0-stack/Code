# Conway's Game of Life - Terminal Edition

A colorful, zero-dependency terminal implementation of [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

Watch complexity emerge from four simple rules:
1. Any live cell with 2 or 3 neighbors survives
2. Any dead cell with exactly 3 neighbors becomes alive
3. All other cells die or stay dead
4. Cells age over time, shifting color from green to red

## Quick Start

```
python life.py
```

That's it. No dependencies needed - just Python 3.

## Options

```
python life.py --pattern glider       # Classic glider
python life.py --pattern gosper        # Gosper glider gun (infinite growth!)
python life.py --pattern pulsar        # Period-3 oscillator
python life.py --pattern rpentomino    # Tiny pattern, huge chaos
python life.py --pattern acorn         # Takes 5206 gens to stabilize
python life.py --pattern diehard       # Dies after exactly 130 gens
python life.py --pattern pentadecathlon # Period-15 oscillator
python life.py --pattern lwss          # Lightweight spaceship

python life.py -W 80 -H 40            # Custom grid size
python life.py --speed 5              # Slower (5 gens/sec)
python life.py --speed 30             # Faster (30 gens/sec)
python life.py --density 0.5          # Denser random soup
```

Press `Ctrl+C` to stop.

## How It Works

The grid wraps around (toroidal topology), so gliders and spaceships fly forever. Cells age each generation, cycling through colors from fresh green to old red - so you can visually trace how the pattern evolves.

## Favorites to Try

- **`--pattern gosper`** - The Gosper glider gun. First known pattern with unbounded growth. Fires a new glider every 30 generations.
- **`--pattern rpentomino`** - Just 5 cells, but takes 1103 generations to stabilize into a mix of still lifes, oscillators, and 6 escaping gliders.
- **`--pattern acorn`** - 7 cells that produce a massive methuselah lasting 5206 generations.
