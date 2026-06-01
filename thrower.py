import math
import os
import sys
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair

LSIZE = (18, 10)
SIZE = None if "f" in sys.argv[1:] else (1600, 1000)
THROWER_LSIZE = (0.5, 1.5)
THROWER_LINE_LSIZE = 1.2
THROWER_LINE_LWIDTH = 0.1
ROTATE_W = 45.0
BALL_LOW_THRESHOLD = 0.45

MARKER_FONT_SIZE = 0.7
BALL_SIDE = 1
BALL_LVMOD = 6
G_LMOD = 2.5


SPRITE_ROOT = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "thrower_images",
    )
)

CABBAGE = pyglet.image.load(os.path.join(SPRITE_ROOT, "cabbage.png"))


class Thrower(Thing):
    angle_deg: float
    line: pyglet.shapes.Line

    def __init__(
        self,
        *,
        lpos: FPair,
        angle_deg: float,
        scaler: Scaler,
    ) -> None:
        body = pyglet.shapes.Rectangle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(THROWER_LSIZE[0]),
            scaler.r_y(THROWER_LSIZE[1]),
            color=(10, 80, 50, 255),
        )
        self.lpos = lpos
        self.lsize = THROWER_LSIZE
        self.angle_deg = angle_deg
        line_lps = self.line_lpoints()
        self.line = pyglet.shapes.Line(
            scaler.r_x(line_lps[0][0]),
            scaler.r_y(line_lps[0][1]),
            scaler.r_x(line_lps[1][0]),
            scaler.r_y(line_lps[1][1]),
            thickness=scaler.r_x(THROWER_LINE_LWIDTH),
            color=(10, 80, 50, 255),
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=THROWER_LSIZE,
            name="thrower",
            sprites={
                "0": body,
                "l": self.line,
            },
            sprite_offsets={
                "0": (0, 0),
                "l": (line_lps[1]),
            },
            t0_s=0.0,
            scaler=scaler,
        )
        self.update_angle_deg(self.angle_deg)

    def update_angle_deg(self, angle_deg: float) -> None:
        self.angle_deg = angle_deg
        new_line_lps = self.line_lpoints()
        self.line = pyglet.shapes.Line(
            self.scaler.r_x(new_line_lps[0][0]),
            self.scaler.r_y(new_line_lps[0][1]),
            self.scaler.r_x(new_line_lps[1][0]),
            self.scaler.r_y(new_line_lps[1][1]),
            thickness=self.scaler.r_x(THROWER_LINE_LWIDTH),
            color=(10, 80, 50, 255),
        )
        self.sprites["l"] = self.line

    def line_lpoints(self) -> tuple[FPair, FPair]:
        line_lp1 = (
            self.lpos[0] + self.lsize[0] * 0.5,
            self.lpos[1] + self.lsize[1] - 0.5 * THROWER_LINE_LWIDTH,
        )
        angle_rad = self.angle_deg * math.pi / 180
        line_lvector = (
            THROWER_LINE_LSIZE * math.cos(angle_rad),
            THROWER_LINE_LSIZE * math.sin(angle_rad),
        )
        line_lp2 = (line_lp1[0] + line_lvector[0], line_lp1[1] + line_lvector[1])
        return (line_lp1, line_lp2)


class Marker(Thing):
    def __init__(self, lpos: FPair, *, text: str, scaler: Scaler) -> None:
        label = pyglet.text.Label(
            text,
            font_name="Times New Roman",
            font_size=scaler.r_x(MARKER_FONT_SIZE),
            x=scaler.r_x(lpos[0]),
            y=scaler.r_x(lpos[1]),
            anchor_x="center",
            anchor_y="center",
            color=(150, 0, 0, 255),
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(0, 0),
            name="marker",
            sprites={
                "0": label,
            },
            sprite_offsets={
                "0": (0, 0),
            },
            t0_s=0.0,
            scaler=scaler,
        )


class Ball(PhysicsThing):
    marked: bool  # TODO improve with ctx in thing life methods

    def __init__(self, lpos: FPair, lv: FPair, scaler: Scaler) -> None:
        x = scaler.r_x(lpos[0])
        y = scaler.r_x(lpos[1])
        ball = pyglet.sprite.Sprite(CABBAGE, x=x, y=y)
        ball.scale_x = scaler.r_x(BALL_SIDE) / ball.width  # type: ignore[attr-defined]
        ball.scale_y = scaler.r_y(BALL_SIDE) / ball.height  # type: ignore[attr-defined]
        PhysicsThing.__init__(
            self,
            lpos=lpos,
            lsize=(BALL_SIDE, BALL_SIDE),
            sprites={"0": ball},
            sprite_offsets={"0": (-0.5 * BALL_SIDE, -0.5 * BALL_SIDE)},
            t0_s=0.0,
            name="ball",
            lv=lv,
            feels_g=True,
            scaler=scaler,
        )
        self.marked = False


class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        sky = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(0),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1]),
            color=(100, 100, 255, 255),
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
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -G_LMOD), time_factor=1.0)
    ctx0.state["keys_map"] = {}
    ctx0.state["marker_count"] = 0

    thrower = Thrower(
        lpos=(1, 0),
        angle_deg=20,
        scaler=ctx0.scaler,
    )

    def on_k_p(
        ctx: Context,
        symbol: int,
        modifiers: int,
    ) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = True
        if symbol == pyglet.window.key.SPACE:
            angle_rad = thrower.angle_deg * math.pi / 180
            lv = (
                BALL_LVMOD * math.cos(angle_rad),
                BALL_LVMOD * math.sin(angle_rad),
            )
            ctx.push_thing(
                Ball(
                    (
                        thrower.lpos[0] + 0.5 * thrower.lsize[0],
                        thrower.lpos[1] + thrower.lsize[1] - 0.5 * THROWER_LINE_LWIDTH,
                    ),
                    lv=lv,
                    scaler=ctx.scaler,
                )
            )
        elif symbol == pyglet.window.key.Q:
            ctx.pop_things(lambda thg: thg.name == "marker")
            ctx.state["marker_count"] = 0
        return None

    def on_k_r(
        ctx: Context,
        symbol: int,
        modifiers: int,
    ) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = False
        return None

    def tk(ctx: Context, dt: float, t: float) -> None:
        delta_degs: float = 0
        if ctx.state["keys_map"].get(pyglet.window.key.LEFT):
            delta_degs += ROTATE_W * dt
        if ctx.state["keys_map"].get(pyglet.window.key.RIGHT):
            delta_degs -= ROTATE_W * dt
        if delta_degs:
            new_delta_degs = max(
                min(thrower.angle_deg + delta_degs, 90),
                0,
            )
            thrower.update_angle_deg(new_delta_degs)
        # marking balls
        for thg in ctx.things:
            if thg.name == "ball":
                ball: Ball = thg  # type: ignore[assignment]
                if not ball.marked and ball.lpos[1] < BALL_LOW_THRESHOLD:
                    ball.marked = True
                    ctx.state["marker_count"] += 1
                    ctx.push_thing(
                        Marker(
                            (ball.lpos[0], BALL_LOW_THRESHOLD),
                            text=f"{ctx.state['marker_count']}",
                            scaler=ctx.scaler,
                        )
                    )

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))
    ctx0.push_thing(thrower)
    # messenger = Messenger("Hello", scaler=ctx0.scaler)
    # ctx0.push_thing(messenger)

    ctx0.run()
