from __future__ import annotations

import pyxel

from .config import (
    SCREEN_SIZE,
    SPRITE_BLOCKER,
    SPRITE_ENTRANCE,
    SPRITE_EXIT,
    SPRITE_LEMMING_DEAD,
    SPRITE_LEMMING_UMBRELLA,
    SPRITE_LEMMING_WALK,
    SPRITE_PLATFORM,
    SPRITE_SHOVEL,
    SPRITE_STAIRS_LEFT,
    SPRITE_STAIRS_RIGHT,
    SPRITE_TORCH,
    SPRITE_UMBRELLA,
    TILE_SIZE,
    TRANSPARENT_COLOR,
    Tile,
)
from .lemming import Lemming
from .level import Level
from .tools import ToolKind

BACKGROUND = 0
MENU_BACKGROUND = 1
TEXT_COLOR = 7
CHAR_WIDTH = 4

TOOL_SPRITES = {
    ToolKind.UMBRELLA: SPRITE_UMBRELLA,
    ToolKind.BLOCKER: SPRITE_BLOCKER,
    ToolKind.STAIRS_RIGHT: SPRITE_STAIRS_RIGHT,
    ToolKind.STAIRS_LEFT: SPRITE_STAIRS_LEFT,
    ToolKind.SHOVEL: SPRITE_SHOVEL,
}

CONTROLS = (
    "CONTROLS\n\n"
    " Release Lemmings - L\n"
    " Umbrella - P\n"
    " Blocker - B\n"
    " Stairs - D / I\n"
    " Shovel - C\n"
    " Restart - R\n"
    " Toggle Music - M\n"
    " Quit - Q"
)


def flashing_color() -> int:
    return pyxel.frame_count % 16


def centered_text(y: int, text: str, color: int) -> None:
    pyxel.text((SCREEN_SIZE - len(text) * CHAR_WIDTH) // 2, y, text, color)


def draw_title_screen() -> None:
    pyxel.cls(MENU_BACKGROUND)
    centered_text(120, "PRESS ENTER TO START", flashing_color())
    pyxel.text(140, 170, CONTROLS, TEXT_COLOR)


def draw_message_screen(title: str, hint: str) -> None:
    pyxel.cls(MENU_BACKGROUND)
    centered_text(80, title, flashing_color())
    centered_text(100, hint, flashing_color())


def draw_level(level: Level, level_number: int) -> None:
    pyxel.cls(BACKGROUND)
    _draw_hud(level, level_number)
    _draw_board(level)
    for tool in level.tools:
        _sprite(level.board.theme, tool.x, tool.y, TOOL_SPRITES[tool.kind])
    for lemming in level.lemmings:
        _draw_lemming(level.board.theme, lemming)


def _draw_hud(level: Level, level_number: int) -> None:
    pyxel.text(10, 5, f"LEVEL: {level_number}", flashing_color())
    pyxel.text(70, 5, f"SAVED: {level.saved}", TEXT_COLOR)
    pyxel.text(130, 5, f"DEAD: {level.dead}", TEXT_COLOR)
    pyxel.text(210, 5, f"ALIVE: {level.alive}", TEXT_COLOR)
    pyxel.text(10, 20, f"STAIRS: {level.remaining['stairs']}", TEXT_COLOR)
    pyxel.text(70, 20, f"UMBRELLAS: {level.remaining['umbrella']}", TEXT_COLOR)
    pyxel.text(130, 20, f"BLOCKERS: {level.remaining['blocker']}", TEXT_COLOR)
    pyxel.text(210, 20, f"SHOVELS: {level.remaining['shovel']}", TEXT_COLOR)


def _draw_board(level: Level) -> None:
    board = level.board
    for tile, sprite in ((Tile.PLATFORM, SPRITE_PLATFORM), (Tile.TORCH, SPRITE_TORCH)):
        for col, column in enumerate(board.grid):
            for row, cell in enumerate(column):
                if cell == tile:
                    _sprite(board.theme, col * TILE_SIZE, row * TILE_SIZE, sprite, transparent=False)
    _sprite(board.theme, *board.entrance, SPRITE_ENTRANCE, transparent=False)
    _sprite(board.theme, *board.exit, SPRITE_EXIT, transparent=False)


def _draw_lemming(theme: int, lemming: Lemming) -> None:
    if lemming.dead:
        _sprite(theme, lemming.x, lemming.y, SPRITE_LEMMING_DEAD)
        return
    sprites = SPRITE_LEMMING_UMBRELLA if lemming.has_umbrella else SPRITE_LEMMING_WALK
    _sprite(theme, lemming.x, lemming.y, sprites[lemming.skin], flip=not lemming.facing_right)


def _sprite(
    bank: int,
    x: int,
    y: int,
    uv: tuple[int, int],
    *,
    flip: bool = False,
    transparent: bool = True,
) -> None:
    width = -TILE_SIZE if flip else TILE_SIZE
    colkey = TRANSPARENT_COLOR if transparent else None
    pyxel.blt(x, y, bank, uv[0], uv[1], width, TILE_SIZE, colkey)
