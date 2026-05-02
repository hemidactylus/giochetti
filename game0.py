import time
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.randomize import i_mrnd
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair, IPair

CAR_LSIZE = (2, 1.4)
LSIZE = (12, 12)
CAR_STEP = 1
FOOD_LSIDE = 0.5

CHART_LDELTA = (1.5, 1.5)
CHART_LSIZE = (10, 10)

class Car(Thing):
    chart_lpos: IPair

    def __init__(self, scaler: Scaler) -> None:
        self.ini = time.time()
        car_img = pyglet.image.load("car.png")
        car_sprite = pyglet.sprite.Sprite(car_img, x=0, y=0)
        car_sprite.scale_x = scaler.r_x(CAR_LSIZE[0]) / car_img.width
        car_sprite.scale_y = scaler.r_y(CAR_LSIZE[1]) / car_img.height
        Thing.__init__(
            self,
            lpos=(
                i_mrnd(CHART_LSIZE[0]),
                i_mrnd(CHART_LSIZE[1]),
            ),
            lsize=CAR_LSIZE,
            sprites={"0": car_sprite},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            name="car",
            scaler=scaler,
        )
        self.update_chart_lpos((0, 0))

    def update_chart_lpos(self, clpos: IPair) -> None:
        self.chart_lpos = clpos
        # remap pos
        lpos = (
            CHART_LDELTA[0] + clpos[0] - 0.5 * self.lsize[0],
            CHART_LDELTA[1] + clpos[1] - 0.5 * self.lsize[1],
        )
        self.lpos = lpos
        self.update_lpos(self.lpos)


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
    chart_lpos: IPair
    terminating: bool

    def __init__(self, chart_lpos: IPair, scaler: Scaler) -> None:
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
            lpos=(0, 0),
            lsize=(FOOD_LSIDE, FOOD_LSIDE),
            sprites={"0": square},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            scaler=scaler,
        )
        self.update_chart_lpos(chart_lpos)

    def update_chart_lpos(self, clpos: IPair) -> None:
        self.chart_lpos = clpos
        # remap pos
        lpos = (
            CHART_LDELTA[0] + clpos[0] - 0.5 * self.lsize[0],
            CHART_LDELTA[1] + clpos[1] - 0.5 * self.lsize[1],
        )
        self.lpos = lpos
        self.update_lpos(self.lpos)

    def terminate(self) -> None:
        self.terminating = True

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        if self.terminating:
            return True
        dying = Thing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s)
        return dying


if __name__ == "__main__":
    ctx0 = Context(size=(1200, 1200), lsize=LSIZE, lg=(0.0, -10.0))

    car = Car(ctx0.scaler)
    food = Food(
        (
            i_mrnd(CHART_LSIZE[0]),
            i_mrnd(CHART_LSIZE[1]),
        ),
        ctx0.scaler,
    )
    ctx0.push_thing(car)
    ctx0.push_thing(food)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        car_n_clpos = car.chart_lpos
        if symbol == pyglet.window.key.UP:
            car_n_clpos = (car_n_clpos[0], car_n_clpos[1] + CAR_STEP)
        elif symbol == pyglet.window.key.DOWN:
            car_n_clpos = (car_n_clpos[0], car_n_clpos[1] - CAR_STEP)
        elif symbol == pyglet.window.key.LEFT:
            car_n_clpos = (car_n_clpos[0] - CAR_STEP, car_n_clpos[1])
        elif symbol == pyglet.window.key.RIGHT:
            car_n_clpos = (car_n_clpos[0] + CAR_STEP, car_n_clpos[1])
        elif symbol == pyglet.window.key.A:
            ctx.push_thing(Poo(car.lpos, ctx.scaler))

        if car_n_clpos != car.chart_lpos:
            car.update_chart_lpos(car_n_clpos)
            # eats?
            foo_delta = (
                abs(food.lpos[0] - car.lcenter[0]),
                abs(food.lpos[1] - car.lcenter[1]),
            )
            if foo_delta[0] <= 0.4 and foo_delta[1] <= 0.5 * CAR_STEP:
                ctx.push_thing(Poo(car.lcenter, ctx.scaler))
                food_n_clpos = (
                    i_mrnd(CHART_LSIZE[0]),
                    i_mrnd(CHART_LSIZE[1]),
                )
                food.update_chart_lpos(food_n_clpos)

        return None

    ctx0.on_key_press(on_k_p)

    ctx0.run()
