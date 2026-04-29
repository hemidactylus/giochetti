from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair


class Boo(Thing):
    def __init__(self, scaler: Scaler) -> None:
        ball = pyglet.shapes.Circle(0, 0, scaler.r_x(1), color=(255, 0, 0, 255))
        Thing.__init__(
            self,
            lpos=(5, 5),
            lsize=(1, 1),
            sprites={"0": ball},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            name="boo",
            scaler=scaler,
        )


class Baa(PhysicsThing):
    def __init__(self, lpos: FPair, scaler: Scaler) -> None:
        ball = pyglet.shapes.Circle(0, 0, scaler.r_x(0.3), color=(0, 255, 0, 255))
        PhysicsThing.__init__(
            self,
            lpos=lpos,
            lsize=(0.3, 0.3),
            sprites={"0": ball},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            lv=(0.6, 1.5),
            feels_g=True,
            scaler=scaler,
        )

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        dying = PhysicsThing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s)
        if dying:
            if self.lpos[1] < 0:
                ctx.push_thing(Baa((8, 8.5), ctx.scaler))
        return dying


if __name__ == "__main__":
    ctx0 = Context(size=(400, 400), lsize=(10.0, 10.0), lg=(0.0, -1.0), time_factor=4.0)

    boo = Boo(ctx0.scaler)
    ctx0.push_thing(boo)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ball_n_pos = boo.lpos
        if symbol == pyglet.window.key.UP:
            ball_n_pos = (ball_n_pos[0], ball_n_pos[1] + 0.5)
        elif symbol == pyglet.window.key.DOWN:
            ball_n_pos = (ball_n_pos[0], ball_n_pos[1] - 0.5)
        elif symbol == pyglet.window.key.LEFT:
            ball_n_pos = (ball_n_pos[0] - 0.5, ball_n_pos[1])
        elif symbol == pyglet.window.key.RIGHT:
            ball_n_pos = (ball_n_pos[0] + 0.5, ball_n_pos[1])
        elif symbol == pyglet.window.key.A:
            ctx.push_thing(Baa(boo.lpos, ctx.scaler))
        if ball_n_pos != boo.lpos:
            boo.update_lpos(ball_n_pos)

        return None

    ctx0.on_key_press(on_k_p)

    ctx0.run()
