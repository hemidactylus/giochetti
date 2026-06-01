import math
import sys
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import Thing
from egame.type_definitions import Color, FPair

LSIZE = (16, 10)
SIZE = None if "f" in sys.argv[1:] else (1600, 1000)


class Sphere(Thing):
    lref: Thing
    omega: float
    lradius: float
    olradius: float
    theta0: float
    actual_t_s: float

    def __init__(
        self,
        *,
        olradius: float,
        color: Color,
        lref: Thing,
        lradius: float,
        theta0: float,
        omega: float,
        scaler: Scaler,
    ) -> None:
        self.lref = lref
        self.omega = omega
        self.lradius = lradius
        self.olradius = olradius
        self.theta0 = theta0
        self.actual_t_s = 0.0

        lpos = self.calc_lpos()

        sphere = pyglet.shapes.Circle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(self.lradius),
            color=color,
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(2 * self.olradius, 2 * self.olradius),
            name="sphere",
            sprites={
                "0": sphere,
            },
            sprite_offsets={
                "0": (0, 0),
            },
            t0_s=0.0,
            scaler=scaler,
        )

    def calc_lpos(self) -> FPair:
        arg = self.actual_t_s * self.omega + self.theta0
        dx = self.olradius * math.cos(arg)
        dy = self.olradius * math.sin(arg)
        lfocus = self.lref.lpos
        return (lfocus[0] + dx, lfocus[1] + dy)

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        if Thing.dies_on_update(self, ctx, dt, t_s):
            return True
        if ctx.state["running"]:
            self.actual_t_s += dt
        self.update_lpos(self.calc_lpos())
        return False


class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        sky = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(0),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1]),
            color=(0, 0, 0, 255),
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
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0), time_factor=0.5)
    ctx0.state["keys_map"] = {}
    ctx0.state["running"] = True

    sun = Sphere(
        olradius=0,
        color=(255, 255, 0, 255),
        lref=Thing(
            lpos=(8, 5),
            lsize=(0, 0),
            sprites={},
            sprite_offsets={},
            t0_s=0,
            scaler=ctx0.scaler,
        ),
        lradius=0.4,
        theta0=0,
        omega=0,
        scaler=ctx0.scaler,
    )
    earth = Sphere(
        olradius=2,
        color=(0, 255, 100, 255),
        lref=sun,
        lradius=0.1,
        theta0=0,
        omega=2,
        scaler=ctx0.scaler,
    )
    moon = Sphere(
        olradius=0.4,
        color=(128, 128, 128, 255),
        lref=earth,
        lradius=0.04,
        theta0=0,
        omega=5,
        scaler=ctx0.scaler,
    )
    mars = Sphere(
        olradius=2.6,
        color=(150, 0, 0, 255),
        lref=sun,
        lradius=0.08,
        theta0=0.6,
        omega=1.4,
        scaler=ctx0.scaler,
    )
    jupiter = Sphere(
        olradius=4.6,
        color=(50, 120, 120, 255),
        lref=sun,
        lradius=0.2,
        theta0=1.2,
        omega=1.3,
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))
    ctx0.push_thing(sun)
    ctx0.push_thing(earth)
    ctx0.push_thing(moon)
    ctx0.push_thing(mars)
    ctx0.push_thing(jupiter)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = True
        if symbol == pyglet.window.key.SPACE:
            ctx.state["running"] = not ctx.state["running"]
        return None

    def on_k_r(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = False
        return None

    def tk(ctx: Context, dt: float, t: float) -> None:
        pass

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.run()
