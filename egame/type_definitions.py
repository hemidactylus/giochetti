from typing import TypeAlias

import pyglet

IPair: TypeAlias = tuple[int, int]
FPair: TypeAlias = tuple[float, float]

Drawable: TypeAlias = (
    pyglet.shapes.Box
    | pyglet.shapes.Circle
    | pyglet.shapes.Rectangle
    | pyglet.sprite.Sprite
    | pyglet.text.Label
)
