import os
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.randomize import fluctuate, i_mrnd, msrnd
from egame.things import PhysicsThing
from egame.type_definitions import FPair

MAX_GEN = 5
NUM_FRAGMENTS = 10
DV_MOD = 12.0
GEN_LC_BASE = 1.3
GEN_LC_DELTA = 0.35

BANANA_MODE = 0  # 1=banana, 2=various sprites
BANANA_FACTOR = 10

LSIZE = (16, 10)
SIZE = (1600, 1000)

COLORS = [
    (0, 255, 0, 255),
    (0, 0, 255, 255),
    (255, 0, 0, 255),
    (255, 255, 0, 255),
    (0, 255, 255, 255),
    (100, 0, 215, 255),
]

SPRITE_ROOT = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "firework_images",
    )
)

if BANANA_MODE == 1:
    BANANA_SPRITES = [pyglet.image.load(os.path.join(SPRITE_ROOT, "banana.png"))]
else:
    BANANA_SPRITES = [
        pyglet.image.load(os.path.join(SPRITE_ROOT, f))
        for f in os.listdir(SPRITE_ROOT)
        if f[-4:] == ".png"
    ]


class Exploder(PhysicsThing):
    lifecycle_s: float | None
    gen: int

    def __init__(
        self,
        *,
        lpos: FPair,
        lv: FPair,
        gen: int,
        lifecycle_s: float | None,
        scaler: Scaler,
    ) -> None:
        self.gen = gen
        rad: float
        if BANANA_MODE == 0:
            rad = max(0.15 * (0.66**self.gen), 0.02)
        else:
            rad = 15 * max(0.15 * (0.66**self.gen), 0.003)

        ball: pyglet.shapes.Circle | pyglet.sprite.Sprite
        if BANANA_MODE == 0:
            ball = pyglet.shapes.Circle(
                0, 0, scaler.r_x(rad), color=COLORS[self.gen % len(COLORS)]
            )
        else:
            tgt_i = i_mrnd(1 if BANANA_MODE == 1 else len(BANANA_SPRITES))
            x = scaler.r_x(lpos[0])
            y = scaler.r_x(lpos[1])
            ball = pyglet.sprite.Sprite(BANANA_SPRITES[tgt_i], x=x, y=y)
            ball.scale_x = scaler.r_x(rad) / ball.width  # type: ignore[attr-defined]
            ball.scale_y = scaler.r_y(rad) / ball.height  # type: ignore[attr-defined]

        PhysicsThing.__init__(
            self,
            lpos=lpos,
            lsize=(rad, rad),
            sprites={"0": ball},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            lv=lv,
            feels_g=True,
            scaler=scaler,
        )
        self.lifecycle_s = lifecycle_s

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        dying = PhysicsThing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s)
        if self.lifecycle_s is not None and self.t_s >= self.lifecycle_s:
            if self.gen < MAX_GEN:
                # generate items
                lc0: float | None
                if self.gen == MAX_GEN - 1:
                    lc0 = None
                else:
                    # TODO debug timescale, it's not s?
                    lc0 = GEN_LC_BASE - self.gen * GEN_LC_DELTA
                for i in range(NUM_FRAGMENTS):
                    new_v = (
                        self.lv[0] + msrnd(DV_MOD),
                        self.lv[1] + msrnd(DV_MOD),
                    )
                    e0 = Exploder(
                        lpos=self.lpos,
                        lv=new_v,
                        gen=self.gen + 1,
                        lifecycle_s=lc0 * fluctuate(1.0, 0.3)  # type: ignore[operator]
                        if lc0
                        else lc0,
                        scaler=ctx.scaler,
                    )
                    ctx.push_thing(e0)
            return True
        return dying


if __name__ == "__main__":
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0), time_factor=1.0)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        if symbol == pyglet.window.key.SPACE:
            x0 = fluctuate(0.5 * LSIZE[0], 0.35 * LSIZE[0])
            vx = msrnd(8.0)
            vy = fluctuate(11, 3.0)

            e0 = Exploder(
                lpos=(x0, 0),
                lv=(vx, vy),
                gen=0,
                lifecycle_s=GEN_LC_BASE if MAX_GEN > 0 else None,
                scaler=ctx0.scaler,
            )
            ctx.push_thing(e0)
        return None

    ctx0.on_key_press(on_k_p)

    ctx0.run()
