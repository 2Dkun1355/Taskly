from datetime import datetime

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget

from presentation.kivy_ui import theme
from presentation.kivy_ui.formatting import section_label
from presentation.kivy_ui.widgets import CalendarButton, LabelText

_MONTHS = (
    "січня", "лютого", "березня", "квітня", "травня", "червня",
    "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
)


class Sidebar(BoxLayout):
    def __init__(self, sections, selected, on_select, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_x=None,
            width=dp(230),
            padding=(dp(18), dp(26), dp(18), dp(18)),
            spacing=dp(6),
            **kwargs,
        )
        with self.canvas.after:
            Color(*theme.FIELD)
            self._divider = Rectangle(
                pos=(self.right - dp(1), self.y),
                size=(dp(1), self.height),
            )
        self.bind(pos=self._redraw_divider, size=self._redraw_divider)
        self._items = {}
        project_header = AnchorLayout(
            size_hint_y=None,
            height=dp(46),
        )
        project_row = BoxLayout(
            size_hint_x=None,
            width=dp(162),
            spacing=dp(6),
            padding=(0, dp(4)),
        )
        project_row.add_widget(CalendarButton())
        project_row.add_widget(LabelText(
            text="Taskly",
            font_size="32sp",
            bold=True,
            size_hint_x=None,
            width=dp(128),
        ))
        project_header.add_widget(project_row)
        self.add_widget(project_header)
        self.add_widget(Widget(size_hint_y=None, height=dp(18)))
        self._time = LabelText(
            size_hint_y=None,
            height=dp(32),
            halign="center",
            font_size="20sp",
            bold=True,
        )
        self.add_widget(self._time)
        self._date = LabelText(
            color=theme.MUTED,
            size_hint_y=None,
            height=dp(24),
            halign="center",
            font_size="14sp",
        )
        self.add_widget(self._date)
        self.add_widget(Widget(size_hint_y=None, height=dp(54)))

        for section in sections[:-1]:
            self._add_section(section, on_select, selected)

        self.add_widget(Widget())
        self._add_section(sections[-1], on_select, selected)
        self._update_clock()
        Clock.schedule_interval(lambda *_: self._update_clock(), 30)

    def _redraw_divider(self, *_):
        self._divider.pos = (self.right - dp(1), self.y)
        self._divider.size = (dp(1), self.height)

    def _add_section(self, section, on_select, selected):
        row = AnchorLayout(
            size_hint_y=None,
            height=dp(42),
            anchor_x="center",
        )
        button = Button(
            text=section_label(section),
            size_hint_y=None,
            height=dp(42),
            size_hint_x=None,
            width=dp(174),
            background_normal="",
            background_down="",
            background_color=theme.ACCENT if section is selected else theme.PANEL,
            color=theme.TEXT if section is selected else theme.MUTED,
            halign="left",
            padding=(dp(14), 0),
        )
        button.bind(on_release=lambda _, value=section: on_select(value))
        self._items[section] = button
        row.add_widget(button)
        self.add_widget(row)

    def _update_clock(self):
        now = datetime.now().astimezone()
        self._time.text = now.strftime("%H:%M")
        self._date.text = f"{now.day} {_MONTHS[now.month - 1]} {now.year}"

    def update(self, selected):
        for section, button in self._items.items():
            active = section is selected
            button.background_color = theme.ACCENT if active else theme.PANEL
            button.color = theme.TEXT if active else theme.MUTED
