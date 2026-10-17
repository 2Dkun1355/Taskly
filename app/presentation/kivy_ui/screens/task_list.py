from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from presentation.kivy_ui import theme
from presentation.kivy_ui.widgets import Text
from presentation.kivy_ui.screens.task_card import TaskCard


class TaskList(GridLayout):
    """Список карток і стан порожнього результату."""

    def __init__(self, state_of, on_edit, on_delete, on_action, **kwargs):
        super().__init__(
            cols=1, spacing=dp(10), size_hint_y=None,
            padding=(0, dp(2), dp(10), dp(10)), **kwargs,
        )
        self.bind(minimum_height=self.setter("height"))
        self._state_of = state_of
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_action = on_action

    def show(self, tasks, empty_title, search):
        self.clear_widgets()
        if not tasks:
            self.add_widget(self._empty_state(empty_title, search))
            return
        for task in tasks:
            self.add_widget(TaskCard(
                task, self._state_of, self._on_edit, self._on_delete, self._on_action,
            ))

    @staticmethod
    def _empty_state(title, search):
        box = BoxLayout(
            orientation="vertical", size_hint_y=None, height=dp(220),
            spacing=dp(6), padding=dp(24),
        )
        if search.strip():
            title, hint = "Нічого не знайдено", "Спробуйте змінити пошуковий запит."
        else:
            hint = "Натисніть «Нове завдання», щоб додати справу."
        box.add_widget(Text(text=title, font_size="18sp", halign="center"))
        box.add_widget(Text(
            text=hint, font_size="13sp", color=theme.MUTED, halign="center",
        ))
        return box
