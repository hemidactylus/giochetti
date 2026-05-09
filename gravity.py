from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair

LSIZE = (16, 10)
SIZE = (1600, 1000)

PLAYER_LSIZE = (0.25, 0.6)
PLAYER_NOSE_RADIUS = 0.05
PLAYER_JUMP_VY = 5.0

PLAYER_V = 2.5

BORDER_BLOCK_WIDTH = 0.2


class Player(PhysicsThing):
    anchored: bool

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
        self.anchored = True
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

    def _orient(self, dir: int) -> None:
        n_off_factor: float
        if dir > 0:
            n_off_factor = 1.0
        elif dir < 0:
            n_off_factor = 0.0
        else:
            n_off_factor = 0.5
        self.update_sprite_offset(
            "n",
            (
                n_off_factor * PLAYER_LSIZE[0],
                0.8 * PLAYER_LSIZE[1],
            ),
        )

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        if Thing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s):
            return True
        new_lv, new_lpos = self.compute_motion(ctx, dt=dt, t_s=t_s, feels_g=True)
        # collision check for player
        blocks: list[Block] = [thg for thg in ctx.things if thg.name[:5] == "block"]  # type: ignore[misc]
        falls_in_block = False
        blocking_blocks: list[Block] = []
        for block in blocks:
            if block.contains(new_lpos, epsilon=0.0001):
                falls_in_block = True
                blocking_blocks.append(block)
        #
        if falls_in_block:
            self.anchored = True
            # TODO bring lpos to touching the first encountered surface (for smooth landing)
            # approximate: take first blocking block
            # TODO avoid sticking to walls or ceiling!
            blocking = blocking_blocks[0]
            landings = [
                (self.lpos[0], blocking.lpos[1]),
                (self.lpos[0], blocking.lpos[1] + blocking.lsize[1]),
                (blocking.lpos[0], self.lpos[1]),
                (blocking.lpos[0] + blocking.lsize[0], self.lpos[1]),
            ]
            land_distances2 = [
                (i, (self.lpos[0] - lx) ** 2 + (self.lpos[1] - ly) ** 2)
                for i, (lx, ly) in enumerate(landings)
            ]
            best_dist_i = sorted(land_distances2, key=lambda id: id[1])[0][0]
            best_landing = landings[best_dist_i]
            self.update_lpos(best_landing)
            #
            self.lv = (self.lv[0], 0.0)
            self.feels_g = False
        else:
            self.anchored = False
            self.feels_g = True
        return PhysicsThing.dies_on_update(self, ctx, dt=dt, t_s=t_s)


class Block(Thing):
    def __init__(
        self,
        lpos: FPair,
        lsize: FPair,
        color: tuple[int, int, int, int],
        name: str,
        scaler: Scaler,
    ) -> None:
        block = pyglet.shapes.Rectangle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(lsize[0]),
            scaler.r_y(lsize[1]),
            color=color,
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=lsize,
            sprites={"0": block},
            sprite_offsets={"0": (0, 0)},
            t0_s=0.0,
            name=name,
            scaler=scaler,
        )

    def contains(self, lpos: FPair, epsilon: float = 0.0) -> bool:
        return (
            lpos[0] + epsilon > self.lpos[0]
            and lpos[0] - epsilon < self.lpos[0] + self.lsize[0]
            and lpos[1] + epsilon > self.lpos[1]
            and lpos[1] - epsilon < self.lpos[1] + self.lsize[1]
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
        lpos=(0.5 * LSIZE[0], BORDER_BLOCK_WIDTH),
        scaler=ctx0.scaler,
    )

    ctx0.state["keys_map"] = {}

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))

    # blocks
    ctx0.push_thing(
        Block(
            lpos=(0, 0),
            lsize=(LSIZE[0], BORDER_BLOCK_WIDTH),
            color=(0, 0, 96, 255),
            name="block0",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        Block(
            lpos=(LSIZE[0] - BORDER_BLOCK_WIDTH, 0),
            lsize=(BORDER_BLOCK_WIDTH, LSIZE[1]),
            color=(0, 0, 96, 255),
            name="block1",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        Block(
            lpos=(0, LSIZE[1] - BORDER_BLOCK_WIDTH),
            lsize=(LSIZE[0], BORDER_BLOCK_WIDTH),
            color=(0, 0, 96, 255),
            name="block2",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        Block(
            lpos=(0, 0),
            lsize=(BORDER_BLOCK_WIDTH, LSIZE[1]),
            color=(0, 0, 96, 255),
            name="block3",
            scaler=ctx0.scaler,
        )
    )

    ctx0.push_thing(
        Block(
            lpos=(3, 1),
            lsize=(LSIZE[0] - 5, BORDER_BLOCK_WIDTH),
            color=(0, 0, 96, 255),
            name="block_temp",
            scaler=ctx0.scaler,
        )
    )

    ctx0.push_thing(player)
    # messenger = Messenger("Hello", scaler=ctx0.scaler)
    # ctx0.push_thing(messenger)

    def on_k_p(
        ctx: Context,
        symbol: int,
        modifiers: int,
    ) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = True
        if symbol == pyglet.window.key.UP:
            if player.anchored:
                player.lv = (player.lv[0], PLAYER_JUMP_VY)
        if symbol == pyglet.window.key.Z:
            # TEMP PoC
            ctx.lg = (0, -ctx.lg[1])
            player.anchored = False
            player.feels_g = True
        return None

    def on_k_r(
        ctx: Context,
        symbol: int,
        modifiers: int,
    ) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = False
        return None

    def tk(ctx: Context, dt: float, t: float) -> None:
        if player.anchored:
            pl_lvx = 0.0
            if ctx.state["keys_map"].get(pyglet.window.key.LEFT):
                pl_lvx -= PLAYER_V
            if ctx.state["keys_map"].get(pyglet.window.key.RIGHT):
                pl_lvx += PLAYER_V
            player.lv = (pl_lvx, player.lv[1])

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.run()
