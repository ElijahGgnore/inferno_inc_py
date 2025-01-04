from __future__ import annotations

import urwid
import asyncio


def unhandled_input(key: str) -> None:
    if key in {"q", "Q"}:
        raise urwid.ExitMainLoop()


class Scene:
    def __init__(self, stage: Stage, root_widget: urwid.Widget):
        self.stage = stage
        self.root_widget = root_widget

    def setup(self):
        raise NotImplementedError()


class Stage:
    """
    This class sets up the loops required to run the application and manages scenes
    """

    def __init__(self):
        self.asyncio_loop = asyncio.new_event_loop()
        self.current_scene: Scene | None = None
        self.urwid_loop: urwid.MainLoop | None = None

    def change_scene(self, scene: Scene):
        self.current_scene = scene
        if self.urwid_loop:
            self.urwid_loop.widget = scene.root_widget

    def run(self):
        self.urwid_loop = urwid.MainLoop(self.current_scene.root_widget, unhandled_input=unhandled_input,
                                         event_loop=urwid.AsyncioEventLoop(loop=self.asyncio_loop))
        self.urwid_loop.run()
