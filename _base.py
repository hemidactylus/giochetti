# from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair

LSIZE = (16, 10)
SIZE = (1600, 1000)

PLAYER_LSIZE = (0.25, 0.6)
PLAYER_NOSE_RADIUS = 0.05


class Player(PhysicsThing):
    def __init__(
        self,
        *,
        lpos: FPair,
        scaler: Scaler,
    ) -> None:
        body = pyglet.shapes.Rectangle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(PLAYER_LSIZE[0]),
            scaler.r_y(PLAYER_LSIZE[1]),
            color=(128, 128, 128, 255),
        )
        nose = pyglet.shapes.Circle(
            scaler.r_x(lpos[0] + 0.5 * PLAYER_LSIZE[0]),
            scaler.r_y(lpos[1] + 0.8 * PLAYER_LSIZE[1]),
            radius=scaler.r_x(PLAYER_NOSE_RADIUS),
            color=(10, 10, 10, 255),
        )
        PhysicsThing.__init__(
            self,
            lpos=lpos,
            lsize=PLAYER_LSIZE,
            name="player",
            sprites={
                "0": body,
                "n": nose,
            },
            sprite_offsets={
                "0": (0, 0),
                "n": (0.5 * PLAYER_LSIZE[0], 0.8 * PLAYER_LSIZE[1]),
            },
            t0_s=0.0,
            lv=(0, 0),
            feels_g=False,
            scaler=scaler,
        )


# class Messenger(Thing):
#     label: pyglet.text.Label

#     def __init__(self, text: str, scaler: Scaler) -> None:
#         self.label = pyglet.text.Label(
#             text,
#             font_name="Times New Roman",
#             font_size=scaler.r_x(2),
#             x=0.5 * LSIZE[0],
#             y=0.5 * LSIZE[1],
#             anchor_x="center",
#             anchor_y="center",
#             color=(40, 255, 60, 128),
#         )
#         Thing.__init__(
#             self,
#             lpos=(0.5 * LSIZE[0], 0.5 * LSIZE[1]),
#             lsize=LSIZE,
#             sprites={"l": self.label},
#             sprite_offsets={"l": (0, 0)},
#             t0_s=0.0,
#             scaler=scaler,
#         )

#     def set_text(self, text: str) -> None:
#         self.label.text = text


class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        sky = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(0),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1]),
            color=(50, 90, 255, 255),
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
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -10.0), time_factor=1.0)

    player = Player(
        lpos=(5, 0),
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))
    ctx0.push_thing(player)
    # messenger = Messenger("Hello", scaler=ctx0.scaler)
    # ctx0.push_thing(messenger)

    ctx0.run()
