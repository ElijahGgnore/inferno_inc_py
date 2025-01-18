from __future__ import annotations

import urwid
import asyncio

DEFAULT_LETTER_DELAY = 1 / 30


class Typewriter(urwid.WidgetWrap):
    signals = ['symbol_typed', 'finished_typing']

    def __init__(self, text_widget: urwid.Text | None = None, edit_widget: urwid.Edit | None = None,
                 letter_delay: float = DEFAULT_LETTER_DELAY) -> None:
        self.text_w = text_widget if text_widget else urwid.Text('')
        self.edit_w = edit_widget if edit_widget else urwid.Edit()

        self.skip = False

        super().__init__(self.text_w)
        self._selectable = True

    # selectability determines whether the widget will receive key presses
    # this overrides the selectable method to allow receiving key presses for typewriter skipping to work
    def selectable(self) -> bool:
        return self._selectable

    def keypress(self, size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        if key == 'enter':
            self.skip = True

        return super().keypress(size, key)

    async def type(self, text: str, edit_after: bool = False, letter_delay: float | None = None, append_text = False):
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
