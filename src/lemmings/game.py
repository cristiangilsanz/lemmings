from __future__ import annotations

import random
from enum import Enum, auto

import pyxel

from . import renderer
from .config import FPS, GRID_SIZE, RESOURCE_FILE, SCREEN_SIZE, THEME_COUNT, TILE_SIZE, WINDOW_TITLE
from .level import Level, Outcome
from .tools import ToolKind

TOOL_KEYS = {
    pyxel.KEY_P: ToolKind.UMBRELLA,
    pyxel.KEY_B: ToolKind.BLOCKER,
    pyxel.KEY_D: ToolKind.STAIRS_RIGHT,
    pyxel.KEY_I: ToolKind.STAIRS_LEFT,
    pyxel.KEY_C: ToolKind.SHOVEL,
}
MUSIC_TRACK = 0


class Screen(Enum):
    TITLE = auto()
    PLAYING = auto()
    WON = auto()
    LOST = auto()


class Game:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.screen = Screen.TITLE
        self.music_on = False
        self.level_number = 1
        self.level = Level.random(self.rng, theme=0)

    def run(self) -> None:
        pyxel.init(SCREEN_SIZE, SCREEN_SIZE, title=WINDOW_TITLE, fps=FPS)
        pyxel.load(str(RESOURCE_FILE))
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def new_level(self, level_number: int) -> None:
        self.level_number = level_number
        self.level = Level.random(self.rng, theme=self.rng.randrange(THEME_COUNT))

    def update(self) -> None:
        self._handle_global_keys()
        if self.screen != Screen.PLAYING:
            return

        for key, kind in TOOL_KEYS.items():
            if pyxel.btnp(key):
                self.level.toggle_tool(kind, *self._mouse_cell())
        if pyxel.btn(pyxel.KEY_L):
            self.level.release_lemmings()

        self.level.step()
        outcome = self.level.outcome
        if outcome == Outcome.WON:
            self.screen = Screen.WON
        elif outcome == Outcome.LOST:
            self.screen = Screen.LOST

    def draw(self) -> None:
        if self.screen == Screen.TITLE:
            renderer.draw_title_screen()
        elif self.screen == Screen.WON:
            renderer.draw_message_screen("YOU WIN!", "Press ENTER to continue")
        elif self.screen == Screen.LOST:
            renderer.draw_message_screen("YOU LOSE", "Press R to restart")
        else:
            renderer.draw_level(self.level, self.level_number)

    def _handle_global_keys(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_M):
            self._set_music(not self.music_on)

        if pyxel.btnp(pyxel.KEY_RETURN) and self.screen in (Screen.TITLE, Screen.WON):
            if self.screen == Screen.WON:
                self.new_level(self.level_number + 1)
            self.screen = Screen.PLAYING
            self._set_music(True)

        if pyxel.btnp(pyxel.KEY_R):
            self.new_level(1)
            if self.screen != Screen.TITLE:
                self.screen = Screen.PLAYING

    def _set_music(self, on: bool) -> None:
        self.music_on = on
        if on:
            pyxel.playm(MUSIC_TRACK, loop=True)
        else:
            pyxel.stop()

    @staticmethod
    def _mouse_cell() -> tuple[int, int]:
        def clamp(value: int) -> int:
            return min(max(value // TILE_SIZE, 0), GRID_SIZE - 1)

        return clamp(pyxel.mouse_x), clamp(pyxel.mouse_y)
