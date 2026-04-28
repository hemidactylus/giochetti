from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import Thing


class Boo(Thing):
    def __init__(self, scaler: Scaler) -> None:
        ball = pyglet.shapes.Circle(0, 0, 50, color=(255, 0, 0, 255))
        Thing.__init__(
            self,
            lpos=(5, 5),
            lsize=(1, 1),
            sprites={"0": ball},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            scaler=scaler,
        )


if __name__ == "__main__":
    ctx = Context(size=(400, 400), lsize=(10.0, 10.0))

    boo = Boo(ctx.scaler)
    ctx.push_thing(boo)

    def on_k_p(symbol: int, modifiers: int) -> Literal[True] | None:
        ball_n_pos = boo.lpos
        if symbol == pyglet.window.key.UP:
            ball_n_pos = (ball_n_pos[0], ball_n_pos[1] + 0.5)
        elif symbol == pyglet.window.key.DOWN:
            ball_n_pos = (ball_n_pos[0], ball_n_pos[1] - 0.5)
        elif symbol == pyglet.window.key.LEFT:
            ball_n_pos = (ball_n_pos[0] - 0.5, ball_n_pos[1])
        elif symbol == pyglet.window.key.RIGHT:
            ball_n_pos = (ball_n_pos[0] + 0.5, ball_n_pos[1])
        if ball_n_pos != boo.lpos:
            boo.update_lpos(ball_n_pos)

        return None

    ctx.on_key_press(on_k_p)

    ctx.run()
