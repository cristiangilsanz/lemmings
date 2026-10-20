from __future__ import annotations

from .board import Board
from .config import LETHAL_FALL_DISTANCE, MAX_STEP_HEIGHT, MOVE_EVERY_N_FRAMES, TILE_SIZE, Tile

RIGHT = 1
LEFT = -1


class Lemming:
    def __init__(self, board: Board, x: int, y: int, skin: int) -> None:
        self.board = board
        self.x = x
        self.y = y
        self.skin = skin
        self.direction = RIGHT
        self.fall_distance = 0
        self.dead = False
        self.has_umbrella = False
        self._ticks = 0

    @property
    def facing_right(self) -> bool:
        return self.direction == RIGHT

    @property
    def cell(self) -> tuple[int, int]:
        return self._center_x // TILE_SIZE, (self.y + TILE_SIZE // 2) // TILE_SIZE

    @property
    def standing(self) -> bool:
        below = self._feet_y + 1
        return any(self.board.is_solid(self.x + dx, below) for dx in range(TILE_SIZE))

    @property
    def _ground_under_center(self) -> bool:
        return self.board.is_solid(self._center_x, self._feet_y + 1)

    @property
    def _center_x(self) -> int:
        return self.x + TILE_SIZE // 2

    @property
    def _feet_y(self) -> int:
        return self.y + TILE_SIZE - 1

    def update(self) -> None:
        if self.board.tile_at(self._center_x, self.y + TILE_SIZE // 2) == Tile.UMBRELLA:
            self.has_umbrella = True

        self._ticks += 1
        if self._ticks % MOVE_EVERY_N_FRAMES:
            return
        if self.standing:
            self._walk()
        else:
            self._fall()

    def _fall(self) -> None:
        speed = 1 if self.has_umbrella else 2
        for _ in range(speed):
            if self.standing:
                break
            self.y += 1
            self.fall_distance += 1
        if self.standing:
            self._land()

    def _land(self) -> None:
        if self.fall_distance >= LETHAL_FALL_DISTANCE and not self.has_umbrella:
            self.dead = True
        self.fall_distance = 0
        self.has_umbrella = False

    def _walk(self) -> None:
        new_x = self.x + self.direction
        lead_x = new_x + (TILE_SIZE - 1 if self.facing_right else 0)
        rise = self._rise_at(new_x + TILE_SIZE // 2)
        if rise is None:
            self.direction = -self.direction
            return

        new_y = self.y - rise
        body_y = new_y + TILE_SIZE // 2
        blocked = self.board.tile_at(lead_x, body_y) == Tile.BLOCKER
        if blocked or self.board.is_wall(lead_x, new_y) or self.board.is_wall(lead_x, body_y):
            self.direction = -self.direction
            return

        self.x, self.y = new_x, new_y
        self._step_down()

    def _rise_at(self, center_x: int) -> int | None:
        for rise in range(MAX_STEP_HEIGHT + 1):
            feet_clear = not self.board.is_solid(center_x, self._feet_y - rise)
            head_clear = not self.board.is_solid(center_x, self.y - rise)
            if feet_clear and head_clear:
                return rise
        return None

    def _step_down(self) -> None:
        for _ in range(MAX_STEP_HEIGHT):
            if self._ground_under_center:
                return
            self.y += 1
        if not self._ground_under_center:
            self.y -= MAX_STEP_HEIGHT
