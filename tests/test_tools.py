import pytest

from lemmings.config import TILE_SIZE
from lemmings.tools import Tool, ToolKind

CELL = (5, 10)
X = CELL[0] * TILE_SIZE


@pytest.mark.parametrize("kind", [ToolKind.UMBRELLA, ToolKind.STAIRS_RIGHT, ToolKind.STAIRS_LEFT])
def test_tools_trigger_when_the_lemming_is_inside_them(kind: ToolKind) -> None:
    tool = Tool(kind, *CELL)
    assert tool.is_touched_by(CELL, X - 7, facing_right=True)
    assert tool.is_touched_by(CELL, X + 7, facing_right=False)
    assert not tool.is_touched_by((4, 10), X - 9, facing_right=True)
    assert not tool.is_touched_by((5, 9), X, facing_right=True)


def test_shovel_waits_until_the_lemming_is_lined_up_with_the_block() -> None:
    tool = Tool(ToolKind.SHOVEL, *CELL)
    assert not tool.is_touched_by(CELL, X - 7, facing_right=True)
    assert not tool.is_touched_by(CELL, X + 7, facing_right=False)
    assert tool.is_touched_by(CELL, X, facing_right=True)
    assert tool.is_touched_by(CELL, X, facing_right=False)


def test_blocker_triggers_from_the_cell_in_front() -> None:
    tool = Tool(ToolKind.BLOCKER, *CELL)
    assert tool.is_touched_by((4, 10), X - TILE_SIZE, facing_right=True)
    assert tool.is_touched_by((6, 10), X + TILE_SIZE, facing_right=False)
    assert not tool.is_touched_by((4, 10), X - TILE_SIZE, facing_right=False)


def test_pixel_position() -> None:
    tool = Tool(ToolKind.STAIRS_LEFT, 3, 7)
    assert (tool.x, tool.y) == (3 * TILE_SIZE, 7 * TILE_SIZE)
    assert tool.kind.pool == ToolKind.STAIRS_RIGHT.pool == "stairs"
