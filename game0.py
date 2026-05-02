import time
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.randomize import mrnd
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair

CAR_LSIZE = (2, 1.4)
CAR_STEP = 0.5
FOOD_LSIDE = 0.5


class Car(Thing):
    def __init__(self, scaler: Scaler) -> None:
        self.ini = time.time()
        car_img = pyglet.image.load("car.png")
        car_sprite = pyglet.sprite.Sprite(car_img, x=0, y=0)
        car_sprite.scale_x = scaler.r_x(CAR_LSIZE[0]) / car_img.width
        car_sprite.scale_y = scaler.r_y(CAR_LSIZE[1]) / car_img.height
        Thing.__init__(
            self,
            lpos=(5, 5),
            lsize=CAR_LSIZE,
            sprites={"0": car_sprite},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            name="car",
            scaler=scaler,
        )


class Poo(PhysicsThing):
    def __init__(self, lpos: FPair, scaler: Scaler) -> None:
        ball = pyglet.shapes.Circle(0, 0, scaler.r_x(0.3), color=(90, 47, 7, 255))
        PhysicsThing.__init__(
            self,
            lpos=lpos,
            lsize=(0.3, 0.3),
            sprites={"0": ball},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            lv=(2.6, 6),
            feels_g=True,
            scaler=scaler,
        )

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        dying = PhysicsThing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s)
        return dying


class Food(Thing):
    terminating: bool

    def __init__(self, lpos: FPair, scaler: Scaler) -> None:
        square = pyglet.shapes.Rectangle(
            0,
            0,
            scaler.r_x(FOOD_LSIDE),
            scaler.r_x(FOOD_LSIDE),
            color=(44, 210, 130, 255),
        )
        self.terminating = False
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(FOOD_LSIDE, FOOD_LSIDE),
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
    ctx0 = Context(size=(1200, 1200), lsize=(10.0, 10.0), lg=(0.0, -10.0))

    car = Car(ctx0.scaler)
    food = Food(
        (
            mrnd(10.0),
            mrnd(10.0),
        ),
        ctx0.scaler,
    )
    ctx0.push_thing(car)
    ctx0.push_thing(food)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        car_n_lpos = car.lpos
        if symbol == pyglet.window.key.UP:
            car_n_lpos = (car_n_lpos[0], car_n_lpos[1] + 0.5)
        elif symbol == pyglet.window.key.DOWN:
            car_n_lpos = (car_n_lpos[0], car_n_lpos[1] - 0.5)
        elif symbol == pyglet.window.key.LEFT:
            car_n_lpos = (car_n_lpos[0] - 0.5, car_n_lpos[1])
        elif symbol == pyglet.window.key.RIGHT:
            car_n_lpos = (car_n_lpos[0] + 0.5, car_n_lpos[1])
        elif symbol == pyglet.window.key.A:
            ctx.push_thing(Poo(car.lpos, ctx.scaler))

        if car_n_lpos != car.lpos:
            car.update_lpos(car_n_lpos)
            # eats?
            foo_delta = (
                abs(food.lpos[0] - car.lcenter[0]),
                abs(food.lpos[1] - car.lcenter[1]),
            )
            if foo_delta[0] <= 0.4 and foo_delta[1] <= 0.4:
                ctx.push_thing(Poo(car.lcenter, ctx.scaler))
                food_n_lpos = (
                    mrnd(10.0),
                    mrnd(10.0),
                )
                food.update_lpos(food_n_lpos)

        return None

    ctx0.on_key_press(on_k_p)

    ctx0.run()
