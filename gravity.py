from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.rectangle_block import RectangleBlock
from egame.things import PhysicsThing, Thing
from egame.type_definitions import FPair

LSIZE = (16, 10)
SIZE = None  # (1600, 1000)

PLAYER_LSIZE = (0.4, 0.7)
PLAYER_NOSE_RADIUS = 0.1

PLAYER_JUMP_VY = 6.5
PLAYER_V = 4.5

BORDER_BLOCK_WIDTH = 0.35
BLOCK_COLOR = (25, 90, 0, 255)
G_BLOCK_COLOR = (120, 220, 80, 255)
SKY_COLOR = (80, 130, 255, 255)

GRAVITY_LMOD = 10


class Player(PhysicsThing):
    anchored: bool
    loffsets: list[FPair]
    n_offset_state: tuple[int, int]

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
        self.loffsets = [
            (0, 0),
            (PLAYER_LSIZE[0], 0),
            (PLAYER_LSIZE[0], PLAYER_LSIZE[1]),
            (0, PLAYER_LSIZE[1]),
        ]
        self.n_offset_state = (1, 0)
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

    def orient(self, g_dir: int, lv: FPair) -> None:
        norm_v: float = 0.0
        if g_dir == 1:
            norm_v = lv[0]
        elif g_dir == 3:
            norm_v = -lv[0]
        elif g_dir == 2:
            norm_v = lv[1]
        elif g_dir == 0:
            norm_v = -lv[1]
        noff: int = 0
        if norm_v > 0:
            noff = 1
        elif norm_v < 0:
            noff = -1
        # now calculate the actual offset
        n_offset_state = (g_dir, noff)
        if n_offset_state != self.n_offset_state:
            self.n_offset_state = n_offset_state
            actual_loffset: FPair = (0, 0)
            if g_dir == 1:
                actual_loffset = (
                    PLAYER_LSIZE[0] * (noff + 1) / 2,
                    PLAYER_LSIZE[1] * 0.2,
                )
            elif g_dir == 3:
                actual_loffset = (
                    PLAYER_LSIZE[0] * (-noff + 1) / 2,
                    PLAYER_LSIZE[1] * 0.8,
                )
            elif g_dir == 0:
                actual_loffset = (
                    PLAYER_LSIZE[0] * 0.2,
                    PLAYER_LSIZE[1] * (-noff + 1) / 2,
                )
            elif g_dir == 2:
                actual_loffset = (
                    PLAYER_LSIZE[0] * 0.8,
                    PLAYER_LSIZE[1] * (noff + 1) / 2,
                )
            self.update_sprite_offset("n", actual_loffset)

    def extended_speculate_motion_and_collide(
        self,
        ctx: Context,
        *,
        dt: float,
        t_s: float,
        feels_g: bool,
        blocks: list[RectangleBlock],
        loffsets: list[FPair],
    ) -> tuple[FPair, FPair, list[tuple[FPair, int]]]:
        new_lv, new_lpos = self.compute_motion(ctx, dt=dt, t_s=t_s, feels_g=feels_g)
        collision_pairs: list[tuple[FPair, int]] = []
        for loffset in loffsets:
            offset_lpos = (
                self.lpos[0] + loffset[0],
                self.lpos[1] + loffset[1],
            )
            offset_new_lpos = (
                new_lpos[0] + loffset[0],
                new_lpos[1] + loffset[1],
            )
            offset_collision_pairs: list[tuple[FPair, int]] = [
                olpp
                for olpp in [
                    block.collides(offset_lpos, offset_new_lpos) for block in blocks
                ]
                if olpp is not None
            ]
            collision_pairs += [
                (
                    (
                        olpp[0][0] - loffset[0],
                        olpp[0][1] - loffset[1],
                    ),
                    olpp[1],
                )
                for olpp in offset_collision_pairs
            ]

        return (new_lv, new_lpos, collision_pairs)

    def dies_on_update(self, ctx: Context, dt: float, t_s: float) -> bool:
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

        new_lv_g, new_lpos_g, collision_pairs_g = (
            self.extended_speculate_motion_and_collide(
                ctx,
                dt=dt,
                t_s=t_s,
                feels_g=True,
                blocks=blocks,
                loffsets=self.loffsets,
            )
        )
        if collision_pairs_g == []:
            self.lv = new_lv_g
            self.update_lpos(new_lpos_g)
            self.anchored = False
        else:
            g_dirs = [(coll_dir_g + 2) % 4 for _, coll_dir_g in collision_pairs_g]
            has_a_below = ctx.state["gravity_dir"] in g_dirs
            # g-computation has hit blockers
            new_lv_0, new_lpos_0, collision_pairs_0 = (
                self.extended_speculate_motion_and_collide(
                    ctx,
                    dt=dt,
                    t_s=t_s,
                    feels_g=False,
                    blocks=blocks,
                    loffsets=self.loffsets,
                )
            )
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


