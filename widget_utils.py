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
