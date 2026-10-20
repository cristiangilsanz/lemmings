import random

import pytest

from lemmings.board import Board
from lemmings.config import CEILING_ROW, FLOOR_ROW, GRID_SIZE, HUD_ROWS, TILE_SIZE, Tile
from lemmings.level import Level

FLOOR_Y = (FLOOR_ROW - 1) * TILE_SIZE


@pytest.fixture
def empty_board() -> Board:
    grid = [[Tile.EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]
    for row in range(GRID_SIZE):
        grid[0][row] = grid[GRID_SIZE - 1][row] = Tile.PLATFORM
    for col in range(GRID_SIZE):
        grid[col][FLOOR_ROW] = grid[col][CEILING_ROW] = Tile.PLATFORM
        for row in range(HUD_ROWS):
            grid[col][row] = Tile.HUD
    return Board(grid=grid, theme=0, entrance=(2 * TILE_SIZE, FLOOR_Y), exit=(13 * TILE_SIZE, FLOOR_Y))


@pytest.fixture
def level(empty_board: Board) -> Level:
    return Level(empty_board, total_lemmings=10, rng=random.Random(0))
