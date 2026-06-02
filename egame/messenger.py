import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import Thing
from egame.type_definitions import Color


class Messenger(Thing):
    label: pyglet.text.Label
    font_lsize: int
    font_color: Color
    _text: str

    def __init__(
        self,
        text: str,
        *,
        font_lsize: int,
        color: Color,
        scaler: Scaler,
        context: Context,
    ) -> None:
        self._text = text
        ctx_lsize = context.lsize
        self.font_lsize = font_lsize
        self.color = color
        self.label = pyglet.text.Label(
            self.text,
            font_name="Times New Roman",
            font_size=scaler.r_x(self.font_lsize),
            x=0,
            y=0,
            anchor_x="center",
            anchor_y="center",
            color=color,
        )
        Thing.__init__(
            self,
            lpos=(0.5 * ctx_lsize[0], 0.5 * ctx_lsize[1]),
            lsize=ctx_lsize,
            sprites={"l": self.label},
            sprite_offsets={"l": (0, 0)},
            t0_s=0.0,
            scaler=scaler,
        )

    @property
    def text(self) -> str:
        return self._text

    def set_text(self, text: str) -> None:
        self._text = text
        self.label.text = self.text
