from math import sqrt

from kivy.graphics import Color, Line, Quad, RoundedRectangle, Triangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from presentation.kivy_ui import theme


class Text(Label):
    """Підпис: вирівняний ліворуч, по центру вертикально, довгий текст обрізається."""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", theme.TEXT)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("shorten", True)
        kwargs.setdefault("shorten_from", "right")
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *_):
        self.text_size = self.size


class Card(BoxLayout):
    """Контейнер із закругленим фоном і, за потреби, кольоровою смужкою зліва."""

    bg_color = ListProperty(theme.SURFACE)
    accent_color = ListProperty((0, 0, 0, 0))
    radius = NumericProperty(0)

    def __init__(self, **kwargs):
        kwargs.setdefault("radius", dp(14))
        super().__init__(**kwargs)

        with self.canvas.before:
            self._bg_instruction = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self.radius]
            )
            self._accent_instruction = Color(*self.accent_color)
            self._accent_rect = RoundedRectangle(
                pos=self.pos, size=(0, 0), radius=[dp(2)]
            )

        self.bind(
            pos=self._redraw,
            size=self._redraw,
            bg_color=self._redraw,
            accent_color=self._redraw,
            radius=self._redraw,
        )
        self._redraw()

    def _redraw(self, *_):
        self._bg_instruction.rgba = self.bg_color
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self.radius]

        x, y = self.pos
        self._accent_instruction.rgba = self.accent_color
        self._accent_rect.pos = (x + dp(10), y + dp(14))
        self._accent_rect.size = (dp(4), max(self.height - dp(28), 0))


class FlatButton(ButtonBehavior, Label):
    """Пласка кнопка із закругленими кутами. bg_color це фон, color це колір тексту."""

    bg_color = ListProperty(theme.SURFACE_ALT)
    radius = NumericProperty(0)

    def __init__(self, **kwargs):
        kwargs.setdefault("color", theme.TEXT)
        kwargs.setdefault("font_size", "13sp")
        kwargs.setdefault("radius", dp(10))
        super().__init__(**kwargs)

        with self.canvas.before:
            self._bg_instruction = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self.radius]
            )

        self.bind(
            pos=self._redraw,
            size=self._redraw,
            bg_color=self._redraw,
            state=self._redraw,
            radius=self._redraw,
        )
        self._redraw()

    def _redraw(self, *_):
        red, green, blue, alpha = self.bg_color
        if self.state == "down":
            # Під час натискання фон трохи світлішає.
            red, green, blue = (min(channel + 0.08, 1) for channel in (red, green, blue))

        self._bg_instruction.rgba = (red, green, blue, alpha)
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self.radius]


