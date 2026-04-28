from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import pyglet

from egame.geometry import Scaler
from egame.things import Thing
from egame.type_definitions import FPair, IPair


@dataclass
class Context:
    size: IPair
    lsize: FPair
    title: str
    scaler: Scaler
    started: bool
    t_s: float
    things: list[Thing]
    _okp: Callable[[int, int], Literal[True] | None] | None
    _window: pyglet.window.Window

    def __init__(self, *, size: IPair, lsize: FPair, title: str = "") -> None:
        self.size = size
        self.lsize = lsize
        self.title = title
        self.started = False
        self._okp = None
        self.t_s = 0.0
        self.things = []
        self.scaler = Scaler(size=size, lsize=lsize)
        self._make_window()

    def on_key_press(self, okp: Callable[[int, int], Literal[True] | None]) -> None:
        if self.started:
            raise ValueError("Already started")
        self._okp = okp

    def push_thing(self, thing: Thing) -> None:
        self.things.append(thing)

    def _make_window(self) -> None:
        # TODO fullscreen support
        self._window = pyglet.window.Window(  # type: ignore[abstract]
            width=self.size[0],
            height=self.size[1],
            caption=self.title,
            fullscreen=False,
        )

    def window(self) -> pyglet.window.Window:
        if self.started:
            raise ValueError("Already started")
        if self._okp:
            keys = pyglet.window.key.KeyStateHandler()
            self._window.push_handlers(keys)

            @self._window.event
            def on_key_press(symbol: int, modifiers: int) -> Literal[True] | None:
                if self._okp is not None:
                    return self._okp(symbol, modifiers)
                else:
                    return None

        @self._window.event
        def on_draw():
            self._window.clear()
            for thing in self.things:
                for drawable in thing.drawables():
                    drawable.draw()

        def update(dt: float) -> None:
            # TODO evolve things
            self.t_s += dt

        pyglet.clock.schedule_interval(update, 1 / 60.0)
        self.started = True
        return self._window

    def run(self) -> None:
        if not self.started:
            self.window()
        pyglet.app.run()
