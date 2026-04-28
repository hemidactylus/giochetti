from egame.type_definitions import FPair, IPair


class Scaler:
    size: IPair
    lsize: FPair
    scale: FPair

    def __init__(self, *, size: IPair, lsize: FPair) -> None:
        self.size = size
        self.lsize = lsize
        self.scale = (
            size[0] / lsize[0],
            size[1] / lsize[1],
        )

    def r_x(self, lx: float) -> int:
        return int(lx * self.scale[0])

    def r_y(self, ly: float) -> int:
        return int(ly * self.scale[1])
