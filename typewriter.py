from __future__ import annotations

import urwid
import asyncio

import widget_utils

DEFAULT_LETTER_DELAY = 1 / 30


class Typewriter(widget_utils.SelectableWidgetWrap):
    signals = ['symbol_typed', 'finished_typing']

    def __init__(self, text_widget: urwid.Text | None = None, edit_widget: urwid.Edit | None = None) -> None:
        self.text_w = text_widget if text_widget else urwid.Text('')
        self.edit_w = edit_widget if edit_widget else urwid.Edit()

        self.skip = False

        super().__init__(self.text_w)

    def keypress(self, size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        if key == 'enter':
            self.skip = True

        return super().keypress(size, key)

    async def type(self, text: str, edit_after: bool = False, letter_delay: float | None = None, append_text=False):
        letter_delay = letter_delay if letter_delay else DEFAULT_LETTER_DELAY
        self._w = self.text_w
        self.skip = False
        if not append_text:
            self.text_w.set_text('')
        for s in text:
            if self.skip:
                self.text_w.set_text(text)
                self._emit('symbol_typed', [s])
                break
            else:
                self.text_w.set_text(self.text_w.text + s)
                self._emit('symbol_typed', [s])
                await asyncio.sleep(letter_delay)
        if edit_after:
            self._w = self.edit_w
            self.edit_w.set_caption(self.text_w.text)
            self.edit_w.set_edit_text('')
        self._emit('finished_typing')
        self.skip = False
