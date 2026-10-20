from __future__ import annotations

import random
from dataclasses import dataclass

from .config import (
    CEILING_ROW,
    FLOOR_ROW,
    GRID_SIZE,
    HUD_ROWS,
    PLATFORM_COUNT,
    PLATFORM_ROWS,
    PLATFORM_WIDTHS,
    SOLID_TILES,
    TILE_SIZE,
    TORCH_COUNT,
    Tile,
)

Grid = list[list[Tile]]


@dataclass
class Board:
    grid: Grid
    theme: int
    entrance: tuple[int, int]
    exit: tuple[int, int]

    @classmethod
    def generate(cls, rng: random.Random, theme: int = 0) -> Board:
        rows = _pick_platform_rows(rng)
        grid: Grid = [[Tile.EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]

        for row in rows:
            start, end = _pick_platform_span(rng)
            for col in range(start, end):
                grid[col][row] = Tile.PLATFORM

        for _ in range(rng.choice(TORCH_COUNT)):
            col, row = rng.randint(1, GRID_SIZE - 1), rng.randint(CEILING_ROW, GRID_SIZE - 1)
            if grid[col][row] != Tile.PLATFORM:
                grid[col][row] = Tile.TORCH

        for row in range(GRID_SIZE):
            grid[0][row] = grid[GRID_SIZE - 1][row] = Tile.PLATFORM
        for col in range(GRID_SIZE):
            grid[col][FLOOR_ROW] = grid[col][CEILING_ROW] = Tile.PLATFORM
            for row in range(HUD_ROWS):
                grid[col][row] = Tile.HUD

        entrance_row, exit_row = rows[0], rows[1]
        entrance_col = next(c for c in range(1, GRID_SIZE) if grid[c][entrance_row] == Tile.PLATFORM)
        exit_col = rng.choice([c for c in range(1, GRID_SIZE - 1) if grid[c][exit_row] == Tile.PLATFORM])
        return cls(
            grid=grid,
            theme=theme,
            entrance=(entrance_col * TILE_SIZE, (entrance_row - 1) * TILE_SIZE),
            exit=(exit_col * TILE_SIZE, (exit_row - 1) * TILE_SIZE),
        )

    @property
    def exit_cell(self) -> tuple[int, int]:
        return self.exit[0] // TILE_SIZE, self.exit[1] // TILE_SIZE

    def tile_at(self, x: float, y: float) -> Tile:
        col, row = int(x) // TILE_SIZE, int(y) // TILE_SIZE
        if x >= 0 and y >= 0 and col < GRID_SIZE and row < GRID_SIZE:
            return self.grid[col][row]
        return Tile.PLATFORM

    def is_solid(self, x: int, y: int) -> bool:
        tile = self.tile_at(x, y)
        if tile in SOLID_TILES:
            return True
        u, v = x % TILE_SIZE, y % TILE_SIZE
        if tile == Tile.STAIRS_RIGHT:
            return v >= TILE_SIZE - 1 - u
        if tile == Tile.STAIRS_LEFT:
            return v >= u
        return False

    def is_wall(self, x: int, y: int) -> bool:
        return self.tile_at(x, y) in SOLID_TILES


def _pick_platform_rows(rng: random.Random) -> list[int]:
    rows: list[int] = []
    while len(rows) < PLATFORM_COUNT:
        row = rng.choice(PLATFORM_ROWS)
        if row in rows or row in {r - 1 for r in rows[:2]}:
            continue
        if len(rows) < 2 and row == PLATFORM_ROWS.start:
            continue
        if len(rows) == 1 and row == rows[0] + 1:
            continue
        rows.append(row)
    return rows


def _pick_platform_span(rng: random.Random) -> tuple[int, int]:
    while True:
        end, start = rng.randint(1, GRID_SIZE - 1), rng.randint(1, GRID_SIZE - 1)
        if end - start in PLATFORM_WIDTHS:
            return start, end
