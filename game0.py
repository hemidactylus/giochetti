import time
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.randomize import i_mrnd
from egame.things import PhysicsThing, Thing
from egame.type_definitions import Drawable, FPair, IPair

SHOW_FOOD = True
EMIT_POO = False

CAR_LSIZE = (2, 1.4)
LSIZE = (12, 12)
FOOD_LSIDE = 0.5

CHART_LDELTA = (1.5, 1.5)
CHART_LSIZE = (10, 10)
CHART_GUIDELINE_THICKNESS = 0.05


class Car(Thing):
    chart_lpos: IPair
    label_visible: bool

    def __init__(self, label: str | None, chart_lpos: IPair, scaler: Scaler) -> None:
        self.ini = time.time()
        self.label_visible = False
        car_img = pyglet.image.load("car.png")
        car_sprite = pyglet.sprite.Sprite(car_img, x=0, y=0)
        car_sprite.scale_x = scaler.r_x(CAR_LSIZE[0]) / car_img.width
        car_sprite.scale_y = scaler.r_y(CAR_LSIZE[1]) / car_img.height
        sprites: dict[str, Drawable] = {"0": car_sprite}
        sprite_offsets: dict[str, FPair] = {"0": (0, 0)}
        if label is not None:
            the_label = pyglet.text.Label(
                label,
                font_name="Times New Roman",
                font_size=scaler.r_x(0.5),
                x=0,
                y=0,
                anchor_x="center",
                anchor_y="center",
                color=(138, 20, 128, 255),
            )
            the_label.visible = self.label_visible
            sprites["label"] = the_label
            sprite_offsets["label"] = (0.5 * CAR_LSIZE[0], 0.7 * CAR_LSIZE[1])
        Thing.__init__(
            self,
            lpos=chart_lpos,
            lsize=CAR_LSIZE,
            sprites=sprites,
            sprite_offsets=sprite_offsets,
            t0_s=0.0,
            name="car",
            scaler=scaler,
        )
        self.update_chart_lpos(chart_lpos)

    def show_label(self) -> None:
        self.label_visible = True
        self.sprites["label"].visible = self.label_visible

    def hide_label(self) -> None:
        self.label_visible = False
        self.sprites["label"].visible = self.label_visible

    def update_label(self, label: str) -> None:
        if "label" not in self.sprites:
            raise ValueError
        the_label = pyglet.text.Label(
            label,
            font_name="Times New Roman",
            font_size=self.scaler.r_x(0.5),
            x=0,
            y=0,
            anchor_x="center",
            anchor_y="center",
            color=(138, 20, 128, 255),
        )
        the_label.visible = self.label_visible
        self.sprites["label"] = the_label

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


class Guideline(Thing):
    def __init__(self, tick_i: int, kind: str, scaler: Scaler) -> None:
        the_line: pyglet.shapes.Rectangle
        lpos: FPair
        lsize: FPair
        if kind == "h":
            y = -0.5 + CHART_LDELTA[1] + tick_i
            xs = (
                -0.5 + CHART_LDELTA[0],
                -0.5 + CHART_LDELTA[0] + CHART_LSIZE[0],
            )
            the_line = pyglet.shapes.Rectangle(
                scaler.r_x(xs[0]),
                scaler.r_y(y - CHART_GUIDELINE_THICKNESS),
                scaler.r_x(xs[1] - xs[0]),
                scaler.r_y(CHART_GUIDELINE_THICKNESS),
                color=(255, 255, 255, 128),
            )
            lpos = (xs[0], y)
            lsize = (xs[1] - xs[0], CHART_GUIDELINE_THICKNESS)
        elif kind == "v":
            x = -0.5 + CHART_LDELTA[0] + tick_i
            ys = (
                -0.5 + CHART_LDELTA[1],
                -0.5 + CHART_LDELTA[1] + CHART_LSIZE[1],
            )
            the_line = pyglet.shapes.Rectangle(
                scaler.r_x(x - CHART_GUIDELINE_THICKNESS),
                scaler.r_y(ys[0]),
                scaler.r_x(CHART_GUIDELINE_THICKNESS),
                scaler.r_y(ys[1] - ys[0]),
                color=(255, 255, 255, 128),
            )
            lpos = (x, ys[0])
            lsize = (CHART_GUIDELINE_THICKNESS, ys[1] - ys[0])
        else:
            raise ValueError
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=lsize,
            sprites={"0": the_line},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            scaler=scaler,
        )


