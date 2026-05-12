from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.rectangle_block import RectangleBlock
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair

LSIZE = (16, 10)
SIZE = (1600, 1000)

PLAYER_LSIZE = (0.25, 0.6)
PLAYER_NOSE_RADIUS = 0.05
PLAYER_JUMP_VY = 5.0

PLAYER_V = 2.5

BORDER_BLOCK_WIDTH = 0.2

GRAVITY_LMOD = 10


class Player(PhysicsThing):
    anchored: bool

    def __init__(
        self,
        *,
        lpos: FPair,
        lv: FPair,
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
        self.anchored = False
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
            lv=lv,
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
        """
        PLAN:
        try-advance with gravity.
            Works? -> commit, mark as unanchored (v and pos updated naturally)
            Does not work? -> try-advance without gravity, collect blockers.
                No blockers? -> commit, mark as anchored (update v and pos)
                Blockers? -> pick closest one (manhattan):
                    zero the right velocity component
                    set pos to its intercept pos
                    anchored = False
        """

        if Thing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s):
            return True

        blocks: list[RectangleBlock] = [
            thg  # type: ignore[misc]
            for thg in ctx.things
            if thg.name[:5] == "block"
        ]

        new_lv_g, new_lpos_g = self.compute_motion(ctx, dt=dt, t_s=t_s, feels_g=True)
        collision_pairs_g: list[tuple[FPair, int]] = [
            lpp
            for lpp in [block.collides(self.lpos, new_lpos_g) for block in blocks]
            if lpp is not None
        ]
        if collision_pairs_g == []:
            self.lv = new_lv_g
            self.update_lpos(new_lpos_g)
            self.anchored = False
        else:
            g_dirs = [(coll_dir_g + 2) % 4 for _, coll_dir_g in collision_pairs_g]
            has_a_below = ctx.state["gravity_dir"] in g_dirs
            # g-computation has hit blockers
            new_lv_0, new_lpos_0 = self.compute_motion(
                ctx, dt=dt, t_s=t_s, feels_g=False
            )
            collision_pairs_0: list[tuple[FPair, int]] = [
                lpp
                for lpp in [block.collides(self.lpos, new_lpos_0) for block in blocks]
                if lpp is not None
            ]
            if collision_pairs_0 == []:
                self.lv = new_lv_0
                self.update_lpos(new_lpos_0)
                self.anchored = has_a_below
            else:
                # blockage occurs: find out closest point (TODO optimize: define elsewhere, make euclidean?)

                def _manhattan(cpp: tuple[FPair, int]) -> float:
                    return abs(cpp[0][0] - self.lpos[0]) + abs(cpp[0][1] - self.lpos[1])

                coll_lpos, coll_dir = sorted(collision_pairs_0, key=_manhattan)[0]

                new_lv_blocked = new_lv_0
                if coll_dir == 0:
                    # new_lv_blocked = (min(0, new_lv_blocked[0]), new_lv_blocked[1])
                    new_lv_blocked = (0, new_lv_blocked[1])
                elif coll_dir == 1:
                    # new_lv_blocked = (new_lv_blocked[0], max(0, new_lv_blocked[1]))
                    new_lv_blocked = (new_lv_blocked[0], 0)
                elif coll_dir == 2:
                    # new_lv_blocked = (max(0, new_lv_blocked[0]), new_lv_blocked[1])
                    new_lv_blocked = (0, new_lv_blocked[1])
                else:  # coll_dir == 3
                    # new_lv_blocked = (new_lv_blocked[0], min(0, new_lv_blocked[1]))
                    new_lv_blocked = (new_lv_blocked[0], 0)

                self.lv = new_lv_blocked
                self.update_lpos(coll_lpos)
                self.anchored = has_a_below

        return self.out_of_boundaries(ctx)


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
    ctx0 = Context(size=SIZE, lsize=LSIZE, lg=(0.0, -GRAVITY_LMOD), time_factor=1.0)

    player = Player(
        lpos=(0.5 * LSIZE[0], 6 + BORDER_BLOCK_WIDTH),
        lv=(8, 4),
        scaler=ctx0.scaler,
    )

    ctx0.state["keys_map"] = {}
    ctx0.state["gravity_dir"] = 3

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))

    # blocks
    ctx0.push_thing(
        RectangleBlock(
            lpos=(0, 0),
            lsize=(LSIZE[0], BORDER_BLOCK_WIDTH),
            color=(0, 0, 96, 255),
            name="block0",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        RectangleBlock(
            lpos=(LSIZE[0] - BORDER_BLOCK_WIDTH, 0),
            lsize=(BORDER_BLOCK_WIDTH, LSIZE[1]),
            color=(0, 0, 96, 255),
            name="block1",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        RectangleBlock(
            lpos=(0, LSIZE[1] - BORDER_BLOCK_WIDTH),
            lsize=(LSIZE[0], BORDER_BLOCK_WIDTH),
            color=(0, 0, 96, 255),
            name="block2",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        RectangleBlock(
            lpos=(0, 0),
            lsize=(BORDER_BLOCK_WIDTH, LSIZE[1]),
            color=(0, 0, 96, 255),
            name="block3",
            scaler=ctx0.scaler,
        )
    )

    ctx0.push_thing(
        RectangleBlock(
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
                if ctx.state["gravity_dir"] == 2:
                    player.lv = (PLAYER_JUMP_VY, player.lv[1])
                elif ctx.state["gravity_dir"] == 3:
                    player.lv = (player.lv[0], PLAYER_JUMP_VY)
                elif ctx.state["gravity_dir"] == 0:
                    player.lv = (-PLAYER_JUMP_VY, player.lv[1])
                else:  # gravity_dir == 1
                    player.lv = (player.lv[0], -PLAYER_JUMP_VY)
        if symbol == pyglet.window.key.Z:
            ctx.state["gravity_dir"] = (ctx.state["gravity_dir"] + 1) % 4
            if ctx.state["gravity_dir"] == 2:
                ctx.lg = (-GRAVITY_LMOD, 0)
            elif ctx.state["gravity_dir"] == 3:
                ctx.lg = (0, -GRAVITY_LMOD)
            elif ctx.state["gravity_dir"] == 0:
                ctx.lg = (GRAVITY_LMOD, 0)
            else:  # gravity_dir == 1
                ctx.lg = (0, GRAVITY_LMOD)
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
            pl_rel_lvx = 0.0
            if ctx.state["keys_map"].get(pyglet.window.key.LEFT):
                pl_rel_lvx -= PLAYER_V
            if ctx.state["keys_map"].get(pyglet.window.key.RIGHT):
                pl_rel_lvx += PLAYER_V
            # apply to actual velocity
            if ctx.state["gravity_dir"] == 2:
                player.lv = (player.lv[0], -pl_rel_lvx)
            elif ctx.state["gravity_dir"] == 3:
                player.lv = (pl_rel_lvx, player.lv[1])
            elif ctx.state["gravity_dir"] == 0:
                player.lv = (player.lv[0], pl_rel_lvx)
            else:  # gravity_dir == 1
                player.lv = (-pl_rel_lvx, player.lv[1])

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.run()
