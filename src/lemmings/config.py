from enum import IntEnum
from pathlib import Path

SCREEN_SIZE = 256
TILE_SIZE = 16
GRID_SIZE = SCREEN_SIZE // TILE_SIZE
FPS = 60
WINDOW_TITLE = "Lemmings - by Alberto García Arribas & Cristian Gil Sanz"
RESOURCE_FILE = Path(__file__).parent / "assets" / "resources.pyxres"
THEME_COUNT = 3


class Tile(IntEnum):
    EMPTY = 0
    PLATFORM = 1
    UMBRELLA = 2
    BLOCKER = 3
    STAIRS_RIGHT = 4
    STAIRS_LEFT = 5
    TORCH = 6
    HUD = 7
    SHOVEL = 8


SOLID_TILES = frozenset({Tile.PLATFORM, Tile.HUD})
PLACEABLE_TILES = frozenset({Tile.EMPTY, Tile.TORCH})

HUD_ROWS = 2
CEILING_ROW = 2
FLOOR_ROW = GRID_SIZE - 1
PLATFORM_COUNT = 7
PLATFORM_ROWS = range(3, GRID_SIZE - 1)
PLATFORM_WIDTHS = range(5, 11)
TORCH_COUNT = range(5, 13)

LEMMINGS_PER_LEVEL = range(10, 21)
SPAWN_INTERVAL_FRAMES = 51
MOVE_EVERY_N_FRAMES = 2
MAX_STEP_HEIGHT = 2
LETHAL_FALL_DISTANCE = 32
TOOL_LIMITS = {"umbrella": 4, "blocker": 2, "stairs": 5, "shovel": 2}


def lemmings_needed(total: int) -> int:
    return total // 2 + 2


SPRITE_PLATFORM = (32, 0)
SPRITE_TORCH = (48, 0)
SPRITE_ENTRANCE = (32, 16)
SPRITE_EXIT = (32, 32)
SPRITE_UMBRELLA = (0, 16)
SPRITE_BLOCKER = (48, 32)
SPRITE_STAIRS_RIGHT = (32, 48)
SPRITE_STAIRS_LEFT = (48, 48)
SPRITE_SHOVEL = (32, 64)
SPRITE_LEMMING_DEAD = (48, 16)
SPRITE_LEMMING_WALK = ((0, 32), (0, 48))
SPRITE_LEMMING_UMBRELLA = ((16, 32), (16, 48))
TRANSPARENT_COLOR = 0
