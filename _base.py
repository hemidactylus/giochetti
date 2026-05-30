from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.messenger import Messenger
from egame.things import Thing
from egame.type_definitions import FPair

LSIZE = (16, 10)
SIZE = (1600, 1000)

BLOCK_LSIZE = (1, 1)
SPHERE_LRADIUS = 0.2

BLOCKV_MOD = 3


class Block(Thing):
    def __init__(
        self,
        *,
        lpos: FPair,
        scaler: Scaler,
    ) -> None:
        body = pyglet.shapes.Rectangle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(BLOCK_LSIZE[0]),
            scaler.r_y(BLOCK_LSIZE[1]),
            color=(0, 0, 255, 255),
        )
        sphere = pyglet.shapes.Circle(
            scaler.r_x(lpos[0] + 0.5 * BLOCK_LSIZE[0]),
            scaler.r_y(lpos[1] + 0.5 * BLOCK_LSIZE[1]),
            radius=scaler.r_x(SPHERE_LRADIUS),
            color=(255, 10, 10, 255),
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=BLOCK_LSIZE,
            name="block",
            sprites={
                "0": body,
                "s": sphere,
            },
            sprite_offsets={
                "0": (0, 0),
                "s": (0.5 * BLOCK_LSIZE[0], 0.5 * BLOCK_LSIZE[1]),
            },
            t0_s=0.0,
            scaler=scaler,
        )


class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        sky = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(0),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1]),
            color=(90, 20, 150, 255),
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


if __name__ == "__main__":
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0), time_factor=1.0)
    ctx0.state["keys_map"] = {}

    block = Block(
        lpos=(5, 5),
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))
    ctx0.push_thing(block)
    messenger = Messenger(
        "CIAO",
        font_lsize=3,
        color=(0, 255, 0, 48),
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
        blockv: list[float] = [0, 0]
        if ctx.state["keys_map"].get(pyglet.window.key.UP):
            blockv[1] += BLOCKV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.DOWN):
            blockv[1] -= BLOCKV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.LEFT):
            blockv[0] -= BLOCKV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.RIGHT):
            blockv[0] += BLOCKV_MOD
        if blockv != (0, 0):
            blockd = (blockv[0] * dt, blockv[1] * dt)
            new_block_lpos = (
                block.lpos[0] + blockd[0],
                block.lpos[1] + blockd[1],
            )
            block.update_lpos(new_block_lpos)

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.run()
