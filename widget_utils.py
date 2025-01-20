import urwid


class SelectableWidgetWrap(urwid.WidgetWrap):
    """
    A WidgetWrap with forced selectability
    """

    def __init__(self, w: urwid.widget.widget.WrappedWidget) -> None:
        super().__init__(w)
        self._selectable = True

    def selectable(self) -> bool:
        return self._selectable


def signal_callback_stub(callback, *static_args, **static_kwargs):
    """
    Wrap a signal callback into a function that throws out
    :param callback: the signal callback to be wrapped
    :param static_args: arguments passed to the callback instead of the args passed by the signal
    :param static_kwargs: keyword arguments passed to the callback instead of the keyword  args passed by the signal
    :return: wrapped callback
    """

    def wrapper(*args, **kwargs):
        return callback(*static_args, **static_kwargs)

    return wrapper
