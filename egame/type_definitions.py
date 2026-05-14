from typing import TypeAlias

import pyglet

IPair: TypeAlias = tuple[int, int]
FPair: TypeAlias = tuple[float, float]
Color: TypeAlias = tuple[int, int, int, int]

Drawable: TypeAlias = (
    pyglet.shapes.Box
    | pyglet.shapes.Circle
    | pyglet.shapes.Rectangle
    | pyglet.shapes.Line
    | pyglet.sprite.Sprite
    | pyglet.text.Label
)
