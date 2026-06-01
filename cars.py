import os
import sys
import time
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.randomize import i_mrnd
from egame.things import PhysicsThing, Thing
from egame.type_definitions import Drawable, FPair, IPair

SHOW_FOOD = True
EMIT_POO = True

SIZE = None if "f" in sys.argv[1:] else (1200, 1000)

CAR_LSIZE = (2, 1.4)
LSIZE = (12, 12)
FOOD_LSIDE = 0.5

CHART_LDELTA = (1.5, 1.5)
CHART_LSIZE = (10, 10)
CHART_GUIDELINE_THICKNESS = 0.05
CAR_LABEL_COLOR = (20, 120, 26, 255)
CAR_LABEL_FORMAT = "(x={x}, y={y})"

MOVEMENT_STYLE = "discrete"
# MOVEMENT_STYLE = "continuum"
# MOVEMENT_STYLE = "physical"
DISCRETE_TORUS = False  # True

CONTINUUM_CAR_LV = 2.5
CONTINUUM_CAR_LA = 8.0
PHYSICAL_FRICTION_K = 1.5
PHYSICAL_MIN_V = 0.1

SPRITE_ROOT = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "cars_images",
    )
)


class Car(Thing):
    chart_lpos: IPair
    label_visible: bool

    def __init__(self, label: str | None, chart_lpos: IPair, scaler: Scaler) -> None:
        self.ini = time.time()
        self.label_visible = False
        car_img = pyglet.image.load(os.path.join(SPRITE_ROOT, "car.png"))
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
                color=CAR_LABEL_COLOR,
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
            color=CAR_LABEL_COLOR,
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
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0))

    car_chart_lpos = (
        i_mrnd(CHART_LSIZE[0]),
        i_mrnd(CHART_LSIZE[1]),
    )
    car = Car(
        CAR_LABEL_FORMAT.format(x=car_chart_lpos[0], y=car_chart_lpos[1]),
        car_chart_lpos,
        ctx0.scaler,
    )
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

    keys_map: dict[int, bool] = {}

    def detect_interactions() -> None:
        # eats?
        foo_delta = (
            abs(food.lpos[0] - car.lcenter[0]),
            abs(food.lpos[1] - car.lcenter[1]),
        )
        if foo_delta[0] <= 0.5 and foo_delta[1] <= 0.5:
            if EMIT_POO:
                ctx0.push_thing(Poo(car.lcenter, ctx0.scaler))
            food_n_clpos = (
                i_mrnd(CHART_LSIZE[0]),
                i_mrnd(CHART_LSIZE[1]),
            )
            food.update_chart_lpos(food_n_clpos)

    # discrete movement:

    def on_k_p_discrete(
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

        if DISCRETE_TORUS:
            car_n_clpos = (
                (car_n_clpos[0] + LSIZE[0]) % LSIZE[0],
                (car_n_clpos[1] + LSIZE[1]) % LSIZE[1],
            )

        if car_n_clpos != car.chart_lpos:
            car.update_label(
                CAR_LABEL_FORMAT.format(x=car_n_clpos[0], y=car_n_clpos[1])
            )
            car.update_chart_lpos(car_n_clpos)
            detect_interactions()

        return None

    # continuum movement:
    def on_k_p_continuum(
        ctx: Context, symbol: int, modifiers: int, show_guidelines=show_guidelines
    ) -> Literal[True] | None:
        if symbol == pyglet.window.key.A:
            ctx.push_thing(Poo(car.lcenter, ctx.scaler))
        elif symbol == pyglet.window.key.C:
            if show_guidelines[0]:
                show_guidelines[0] = False
                car.hide_label()
                for gl in guideline_things:
                    gl.hide()
            else:
                show_guidelines[0] = True
                for gl in guideline_things:
                    gl.show()

        keys_map[symbol] = True
        return None

    def on_k_r_continuum(
        ctx: Context, symbol: int, modifiers: int, show_guidelines=show_guidelines
    ) -> Literal[True] | None:
        keys_map[symbol] = False
        return None

    def tk_continuum(ctx: Context, dt: float, t: float) -> None:
        lv: list[float] = [0, 0]
        if keys_map.get(pyglet.window.key.UP):
            lv[1] += CONTINUUM_CAR_LV
        if keys_map.get(pyglet.window.key.DOWN):
            lv[1] -= CONTINUUM_CAR_LV
        if keys_map.get(pyglet.window.key.LEFT):
            lv[0] -= CONTINUUM_CAR_LV
        if keys_map.get(pyglet.window.key.RIGHT):
            lv[0] += CONTINUUM_CAR_LV
        if lv != (0, 0):
            ld = (lv[0] * dt, lv[1] * dt)
            new_car_lpos = (
                car.lpos[0] + ld[0],
                car.lpos[1] + ld[1],
            )
            car.update_lpos((new_car_lpos[0], new_car_lpos[1]))
            detect_interactions()

    car_lv: list[tuple[float, float]] = [(0, 0)]

    def tk_physical(ctx: Context, dt: float, t: float) -> None:
        la: list[float] = [0, 0]
        if keys_map.get(pyglet.window.key.UP):
            la[1] += CONTINUUM_CAR_LA
        if keys_map.get(pyglet.window.key.DOWN):
            la[1] -= CONTINUUM_CAR_LA
        if keys_map.get(pyglet.window.key.LEFT):
            la[0] -= CONTINUUM_CAR_LA
        if keys_map.get(pyglet.window.key.RIGHT):
            la[0] += CONTINUUM_CAR_LA
        if la[0] == 0 and car_lv[0][0] != 0:
            la[0] = -PHYSICAL_FRICTION_K * car_lv[0][0]
        if la[1] == 0 and car_lv[0][1] != 0:
            la[1] = -PHYSICAL_FRICTION_K * car_lv[0][1]
        delta_lv = (la[0] * dt, la[1] * dt)
        if delta_lv != (0, 0):
            new_car_lv = (car_lv[0][0] + delta_lv[0], car_lv[0][1] + delta_lv[1])
            car_lv[0] = (
                new_car_lv[0] if abs(new_car_lv[0]) > PHYSICAL_MIN_V else 0.0,
                new_car_lv[1] if abs(new_car_lv[1]) > PHYSICAL_MIN_V else 0.0,
            )
        if car_lv[0] != (0, 0):
            delta_l = (new_car_lv[0] * dt, new_car_lv[1] * dt)
            new_car_lpos = (car.lpos[0] + delta_l[0], car.lpos[1] + delta_l[1])
            car.update_lpos(new_car_lpos)
            detect_interactions()

    if MOVEMENT_STYLE == "discrete":
        ctx0.on_key_press(on_k_p_discrete)
    elif MOVEMENT_STYLE == "continuum":
        ctx0.on_key_press(on_k_p_continuum)
        ctx0.on_key_release(on_k_r_continuum)
        ctx0.tick(tk_continuum)
    elif MOVEMENT_STYLE == "physical":
        ctx0.on_key_press(on_k_p_continuum)
        ctx0.on_key_release(on_k_r_continuum)
        ctx0.tick(tk_physical)
    else:
        raise ValueError

    ctx0.run()
