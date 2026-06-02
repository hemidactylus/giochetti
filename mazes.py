import os
import sys
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.messenger import Messenger
from egame.rectangle_block import RectangleBlock
from egame.things import Thing
from egame.type_definitions import FPair

# temporary plumbing!
from maze_temp_lib.mazes import Maze, make_maze

LSIZE = (16, 10)
SIZE = None if "f" in sys.argv[1:] else (1600, 1000)

MAZE_GRID = (8, 5)

PLAYER_LSIZE = (
    0.36 * LSIZE[0] / MAZE_GRID[0],
    0.43 * LSIZE[1] / MAZE_GRID[1],
)
SPHERE_LRADIUS = min(*PLAYER_LSIZE) / 3

PLAYER_LV = 3

GOAL_LSIZE = (
    1.2 * PLAYER_LSIZE[0],
    1.6 * PLAYER_LSIZE[1],
)
GOAL_REACHED_DISTANCE = 0.3

BLOCK_REL_LWIDTH = 0.08

SPRITE_ROOT = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "mazes_images",
    )
)
FOX = pyglet.image.load(os.path.join(SPRITE_ROOT, "fox.png"))
GRAPES = pyglet.image.load(os.path.join(SPRITE_ROOT, "grapes.png"))


class Goal(Thing):
    def __init__(
        self,
        *,
        lpos: FPair,
        scaler: Scaler,
    ) -> None:
        x = scaler.r_x(lpos[0])
        y = scaler.r_x(lpos[1])
        sprite = pyglet.sprite.Sprite(GRAPES, x=x, y=y)
        sprite.scale_x = scaler.r_x(GOAL_LSIZE[0]) / sprite.width  # type: ignore[attr-defined]
        sprite.scale_y = scaler.r_y(GOAL_LSIZE[1]) / sprite.height  # type: ignore[attr-defined]
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=GOAL_LSIZE,
            name="goal",
            sprites={
                "0": sprite,
            },
            sprite_offsets={
                "0": (0, 0),
            },
            t0_s=0.0,
            scaler=scaler,
        )


class Player(Thing):
    loffsets: list[FPair]

    def __init__(
        self,
        *,
        lpos: FPair,
        scaler: Scaler,
    ) -> None:
        x = scaler.r_x(lpos[0])
        y = scaler.r_x(lpos[1])
        sprite = pyglet.sprite.Sprite(FOX, x=x, y=y)
        sprite.scale_x = scaler.r_x(PLAYER_LSIZE[0]) / sprite.width  # type: ignore[attr-defined]
        sprite.scale_y = scaler.r_y(PLAYER_LSIZE[1]) / sprite.height  # type: ignore[attr-defined]
        self.loffsets = [
            (0, 0),
            (PLAYER_LSIZE[0], 0),
            (0, PLAYER_LSIZE[1]),
            (PLAYER_LSIZE[0], PLAYER_LSIZE[1]),
            #
            (0.25 * PLAYER_LSIZE[0], 0),
            (0.50 * PLAYER_LSIZE[0], 0),
            (0.75 * PLAYER_LSIZE[0], 0),
            (0, 0.25 * PLAYER_LSIZE[1]),
            (0, 0.50 * PLAYER_LSIZE[1]),
            (0, 0.75 * PLAYER_LSIZE[1]),
            (0.25 * PLAYER_LSIZE[0], PLAYER_LSIZE[1]),
            (0.50 * PLAYER_LSIZE[0], PLAYER_LSIZE[1]),
            (0.75 * PLAYER_LSIZE[0], PLAYER_LSIZE[1]),
            (PLAYER_LSIZE[0], 0.25 * PLAYER_LSIZE[1]),
            (PLAYER_LSIZE[0], 0.50 * PLAYER_LSIZE[1]),
            (PLAYER_LSIZE[0], 0.75 * PLAYER_LSIZE[1]),
        ]
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=PLAYER_LSIZE,
            name="player",
            sprites={
                "0": sprite,
            },
            sprite_offsets={
                "0": (0, 0),
            },
            t0_s=0.0,
            scaler=scaler,
        )

    def try_update_lpos(
        self, ctx: Context, lv: FPair, dt: float, collidables: list[RectangleBlock]
    ) -> None:
        lpos_delta = (lv[0] * dt, lv[1] * dt)
        new_lpos = (
            self.lpos[0] + lpos_delta[0],
            self.lpos[1] + lpos_delta[1],
        )
        collisions = self.find_collisions(
            ctx,
            new_lpos,
            blocks=collidables,
            loffsets=self.loffsets,
        )
        forbidden_directions = {dir_i % 2 for _, dir_i in collisions}
        actual_lv_x, actual_lv_y = lv
        if 0 in forbidden_directions:
            actual_lv_x = 0
        if 1 in forbidden_directions:
            actual_lv_y = 0
        #
        actual_lpos_delta = (actual_lv_x * dt, actual_lv_y * dt)
        actual_new_lpos = (
            self.lpos[0] + actual_lpos_delta[0],
            self.lpos[1] + actual_lpos_delta[1],
        )
        self.update_lpos(actual_new_lpos)

    def find_collisions(
        self,
        ctx: Context,
        new_lpos: FPair,
        *,
        blocks: list[RectangleBlock],
        loffsets: list[FPair],
    ) -> list[tuple[FPair, int]]:
        collision_pairs: list[tuple[FPair, int]] = []
        for loffset in loffsets:
            offset_lpos = (
                self.lpos[0] + loffset[0],
                self.lpos[1] + loffset[1],
            )
            offset_new_lpos = (
                new_lpos[0] + loffset[0],
                new_lpos[1] + loffset[1],
            )
            offset_collision_pairs: list[tuple[FPair, int]] = [
                olpp
                for olpp in [
                    block.collides(offset_lpos, offset_new_lpos) for block in blocks
                ]
                if olpp is not None
            ]
            collision_pairs += [
                (
                    (
                        olpp[0][0] - loffset[0],
                        olpp[0][1] - loffset[1],
                    ),
                    olpp[1],
                )
                for olpp in offset_collision_pairs
            ]

        return collision_pairs


