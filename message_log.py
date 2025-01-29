from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import Any, Iterable

import urwid

import stage
import typewriter
from widget_utils import signal_callback_stub, SelectableWidgetWrap


class MessageLog(stage.Scene):
    def __init__(self) -> None:
        self.list_body = urwid.SimpleFocusListWalker([])
        self.list_box = urwid.ListBox(self.list_body)
        super().__init__(self.list_box)

    def append_message(self, message: Message):
        if self.list_body:  # disable interaction with previous message
            self.list_body[-1] = urwid.WidgetDisable(self.list_body[-1])
        self.list_body.append(message)
        self.list_box.focus_position = len(self.list_body) - 1
        message.setup(self)

        if self.stage.main_loop.screen.started:  # redraw the screen, but only if the screen has been started
            self.stage.main_loop.draw_screen()


class Message(urwid.WidgetWrap):
    def __init__(self, w):
        super().__init__(w)
        self._message_log: MessageLog | None = None

    @property
    def message_log(self):
        return self._message_log

    def setup(self, message_log):
        """
        Called by MessageLog after appending the message.
        All MessageLog related setup should be done in this method.
        """
        self._message_log = message_log


class TextMessage(Message, SelectableWidgetWrap):
    def __init__(self, parts: list[TextMessagePart],
                 final_callback: Callable[[TextMessage], Any] | None = None):
        self.parts: deque[TextMessagePart] = deque(parts)
        self.final_callback = final_callback

        self._typewriter = typewriter.Typewriter()
        self._pile = urwid.Pile([self._typewriter])

        self._continue_hint = urwid.Text('[Press ENTER to continue]')
        self._can_continue = False

        self.input_vars: dict[str, str] = {}
        self._current_part: TextMessagePart | None = None

        super().__init__(self._pile)

    @property
    def typewriter(self):
        return self._typewriter

    @property
    def pile(self):
        return self._pile

    def setup(self, message_log):
        super().setup(message_log)
        self._typewriter.event_loop = message_log.stage.main_loop.event_loop
        urwid.connect_signal(self._typewriter,
                             'fragment_typed',
                             signal_callback_stub(message_log.stage.main_loop.draw_screen))

        def on_typewriter_finished():
            if self._current_part.store_input_at is not None:
                self._typewriter.enable_input()
                self._message_log.stage.main_loop.draw_screen()
            elif self._current_part.auto_continue:
                self.continue_()
            else:
                self.enable_continue()

        urwid.connect_signal(self._typewriter,
                             'finished_typing',
                             signal_callback_stub(on_typewriter_finished))
        self.continue_()

    def keypress(self, size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        if key == 'enter':
            if self._current_part is not None:
                if self._typewriter.is_typing():
                    self._typewriter.skip()
                elif self._current_part.store_input_at is not None:
                    edit_text = self._typewriter.edit_widget.edit_text
                    if self._current_part.store_input_globally:
                        self._message_log.stage.set_global_var(self._current_part.store_input_at, edit_text)
                    else:
                        self.input_vars[self._current_part.store_input_at] = edit_text
                    self._typewriter.disable_input(append_input=self._current_part.append_input)
                    self.continue_()
                elif self._can_continue:
                    self.disable_continue()
                    self.continue_()
            return None

        return self._typewriter.keypress(size, key)  # Pass input to typewriter directly

    def continue_(self):
        if len(self.parts):
            self._current_part = self.parts.popleft()

            if self._current_part.preliminary_callback:
                self._current_part.preliminary_callback(self, self._current_part)

            self._typewriter.type(self._current_part.text, typing_delay=self._current_part.symbol_delay)
        else:
            self._current_part = None
            if self.final_callback is not None:
                self.final_callback(self)

    def enable_continue(self):
        if not self._can_continue:
            self._pile.contents.append((self._continue_hint, self._pile.options()))
            self._message_log.stage.main_loop.draw_screen()
        self._can_continue = True

    def disable_continue(self):
        if self._can_continue:
            self._pile.contents.pop(1)
            self._message_log.stage.main_loop.draw_screen()
        self._can_continue = False


class TextMessagePart:
    def __init__(self, text: str,
                 symbol_delay: float | None = None,
                 auto_continue: bool = False, store_input_at: str | None = None,
                 store_input_globally: bool = False,
                 append_input: bool = True,
                 preliminary_callback: Callable[[TextMessage, TextMessagePart], Any] | None = None):
        self.text = text
        self.symbol_delay = symbol_delay
        self.auto_continue = auto_continue
        self.store_input_at = store_input_at
        self.store_input_globally = store_input_globally
        self.append_input = append_input
        self.preliminary_callback = preliminary_callback


class ButtonMessage(Message):
    def __init__(self, options: Iterable[ButtonMessageOption]):
        buttons = []
        for o in options:
            b = urwid.Button(o.text)
            urwid.connect_signal(b, 'click', o.callback, user_args=[self])
            buttons.append(b)
        self._pile = urwid.Pile(buttons)
        super().__init__(self._pile)


class ButtonMessageOption:
    def __init__(self, text: str, callback: Callable[[ButtonMessage, urwid.Button], None]) -> None:
        self.text = text
        self.callback = callback
