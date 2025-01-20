from __future__ import annotations

import urwid
import asyncio


def unhandled_input(key: str) -> None:
    if key in {"q", "Q"}:
        raise urwid.ExitMainLoop()


class StageError(Exception):
    pass


class Scene(urwid.WidgetWrap):
    def __init__(self, root_widget: urwid.Widget):
        super().__init__(root_widget)
        self._stage: Stage | None = None

    @property
    def stage(self):
        return self._stage

    def setup(self, stage):
        self._stage = stage


class Stage:
    """
    This class manages scenes and sets up the loops required to run the application
    """

    def __init__(self):
        self._asyncio_loop = asyncio.new_event_loop()
        self._current_scene: Scene | None = None
        self._urwid_loop: urwid.MainLoop | None = None

    @property
    def asyncio_loop(self):
        return self._asyncio_loop

    @property
    def urwid_loop(self):
        if self._urwid_loop:
            return self._urwid_loop
        else:
            raise StageError("urwid loop hasn't been created yet")

    @property
    def current_scene(self):
        return self._current_scene

    def set_scene(self, scene: Scene):
        if not self._current_scene:
            self._urwid_loop = urwid.MainLoop(scene.base_widget, unhandled_input=unhandled_input,
                                              event_loop=urwid.AsyncioEventLoop(loop=self.asyncio_loop))
        else:
            self._urwid_loop.widget = scene.base_widget
        self._current_scene = scene
        self._current_scene.setup(self)

    def run(self):
        if self._current_scene:
            self.urwid_loop.run()
        else:
            raise StageError("No scene has been set")
