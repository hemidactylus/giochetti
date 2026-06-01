import sys
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.messenger import Messenger
from egame.randomize import fluctuate, i_mrnd, rnd
from egame.things import PhysicsThing, Thing
from egame.type_definitions import Drawable, FPair

LSIZE = (16, 10)
SIZE = None if "f" in sys.argv[1:] else (1600, 1000)

MIN_LRAD = 0.8
MAX_LRAD = 2.0
ZERO_LRAD = 1.2
DELTA_FLATE = 0.1

BOX_LSIDE = 0.45

GROUND_LY = 1.2
BALLOON_START_X = 0.25 * LSIZE[0]
BALLOON_END_X = 0.75 * LSIZE[0]
BALLOON_END_X_RANGE = 0.1 * LSIZE[0]

BUOYANCY_K = 5.0
C_X = 0.4
WIND_FORCE = 42.0

CLOUDS_PER_SECOND = 0.55
CLOUD_RADIUS = 0.3

LEFT_WIND_LY = 4.0
RIGHT_WIND_LY = 6.0
WIND_STRIP_HWIDTH = 0.6


class Balloon(PhysicsThing):
    lrad: float

    def __init__(
        self,
        *,
        lpos: FPair,
        lrad: float,
        scaler: Scaler,
    ) -> None:
        self.lrad = lrad
        ball = pyglet.shapes.Circle(
            0, 0, scaler.r_x(self.lrad), color=(100, 20, 200, 255)
        )
        box = pyglet.shapes.Rectangle(
            0,
            0,
            scaler.r_x(BOX_LSIDE),
            scaler.r_y(BOX_LSIDE),
            color=(60, 40, 0, 255),
        )
        PhysicsThing.__init__(
            self,
            lpos=lpos,
            lsize=(MAX_LRAD, MAX_LRAD),
            name="balloon",
            sprites={
                "0": ball,
                "box": box,
            },
            sprite_offsets={
                "0": (0, self.lrad + BOX_LSIDE),
                "box": (-0.5 * BOX_LSIDE, 0),
            },
            t0_s=0.0,
            lv=(0, 0),
            feels_g=False,
            scaler=scaler,
        )

    def flate(self, d_lrad: float) -> None:
        self.lrad = self.lrad + d_lrad
        if self.lrad < MIN_LRAD:
            self.lrad = MIN_LRAD
        if self.lrad > MAX_LRAD:
            self.lrad = MAX_LRAD
        self._refresh_balloon()

    def _refresh_balloon(self) -> None:
        pos = (
            self.scaler.r_x(self.lpos[0]),
            self.scaler.r_y(self.lpos[1] + self.lrad + BOX_LSIDE),
        )
        self.sprites["0"].delete()
        ball = pyglet.shapes.Circle(
            pos[0],
            pos[1],
            self.scaler.r_x(self.lrad),
            color=(100, 20, 200, 255),
        )
        self.sprites["0"] = ball
        self.update_sprite_offset("0", (0, self.lrad + BOX_LSIDE))

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        if ctx.state["mode"] == "playing":
            ax: float = 0
            ay: float = 0

            buoyancy = self.lrad - ZERO_LRAD
            if buoyancy < 0:
                if self.lpos[1] > GROUND_LY:
                    ay = buoyancy * BUOYANCY_K - self.lv[1] * C_X
                else:
                    if abs(self.lpos[0] - BALLOON_END_X) <= BALLOON_END_X_RANGE:
                        ctx.state["inbox"].append("won")
            elif buoyancy > 0:
                ay = buoyancy * BUOYANCY_K - self.lv[1] * C_X

            b_y = self.lpos[1] + self.lrad + BOX_LSIDE
            if abs(b_y - RIGHT_WIND_LY) < WIND_STRIP_HWIDTH:
                ax = WIND_FORCE * dt - self.lv[0] * C_X
            elif abs(b_y - LEFT_WIND_LY) < WIND_STRIP_HWIDTH:
                ax = -WIND_FORCE * dt - self.lv[0] * C_X

            new_lvx = self.lv[0] + ax * dt
            new_lvy = self.lv[1] + ay * dt
            if new_lvy < 0 and self.lpos[1] < GROUND_LY:
                new_lvy = 0
                new_lvx = 0
            self.lv = (new_lvx, new_lvy)

            dying = PhysicsThing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s)
            if dying:
                ctx.state["inbox"].append("lost")
            return dying
        elif ctx.state["mode"] == "idle":
            return False
        else:
            raise ValueError


