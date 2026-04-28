from collections.abc import Iterable

from egame.geometry import Scaler
from egame.type_definitions import Drawable, FPair


class Thing:
    lpos: FPair
    lsize: FPair
    sprites: dict[str, Drawable]
    sprite_offsets: dict[str, FPair]
    _sprite_offsets_scaled: dict[str, FPair]
    t_s: float
    t0_s: float
    scaler: Scaler

    def __init__(
        self,
        *,
        lpos: FPair,
        lsize: FPair,
        sprites: dict[str, Drawable],
        sprite_offsets: dict[str, FPair],
        t0_s: float,
        scaler: Scaler,
    ) -> None:
        self.lsize = lsize
        self.sprites = sprites
        self.sprite_offsets = sprite_offsets
        self.t_s = 0.0
        self.t0_s = t0_s
        self.scaler = scaler
        self._sprite_offsets_scaled = {
            sk: (self.scaler.r_x(soffset[0]), self.scaler.r_y(soffset[1]))
            for sk, soffset in self.sprite_offsets.items()
        }
        self.update_lpos(lpos)

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

    def dies_on_update(self, dt: float, t_s: float) -> bool:
        self.t_s += t_s - self.t0_s
        return False
