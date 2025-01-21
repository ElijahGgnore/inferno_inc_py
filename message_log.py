from __future__ import annotations
from collections import deque
from collections.abc import Callable
from typing import Any

import urwid

import stage
import typewriter
from widget_utils import signal_callback_stub


class MessageLog(stage.Scene):
    def __init__(self) -> None:
        self.list_body = urwid.SimpleFocusListWalker([])
        self.list_box = urwid.ListBox(self.list_body)
        super().__init__(self.list_box)

    def append_message(self, message: Message):
        self.list_body.append(message)
        message.setup(self)


class Message(urwid.WidgetWrap):
    def __init__(self, w):
        super().__init__(w)
        self._message_log: MessageLog | None = None

    def setup(self, message_log):
        """
        Called by MessageLog after appending the message.
        All MessageLog related setup should be done in this method.
        """
        self._message_log = message_log


class TextMessage(Message):
    def __init__(self, parts: list[TextMessagePart],
                 final_callback: Callable[[TextMessage], Any] | None = None):
        self.parts: deque[TextMessagePart] = deque(parts)
        self.final_callback = final_callback

        self._typewriter = typewriter.Typewriter()
        self._pile = urwid.Pile([self._typewriter])

        self._continue_hint = urwid.Text('[Press ENTER to continue]')
        self._can_continue = False
        self._auto_continue = False

        super().__init__(self._pile)

    def setup(self, message_log):
        super().setup(message_log)
        urwid.connect_signal(self._typewriter, 'symbol_typed',
                             signal_callback_stub(message_log.stage.urwid_loop.draw_screen))
        urwid.connect_signal(self._typewriter, 'finished_typing', signal_callback_stub(
            lambda: self.continue_() if self._auto_continue else self.enable_continue()))
        self.continue_()

    def keypress(self, size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        if key == 'enter' and self._can_continue:
            self.disable_continue()
            self.continue_()
            return None
        return super().keypress(size, key)

    def continue_(self):
        if len(self.parts):
            m = self.parts.popleft()
            self._auto_continue = m.auto_continue
            self._message_log.stage.asyncio_loop.create_task(
                self._typewriter.type(m.text, symbol_delay=m.symbol_delay, append_text=m.append_text))
        else:
            if self.final_callback:
                self.final_callback(self)

    def enable_continue(self):
        if not self._can_continue:
            self._pile.contents.append((self._continue_hint, self._pile.options()))
            self._message_log.stage.urwid_loop.draw_screen()
        self._can_continue = True

    def disable_continue(self):
        if self._can_continue:
            self._pile.contents.pop(1)
            self._message_log.stage.urwid_loop.draw_screen()
        self._can_continue = False


class TextMessagePart:
    def __init__(self, text: str, append_text: bool = True, symbol_delay: float | None = None,
                 auto_continue: bool = False):
        self.text = text
        self.append_text = append_text
        self.symbol_delay = symbol_delay
        self.auto_continue = auto_continue
