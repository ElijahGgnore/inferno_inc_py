from __future__ import annotations

import urwid
import asyncio

import widget_utils

DEFAULT_SYMBOL_DELAY = 1 / 30


class Typewriter(widget_utils.SelectableWidgetWrap):
    signals = ['symbol_typed', 'finished_typing']

    def __init__(self, text_widget: urwid.Text | None = None, edit_widget: urwid.Edit | None = None) -> None:
        self._text_widget = text_widget if text_widget else urwid.Text('')
        self._edit_widget = edit_widget if edit_widget else urwid.Edit()

        self.skip = False

        super().__init__(self._text_widget)

    @property
    def text_widget(self):
        return self._text_widget

    @property
    def edit_widget(self):
        return self._edit_widget

    def keypress(self, size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        if key == 'enter':
            self.skip = True

        return super().keypress(size, key)

    def enable_input(self):
        if self._w is self._text_widget:
            self._w = self._edit_widget
            self._edit_widget.set_caption(self._text_widget.text)

    def disable_input(self, append_input: bool = True):
        if self._w is self._edit_widget:
            self._w = self._text_widget
            if append_input:
                self._text_widget.set_text(self._edit_widget.text)
            else:
                self._text_widget.set_text(self._edit_widget.caption)

    def append_text(self, text):
        self._text_widget.set_text(self._text_widget.text + text)

    async def type(self, text: str, edit_after: bool = False, symbol_delay: float | None = None, append_text=True):
        symbol_delay = DEFAULT_SYMBOL_DELAY if symbol_delay is None else symbol_delay
        self._w = self._text_widget
        self.skip = False
        if not append_text:
            self._text_widget.set_text('')
        if symbol_delay:
            for i in range(len(text)):
                s = text[i]
                if self.skip:
                    left_to_type = text[i:]
                    self.append_text(left_to_type)
                    self._emit('symbol_typed', [left_to_type])
                    break
                else:
                    self.append_text(s)
                    self._emit('symbol_typed', [s])
                    await asyncio.sleep(symbol_delay)
        else:
            self.append_text(text)
            self._emit('symbol_typed', [text])
        if edit_after:
            self.enable_input()
            self._edit_widget.set_edit_text('')

        self._emit('finished_typing')
        self.skip = False
