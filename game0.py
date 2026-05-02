import random  # TODO rnd lib

from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair


class Boo(Thing):
    def __init__(self, scaler: Scaler) -> None:
        car_img = pyglet.image.load("car.png")
        car_sprite = pyglet.sprite.Sprite(car_img, x=0, y=0)
        car_sprite.scale_x = scaler.r_x(2) / car_img.width
        car_sprite.scale_y = scaler.r_y(1.4) / car_img.height
        Thing.__init__(
            self,
            lpos=(5, 5),
            lsize=(3, 3),
            sprites={"0": car_sprite},
            sprite_offsets={"0": (-1.5, -1.5)},
            t0_s=0.0,
            name="boo",
            scaler=scaler,
        )


class Baa(PhysicsThing):
    def __init__(self, lpos: FPair, scaler: Scaler) -> None:
        ball = pyglet.shapes.Circle(0, 0, scaler.r_x(0.3), color=(90, 47, 7, 255))
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
        return dying


class Food(Thing):
    terminating: bool

    def __init__(self, lpos: FPair, scaler: Scaler) -> None:
        square = pyglet.shapes.Rectangle(0, 0, scaler.r_x(0.3), scaler.r_x(0.3), color=(44, 210, 130, 255))
        self.terminating = False
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(0.3, 0.3),
            sprites={"0": square},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            scaler=scaler,
        )

    def terminate(self) -> None:
        self.terminating = True

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        if self.terminating:
            return True
        dying = Thing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s)
        return dying


if __name__ == "__main__":
    ctx0 = Context(size=(1200, 1200), lsize=(10.0, 10.0), lg=(0.0, -1.0), time_factor=4.0)

    boo = Boo(ctx0.scaler)
    foo = Food(
        (
            random.random() * 10.0,
            random.random() * 10.0,
        ),
        ctx0.scaler,
    )
    ctx0.push_thing(boo)
    ctx0.push_thing(foo)

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
            # has eaten food?
            foo_delta = (
                abs(foo.lpos[0] + foo.sprite_offsets["0"][0] - boo.lpos[0]),
                abs(foo.lpos[1] + foo.sprite_offsets["0"][1] - boo.lpos[1]),
            )
            # TODO bug with position (-> expose center position on a main sprite?)
            if foo_delta[0] <= 0.7 and foo_delta[1] <= 1.2:
                ctx.push_thing(Baa(boo.lpos, ctx.scaler))
                new_foo_lpos = (
                    random.random() * 10.0,
                    random.random() * 10.0,
                )
                foo.update_lpos(new_foo_lpos)
            #
            boo.update_lpos(ball_n_pos)

        return None

    ctx0.on_key_press(on_k_p)

    ctx0.run()
