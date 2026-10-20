from __future__ import annotations

import random
from enum import Enum, auto

from .board import Board
from .config import (
    FLOOR_ROW,
    LEMMINGS_PER_LEVEL,
    PLACEABLE_TILES,
    SPAWN_INTERVAL_FRAMES,
    TILE_SIZE,
    TOOL_LIMITS,
    Tile,
    lemmings_needed,
)
from .lemming import Lemming
from .tools import Tool, ToolKind


class Outcome(Enum):
    PLAYING = auto()
    WON = auto()
    LOST = auto()


class Level:
    def __init__(self, board: Board, total_lemmings: int, rng: random.Random) -> None:
        self.board = board
        self.total_lemmings = total_lemmings
        self.rng = rng
        self.lemmings: list[Lemming] = []
        self.tools: list[Tool] = []
        self.remaining = dict(TOOL_LIMITS)
        self.spawned = 0
        self.saved = 0
        self.dead = 0
        self.releasing = False
        self._spawn_timer = 0

    @classmethod
    def random(cls, rng: random.Random, theme: int = 0) -> Level:
        return cls(Board.generate(rng, theme), rng.choice(LEMMINGS_PER_LEVEL), rng)

    @property
    def alive(self) -> int:
        return self.total_lemmings - self.dead

    @property
    def outcome(self) -> Outcome:
        needed = lemmings_needed(self.total_lemmings)
        if self.dead >= needed:
            return Outcome.LOST
        if self.saved >= needed:
            return Outcome.WON
        if self.spawned == self.total_lemmings and not self.lemmings:
            return Outcome.LOST
        return Outcome.PLAYING

    def release_lemmings(self) -> None:
        self.releasing = True

    def toggle_tool(self, kind: ToolKind, col: int, row: int) -> None:
        grid = self.board.grid
        tile = grid[col][row]
        if tile == kind.tile:
            tool = next((t for t in self.tools if (t.col, t.row) == (col, row)), None)
            if tool is not None and not tool.used:
                self.tools.remove(tool)
                grid[col][row] = tool.replaced_tile
                self.remaining[kind.pool] += 1
            return

        if self.remaining[kind.pool] <= 0 or tile not in PLACEABLE_TILES:
            return
        if kind == ToolKind.SHOVEL and row == FLOOR_ROW - 1:
            return
        if kind.pool == "stairs" and self._lemming_overlaps(col, row):
            return
        self.tools.append(Tool(kind, col, row, replaced_tile=tile))
        grid[col][row] = kind.tile
        self.remaining[kind.pool] -= 1

    def _lemming_overlaps(self, col: int, row: int) -> bool:
        left, top = col * TILE_SIZE, row * TILE_SIZE
        return any(abs(lem.x - left) < TILE_SIZE and abs(lem.y - top) < TILE_SIZE for lem in self.lemmings)

    def step(self) -> None:
        self._mark_used_tools()
        self._dig_with_shovels()
        self._spawn_lemmings()
        self._move_lemmings()

    def _mark_used_tools(self) -> None:
        for tool in self.tools:
            if any(tool.is_touched_by(lem.cell, lem.x, lem.facing_right) for lem in self.lemmings):
                tool.used = True

    def _dig_with_shovels(self) -> None:
        for tool in [t for t in self.tools if t.kind == ToolKind.SHOVEL and t.used]:
            self.board.grid[tool.col][tool.row] = Tile.EMPTY
            self.board.grid[tool.col][tool.row + 1] = Tile.EMPTY
            self.tools.remove(tool)

    def _spawn_lemmings(self) -> None:
        if not self.releasing:
            return
        self._spawn_timer += 1
        if self._spawn_timer < SPAWN_INTERVAL_FRAMES:
            return
        if self.spawned < self.total_lemmings:
            self._spawn_timer = 0
            x, y = self.board.entrance
            self.lemmings.append(Lemming(self.board, x, y, skin=self.rng.randint(0, 1)))
            self.spawned += 1
        else:
            self.releasing = False

    def _move_lemmings(self) -> None:
        for lemming in list(self.lemmings):
            if lemming.dead:
                self.lemmings.remove(lemming)
                self.dead += 1
                continue
            lemming.update()
            if lemming.standing and lemming.cell == self.board.exit_cell:
                self.lemmings.remove(lemming)
                self.saved += 1