class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        ground = pyglet.shapes.Rectangle(
            0,
            0,
            scaler.r_x(LSIZE[0]),
            scaler.r_y(GROUND_LY),
            color=(0, 70, 20, 255),
        )
        sky = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(GROUND_LY),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1] - GROUND_LY),
            color=(50, 90, 255, 255),
        )
        target = pyglet.shapes.Rectangle(
            scaler.r_x(BALLOON_END_X - BALLOON_END_X_RANGE),
            scaler.r_y(GROUND_LY - 0.2),
            scaler.r_x(2 * BALLOON_END_X_RANGE),
            scaler.r_y(0.2),
            color=(255, 40, 40, 255),
        )
        Thing.__init__(
            self,
            lpos=(0, 0),
            lsize=LSIZE,
            sprites={
                "g": ground,
                "s": sky,
                "t": target,
            },
            sprite_offsets={
                "g": (0, 0),
                "s": (0, GROUND_LY),
                "t": (
                    BALLOON_END_X - BALLOON_END_X_RANGE,
                    GROUND_LY - 0.2,
                ),
            },
            t0_s=0.0,
            scaler=scaler,
        )


class Cloudette(PhysicsThing):
    def __init__(self, *, lpos: FPair, lvx: float, scaler: Scaler) -> None:
        shape: dict[str, Drawable] = {
            f"{i}": pyglet.shapes.Circle(
                0,
                0,
                scaler.r_x(CLOUD_RADIUS),
                color=(255, 255, 255, 128),
            )
            for i in range(3)
        }
        offsets: dict[str, FPair] = {
            "0": (-0.2, -0.5 * CLOUD_RADIUS),
            "1": (0.0, -0.5 * CLOUD_RADIUS),
            "2": (0.2, -0.5 * CLOUD_RADIUS),
        }
        PhysicsThing.__init__(
            self,
            lpos=lpos,
            lsize=(CLOUD_RADIUS, 3 * CLOUD_RADIUS),
            sprites=shape,
            sprite_offsets=offsets,
            t0_s=0.0,
            lv=(lvx, 0),
            feels_g=False,
            scaler=scaler,
        )


if __name__ == "__main__":
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0), time_factor=1.0)

    ctx0.state["mode"] = "idle"
    ctx0.state["inbox"] = []

    balloon = Balloon(
        lpos=(BALLOON_START_X, GROUND_LY),
        lrad=MIN_LRAD,
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))
    ctx0.push_thing(balloon)
    messenger = Messenger(
        "i = inizia",
        font_lsize=2,
        color=(40, 255, 60, 128),
        scaler=ctx0.scaler,
        context=ctx0,
    )
    ctx0.push_thing(messenger)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        b: Balloon | None
        b = ctx.thing_by_name("balloon")  # type: ignore[assignment]
        if ctx.state["mode"] == "playing":
            if b is None:
                raise ValueError("no balloon")
            if symbol == pyglet.window.key.Q:
                b.flate(DELTA_FLATE)
            elif symbol == pyglet.window.key.Z:
                b.flate(-DELTA_FLATE)
        elif ctx.state["mode"] == "idle":
            if symbol == pyglet.window.key.I:
                messenger.set_text("")
                ctx.state["mode"] = "playing"
                if b is None:
                    new_b = Balloon(
                        lpos=(BALLOON_START_X, GROUND_LY),
                        lrad=MIN_LRAD,
                        scaler=ctx.scaler,
                    )
                    ctx.push_thing(new_b)
                else:
                    # just reposition
                    b.update_lpos((BALLOON_START_X, GROUND_LY))
        else:
            raise ValueError
        return None

    def tk(ctx: Context, dt: float, t: float) -> None:
        if ctx.state["inbox"]:
            action = ctx.state["inbox"][0]
            messenger.set_text({"won": "Hai vinto!", "lost": "Hai perso."}[action])
            ctx.state["inbox"] = []
            ctx.state["mode"] = "idle"

        chance = CLOUDS_PER_SECOND * dt
        if rnd() < chance:
            if i_mrnd(2) == 0:
                # up
                cloud_y = fluctuate(LEFT_WIND_LY, WIND_STRIP_HWIDTH)
                ctx.push_thing(
                    Cloudette(
                        lpos=(LSIZE[0], cloud_y),
                        lvx=-0.6,
                        scaler=ctx.scaler,
                    )
                )
            else:
                # down
                cloud_y = fluctuate(RIGHT_WIND_LY, WIND_STRIP_HWIDTH)
                ctx.push_thing(
                    Cloudette(
                        lpos=(0, cloud_y),
                        lvx=0.6,
                        scaler=ctx.scaler,
                    )
                )

    ctx0.tick(tk)
    ctx0.on_key_press(on_k_p)

    ctx0.run()
