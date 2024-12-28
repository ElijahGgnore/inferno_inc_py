from __future__ import annotations

import urwid
import asyncio


DEFAULT_LETTER_DELAY = 1 / 30


class Typewriter(urwid.WidgetWrap):
    def __init__(self, text_widget: urwid.Text | None = None, edit_widget: urwid.Edit | None = None, letter_delay: float = DEFAULT_LETTER_DELAY) -> None:
        self.text_w = text_widget if text_widget else urwid.Text('')
        self.edit_w = edit_widget if edit_widget else urwid.Edit()
        self.skip = False
        self.letter_delay = letter_delay
        super().__init__(self.text_w)
        self._selectable = True

    def selectable(self) -> bool:
        return self._selectable

    def keypress(self, size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        if key == 's':
            self.skip = True

        return super().keypress(size, key)

    async def type(self, loop: urwid.MainLoop, text: str, edit_after: bool = False):
        self._w = self.text_w
        self.skip = False
        self.text_w.set_text('')
        for s in text:
            if self.skip:
                self.text_w.set_text(text)
                loop.draw_screen()
                break
            else:
                self.text_w.set_text(self.text_w.text + s)
                loop.draw_screen()
                await asyncio.sleep(self.letter_delay)
        if edit_after:
            self._w = self.edit_w
            self.edit_w.set_caption(text)
            loop.draw_screen()
        self.skip = False

    def schedule_typing(self, loop: urwid.MainLoop, text):
        asyncio.create_task(self.type(loop, text))
