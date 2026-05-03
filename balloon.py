from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import PhysicsThing
from egame.type_definitions import FPair

LSIZE = (16, 10)
SIZE = (1600, 1000)

MIN_LRAD = 0.8
MAX_LRAD = 2.0
ZERO_LRAD = 1.2
DELTA_FLATE = 0.1

GROUND_LY = 2

BUOYANCY_K = 10.0
WIND_V = 2.0

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
        PhysicsThing.__init__(
            self,
            lpos=lpos,
            lsize=(self.lrad, self.lrad),
            sprites={"0": ball},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            lv=(0, 0),
            feels_g=False,  # todo?
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
        pos = (self.scaler.r_x(self.lpos[0]), self.scaler.r_y(self.lpos[1]))
        ball = pyglet.shapes.Circle(
            pos[0],
            pos[1],
            self.scaler.r_x(self.lrad),
            color=(100, 20, 200, 255),
        )
        self.sprites["0"] = ball

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        dying = PhysicsThing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s)
        if dying:
            print("HAI PERSO!")
            return dying
        # movement (TODO improve, more physical)
        delta_y: float = 0
        delta_x = 0

        buoyancy = self.lrad - ZERO_LRAD
        if buoyancy < 0:
            if self.lpos[1] > GROUND_LY:
                delta_y = buoyancy * BUOYANCY_K * dt
        elif buoyancy > 0:
            delta_y = buoyancy * BUOYANCY_K * dt

        b_y = self.lpos[1]
        if b_y > 3.5 and b_y < 4.5:
            delta_x = WIND_V * dt
        elif b_y > 5.2 and b_y < 6.6:
            delta_x = -WIND_V * dt

        if delta_y != 0 or delta_x != 0:
            self.update_lpos((self.lpos[0] + delta_x, self.lpos[1] + delta_y))
        return False


if __name__ == "__main__":
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0), time_factor=1.0)

    balloon = Balloon(
        lpos=(5, GROUND_LY),
        lrad=MIN_LRAD,
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(balloon)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        if symbol == pyglet.window.key.Q:
            balloon.flate(DELTA_FLATE)
        elif symbol == pyglet.window.key.Z:
            balloon.flate(-DELTA_FLATE)
        return None

    ctx0.on_key_press(on_k_p)

    ctx0.run()
