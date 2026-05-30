import math
from typing import Literal

import pyglet

from egame.context import Context
from egame.geometry import Scaler
from egame.randomize import fluctuate, rnd
from egame.things import Thing
from egame.type_definitions import Drawable, FPair

LSIZE = (16, 10)
SIZE = (1600, 1000)

BLOCK_LSIZE = (1, 1)
SPHERE_LRADIUS = 0.2

D_FLOWER_LRADIUS = 0.4
SPAWN_CHANCE_PER_SECOND = 0.3
D_FLOWER_LIFETIME_S = 3

DANDELION_N_PUFFS = 20
DANDELION_PUFF_LRADIUS = 0.2
DANDELION_LRADIUS = 0.4
PUFF_COLOR = (255, 255, 255, 96)

D_LIFETIME_S = 3  # TEMP

BLOCKV_MOD = 3

PUFF_LVEL = ((1.5, 0.5), (1.0, 0.3))
PUFF_LVEL_A = ((0.2, 0.1), (0.2, 0.1))
PUFF_LVEL_OMEGA = ((1, 0.8), (1.2, 0.9))


class Puff(Thing):
    p_lvel: FPair
    p_lvel_a: FPair
    p_lvel_omega: FPair

    def __init__(
        self,
        *,
        lpos: FPair,
        t0_s: float,
        scaler: Scaler,
    ) -> None:
        puff = pyglet.shapes.Circle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(DANDELION_PUFF_LRADIUS),
            color=PUFF_COLOR,
        )
        self.p_lvel = (fluctuate(*PUFF_LVEL[0]), fluctuate(*PUFF_LVEL[1]))
        self.p_lvel_a = (fluctuate(*PUFF_LVEL_A[0]), fluctuate(*PUFF_LVEL_A[1]))
        self.p_lvel_omega = (
            fluctuate(*PUFF_LVEL_OMEGA[0]),
            fluctuate(*PUFF_LVEL_OMEGA[1]),
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(DANDELION_PUFF_LRADIUS, DANDELION_PUFF_LRADIUS),
            name="puff",
            sprites={"0": puff},
            sprite_offsets={"0": (0, 0)},
            t0_s=t0_s,
            scaler=scaler,
        )

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        tdies = Thing.dies_on_update(self, ctx, dt, t_s)
        if tdies:
            return True
        oob = Thing.out_of_boundaries(self, ctx, lpos=self.lpos)
        if oob:
            return True
        # evolve TEMP
        this_p_lvel = (
            self.p_lvel[0] + self.p_lvel_a[0] * math.cos(self.p_lvel_omega[0] * t_s),
            self.p_lvel[1] + self.p_lvel_a[1] * math.cos(self.p_lvel_omega[1] * t_s),
        )
        self.update_lpos(
            (
                self.lpos[0] + this_p_lvel[0] * dt,
                self.lpos[1] + this_p_lvel[1] * dt,
            )
        )
        return False


class Dandelion(Thing):
    def __init__(
        self,
        *,
        lpos: FPair,
        t0_s: float,
        scaler: Scaler,
    ) -> None:
        sprite_offsets = {
            f"{ii}": (
                DANDELION_LRADIUS * math.cos(theta),
                DANDELION_LRADIUS * math.sin(theta),
            )
            for theta, ii in (
                (2 * math.pi * i / DANDELION_N_PUFFS, i)
                for i in range(DANDELION_N_PUFFS)
            )
        }
        puff_map: dict[str, Drawable] = {
            spr_k: pyglet.shapes.Circle(
                scaler.r_x(lpos[0] + spr_off[0]),
                scaler.r_y(lpos[1] + spr_off[1]),
                scaler.r_x(DANDELION_PUFF_LRADIUS),
                color=PUFF_COLOR,
            )
            for spr_k, spr_off in sprite_offsets.items()
        }
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(DANDELION_LRADIUS, DANDELION_LRADIUS),
            name="dandelion",
            sprites=puff_map,
            sprite_offsets=sprite_offsets,
            t0_s=t0_s,
            scaler=scaler,
        )

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        tdies = Thing.dies_on_update(self, ctx, dt, t_s)
        if tdies:
            return tdies
        if self.t_s > D_LIFETIME_S:
            # spawn puffs
            for pkey, poffset in self.sprite_offsets.items():
                ctx.push_thing(
                    Puff(
                        lpos=(
                            self.lpos[0] + poffset[0],
                            self.lpos[1] + poffset[1],
                        ),
                        t0_s=t_s,
                        scaler=self.scaler,
                    )
                )
            return True
        return False


