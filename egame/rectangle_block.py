import pyglet

from egame.geometry import Scaler
from egame.things import Thing
from egame.type_definitions import FPair

EPSILON = 0.0001


class RectangleBlock(Thing):
    def __init__(
        self,
        *,
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

    def contains(self, lpos: FPair, epsilon: float = EPSILON) -> bool:
        return (
            lpos[0] + epsilon > self.lpos[0]
            and lpos[0] - epsilon < self.lpos[0] + self.lsize[0]
            and lpos[1] + epsilon > self.lpos[1]
            and lpos[1] - epsilon < self.lpos[1] + self.lsize[1]
        )

    def _quadrant(self, lp: FPair) -> tuple[int, int]:
        lpx, lpy = lp
        qx: int
        qy: int
        if lpx <= self.lpos[0]:
            qx = 0
        elif lpx < self.lpos[0] + self.lsize[0]:
            qx = 1
        else:
            qx = 2
        if lpy <= self.lpos[1]:
            qy = 0
        elif lpy < self.lpos[1] + self.lsize[1]:
            qy = 1
        else:
            qy = 2
        return (qx, qy)

    def _intersect_lx(self, lx: float, lp0: FPair, lp1: FPair) -> FPair | None:
        """
        Returns only if in the block range
        """
        if lp0[0] == lp1[0]:
            return None
        else:
            # compute point
            ly = lp1[1] - (lp1[0] - lx) * (lp1[1] - lp0[1]) / (lp1[0] - lp0[0])
            if (
                ly >= self.lpos[1] - EPSILON
                and ly <= self.lpos[1] + self.lsize[1] + EPSILON
            ):
                ly_low, ly_high = sorted((lp0[1], lp1[1]))
                if ly >= ly_low and ly <= ly_high:
                    return (lx, ly)
                else:
                    return None
            else:
                return None

    def _intersect_ly(self, ly: float, lp0: FPair, lp1: FPair) -> FPair | None:
        """
        Returns only if in the block range
        """
        if lp0[1] == lp1[1]:
            return None
        else:
            # compute point
            lx = lp1[0] - (lp1[1] - ly) * (lp0[0] - lp1[0]) / (lp0[1] - lp1[1])
            if (
                lx >= self.lpos[0] - EPSILON
                and lx <= self.lpos[0] + self.lsize[0] + EPSILON
            ):
                lx_low, lx_high = sorted((lp0[0], lp1[0]))
                if lx >= lx_low and lx <= lx_high:
                    return (lx, ly)
                else:
                    return None
            else:
                return None

    def collides(self, lp0: FPair, lp1: FPair) -> tuple[FPair, int] | None:
        """
        TO DO.
        Note: not excessively optimized
        """
        q0x, q0y = self._quadrant(lp0)
        q1x, q1y = self._quadrant(lp1)

        if q0x == 1 and q0y == 1:
            # first points is inside:
            return None

        # same-side early nulls
        if q0y == 0 and q1y == 0:
            return None
        if q0y == 2 and q1y == 2:
            return None
        if q0x == 0 and q1x == 0:
            return None
        if q0x == 2 and q1x == 2:
            return None

        # actual intersection computations:
        xpoint_pairs: list[tuple[FPair, int]] = [
            xpp  # type: ignore[misc]
            for xpp in [
                (self._intersect_lx(self.lpos[0], lp0, lp1), 2),
                (self._intersect_lx(self.lpos[0] + self.lsize[0], lp0, lp1), 0),
                (self._intersect_ly(self.lpos[1], lp0, lp1), 3),
                (self._intersect_ly(self.lpos[1] + self.lsize[1], lp0, lp1), 1),
            ]
            if xpp[0] is not None
        ]
        if xpoint_pairs:
            if len(xpoint_pairs) == 1:
                return xpoint_pairs[0]
            else:
                # must pick the closest hit point
                def _manhattan(xpp: tuple[FPair, int]) -> float:
                    return abs(xpp[0][0] - lp0[0]) + abs(xpp[0][1] - lp0[1])

                return sorted(xpoint_pairs, key=_manhattan)[0]
        else:
            return None
