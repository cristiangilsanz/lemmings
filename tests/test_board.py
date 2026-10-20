import random

import pytest

from lemmings.board import Board
from lemmings.config import (
    CEILING_ROW,
    FLOOR_ROW,
    GRID_SIZE,
    HUD_ROWS,
    PLATFORM_ROWS,
    SCREEN_SIZE,
    TILE_SIZE,
    Tile,
)

SEEDS = range(200)


@pytest.mark.parametrize("seed", SEEDS)
def test_board_is_enclosed(seed: int) -> None:
    grid = Board.generate(random.Random(seed)).grid
    for row in range(HUD_ROWS, GRID_SIZE):
        assert grid[0][row] == grid[GRID_SIZE - 1][row] == Tile.PLATFORM
    for col in range(GRID_SIZE):
        assert grid[col][FLOOR_ROW] == grid[col][CEILING_ROW] == Tile.PLATFORM
        assert all(grid[col][row] == Tile.HUD for row in range(HUD_ROWS))


@pytest.mark.parametrize("seed", SEEDS)
def test_entrance_and_exit_stand_on_platforms(seed: int) -> None:
    board = Board.generate(random.Random(seed))
    for x, y in (board.entrance, board.exit):
        col, row = x // TILE_SIZE, y // TILE_SIZE
        assert row + 1 in PLATFORM_ROWS
        assert board.grid[col][row + 1] == Tile.PLATFORM
        assert board.grid[col][row] != Tile.PLATFORM, "no platform directly above"
        assert row > CEILING_ROW


@pytest.mark.parametrize("seed", SEEDS)
def test_seven_floating_platforms(seed: int) -> None:
    grid = Board.generate(random.Random(seed)).grid
    rows_with_platforms = [
        row
        for row in PLATFORM_ROWS
        if any(grid[col][row] == Tile.PLATFORM for col in range(1, GRID_SIZE - 1))
    ]
    assert len(rows_with_platforms) == 7


def test_same_seed_gives_same_board() -> None:
    assert Board.generate(random.Random(42), 1) == Board.generate(random.Random(42), 1)


def test_tile_at_treats_off_map_as_solid() -> None:
    board = Board.generate(random.Random(0))
    for x, y in ((-1, 100), (100, -1), (SCREEN_SIZE, 100), (100, SCREEN_SIZE)):
        assert board.tile_at(x, y) == Tile.PLATFORM
        assert board.is_solid(x, y)


def test_hud_rows_are_solid() -> None:
    board = Board.generate(random.Random(0))
    assert board.is_solid(5 * TILE_SIZE, 0)
