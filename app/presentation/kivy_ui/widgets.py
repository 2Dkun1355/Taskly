from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ColorProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from presentation.kivy_ui import theme


class LabelText(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", theme.TEXT)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("shorten", True)
        super().__init__(**kwargs)
        self.bind(size=lambda *_: setattr(self, "text_size", self.size))


class CalendarButton(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(size_hint=(None, None), size=(dp(38), dp(38)), **kwargs)
        with self.canvas:
            Color(*theme.FIELD)
            self._body = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(6)])
            Color(*theme.ACCENT)
            self._outline = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(6)),
                width=1.2,
            )
            self._divider = Line(
                points=(self.x + dp(5), self.y + dp(23), self.right - dp(5), self.y + dp(23)),
                width=1.2,
            )
            self._left_ring = Line(
                points=(self.x + dp(11), self.top, self.x + dp(11), self.top - dp(7)),
                width=1.5,
            )
            self._right_ring = Line(
                points=(self.right - dp(11), self.top, self.right - dp(11), self.top - dp(7)),
                width=1.5,
            )
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self._body.pos = self.pos
        self._body.size = self.size
        self._outline.rounded_rectangle = (
            self.x, self.y, self.width, self.height, dp(6)
        )
        self._divider.points = (
            self.x + dp(5), self.y + dp(23), self.right - dp(5), self.y + dp(23)
        )
        self._left_ring.points = (
            self.x + dp(11), self.top, self.x + dp(11), self.top - dp(7)
        )
        self._right_ring.points = (
            self.right - dp(11), self.top, self.right - dp(11), self.top - dp(7)
        )


class Card(BoxLayout):
    def __init__(self, **kwargs):
        background = kwargs.pop("background", theme.PANEL)
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*background)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class UiButton(Button):
    background = ColorProperty(theme.FIELD)

    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", self.background)
        kwargs.setdefault("color", theme.TEXT)
        kwargs.setdefault("font_size", "13sp")
        super().__init__(**kwargs)
        self.bind(background=self._sync)

    def _sync(self, *_):
        self.background_color = self.background


class ChoiceBar(BoxLayout):
    value = StringProperty("")

    def __init__(self, options, value, on_change=None, **kwargs):
        super().__init__(size_hint_y=None, height=dp(34), spacing=dp(5), **kwargs)
        self.value = value
        self._buttons = {}
        self._on_change = on_change
        for key, label in options:
            button = ToggleButton(
                text=label,
                group=f"choice-{id(self)}",
                state="down" if key == value else "normal",
                background_normal="",
                background_down="",
                background_color=theme.FIELD,
                color=theme.MUTED,
                font_size="12sp",
            )
            button.bind(state=lambda instance, state, chosen=key: self._changed(chosen, state))
            self._buttons[key] = button
            self.add_widget(button)
        self._set_active_colors(value)

    def _changed(self, key, state):
        if state != "down":
            return
        self.value = key
        self._set_active_colors(key)
        if self._on_change is not None:
            self._on_change(key)

    def _set_active_colors(self, key):
        for name, button in self._buttons.items():
            button.background_color = theme.ACCENT if name == key else theme.FIELD
            button.color = theme.TEXT if name == key else theme.MUTED

    def set_enabled(self, enabled):
        self.disabled = not enabled
        for button in self._buttons.values():
            button.disabled = not enabled


class SearchField(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault("multiline", False)
        kwargs.setdefault("hint_text_color", theme.DIM)
        kwargs.setdefault("foreground_color", theme.TEXT)
        kwargs.setdefault("cursor_color", theme.ACCENT)
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs.setdefault("background_color", theme.FIELD)
        kwargs.setdefault("padding", (dp(12), dp(10)))
        kwargs.setdefault("font_size", "14sp")
        super().__init__(**kwargs)


class ScheduleField(BoxLayout):
    """Поле локальної дати й часу для форми задачі."""

    def __init__(self, label, value=None, **kwargs):
        super().__init__(size_hint_y=None, height=dp(42), spacing=dp(6), **kwargs)
        local = value.astimezone() if value else None
        self.input = SearchField(
            text=local.strftime("%d.%m.%Y %H:%M") if local else "",
            hint_text=f"{label}: дд.мм.рррр гг:хх",
            size_hint_y=None,
            height=dp(42),
            font_size="12sp",
        )
        self.add_widget(self.input)

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, value):
        self.input.text = value

    def set_enabled(self, enabled):
        self.disabled = not enabled
        self.input.disabled = not enabled
        self.input.foreground_color = theme.TEXT if enabled else theme.DIM
        self.input.background_color = theme.FIELD if enabled else theme.PANEL


class Modal(ModalView):
    def __init__(self, title, **kwargs):
        kwargs.setdefault("size", (dp(500), dp(460)))
        super().__init__(
            size_hint=(None, None),
            background_color=(0, 0, 0, 0.65),
            auto_dismiss=False,
            **kwargs,
        )
        panel = BoxLayout(
            orientation="vertical",
            padding=(dp(22), dp(12), dp(22), dp(18)),
            spacing=dp(12),
        )
        with panel.canvas.before:
            self._body_color = Color(*theme.PANEL)
            self._body_rect = RoundedRectangle(pos=panel.pos, size=panel.size, radius=[dp(12)])
        panel.bind(pos=self._redraw_body, size=self._redraw_body)
        panel.add_widget(LabelText(text=title, font_size="20sp", bold=True, size_hint_y=None, height=dp(32)))

        content_anchor = AnchorLayout(anchor_y="top")
        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(12))
        content.bind(minimum_height=content.setter("height"))
        content_anchor.add_widget(content)
        panel.add_widget(content_anchor)
        self.body = content
        self.footer = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        panel.add_widget(self.footer)
        self.add_widget(panel)

    def _redraw_body(self, panel, *_):
        self._body_rect.pos = panel.pos
        self._body_rect.size = panel.size


def message(title, text):
    modal = Modal(title, size=(dp(460), dp(260)))
    modal.body.add_widget(LabelText(text=text, color=theme.MUTED, shorten=False))
    close = UiButton(text="Закрити", background=theme.ACCENT, size_hint_y=None, height=dp(40))
    close.bind(on_release=lambda *_: modal.dismiss())
    modal.footer.add_widget(close)
    modal.open()


def confirm(title, text, action_text, action, danger=False):
    modal = Modal(title, size=(dp(460), dp(260)))
    modal.body.add_widget(LabelText(text=text, color=theme.MUTED, shorten=False))
    back = UiButton(text="Назад")
    accept = UiButton(text=action_text, background=theme.RED if danger else theme.ACCENT)
    back.bind(on_release=lambda *_: modal.dismiss())
    accept.bind(on_release=lambda *_: (modal.dismiss(), action()))
    modal.footer.add_widget(back)
    modal.footer.add_widget(accept)
    modal.open()
