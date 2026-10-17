from kivy.metrics import dp
from kivy.uix.widget import Widget

from presentation.kivy_ui import theme
from presentation.kivy_ui.formatting import today_caption
from presentation.kivy_ui.widgets import Card, NavItem, Text


class Sidebar(Card):
    """Бічна навігація із заголовком, розділами та лічильниками."""

    def __init__(self, sections, archive_section, on_select, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_x=None,
            width=dp(240),
            bg_color=theme.SIDEBAR,
            radius=0,
            padding=(dp(16), dp(24), dp(16), dp(18)),
            spacing=dp(6),
            **kwargs,
        )
        self._items = {}
        self._on_select = on_select

        self.add_widget(Text(
            text="Taskly", font_size="28sp", bold=True,
            size_hint_y=None, height=dp(44),
        ))
        self.add_widget(Text(
            text=today_caption(), font_size="12sp", color=theme.MUTED,
            size_hint_y=None, height=dp(22),
        ))
        self.add_widget(Widget(size_hint_y=None, height=dp(18)))

        for key, label in sections:
            self._add_item(key, label)

        self.add_widget(Widget())
        self._add_item(*archive_section)

    def _add_item(self, key, label):
        item = NavItem(label)
        item.bind(on_release=lambda _, section=key: self._on_select(section))
        self._items[key] = item
        self.add_widget(item)

    def update(self, selected_section, counts):
        """Оновлює вибраний пункт і лічильники без повторної побудови меню."""
        for key, item in self._items.items():
            item.selected = key == selected_section
            item.set_count(counts.get(key, 0))