class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        sky = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(0),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1]),
            color=SKY_COLOR,
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
        lpos=(15, 1),
        lv=(-3, 3.5),
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))

    # blocks
    border_blocks = {
        0: RectangleBlock(
            lpos=(LSIZE[0] - BORDER_BLOCK_WIDTH, 0),
            lsize=(BORDER_BLOCK_WIDTH, LSIZE[1]),
            color=BLOCK_COLOR,
            name="block0",
            scaler=ctx0.scaler,
        ),
        1: RectangleBlock(
            lpos=(0, LSIZE[1] - BORDER_BLOCK_WIDTH),
            lsize=(LSIZE[0], BORDER_BLOCK_WIDTH),
            color=BLOCK_COLOR,
            name="block1",
            scaler=ctx0.scaler,
        ),
        2: RectangleBlock(
            lpos=(0, 0),
            lsize=(BORDER_BLOCK_WIDTH, LSIZE[1]),
            color=BLOCK_COLOR,
            name="block2",
            scaler=ctx0.scaler,
        ),
        3: RectangleBlock(
            lpos=(0, 0),
            lsize=(LSIZE[0], BORDER_BLOCK_WIDTH),
            color=BLOCK_COLOR,
            name="block3",
            scaler=ctx0.scaler,
        ),
    }

    for b_block in border_blocks.values():
        ctx0.push_thing(b_block)

    ctx0.state["keys_map"] = {}

    def update_gravity_dir(ctx: Context, new_value: int) -> None:
        ctx.state["gravity_dir"] = new_value
        for bb_dir, b_block in border_blocks.items():
            b_block.update_color(G_BLOCK_COLOR if bb_dir == new_value else BLOCK_COLOR)

    update_gravity_dir(ctx0, 3)

    ctx0.push_thing(
        RectangleBlock(
            lpos=(4, 1.7),
            lsize=(8, BORDER_BLOCK_WIDTH),
            color=BLOCK_COLOR,
            name="block_step0",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        RectangleBlock(
            lpos=(BORDER_BLOCK_WIDTH - 0.01, 3.4),
            lsize=(2, BORDER_BLOCK_WIDTH),
            color=BLOCK_COLOR,
            name="block_step1",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        RectangleBlock(
            lpos=(4, 5.1),
            lsize=(4, BORDER_BLOCK_WIDTH),
            color=BLOCK_COLOR,
            name="block_step2",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        RectangleBlock(
            lpos=(2, 6.6),
            lsize=(3, BORDER_BLOCK_WIDTH),
            color=BLOCK_COLOR,
            name="block_step3",
            scaler=ctx0.scaler,
        )
    )
    ctx0.push_thing(
        RectangleBlock(
            lpos=(5, 8),
            lsize=(5, BORDER_BLOCK_WIDTH),
            color=BLOCK_COLOR,
            name="block_step4",
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
            update_gravity_dir(ctx, (ctx.state["gravity_dir"] + 1) % 4)
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
            player.orient(ctx.state["gravity_dir"], player.lv)

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.run()
