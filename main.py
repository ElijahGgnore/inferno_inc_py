from __future__ import annotations

import stage

import urwid
import typewriter

text_w = typewriter.Typewriter()
fill = urwid.Filler(text_w, "top")
lbox = urwid.LineBox(fill)

game = stage.Stage()
scene = stage.Scene(game, lbox)
game.change_scene(scene)

game.asyncio_loop.create_task(text_w.type('What\'s your name?\n', True))

d = lambda *_: game.urwid_loop.draw_screen()
urwid.connect_signal(text_w, 'symbol_typed', d)
urwid.connect_signal(text_w, 'finished_typing', d)
game.run()