from __future__ import annotations

import collections
import random
import sys
import traceback

import pyxel

from lemmings.board import Board
from lemmings.config import RESOURCE_FILE, SCREEN_SIZE, TILE_SIZE
from lemmings.game import TOOL_KEYS, Game, Screen
from lemmings.lemming import Lemming

MAX_FRAMES = 20_000
TOLERANCE = 0
WOBBLE_WINDOW = 12
FIELD_MIN_X, FIELD_MAX_X = TILE_SIZE - TOLERANCE, SCREEN_SIZE - 2 * TILE_SIZE + TOLERANCE
FIELD_MIN_Y, FIELD_MAX_Y = 3 * TILE_SIZE - TOLERANCE, SCREEN_SIZE - 2 * TILE_SIZE + TOLERANCE

pressed: set[int] = set()
pyxel.btnp = lambda key, *args, **kwargs: key in pressed
pyxel.btn = lambda key, *args, **kwargs: key in pressed
pyxel.playm = lambda *args, **kwargs: None


def check_motion(board: Board, lemming: Lemming, path: list[tuple[int, int]]) -> str | None:
    x, y = lemming.x, lemming.y
    if not (FIELD_MIN_X <= x <= FIELD_MAX_X and FIELD_MIN_Y <= y <= FIELD_MAX_Y):
        return f"escaped playfield at ({x}, {y})"
    if board.is_solid(x + TILE_SIZE // 2, y + TILE_SIZE - 1):
        return "embedded in the ground"
    if path and path[-1] == (x, y):
        return None
    if path:
        px, py = path[-1]
        if abs(x - px) > 1 or abs(y - py) > 2:
            return f"jumped from ({px}, {py}) to ({x}, {y})"
    path.append((x, y))
    recent = path[-WOBBLE_WINDOW:]
    signs = [(b[1] > a[1]) - (b[1] < a[1]) for a, b in zip(recent, recent[1:], strict=False) if b[1] != a[1]]
    reversals = sum(a != b for a, b in zip(signs, signs[1:], strict=False))
    if reversals >= 3:
        return "wobbles up and down"
    return None


def play_level(seed: int) -> str:
    bot = random.Random(seed)
    game = Game(seed)
    game.screen = Screen.PLAYING
    history: dict[Lemming, list[tuple[int, int]]] = {}

    def step(*keys: int) -> None:
        pressed.clear()
        pressed.update(keys)
        game.update()
        game.draw()

    for frame in range(MAX_FRAMES):
        keys = [pyxel.KEY_L] if frame == 5 else []
        if frame % 120 == 0 and bot.random() < 0.5:
            pyxel.mouse_x = bot.randint(0, SCREEN_SIZE - 1)
            pyxel.mouse_y = bot.randint(3 * TILE_SIZE, SCREEN_SIZE - 1)
            keys.append(bot.choice(list(TOOL_KEYS)))
        step(*keys)
        for lemming in game.level.lemmings:
            problem = check_motion(game.level.board, lemming, history.setdefault(lemming, []))
            if problem:
                return problem
        if game.screen == Screen.WON:
            return "win"
        if game.screen == Screen.LOST:
            return "loss"
    return "timeout"


def main() -> None:
    levels = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    pyxel.init(SCREEN_SIZE, SCREEN_SIZE)
    pyxel.load(str(RESOURCE_FILE))

    results: collections.Counter[str] = collections.Counter()
    first_seed: dict[str, int] = {}
    for seed in range(levels):
        try:
            outcome = play_level(seed)
        except Exception as exc:
            frame = traceback.extract_tb(exc.__traceback__)[-1]
            outcome = f"crash: {type(exc).__name__}: {exc} at {frame.filename}:{frame.lineno}"
        results[outcome] += 1
        first_seed.setdefault(outcome, seed)

    print(f"{levels} levels")
    for outcome, count in results.most_common():
        print(f"  {count:4d}  {outcome}  (first seed {first_seed[outcome]})")
    sys.exit(any(not o.startswith(("win", "loss", "timeout")) for o in results))


if __name__ == "__main__":
    main()
