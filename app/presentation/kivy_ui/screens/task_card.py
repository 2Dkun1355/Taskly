from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from domain.enums import TaskStatus
from presentation.kivy_ui import theme
from presentation.kivy_ui.formatting import format_schedule
from presentation.kivy_ui.widgets import Card, Chip, FlatButton, IconButton, Text


class TaskCard(Card):
    """Візуальне представлення одного завдання та його дій."""

    def __init__(self, task, state_of, on_edit, on_delete, on_action, **kwargs):
        description = (task.description.value if task.description else "").replace(
            "\n", " "
        )
        priority = task.priority

        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(144 if description else 120),
            padding=(dp(28), dp(12), dp(16), dp(12)),
            spacing=dp(4),
            accent_color=(
                theme.PRIORITY_COLORS.get(priority.name, theme.DIM)
                if task.is_planned else theme.DIM
            ),
            **kwargs,
        )
        self._task = task
        self._on_action = on_action
        self._build_header(task, state_of(task), priority, on_edit, on_delete)
        if description:
            self.add_widget(Text(
                text=description, font_size="12sp", color=theme.MUTED,
                size_hint_y=None, height=dp(20),
            ))
        self._build_metadata(task, priority)
        self._build_actions(task)

    def _build_header(self, task, state, priority, on_edit, on_delete):
        top = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        top.add_widget(Text(text=task.title.value, font_size="16sp", bold=True))
        state_label = (
            "Без дати"
            if state == "inbox"
            else TaskStatus(state).label.capitalize()
        )
        top.add_widget(Chip(text=state_label, tone=theme.STATE_COLORS[state]))
        if task.is_planned:
            top.add_widget(self._icon_button("edit", lambda *_: on_edit(task)))
        top.add_widget(self._icon_button(
            "delete", lambda *_: on_delete(task), press_tone=theme.RED,
        ))
        self.add_widget(top)

    def _build_metadata(self, task, priority):
        meta = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(10))
        meta.add_widget(Text(
            text=format_schedule(task.schedule), font_size="12sp", color=theme.MUTED,
        ))
        meta.add_widget(Text(
            text=f"Пріоритет: {priority.label}",
            font_size="12sp", color=theme.PRIORITY_COLORS.get(priority.name, theme.MUTED),
            halign="right", size_hint_x=None, width=dp(170),
        ))
        self.add_widget(meta)

    def _build_actions(self, task):
        actions = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        actions.add_widget(Widget())
        if task.is_planned:
            actions.add_widget(self._action_button(
                "Скасувати", "cancel", "Завдання скасовано", theme.RED,
            ))
            actions.add_widget(self._action_button(
                "Не виконано", "not_completed", "Позначено як невиконане", theme.ORANGE,
            ))
            actions.add_widget(self._action_button(
                "Виконано", "complete", "Завдання виконано", theme.WHITE, theme.GREEN,
            ))
        else:
            actions.add_widget(self._action_button(
                "Відновити", "restart", "Завдання повернуто без дати", theme.WHITE, theme.ACCENT,
            ))
        self.add_widget(actions)

    def _action_button(self, text, action, message, color, bg=theme.SURFACE_ALT):
        button = FlatButton(
            text=text, bg_color=bg, color=color, font_size="12sp",
            size_hint=(None, None), size=(dp(104), dp(34)),
        )
        button.bind(on_release=lambda *_: self._on_action(self._task, action, message))
        return button

    @staticmethod
    def _icon_button(icon, on_release, press_tone=theme.TEXT):
        button = IconButton(
            icon=icon, press_tone=press_tone, size=(dp(30), dp(30)),
            pos_hint={"center_y": 0.5},
        )
        button.bind(on_release=on_release)
        return button