class IconButton(ButtonBehavior, Widget):
    """Невелика кнопка-піктограма без фону: «edit» (олівець) або «delete» (урна).

    У спокої піктограма приглушена, а при натисканні підсвічується кольором press_tone.
    """

    icon = StringProperty("edit")
    tone = ListProperty(theme.MUTED)
    press_tone = ListProperty(theme.TEXT)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(30), dp(30)))
        super().__init__(**kwargs)

        self.bind(
            pos=self._redraw,
            size=self._redraw,
            state=self._redraw,
            icon=self._redraw,
            tone=self._redraw,
            press_tone=self._redraw,
        )
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()

        pressed = self.state == "down"
        center_x, center_y = self.center

        with self.canvas:
            if pressed:
                # Ледь помітна підсвітка під час натискання.
                Color(1, 1, 1, 0.08)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])

            Color(*(self.press_tone if pressed else self.tone))
            if self.icon == "delete":
                self._draw_trash(center_x, center_y)
            else:
                self._draw_pencil(center_x, center_y)

    @staticmethod
    def _draw_pencil(cx, cy):
        """Контурний олівець, нахилений угору вправо."""
        unit = dp(1)
        k = sqrt(0.5)
        half = 2.4

        def point(along, across):
            # along: вздовж олівця, across: упоперек (в одиницях unit).
            return (
                cx + (k * along - k * across) * unit,
                cy + (k * along + k * across) * unit,
            )

        Line(
            points=[
                *point(8, half),
                *point(8, -half),
                *point(-3, -half),
                *point(-9, 0),
                *point(-3, half),
            ],
            width=dp(1.3),
            joint="round",
            close=True,
        )
        Line(
            points=[*point(-3, half), *point(-3, -half)],
            width=dp(1.3),
            cap="round",
        )

    @staticmethod
    def _draw_trash(cx, cy):
        """Контурна урна з кришкою, ручкою та двома смужками."""
        unit = dp(1)
        width = dp(1.3)

        # Кришка і її ручка.
        Line(
            points=[cx - 7 * unit, cy + 5 * unit, cx + 7 * unit, cy + 5 * unit],
            width=width,
            cap="round",
        )
        Line(
            points=[
                cx - 2.5 * unit, cy + 5 * unit,
                cx - 2.5 * unit, cy + 8 * unit,
                cx + 2.5 * unit, cy + 8 * unit,
                cx + 2.5 * unit, cy + 5 * unit,
            ],
            width=width,
            joint="round",
        )
        # Корпус.
        Line(
            points=[
                cx - 5.5 * unit, cy + 5 * unit,
                cx - 4.5 * unit, cy - 8 * unit,
                cx + 4.5 * unit, cy - 8 * unit,
                cx + 5.5 * unit, cy + 5 * unit,
            ],
            width=width,
            joint="round",
        )
        # Смужки.
        for offset in (-1.8, 1.8):
            Line(
                points=[cx + offset * unit, cy + 2 * unit, cx + offset * unit, cy - 5 * unit],
                width=width,
                cap="round",
            )


class Chip(Label):
    """Невелика кольорова позначка, наприклад статус завдання."""

    tone = ListProperty(theme.ACCENT)

    def __init__(self, **kwargs):
        kwargs.setdefault("font_size", "11sp")
        kwargs.setdefault("bold", True)
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("height", dp(22))
        kwargs.setdefault("pos_hint", {"center_y": 0.5})
        super().__init__(**kwargs)

        with self.canvas.before:
            self._bg_instruction = Color(0, 0, 0, 0)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(11)]
            )

        self.bind(
            pos=self._redraw,
            size=self._redraw,
            tone=self._redraw,
            texture_size=self._fit,
        )
        self._fit()
        self._redraw()

    def _fit(self, *_):
        self.width = self.texture_size[0] + dp(20)

    def _redraw(self, *_):
        red, green, blue, _alpha = self.tone
        self.color = (red, green, blue, 1)
        self._bg_instruction.rgba = (red, green, blue, 0.18)
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class Field(Card):
    """Поле введення із закругленим фоном. Текст доступний через властивість text."""

    def __init__(self, text="", hint="", multiline=False, height=44, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        super().__init__(
            bg_color=theme.FIELD,
            radius=dp(10),
            height=dp(height),
            **kwargs,
        )

        self.input = TextInput(
            text=text,
            hint_text=hint,
            multiline=multiline,
            background_normal="",
            background_active="",
            background_disabled_normal="",
            background_color=(0, 0, 0, 0),
            foreground_color=theme.TEXT,
            hint_text_color=theme.DIM,
            cursor_color=theme.ACCENT,
            padding=(dp(10), dp(12), dp(10), dp(12)),
            font_size="14sp",
        )
        self.input.bind(focus=self._on_focus)
        self.add_widget(self.input)

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, value):
        self.input.text = value

    def _on_focus(self, _, focused):
        self.bg_color = theme.FIELD_FOCUS if focused else theme.FIELD