class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        sky = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(0),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1]),
            color=(128, 50, 0, 255),
        )
        Thing.__init__(
            self,
            lpos=(0, 0),
            lsize=LSIZE,
            sprites={
                "s": sky,
            },
            sprite_offsets={
                "s": (0, 0),
            },
            t0_s=0.0,
            scaler=scaler,
        )


def maze_to_blocks(ctx: Context, maze: Maze) -> list[RectangleBlock]:
    cell_lsize = (ctx.lsize[0] / MAZE_GRID[0], ctx.lsize[1] / MAZE_GRID[1])
    hwx = cell_lsize[0] * BLOCK_REL_LWIDTH
    hwy = cell_lsize[1] * BLOCK_REL_LWIDTH
    blocks: list[RectangleBlock] = []
    for (x, y, d), is_wall in maze.items():
        if is_wall:
            if d == 0:
                lx1 = x * cell_lsize[0]
                ly = y * cell_lsize[1]
                blocks.append(
                    RectangleBlock(
                        lpos=(lx1 - hwx, ly - hwy),
                        lsize=(cell_lsize[0] + 2 * hwx, 2 * hwy),
                        color=(0, 0, 0, 255),
                        name=f"block_{x}.{y}.{d}",
                        scaler=ctx.scaler,
                    )
                )
            else:  # d == 1
                lx = x * cell_lsize[0]
                ly1 = y * cell_lsize[1]
                blocks.append(
                    RectangleBlock(
                        lpos=(lx - hwx, ly1 - hwy),
                        lsize=(2 * hwx, cell_lsize[1] + 2 * hwy),
                        color=(0, 0, 0, 255),
                        name=f"block_{x}.{y}.{d}",
                        scaler=ctx.scaler,
                    )
                )
    return blocks


if __name__ == "__main__":
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0), time_factor=1.0)
    ctx0.state["keys_map"] = {}

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))

    goal_lpos = (
        LSIZE[0] * (MAZE_GRID[0] - 0.5) / MAZE_GRID[0] - 0.5 * GOAL_LSIZE[0],
        LSIZE[1] * (MAZE_GRID[1] - 0.5) / MAZE_GRID[1] - 0.5 * GOAL_LSIZE[1],
    )
    goal = Goal(
        lpos=goal_lpos,
        scaler=ctx0.scaler,
    )
    ctx0.push_thing(goal)

    start_lpos = (
        LSIZE[0] * 0.5 / MAZE_GRID[0] - 0.5 * PLAYER_LSIZE[0],
        LSIZE[1] * 0.5 / MAZE_GRID[1] - 0.5 * PLAYER_LSIZE[1],
    )
    player = Player(
        lpos=start_lpos,
        scaler=ctx0.scaler,
    )
    ctx0.push_thing(player)

    maze = make_maze(*MAZE_GRID)
    blocks = maze_to_blocks(ctx0, maze)
    for block in blocks:
        ctx0.push_thing(block)

    messenger = Messenger(
        "",
        font_lsize=2,
        color=(255, 255, 255, 255),
        context=ctx0,
        scaler=ctx0.scaler,
    )
    ctx0.push_thing(messenger)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = True
        return None

    def on_k_r(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = False
        return None

    def tk(ctx: Context, dt: float, t: float) -> None:
        player_lv: list[float] = [0, 0]
        if ctx.state["keys_map"].get(pyglet.window.key.UP):
            player_lv[1] += PLAYER_LV
        if ctx.state["keys_map"].get(pyglet.window.key.DOWN):
            player_lv[1] -= PLAYER_LV
        if ctx.state["keys_map"].get(pyglet.window.key.LEFT):
            player_lv[0] -= PLAYER_LV
        if ctx.state["keys_map"].get(pyglet.window.key.RIGHT):
            player_lv[0] += PLAYER_LV
        lv_tuple: FPair = tuple(player_lv)  # type: ignore[assignment]
        if lv_tuple != (0, 0):
            player.try_update_lpos(ctx, lv_tuple, dt, blocks)
            # winning?
            goal_distance = (
                (player.lpos[0] - goal.lpos[0]) ** 2
                + (player.lpos[1] - goal.lpos[1]) ** 2
            ) ** 0.5
            if goal_distance < GOAL_REACHED_DISTANCE:
                msg = "HAI VINTO"
            else:
                msg = ""
            if msg != messenger.text:
                messenger.set_text(msg)

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.run()
