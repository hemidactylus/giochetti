import os
import sys
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import Thing
from egame.type_definitions import Drawable, FPair

LSIZE = (16, 10)
SIZE = None if "f" in sys.argv[1:] else (1600, 1000)

FARMER_LSIZE = (1, 2.4)
SPHERE_LRADIUS = 0.2
VEGETABLE_LSIZE = (1.5, 1.2)

FARMERV_MOD = 4.5

SPRITE_ROOT = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "farmer_images",
    )
)

vegetable_image_map: dict[int, pyglet.image.AbstractImage] = {
    key: pyglet.image.load(os.path.join(SPRITE_ROOT, f"{vname}.png"))
    for key, vname in {
        pyglet.window.key.Q: "broccoli",
        pyglet.window.key.W: "carrot",
        pyglet.window.key.E: "turnip",
    }.items()
}


class Vegetable(Thing):
    def __init__(
        self,
        *,
        lpos: FPair,
        vegetable_key: int,
        scaler: Scaler,
    ) -> None:
        image = vegetable_image_map[vegetable_key]
        x = scaler.r_x(lpos[0])
        y = scaler.r_x(lpos[1])
        sprite = pyglet.sprite.Sprite(image, x=x, y=y)
        sprite.scale_x = scaler.r_x(VEGETABLE_LSIZE[0]) / sprite.width  # type: ignore[attr-defined]
        sprite.scale_y = scaler.r_y(VEGETABLE_LSIZE[1]) / sprite.height  # type: ignore[attr-defined]
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=VEGETABLE_LSIZE,
            name="veg",
            sprites={
                "0": sprite,
            },
            sprite_offsets={
                "0": (0, 0),
            },
            t0_s=0.0,
            scaler=scaler,
        )


class Farmer(Thing):
    xdir: int

    def __init__(
        self,
        *,
        lpos: FPair,
        scaler: Scaler,
    ) -> None:
        farmer_images = {
            "c": pyglet.image.load(os.path.join(SPRITE_ROOT, "farmer_still.png")),
            "l": pyglet.image.load(os.path.join(SPRITE_ROOT, "farmer_left.png")),
            "r": pyglet.image.load(os.path.join(SPRITE_ROOT, "farmer_right.png")),
        }
        farmer_sprites: dict[str, Drawable] = {}
        farmer_offsets: dict[str, FPair] = {}
        for k, image in farmer_images.items():
            x = scaler.r_x(lpos[0])
            y = scaler.r_x(lpos[1])
            sprite = pyglet.sprite.Sprite(image, x=x, y=y)
            sprite.scale_x = scaler.r_x(FARMER_LSIZE[0]) / sprite.width  # type: ignore[attr-defined]
            sprite.scale_y = scaler.r_y(FARMER_LSIZE[1]) / sprite.height  # type: ignore[attr-defined]
            farmer_sprites[k] = sprite
            farmer_offsets[k] = (0, 0)

        Thing.__init__(
            self,
            lpos=lpos,
            lsize=FARMER_LSIZE,
            name="farmer",
            sprites=farmer_sprites,
            sprite_offsets=farmer_offsets,
            t0_s=0.0,
            scaler=scaler,
        )

        self.xdir = 1
        self.orient(0)

    def orient(self, lvx: int) -> None:
        xdir: int = 0
        if lvx > 0:
            xdir = 1
        elif lvx < 0:
            xdir = -1
        if xdir != self.xdir:
            self.xdir = xdir
            sprite_on = {0: "c", 1: "r", -1: "l"}[xdir]
            for k, v in self.sprites.items():
                v.visible = k == sprite_on

class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        field = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(0),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1]),
            color=(0, 192, 15, 255),
        )
        Thing.__init__(
            self,
            lpos=(0, 0),
            lsize=LSIZE,
            sprites={
                "f": field,
            },
            sprite_offsets={
                "f": (0, 0),
            },
            t0_s=0.0,
            scaler=scaler,
        )


if __name__ == "__main__":
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0), time_factor=1.0)
    ctx0.state["keys_map"] = {}

    farmer = Farmer(
        lpos=(5, 5),
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))
    ctx0.push_thing(farmer)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = True
        if symbol in vegetable_image_map:
            ctx.push_thing(
                Vegetable(
                    lpos=(
                        farmer.center_lpos[0] - 0.5 * VEGETABLE_LSIZE[0],
                        farmer.center_lpos[1] - 0.5 * VEGETABLE_LSIZE[1],
                    ),
                    vegetable_key=symbol,
                    scaler=ctx.scaler,
                )
            )
        return None

    def on_k_r(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = False
        return None

    def tk(ctx: Context, dt: float, t: float) -> None:
        farmerv: list[float] = [0, 0]
        if ctx.state["keys_map"].get(pyglet.window.key.UP):
            farmerv[1] += FARMERV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.DOWN):
            farmerv[1] -= FARMERV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.LEFT):
            farmerv[0] -= FARMERV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.RIGHT):
            farmerv[0] += FARMERV_MOD
        farmer.orient(farmerv[0])
        if farmerv != (0, 0):
            farmerd = (farmerv[0] * dt, farmerv[1] * dt)
            new_farmer_lpos = (
                farmer.lpos[0] + farmerd[0],
                farmer.lpos[1] + farmerd[1],
            )
            if not farmer.partially_out_of_boundaries(ctx, new_farmer_lpos):
                farmer.update_lpos(new_farmer_lpos)

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.run()