class NavItem(ButtonBehavior, BoxLayout):
    """Пункт бічного меню з лічильником справа."""

    selected = BooleanProperty(False)

    def __init__(self, text, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            padding=(dp(14), 0, dp(12), 0),
            spacing=dp(8),
            **kwargs,
        )

        self._title = Text(text=text, font_size="14sp", color=theme.MUTED)
        self._count = Text(
            text="",
            font_size="12sp",
            bold=True,
            halign="right",
            size_hint_x=None,
            width=dp(34),
            color=theme.MUTED,
        )
        self.add_widget(self._title)
        self.add_widget(self._count)

        with self.canvas.before:
            self._bg_instruction = Color(0, 0, 0, 0)
            self._bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(10)]
            )

        self.bind(
            pos=self._redraw,
            size=self._redraw,
            selected=self._redraw,
            state=self._redraw,
        )
        self._redraw()

    def set_count(self, count, alert=False):
        """Показує кількість завдань; нуль не показується."""
        self._count.text = str(count) if count else ""
        self._count.color = theme.RED if (alert and count) else theme.MUTED

    def _redraw(self, *_):
        if self.selected:
            rgba = (*theme.ACCENT[:3], 0.22)
        elif self.state == "down":
            rgba = (1, 1, 1, 0.06)
        else:
            rgba = (0, 0, 0, 0)

        self._bg_instruction.rgba = rgba
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._title.color = theme.TEXT if self.selected else theme.MUTED
        self._title.bold = self.selected


class Segmented(BoxLayout):
    """Перемикач із кількох варіантів. Обраний ключ лежить у властивості value."""

    value = StringProperty("")

    def __init__(self, options, value, **kwargs):
        super().__init__(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(6),
            **kwargs,
        )
        self._buttons = {}

        for key, label in options:
            button = FlatButton(text=label)
            button.bind(
                on_release=lambda _, chosen=key: setattr(self, "value", chosen)
            )
            self._buttons[key] = button
            self.add_widget(button)

        self.bind(value=self._refresh)
        self.value = value
        self._refresh()

    def _refresh(self, *_):
        for key, button in self._buttons.items():
            selected = key == self.value
            button.bg_color = theme.ACCENT if selected else theme.FIELD
            button.color = theme.TEXT if selected else theme.MUTED


class ModalCard(ModalView):
    """Вікно-картка поверх застосунку: заголовок і порожня область body для вмісту."""

    def __init__(self, title, width=460, height=260, **kwargs):
        from kivy.core.window import Window

        kwargs.setdefault("auto_dismiss", True)
        super().__init__(
            size_hint=(None, None),
            size=(
                min(dp(width), Window.width * 0.94),
                min(dp(height), Window.height * 0.94),
            ),
            background="",
            background_color=(0, 0, 0, 0),
            overlay_color=(0, 0, 0, 0.6),
            **kwargs,
        )

        card = Card(
            orientation="vertical",
            bg_color=theme.SURFACE,
            padding=dp(22),
            spacing=dp(14),
        )
        card.add_widget(
            Text(
                text=title,
                font_size="19sp",
                bold=True,
                size_hint_y=None,
                height=dp(30),
            )
        )

        self.body = BoxLayout(orientation="vertical", spacing=dp(12))
        card.add_widget(self.body)
        self.add_widget(card)


def show_message(title, text):
    """Показує повідомлення з кнопкою «Закрити»."""
    modal = ModalCard(title, height=230)
    modal.body.add_widget(
        Text(
            text=text,
            font_size="14sp",
            color=theme.MUTED,
            shorten=False,
            valign="top",
        )
    )

    close = FlatButton(
        text="Закрити",
        bg_color=theme.ACCENT,
        size_hint_y=None,
        height=dp(42),
    )
    close.bind(on_release=lambda *_: modal.dismiss())
    modal.body.add_widget(close)
    modal.open()


def confirm(title, text, confirm_text, on_confirm, danger=False):
    """Просить підтвердити дію; on_confirm викликається лише після згоди."""
    modal = ModalCard(title, height=230)
    modal.body.add_widget(
        Text(
            text=text,
            font_size="14sp",
            color=theme.MUTED,
            shorten=False,
            valign="top",
        )
    )

    row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
    back = FlatButton(text="Назад", bg_color=theme.SURFACE_ALT)
    accept = FlatButton(
        text=confirm_text,
        bg_color=theme.RED if danger else theme.ACCENT,
        bold=True,
    )

    def on_accept(*_):
        modal.dismiss()
        on_confirm()

    back.bind(on_release=lambda *_: modal.dismiss())
    accept.bind(on_release=on_accept)
    row.add_widget(back)
    row.add_widget(accept)
    modal.body.add_widget(row)
    modal.open()