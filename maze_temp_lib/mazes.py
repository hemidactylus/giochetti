from dataclasses import dataclass

CellType = tuple[int, int]
LineState = int
LinePos = tuple[int, int, int]
Maze = dict[LinePos, LineState]

IMP_WHITE = 0
IMP_WALL = 1
GROWN_WALL = 2
CAND_GROWABLE_WALL = 10
CAND_UNGROWABLE_WALL = 11


@dataclass
class CandidateState:
    growable: bool
    weight: float
    meta: dict[str, int]


@dataclass
class MazeGeo:
    n: int
    m: int
    arena: set[LinePos]


@dataclass
class MazeStartState:
    geo: MazeGeo
    meta: dict[str, int | float]
    impositions: Maze


def calc_start_state(
    n: int, m: int, dcells: set[CellType], dimps: dict[LinePos, int]
) -> MazeStartState:
    # work out all impositions
    arena: set[LinePos] = set()
    imposed: Maze = {}
    for x in range(n + 1):
        for y in range(m + 1):
            is_dead = (x, y) in dcells
            if y < m:
                # vert line before cell
                vl = (x, y, 1)
                arena.add(vl)
                if x == 0:
                    imposed[vl] = IMP_WHITE if is_dead else IMP_WALL
                elif x == n:
                    imposed[vl] = IMP_WHITE if (x - 1, y) in dcells else IMP_WALL
                else:
                    # on the inside, impose if on interface only
                    if is_dead ^ ((x - 1, y) in dcells):
                        imposed[vl] = IMP_WALL
                    elif is_dead:
                        # within the dead zone entirely
                        imposed[vl] = IMP_WHITE
            if x < n:
                # horiz line below cell
                hl = (x, y, 0)
                arena.add(hl)
                if y == 0:
                    imposed[hl] = IMP_WHITE if is_dead else IMP_WALL
                elif y == m:
                    imposed[hl] = IMP_WHITE if (x, y - 1) in dcells else IMP_WALL
                else:
                    # on the inside, check for interface
                    if is_dead ^ ((x, y - 1) in dcells):
                        imposed[hl] = IMP_WALL
                    elif is_dead:
                        # within the dead zone entirely
                        imposed[hl] = IMP_WHITE
    # direct impositions if any
    for line, imposed_state in dimps.items():
        imposed[line] = IMP_WALL if imposed_state else IMP_WHITE
    # full return value
    return MazeStartState(
        geo=MazeGeo(
            n=n,
            m=m,
            arena=arena,
        ),
        meta={"temp": 100},  # TODO
        impositions=imposed,
    )


def is_wall(ls: LineState | None) -> bool:
    if ls is None:
        return False
    elif ls == IMP_WALL:
        return True
    elif ls == GROWN_WALL:
        return True
    elif ls == IMP_WHITE:
        return False
    else:
        raise ValueError(f"is_wall got {ls}")


def calc_growable_state(
    line_pos: LinePos, maze: Maze, arena: set[LinePos]
) -> CandidateState:
    is_growable: bool
    if is_wall(maze.get(line_pos)):
        is_growable = False
    else:
        neighbours = list_actual_neighbours(line_pos, arena)
        wallnesses = [
            [1 if is_wall(maze.get(n_lpos)) else 0 for n_lpos in n_side]
            for n_side in neighbours
        ]
        is_growable = (sum(wallnesses[0]) == 0) ^ (sum(wallnesses[1]) == 0)
    return CandidateState(
        growable=is_growable,
        weight=1.0 if is_growable else 0.0,  # TODO: use strategies
        meta={},  # TODO: ditto
    )


def list_actual_neighbours(
    line_pos: LinePos, arena: set[LinePos]
) -> list[list[LinePos]]:
    """
          0a  1a
          '   '
          '   '
    0b....____....1b
          '   '
          '   '
          0c  1c

          0b
          '
          '
          '
    0c.... ....0a
          |
          |
    1c....|....1a
          '
          '
          '
          1b
    """
    lx, ly, lt = line_pos
    neighbours0: list[list[LinePos]]
    if lt == 0:
        neighbours0 = [
            [
                (lx, ly, 1),
                (lx - 1, ly, 0),
                (lx, ly - 1, 1),
            ],
            [
                (lx + 1, ly, 1),
                (lx + 1, ly, 0),
                (lx + 1, ly - 1, 1),
            ],
        ]
    elif lt == 1:
        neighbours0 = [
            [
                (lx, ly + 1, 0),
                (lx, ly + 1, 1),
                (lx - 1, ly + 1, 0),
            ],
            [
                (lx, ly, 0),
                (lx, ly - 1, 1),
                (lx - 1, ly, 0),
            ],
        ]
    else:
        raise ValueError
    return [[n_lpos for n_lpos in n_side if n_lpos in arena] for n_side in neighbours0]


def calc_candidates(start_state: MazeStartState) -> dict[LinePos, CandidateState]:
    cands: set[LinePos] = set()
    for x in range(start_state.geo.n + 1):
        for y in range(start_state.geo.m + 1):
            if y < start_state.geo.m:
                # vert line before cell
                if (x, y, 1) not in start_state.impositions:
                    cands.add((x, y, 1))
            if x < start_state.geo.n:
                # horiz line below cell
                if (x, y, 0) not in start_state.impositions:
                    cands.add((x, y, 0))
    # recalc growable for all candidates into the map
    maze0 = {
        line_pos: IMP_WALL
        for line_pos, line_state in start_state.impositions.items()
        if line_state == IMP_WALL
    }
    candidate_map = {
        line_pos: calc_growable_state(line_pos, maze0, start_state.geo.arena)
        for line_pos in cands
    }
    return candidate_map


def calc_start_maze(start_state: MazeStartState) -> Maze:
    return {lp: ls for lp, ls in start_state.impositions.items()}


def list_growables(
    cand_map: dict[LinePos, CandidateState],
) -> list[tuple[LinePos, float]]:
    return [
        (l_pos, c_state.weight)
        for l_pos, c_state in cand_map.items()
        if c_state.growable
    ]


def add_wall_to_maze(
    wall: LinePos,
    cand_map: dict[LinePos, CandidateState],
    maze: Maze,
    geo: MazeGeo,
) -> None:
    maze[wall] = GROWN_WALL
    cand_map[wall] = calc_growable_state(wall, maze, geo.arena)
    for n_side in list_actual_neighbours(wall, geo.arena):
        for n_pos in n_side:
            if n_pos in cand_map:
                cand_map[n_pos] = calc_growable_state(n_pos, maze, geo.arena)


def weighted_pick_one(items_weights: list[tuple[LinePos, float]]) -> LinePos:
    # TEMP uniform picking
    from egame.randomize import i_mrnd
    index = i_mrnd(len(items_weights))
    return items_weights[index][0]


def make_maze(N: int, M: int) -> Maze:
    print("WARNING: TEMPORARY PLUMBING FOR THIS LIBRARY")
    dead_cells: set[CellType] = set()
    direct_impositions: dict[LinePos, int] = {}
    #
    start_state = calc_start_state(N, M, dead_cells, direct_impositions)
    candidate_map = calc_candidates(start_state)
    growables = list_growables(candidate_map)
    maze = calc_start_maze(start_state)
    assert candidate_map.keys() & start_state.impositions.keys() == set()

    iteration = 0
    while growables:
        iteration += 1
        this_wall = weighted_pick_one(growables)
        add_wall_to_maze(this_wall, candidate_map, maze, start_state.geo)
        growables = list_growables(candidate_map)

    return maze