class DandelionFlower(Thing):
    def __init__(
        self,
        *,
        lpos: FPair,
        t0_s: float,
        scaler: Scaler,
    ) -> None:
        body = pyglet.shapes.Circle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(D_FLOWER_LRADIUS),
            color=(200, 170, 0, 255),
        )
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=(D_FLOWER_LRADIUS, D_FLOWER_LRADIUS),
            name="flower",
            sprites={
                "0": body,
            },
            sprite_offsets={
                "0": (0, 0),
            },
            t0_s=t0_s,
            scaler=scaler,
        )

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        tdies = Thing.dies_on_update(self, ctx, dt, t_s)
        if tdies:
            return tdies
        if self.t_s > D_FLOWER_LIFETIME_S:
            # spawn a dandelion
            ctx.push_thing(
                Dandelion(
                    lpos=self.lpos,
                    t0_s=t_s,
                    scaler=self.scaler,
                )
            )
            return True
        return False


class Block(Thing):
    lvdir: int

    def __init__(
        self,
        *,
        lpos: FPair,
        scaler: Scaler,
    ) -> None:
        body = pyglet.shapes.Rectangle(
            scaler.r_x(lpos[0]),
            scaler.r_y(lpos[1]),
            scaler.r_x(BLOCK_LSIZE[0]),
            scaler.r_y(BLOCK_LSIZE[1]),
            color=(0, 0, 255, 255),
        )
        sphere = pyglet.shapes.Circle(
            scaler.r_x(lpos[0] + 0.5 * BLOCK_LSIZE[0]),
            scaler.r_y(lpos[1] + 0.5 * BLOCK_LSIZE[1]),
            radius=scaler.r_x(SPHERE_LRADIUS),
            color=(255, 10, 10, 255),
        )
        self.lvdir = 0
        Thing.__init__(
            self,
            lpos=lpos,
            lsize=BLOCK_LSIZE,
            name="block",
            sprites={
                "0": body,
                "s": sphere,
            },
            sprite_offsets={
                "0": (0, 0),
                "s": (0.5 * BLOCK_LSIZE[0], 0.5 * BLOCK_LSIZE[1]),
            },
            t0_s=0.0,
            scaler=scaler,
        )

    def orient(self, lvx: float) -> None:
        if lvx == 0:
            return
        elif lvx > 0:
            lvdir = 1
        else:
            lvdir = -1
        if lvdir != self.lvdir:
            new_s_sprite_offset = (
                (0.5 + lvdir * 0.3) * BLOCK_LSIZE[0],
                0.5 * BLOCK_LSIZE[1],
            )
            self.update_sprite_offset("s", new_s_sprite_offset)
            self.lvdir = lvdir


class Scenery(Thing):
    def __init__(self, scaler: Scaler) -> None:
        sky = pyglet.shapes.Rectangle(
            0,
            scaler.r_y(0),
            scaler.r_x(LSIZE[0]),
            scaler.r_y(LSIZE[1]),
            color=(90, 20, 150, 255),
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
    ctx0.state["keys_map"] = {}

    block = Block(
        lpos=(5, 5),
        scaler=ctx0.scaler,
    )

    ctx0.push_thing(Scenery(scaler=ctx0.scaler))
    ctx0.push_thing(block)

    def on_k_p(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = True
        return None

    def on_k_r(ctx: Context, symbol: int, modifiers: int) -> Literal[True] | None:
        ctx.state["keys_map"][symbol] = False
        return None

    def tk(ctx: Context, dt: float, t: float) -> None:
        # spawn
        chance = rnd()
        if chance <= SPAWN_CHANCE_PER_SECOND * dt:
            new_lpos = (
                0.1 * LSIZE[0] + rnd() * (LSIZE[0] * 0.8),
                0.1 * LSIZE[1] + rnd() * (LSIZE[1] * 0.8),
            )
            ctx.push_thing(
                DandelionFlower(
                    lpos=new_lpos,
                    t0_s=t,
                    scaler=ctx.scaler,
                )
            )
        # movement
        blockv: list[float] = [0, 0]
        if ctx.state["keys_map"].get(pyglet.window.key.UP):
            blockv[1] += BLOCKV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.DOWN):
            blockv[1] -= BLOCKV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.LEFT):
            blockv[0] -= BLOCKV_MOD
        if ctx.state["keys_map"].get(pyglet.window.key.RIGHT):
            blockv[0] += BLOCKV_MOD
        block.orient(blockv[0])
        if blockv != (0, 0):
            blockd = (blockv[0] * dt, blockv[1] * dt)
            new_block_lpos = (
                block.lpos[0] + blockd[0],
                block.lpos[1] + blockd[1],
            )
            block.update_lpos(new_block_lpos)

    ctx0.on_key_press(on_k_p)
    ctx0.on_key_release(on_k_r)
    ctx0.tick(tk)

    ctx0.run()
