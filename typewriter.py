from __future__ import annotations

from typing import Any

import urwid
from collections import deque

DEFAULT_TYPING_DELAY = 1 / 30


class Typewriter(urwid.WidgetWrap):
    signals = ['fragment_typed', 'finished_typing']

    def __init__(self) -> None:
        self._text_widget = urwid.Text('')
        self._edit_widget = urwid.Edit()

        self._event_loop: urwid.EventLoop | None = None
        self._typing_queue: deque[tuple[str, float]] = deque()
        self._current_fragment: str | None = None
        self._current_handle: Any | None = None

        super().__init__(self._text_widget)

    @property
    def event_loop(self):
        return self._event_loop

    @event_loop.setter
    def event_loop(self, value):
        self.safe_stop()
        self._typing_queue.clear()
        self._event_loop = value

    @property
    def text_widget(self):
        return self._text_widget

    @property
    def edit_widget(self):
        return self._edit_widget

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

    def is_typing(self):
        return self._current_fragment is not None

    def safe_stop(self):
        if self._current_fragment is not None:
            self._current_fragment = None
            if self._current_handle is not None:
                self._event_loop.remove_alarm(self._current_handle)
                self._current_handle = None

    def clear_queue(self):
        self._typing_queue.clear()

    def clear_text(self):
        self._text_widget.set_text('')
        self._edit_widget.set_caption('')

    def skip(self):
        """
        Instantly type all the queued text fragments
        :return:
        """
        if self.is_typing():
            text = self._current_fragment
            self._current_fragment = None

            if self._current_handle is not None:
                self._event_loop.remove_alarm(self._current_handle)
                self._current_handle = None

            for _ in range(len(self._typing_queue)):
                text += self._typing_queue.popleft()[0]

            self.append_text(text)
            self._emit('fragment_typed', text)
            self._emit('finished_typing')

    def add_to_queue(self, fragment: str, typing_delay: float):
        """
        Add a text fragment to typing queue
        :param fragment: a string of any size that will be typed entirely when its turn comes
        :param typing_delay: delay in seconds before typing each symbol. 0 to type instantly
        :return:
        """
        self._typing_queue.append((fragment, typing_delay))

    def _process_next(self):
        fragment, delay = self._typing_queue.popleft()
        if delay:
            self._current_fragment = fragment
            self._current_handle = self._event_loop.alarm(delay, self._process_current)
        else:
            self._current_fragment = fragment
            self._current_handle = None
            self._process_current()

    def _process_current(self):
        self.append_text(self._current_fragment)
        self._emit('fragment_typed', self._current_fragment)

        if self._typing_queue:
            self._process_next()
        else:
            self._current_fragment = None
            self._current_handle = None
            self._emit('finished_typing')

    def safe_start(self):
        """
        Start typing, but only if not already typing, and there is something to type
        """
        if not self.is_typing() and self._typing_queue:
            self._process_next()

    def type(self, text: str, typing_delay: float | None = None):
        """
        Add every symbol in text to the queue and start typing
        :param text: text to type
        :param typing_delay: delay in seconds before typing each symbol.
        None to type with default delay. 0 to type instantly
        :return:
        """
        typing_delay = DEFAULT_TYPING_DELAY if typing_delay is None else typing_delay

        for symbol in text:
            self.add_to_queue(symbol, typing_delay)

        self.safe_start()
