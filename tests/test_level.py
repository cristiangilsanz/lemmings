import pytest
from conftest import FLOOR_Y

from lemmings.config import FLOOR_ROW, SPAWN_INTERVAL_FRAMES, TILE_SIZE, TOOL_LIMITS, Tile, lemmings_needed
from lemmings.lemming import Lemming
from lemmings.level import Level, Outcome
from lemmings.tools import ToolKind

ROW = FLOOR_ROW - 1


def test_place_and_pick_up_a_tool(level: Level) -> None:
    level.toggle_tool(ToolKind.UMBRELLA, 5, ROW)
    assert level.board.grid[5][ROW] == Tile.UMBRELLA
    assert level.remaining["umbrella"] == TOOL_LIMITS["umbrella"] - 1

    level.toggle_tool(ToolKind.UMBRELLA, 5, ROW)
    assert level.board.grid[5][ROW] == Tile.EMPTY
    assert level.remaining["umbrella"] == TOOL_LIMITS["umbrella"]
    assert level.tools == []


def test_tool_limit(level: Level) -> None:
    for col in range(1, 10):
        level.toggle_tool(ToolKind.BLOCKER, col, ROW)
    assert len(level.tools) == TOOL_LIMITS["blocker"]
    assert level.remaining["blocker"] == 0


def test_both_stairs_share_one_pool(level: Level) -> None:
    for col in range(1, 4):
        level.toggle_tool(ToolKind.STAIRS_RIGHT, col, ROW)
    for col in range(4, 10):
        level.toggle_tool(ToolKind.STAIRS_LEFT, col, ROW)
    assert len(level.tools) == TOOL_LIMITS["stairs"]


@pytest.mark.parametrize("tile", [Tile.PLATFORM, Tile.HUD, Tile.BLOCKER])
def test_cannot_place_on_occupied_cells(level: Level, tile: Tile) -> None:
    level.board.grid[5][ROW] = tile
    level.toggle_tool(ToolKind.UMBRELLA, 5, ROW)
    assert level.tools == []


def test_can_place_on_a_torch_and_get_it_back(level: Level) -> None:
    level.board.grid[5][ROW] = Tile.TORCH
    level.toggle_tool(ToolKind.BLOCKER, 5, ROW)
    level.toggle_tool(ToolKind.BLOCKER, 5, ROW)
    assert level.board.grid[5][ROW] == Tile.TORCH


def test_shovel_cannot_dig_through_the_floor(level: Level) -> None:
    level.toggle_tool(ToolKind.SHOVEL, 5, FLOOR_ROW - 1)
    assert level.tools == []


def test_used_tool_cannot_be_picked_up(level: Level) -> None:
    level.toggle_tool(ToolKind.UMBRELLA, 5, ROW)
    level.lemmings.append(Lemming(level.board, 5 * TILE_SIZE, FLOOR_Y, skin=0))
    level.step()
    level.toggle_tool(ToolKind.UMBRELLA, 5, ROW)
    assert len(level.tools) == 1
    assert level.board.grid[5][ROW] == Tile.UMBRELLA


def test_shovel_digs_a_hole_and_disappears(level: Level) -> None:
    row = 10
    level.board.grid[5][row + 1] = Tile.PLATFORM
    level.toggle_tool(ToolKind.SHOVEL, 5, row)
    level.lemmings.append(Lemming(level.board, 5 * TILE_SIZE, row * TILE_SIZE, skin=0))
    level.step()
    assert level.tools == []
    assert level.board.grid[5][row] == level.board.grid[5][row + 1] == Tile.EMPTY
    assert level.remaining["shovel"] == TOOL_LIMITS["shovel"] - 1


def test_lemmings_spawn_at_a_fixed_interval(level: Level) -> None:
    level.release_lemmings()
    for _ in range(SPAWN_INTERVAL_FRAMES - 1):
        level.step()
    assert level.spawned == 0
    level.step()
    assert level.spawned == 1
    assert (level.lemmings[0].x, level.lemmings[0].y) == level.board.entrance


def test_reaching_the_exit_saves_a_lemming(level: Level) -> None:
    exit_x, exit_y = level.board.exit
    level.lemmings.append(Lemming(level.board, exit_x - 1, exit_y, skin=0))
    for _ in range(2):
        level.step()
    assert level.saved == 1
    assert level.lemmings == []


def test_dead_lemmings_are_counted_once(level: Level) -> None:
    lemming = Lemming(level.board, 32, FLOOR_Y, skin=0)
    lemming.dead = True
    level.lemmings.append(lemming)
    level.step()
    level.step()
    assert level.dead == 1
    assert level.alive == level.total_lemmings - 1


def test_outcomes(level: Level) -> None:
    needed = lemmings_needed(level.total_lemmings)
    assert level.outcome == Outcome.PLAYING
    level.saved = needed
    assert level.outcome == Outcome.WON
    level.saved, level.dead = 0, needed
    assert level.outcome == Outcome.LOST


def test_level_ends_when_everyone_is_out(level: Level) -> None:
    level.spawned = level.total_lemmings
    level.saved = lemmings_needed(level.total_lemmings) - 1
    assert level.outcome == Outcome.LOST


def test_stairs_cannot_be_built_through_a_lemming(level: Level) -> None:
    level.lemmings.append(Lemming(level.board, 5 * TILE_SIZE + 3, FLOOR_Y, skin=0))
    level.toggle_tool(ToolKind.STAIRS_RIGHT, 5, ROW)
    assert level.tools == []
    level.toggle_tool(ToolKind.UMBRELLA, 5, ROW)
    assert len(level.tools) == 1


@pytest.mark.parametrize(("start_x", "direction"), [(3 * TILE_SIZE, 1), (8 * TILE_SIZE, -1)])
def test_lemming_drops_through_the_middle_of_a_shovel_hole(
    level: Level, start_x: int, direction: int
) -> None:
    row = 10
    for col in range(1, 10):
        level.board.grid[col][row + 1] = Tile.PLATFORM
    level.toggle_tool(ToolKind.SHOVEL, 5, row)
    lemming = Lemming(level.board, start_x, row * TILE_SIZE, skin=0)
    lemming.direction = direction
    level.lemmings.append(lemming)
    for _ in range(8 * TILE_SIZE):
        level.step()
        if level.board.grid[5][row + 1] == Tile.EMPTY:
            break
    assert level.board.grid[5][row + 1] == Tile.EMPTY, "the shovel never dug"
    assert lemming.x == 5 * TILE_SIZE, "the hole opened before the lemming was lined up"
    for _ in range(20):
        level.step()
    assert lemming.x == 5 * TILE_SIZE and lemming.y > (row + 1) * TILE_SIZE, "it fell straight down"
