import pytest
from conftest import FLOOR_Y

from lemmings.board import Board
from lemmings.config import FLOOR_ROW, GRID_SIZE, TILE_SIZE, Tile
from lemmings.lemming import LEFT, RIGHT, Lemming


def run(lemming: Lemming, frames: int) -> None:
    for _ in range(frames):
        lemming.update()


def test_walks_one_pixel_every_two_frames(empty_board: Board) -> None:
    lemming = Lemming(empty_board, 32, FLOOR_Y, skin=0)
    run(lemming, 20)
    assert (lemming.x, lemming.y) == (42, FLOOR_Y)


def test_turns_around_at_a_wall(empty_board: Board) -> None:
    wall_x = (GRID_SIZE - 1) * TILE_SIZE
    lemming = Lemming(empty_board, wall_x - TILE_SIZE - 2, FLOOR_Y, skin=0)
    run(lemming, 10)
    assert lemming.direction == LEFT
    assert lemming.x + TILE_SIZE <= wall_x


def test_bounces_off_a_blocker(empty_board: Board) -> None:
    empty_board.grid[5][FLOOR_ROW - 1] = Tile.BLOCKER
    lemming = Lemming(empty_board, 3 * TILE_SIZE, FLOOR_Y, skin=0)
    run(lemming, 4 * TILE_SIZE)
    assert lemming.direction == LEFT
    assert lemming.x <= 4 * TILE_SIZE


def test_long_fall_is_lethal(empty_board: Board) -> None:
    lemming = Lemming(empty_board, 32, FLOOR_Y - 4 * TILE_SIZE, skin=0)
    run(lemming, 100)
    assert lemming.dead
    assert lemming.y == FLOOR_Y


def test_short_fall_is_safe(empty_board: Board) -> None:
    lemming = Lemming(empty_board, 32, FLOOR_Y - TILE_SIZE, skin=0)
    run(lemming, 100)
    assert not lemming.dead


def test_umbrella_breaks_a_long_fall_once(empty_board: Board) -> None:
    lemming = Lemming(empty_board, 32, FLOOR_Y - 4 * TILE_SIZE, skin=0)
    lemming.has_umbrella = True
    run(lemming, 200)
    assert not lemming.dead
    assert not lemming.has_umbrella


def test_umbrella_halves_the_fall_speed(empty_board: Board) -> None:
    falling = Lemming(empty_board, 32, FLOOR_Y - 4 * TILE_SIZE, skin=0)
    floating = Lemming(empty_board, 32, FLOOR_Y - 4 * TILE_SIZE, skin=0)
    floating.has_umbrella = True
    run(falling, 10)
    run(floating, 10)
    assert falling.y - (FLOOR_Y - 4 * TILE_SIZE) == 2 * (floating.y - (FLOOR_Y - 4 * TILE_SIZE))


def test_picks_up_an_umbrella_tile(empty_board: Board) -> None:
    empty_board.grid[2][FLOOR_ROW - 1] = Tile.UMBRELLA
    lemming = Lemming(empty_board, 2 * TILE_SIZE, FLOOR_Y, skin=0)
    lemming.update()
    assert lemming.has_umbrella


def test_never_climbs_into_the_ceiling(empty_board: Board) -> None:
    empty_board.grid[4][3] = Tile.STAIRS_RIGHT
    for col in range(1, GRID_SIZE - 1):
        empty_board.grid[col][4] = Tile.PLATFORM
    lemming = Lemming(empty_board, 3 * TILE_SIZE, 3 * TILE_SIZE, skin=0)
    for _ in range(2000):
        lemming.update()
        assert lemming.y >= 3 * TILE_SIZE - 1
        assert TILE_SIZE - 1 <= lemming.x <= (GRID_SIZE - 2) * TILE_SIZE + 1


def test_starts_facing_right(empty_board: Board) -> None:
    assert Lemming(empty_board, 32, FLOOR_Y, skin=1).direction == RIGHT


def assert_smooth(path: list[tuple[int, int, int]]) -> None:
    for (x0, y0, _), (x1, y1, _) in zip(path, path[1:], strict=False):
        assert abs(x1 - x0) <= 1
        assert abs(y1 - y0) <= 2
    vertical = [b[1] - a[1] for a, b in zip(path, path[1:], strict=False) if b[1] != a[1]]
    assert all(dy < 0 for dy in vertical) or all(dy > 0 for dy in vertical), "y bobs up and down"


