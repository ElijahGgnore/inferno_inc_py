from __future__ import annotations

import asyncio

import urwid
import typewriter


def exit_on_q(key: str) -> None:
    if key in {"q", "Q"}:
        raise urwid.ExitMainLoop()


text_w = typewriter.Typewriter()
fill = urwid.Filler(text_w, "top")
lbox = urwid.LineBox(fill)

loop = asyncio.new_event_loop()
urwid_loop = urwid.MainLoop(lbox, unhandled_input=exit_on_q, event_loop=urwid.AsyncioEventLoop(loop=loop))
loop.create_task(text_w.type(urwid_loop, 'What\'s your name?\n', True))
urwid_loop.run()
