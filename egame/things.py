from collections.abc import Iterable
from typing import TYPE_CHECKING

from egame.geometry import Scaler
from egame.type_definitions import Drawable, FPair

if TYPE_CHECKING:
    from egame.context import Context


class Thing:
    lpos: FPair
    lsize: FPair
    sprites: dict[str, Drawable]
    sprite_offsets: dict[str, FPair]
    _sprite_offsets_scaled: dict[str, FPair]
    t_s: float
    t0_s: float
    name: str
    scaler: Scaler

    def __init__(
        self,
        *,
        lpos: FPair,
        lsize: FPair,
        sprites: dict[str, Drawable],
        sprite_offsets: dict[str, FPair],
        t0_s: float,
        name: str = "",
        scaler: Scaler,
    ) -> None:
        self.lsize = lsize
        self.sprites = sprites
        self.t_s = 0.0
        self.t0_s = t0_s
        self.scaler = scaler
        self.name = name  # TODO autogen
        self.sprite_offsets = sprite_offsets
        self._sprite_offsets_scaled = {
            sk: (self.scaler.r_x(soffset[0]), self.scaler.r_y(soffset[1]))
            for sk, soffset in self.sprite_offsets.items()
        }
        self.update_lpos(lpos)

    @property
    def lcenter(self) -> FPair:
        return (
            self.lpos[0] + 0.5 * self.lsize[0],
            self.lpos[1] + 0.5 * self.lsize[1],
        )

    def update_sprite_offset(self, sprite_key: str, sprite_offset: FPair) -> None:
        self.sprite_offsets[sprite_key] = sprite_offset
        self._sprite_offsets_scaled[sprite_key] = (
            self.scaler.r_x(sprite_offset[0]),
            self.scaler.r_y(sprite_offset[1]),
        )

    def update_lpos(self, lpos: FPair) -> None:
        self.lpos = lpos
        self.update_pos()

    def update_pos(self) -> None:
        _sx_scaled = self.scaler.r_x(self.lpos[0])
        _sy_scaled = self.scaler.r_y(self.lpos[1])
        for sk, sprite in self.sprites.items():
            sprite.x = self._sprite_offsets_scaled[sk][0] + _sx_scaled
            sprite.y = self._sprite_offsets_scaled[sk][1] + _sy_scaled

    def drawables(self) -> Iterable[Drawable]:
        yield from self.sprites.values()

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        self.t_s = t_s - self.t0_s
        return False

    def die(self) -> None:
        for sprite in self.sprites.values():
            sprite.delete()

    def hide(self) -> None:
        for sprite in self.sprites.values():
            sprite.visible = False

    def show(self) -> None:
        for sprite in self.sprites.values():
            sprite.visible = True


class PhysicsThing(Thing):
    lv: FPair
    feels_g: bool

    def __init__(
        self,
        *,
        lpos: FPair,
        lsize: FPair,
        sprites: dict[str, Drawable],
        sprite_offsets: dict[str, FPair],
        t0_s: float,
        name: str = "",
        lv: FPair,
        feels_g: bool,
        scaler: Scaler,
    ) -> None:
        Thing.__init__(
            self=self,
            lpos=lpos,
            lsize=lsize,
            sprites=sprites,
            sprite_offsets=sprite_offsets,
            t0_s=t0_s,
            name=name,
            scaler=scaler,
        )
        self.lv = lv
        self.feels_g = feels_g

    def compute_motion(
        self,
        ctx: "Context",
        dt: float,
        t_s: float,
        feels_g: float,
    ) -> tuple[FPair, FPair]:
        new_lv: FPair
        new_lpos: FPair
        if feels_g:
            new_lv = (
                self.lv[0] + ctx.lg[0] * dt,
                self.lv[1] + ctx.lg[1] * dt,
            )
        else:
            new_lv = self.lv
        new_lpos = (
            self.lpos[0] + new_lv[0] * dt,
            self.lpos[1] + new_lv[1] * dt,
        )
        return new_lv, new_lpos

    def dies_on_update(self, ctx: "Context", dt: float, t_s: float) -> bool:
        if Thing.dies_on_update(self, ctx=ctx, dt=dt, t_s=t_s):
            return True
        new_lv, new_lpos = self.compute_motion(
            ctx, dt=dt, t_s=t_s, feels_g=self.feels_g
        )
        self.lv = new_lv
        self.update_lpos(new_lpos)
        return self.out_of_boundaries(ctx)

    def out_of_boundaries(self, ctx: "Context") -> bool:
        if self.lpos[0] + self.lsize[0] < 0:
            return True
        if self.lpos[1] + self.lsize[1] < 0:
            return True
        if self.lpos[0] > ctx.lsize[0]:
            return True
        if self.lpos[1] > ctx.lsize[1]:
            return True
        return False
