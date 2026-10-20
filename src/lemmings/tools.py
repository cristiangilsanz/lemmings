from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .config import TILE_SIZE, Tile


class ToolKind(Enum):
    UMBRELLA = (Tile.UMBRELLA, "umbrella")
    BLOCKER = (Tile.BLOCKER, "blocker")
    STAIRS_RIGHT = (Tile.STAIRS_RIGHT, "stairs")
    STAIRS_LEFT = (Tile.STAIRS_LEFT, "stairs")
    SHOVEL = (Tile.SHOVEL, "shovel")

    @property
    def tile(self) -> Tile:
        return self.value[0]

    @property
    def pool(self) -> str:
        return self.value[1]


@dataclass
class Tool:
    kind: ToolKind
    col: int
    row: int
    replaced_tile: Tile = Tile.EMPTY
    used: bool = False

    @property
    def x(self) -> int:
        return self.col * TILE_SIZE

    @property
    def y(self) -> int:
        return self.row * TILE_SIZE

    def is_touched_by(self, lemming_cell: tuple[int, int], lemming_x: int, facing_right: bool) -> bool:
        col, row = lemming_cell
        if self.kind == ToolKind.BLOCKER:
            col += 1 if facing_right else -1
        if self.kind == ToolKind.SHOVEL and lemming_x != self.x:
            return False
        return (col, row) == (self.col, self.row)