def walk(lemming: Lemming, frames: int) -> list[tuple[int, int, int]]:
    path = []
    for _ in range(frames):
        lemming.update()
        path.append((lemming.x, lemming.y, lemming.direction))
    return path


LEDGE_Y = FLOOR_Y - TILE_SIZE


@pytest.mark.parametrize(
    ("stairs", "stairs_col", "ledge_cols", "start_x", "direction"),
    [
        (Tile.STAIRS_RIGHT, 6, range(7, 12), 4 * TILE_SIZE, RIGHT),
        (Tile.STAIRS_LEFT, 9, range(4, 9), 11 * TILE_SIZE, LEFT),
    ],
)
def test_climbs_stairs_onto_a_ledge_smoothly(
    empty_board: Board, stairs: Tile, stairs_col: int, ledge_cols: range, start_x: int, direction: int
) -> None:
    empty_board.grid[stairs_col][FLOOR_ROW - 1] = stairs
    for col in ledge_cols:
        empty_board.grid[col][FLOOR_ROW - 1] = Tile.PLATFORM
    lemming = Lemming(empty_board, start_x, FLOOR_Y, skin=0)
    lemming.direction = direction
    path = walk(lemming, 4 * TILE_SIZE * 2)
    assert_smooth(path)
    assert all(d == direction for *_, d in path), "turned around on the stairs"
    assert lemming.y == LEDGE_Y
    assert not lemming.dead


@pytest.mark.parametrize(
    ("stairs", "stairs_col", "ledge_cols", "start_x", "direction"),
    [
        (Tile.STAIRS_LEFT, 7, range(3, 7), 3 * TILE_SIZE, RIGHT),
        (Tile.STAIRS_RIGHT, 8, range(9, 13), 12 * TILE_SIZE, LEFT),
    ],
)
def test_walks_down_stairs_off_a_ledge_smoothly(
    empty_board: Board, stairs: Tile, stairs_col: int, ledge_cols: range, start_x: int, direction: int
) -> None:
    empty_board.grid[stairs_col][FLOOR_ROW - 1] = stairs
    for col in ledge_cols:
        empty_board.grid[col][FLOOR_ROW - 1] = Tile.PLATFORM
    lemming = Lemming(empty_board, start_x, LEDGE_Y, skin=0)
    lemming.direction = direction
    path = walk(lemming, 6 * TILE_SIZE * 2)
    assert_smooth(path)
    assert lemming.y == FLOOR_Y
    assert lemming.fall_distance == 0
    assert not lemming.dead


def test_staircase_climbs_several_tiles(empty_board: Board) -> None:
    for step in range(3):
        empty_board.grid[5 + step][FLOOR_ROW - 1 - step] = Tile.STAIRS_RIGHT
        for row in range(FLOOR_ROW - step, FLOOR_ROW):
            empty_board.grid[5 + step][row] = Tile.PLATFORM
    for col in range(8, 12):
        for row in range(FLOOR_ROW - 3, FLOOR_ROW):
            empty_board.grid[col][row] = Tile.PLATFORM
    lemming = Lemming(empty_board, 3 * TILE_SIZE, FLOOR_Y, skin=0)
    path = walk(lemming, 7 * TILE_SIZE * 2)
    assert_smooth(path)
    assert lemming.y == FLOOR_Y - 3 * TILE_SIZE


@pytest.mark.parametrize(("start_x", "direction"), [(3 * TILE_SIZE, RIGHT), (8 * TILE_SIZE, LEFT)])
def test_walks_off_an_edge_until_it_is_over_the_gap(empty_board: Board, start_x: int, direction: int) -> None:
    for col in range(1, GRID_SIZE - 1):
        empty_board.grid[col][FLOOR_ROW - 1] = Tile.PLATFORM
    gap = 6
    empty_board.grid[gap][FLOOR_ROW - 1] = Tile.EMPTY
    lemming = Lemming(empty_board, start_x, LEDGE_Y, skin=0)
    lemming.direction = direction
    for _ in range(8 * TILE_SIZE):
        lemming.update()
        if lemming.y > LEDGE_Y:
            break
    assert lemming.y > LEDGE_Y, "it never fell"
    assert lemming.x == gap * TILE_SIZE, "it fell before it was over the gap"
