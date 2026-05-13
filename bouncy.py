from typing import Literal  # noqa: F401

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.randomize import i_mrnd, rrnd  # noqa: F401
from egame.things import PhysicsThing, Thing  # noqa F821
from egame.type_definitions import Color, FPair

LSIZE = (16, 10)
SIZE = (1600, 1000)

LRADIUS = 1
BOUNCE_K = 0.75
VY_LEPSILON = 1.2
VX_LEPSILON = 0.3
FRICTION_PER_S = 0.1


class Ball(Thing):
    vel: FPair
    color: Color
    lgy: float

    def __init__(
        self,
        *,
        lpos: FPair,
        color: Color,
        scaler: Scaler,
    ) -> None:
        self.vel = (2.4, 1.8)
        self.lgy = -4.0
        self.color = color
        ball = pyglet.shapes.Circle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(LRADIUS),
            color=self.color,
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(LRADIUS, LRADIUS),
            name="ball",
            sprites={
                "0": ball,
            },
            sprite_offsets={
                "0": (0, 0),
            },
            t0_s=0.0,
            scaler=scaler,
        )

    # def dies_on_update(self, ctx: Context, dt: float, t_s: float) -> bool:
    #     x, y = self.lpos
    #     new_x = x + self.vel[0] * dt
    #     new_y = y + self.vel[1] * dt
    #     new_vel_x, new_vel_y = self.vel
    #     if new_y > LRADIUS:
    #         new_vel_y = new_vel_y + self.lgy * dt
    #     else:
    #         new_vel_x -= FRICTION_PER_S * dt * new_vel_x
    #         if abs(new_vel_x) < VX_LEPSILON:
    #             new_vel_x = 0

    #     if new_x + self.lsize[0] >= LSIZE[0]:
    #         new_vel_x = -BOUNCE_K * new_vel_x
    #         new_x = x + new_vel_x * dt
    #     elif new_x - self.lsize[0] <= 0:
    #         new_vel_x = -BOUNCE_K * new_vel_x
    #         new_x = x + new_vel_x * dt

    #     if new_y + self.lsize[1] >= LSIZE[1]:
    #         new_vel_y = -BOUNCE_K * new_vel_y
    #         new_y = y + new_vel_y * dt
    #     elif new_y - self.lsize[1] <= 0:
    #         new_vel_y = -BOUNCE_K * new_vel_y
    #         if abs(new_vel_y) < VY_LEPSILON:
    #             new_vel_y = 0
    #             new_y = LRADIUS
    #         else:
    #             new_y = y + new_vel_y * dt

    #     self.update_lpos((new_x, new_y))
    #     self.vel = (new_vel_x, new_vel_y)

    #     return False


"""
1. nothing
2. ball in center
3. vx uniform, escape
4. stop at border, (4b: use lpos+radius)
5. introduce self.vel and reverse it
6. both sides, back-and-forth
7. 2d velocity and all-side bounce
8. turn on gravity, (still 100% elastic bounces)
9. introduce energy loss in bounces (only on ground?)
10. advanced:
    on lower y check:
        v_i=0 if under epsilon
        y = LRADIUS also
        else update y
    apply lgy only if y>0 (i.e. flying)
    rolling friction (+ epsilon vx check)
11. multiple balls on space bar !
"""

if __name__ == "__main__":
    ctx0 = Context(size=SIZE, lsize=LSIZE, time_factor=2.0)

    ball = Ball(
        lpos=(8, 5),
        color=(0, 100, 0, 255),
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(ball)

    # # multi-ball
    # def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
    #     if symbol == pyglet.window.key.SPACE:
    #         lpos = (rrnd((3, 13)), rrnd((3, 8)))
    #         ball = Ball(
    #             lpos=lpos,
    #             color=(i_mrnd(256), i_mrnd(256), i_mrnd(256), i_mrnd(256)),
    #             scaler=ctx.scaler,
    #         )
    #         ctx.push_thing(ball)
    #     return None

    # ctx0.on_key_press(on_k_p)

    ctx0.run()
