from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from presentation.kivy_ui import theme
from presentation.kivy_ui.formatting import format_schedule, priority_label, status_label
from presentation.kivy_ui.widgets import Card, LabelText, UiButton


class TaskRow(Card):
    def __init__(self, task, on_edit, on_delete, on_action, **kwargs):
        description = task.description.value if task.description else ""
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(142 if description else 118),
            padding=(dp(16), dp(12)),
            spacing=dp(8),
            background=theme.PANEL,
            **kwargs,
        )
        self._task = task

        header = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(10))
        title = LabelText(text=task.title.value, font_size="15sp", bold=True)
        header.add_widget(title)
        header.add_widget(Widget())
        header.add_widget(LabelText(
            text=priority_label(task.priority),
            color=theme.PRIORITY_COLORS[task.priority.name],
            font_size="12sp",
            size_hint_x=None,
            width=dp(86),
            halign="right",
        ))
        self.add_widget(header)

        meta = BoxLayout(size_hint_y=None, height=dp(18), spacing=dp(10))
        if not task.is_planned:
            meta.add_widget(LabelText(
                text=status_label(task.status),
                color=theme.STATUS_COLORS[task.status.value],
                font_size="12sp",
                size_hint_x=None,
                width=dp(100),
                halign="left",
            ))
        self.add_widget(meta)

        if description:
            self.add_widget(LabelText(
                text=description.replace("\n", " "),
                color=theme.MUTED,
                font_size="12sp",
                size_hint_y=None,
                height=dp(18),
            ))

        actions = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(6))
        actions.add_widget(LabelText(
            text=format_schedule(task.schedule),
            color=theme.MUTED,
            font_size="12sp",
            size_hint_x=None,
            width=dp(150),
        ))
        actions.add_widget(Widget())
        for label, action, color in self._actions(task):
            button = UiButton(
                text=label,
                background=color,
                size_hint_x=None,
                width=dp(92),
                font_size="11sp",
            )
            button.bind(on_release=lambda *_ , action=action: on_action(task, action, "Готово"))
            actions.add_widget(button)

        if task.is_planned:
            edit = UiButton(text="Редагувати", size_hint_x=None, width=dp(92), font_size="11sp")
            edit.bind(on_release=lambda *_: on_edit(task))
            actions.add_widget(edit)

        delete = UiButton(text="Видалити", background=theme.FIELD, size_hint_x=None, width=dp(82), font_size="11sp")
        delete.bind(on_release=lambda *_: on_delete(task))
        actions.add_widget(delete)
        self.add_widget(actions)

    @staticmethod
    def _actions(task):
        if task.is_planned:
            return (
                ("Виконати", "complete", theme.GREEN),
                ("Не виконано", "not_completed", theme.ORANGE),
                ("Скасувати", "cancel", theme.RED),
            )
        return (("Відновити", "restart", theme.ACCENT),)