class Label(Thing):
    def __init__(self, chart_lpos: IPair, text: str, scaler: Scaler) -> None:
        lpos = (
            CHART_LDELTA[0] + chart_lpos[0],
            CHART_LDELTA[1] + chart_lpos[1],
        )
        the_text = pyglet.text.Label(
            text,
            font_name="Times New Roman",
            font_size=scaler.r_x(0.7),
            x=scaler.r_x(lpos[0]),
            y=scaler.r_y(lpos[1]),
            anchor_x="center",
            anchor_y="center",
            color=(255, 255, 255, 128),
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(0, 0),
            sprites={"0": the_text},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            scaler=scaler,
        )


if __name__ == "__main__":
    ctx0 = Context(size=(1200, 1200), lsize=LSIZE, lg=(0.0, -10.0))

    car_chart_lpos = (
        i_mrnd(CHART_LSIZE[0]),
        i_mrnd(CHART_LSIZE[1]),
    )
    car = Car(f"({car_chart_lpos[0]},{car_chart_lpos[1]})", car_chart_lpos, ctx0.scaler)
    food = Food(
        (
            i_mrnd(CHART_LSIZE[0]) if SHOW_FOOD else CHART_LSIZE[0] + 10,
            i_mrnd(CHART_LSIZE[1]) if SHOW_FOOD else CHART_LSIZE[1] + 10,
        ),
        ctx0.scaler,
    )

    guideline_things: list[Thing] = []
    for tick_i in range(CHART_LSIZE[0] + 1):
        guideline_things.append(Guideline(tick_i=tick_i, kind="h", scaler=ctx0.scaler))
        guideline_things.append(Guideline(tick_i=tick_i, kind="v", scaler=ctx0.scaler))
    for tick_i in range(CHART_LSIZE[0]):
        guideline_things.append(
            Label(chart_lpos=(tick_i, -1), text=f"{tick_i}", scaler=ctx0.scaler)
        )
        guideline_things.append(
            Label(chart_lpos=(-1, tick_i), text=f"{tick_i}", scaler=ctx0.scaler)
        )
    for gl in guideline_things:
        gl.hide()
        ctx0.push_thing(gl)

    ctx0.push_thing(car)
    ctx0.push_thing(food)

    show_guidelines = [False]

    def on_k_p(
        ctx: Context, symbol: int, modifiers: int, show_guidelines=show_guidelines
    ) -> Literal[True] | None:
        car_n_clpos = car.chart_lpos
        if symbol == pyglet.window.key.UP:
            car_n_clpos = (
                car_n_clpos[0],
                car_n_clpos[1] + 1,
            )
        elif symbol == pyglet.window.key.DOWN:
            car_n_clpos = (
                car_n_clpos[0],
                car_n_clpos[1] - 1,
            )
        elif symbol == pyglet.window.key.LEFT:
            car_n_clpos = (
                car_n_clpos[0] - 1,
                car_n_clpos[1],
            )
        elif symbol == pyglet.window.key.RIGHT:
            car_n_clpos = (
                car_n_clpos[0] + 1,
                car_n_clpos[1],
            )
        elif symbol == pyglet.window.key.A:
            ctx.push_thing(Poo(car.lcenter, ctx.scaler))
        elif symbol == pyglet.window.key.C:
            if show_guidelines[0]:
                show_guidelines[0] = False
                car.hide_label()
                for gl in guideline_things:
                    gl.hide()
            else:
                show_guidelines[0] = True
                car.show_label()
                for gl in guideline_things:
                    gl.show()

        if car_n_clpos != car.chart_lpos:
            car.update_label(f"({car_n_clpos[0]},{car_n_clpos[1]})")
            car.update_chart_lpos(car_n_clpos)
            # eats?
            foo_delta = (
                abs(food.lpos[0] - car.lcenter[0]),
                abs(food.lpos[1] - car.lcenter[1]),
            )
            if foo_delta[0] <= 0.4 and foo_delta[1] <= 0.4:
                if EMIT_POO:
                    ctx.push_thing(Poo(car.lcenter, ctx.scaler))
                food_n_clpos = (
                    i_mrnd(CHART_LSIZE[0]),
                    i_mrnd(CHART_LSIZE[1]),
                )
                food.update_chart_lpos(food_n_clpos)

        return None

    ctx0.on_key_press(on_k_p)

    ctx0.run()
