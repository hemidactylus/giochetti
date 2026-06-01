import sys
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import Thing
from egame.type_definitions import Color, FPair

LSIZE = (9, 10)
SIZE = None if "f" in sys.argv[1:] else (1600, 1000)


class LabeledBlock(Thing):
    label: pyglet.text.Label

    def __init__(
        self,
        *,
        lpos: FPair,
        lsize: FPair,
        color: Color,
        text: str,
        font_lsize: float,
        font_color: Color,
        name: str,
        scaler: Scaler,
    ) -> None:
        area = pyglet.shapes.Rectangle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(lsize[0]),
            scaler.r_y(lsize[1]),
            color=color,
        )
        border = pyglet.shapes.Box(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(lsize[0]),
            scaler.r_y(lsize[1]),
            color=(255, 255, 255, 255),
            thickness=scaler.r_x(0.02),
        )
        label_loffset = (
            0.5 * lsize[0],
            -0.5 * lsize[1],
        )
        self.label = pyglet.text.Label(
            text,
            font_name="Times New Roman",
            font_size=scaler.r_x(font_lsize),
            x=scaler.r_x(lpos[0] + label_loffset[0]),
            y=scaler.r_y(lpos[1] + label_loffset[1]),
            anchor_x="center",
            anchor_y="center",
            color=font_color,
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=lsize,
            name=name,
            sprites={
                "0": area,
                "b": border,
                "l": self.label,
            },
            sprite_offsets={
                "0": (0, 0),
                "b": (0, 0),
                "l": label_loffset,
            },
            t0_s=0.0,
            scaler=scaler,
        )

    def update(self, *, color: Color, text: str) -> None:
        self.label.text = text
        self.sprites["0"].color = color


if __name__ == "__main__":
    ctx0 = Context(size=SIZE, lsize=LSIZE, time_factor=1.0)

    ctx0.state["rgb"] = [10, 10, 10]
    rgb_ = [int(v * 255 / 10) for v in ctx0.state["rgb"]]

    red_block = LabeledBlock(
        lpos=(1, 2),
        lsize=(1, 1),
        color=(rgb_[0], 0, 0, 255),
        text=f"R = {ctx0.state['rgb'][0]}",
        font_lsize=0.3,
        font_color=(255, 0, 0, 255),
        name="red",
        scaler=ctx0.scaler,
    )
    green_block = LabeledBlock(
        lpos=(4, 2),
        lsize=(1, 1),
        color=(0, rgb_[1], 0, 255),
        text=f"G = {ctx0.state['rgb'][1]}",
        font_lsize=0.3,
        font_color=(0, 255, 0, 255),
        name="green",
        scaler=ctx0.scaler,
    )
    blue_block = LabeledBlock(
        lpos=(7, 2),
        lsize=(1, 1),
        color=(0, 0, rgb_[2], 255),
        text=f"B = {ctx0.state['rgb'][2]}",
        font_lsize=0.3,
        font_color=(0, 0, 255, 255),
        name="blue",
        scaler=ctx0.scaler,
    )

    final_block = LabeledBlock(
        lpos=(3, 7),
        lsize=(3, 2),
        color=(rgb_[0], rgb_[1], rgb_[2], 255),
        text=f"(R, G, B) = ({ctx0.state['rgb'][0]}, {ctx0.state['rgb'][1]}, {ctx0.state['rgb'][2]})",
        font_lsize=0.45,
        font_color=(255, 255, 255, 255),
        name="final",
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(red_block)
    ctx0.push_thing(green_block)
    ctx0.push_thing(blue_block)
    ctx0.push_thing(final_block)

    # key-press:
    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        new_rgb = [v for v in ctx.state["rgb"]]
        if symbol == pyglet.window.key.Q:
            new_rgb[0] += 1
        if symbol == pyglet.window.key.A:
            new_rgb[0] -= 1
        if symbol == pyglet.window.key.W:
            new_rgb[1] += 1
        if symbol == pyglet.window.key.S:
            new_rgb[1] -= 1
        if symbol == pyglet.window.key.E:
            new_rgb[2] += 1
        if symbol == pyglet.window.key.D:
            new_rgb[2] -= 1
        for i in range(3):
            new_rgb[i] = min(max(new_rgb[i], 0), 10)
        if new_rgb != ctx.state["rgb"]:
            ctx.state["rgb"] = new_rgb
            # recalc
            rgb_ = [int(v * 255 / 10) for v in ctx.state["rgb"]]
            red_block.update(
                color=(rgb_[0], 0, 0, 255), text=f"R = {ctx.state['rgb'][0]}"
            )
            green_block.update(
                color=(0, rgb_[1], 0, 255), text=f"G = {ctx.state['rgb'][1]}"
            )
            blue_block.update(
                color=(0, 0, rgb_[2], 255), text=f"B = {ctx.state['rgb'][2]}"
            )
            final_block.update(
                color=(rgb_[0], rgb_[1], rgb_[2], 255),
                text=f"(R, G, B) = ({ctx.state['rgb'][0]}, {ctx.state['rgb'][1]}, {ctx.state['rgb'][2]})",
            )
        return None

    ctx0.on_key_press(on_k_p)

    ctx0.run()
