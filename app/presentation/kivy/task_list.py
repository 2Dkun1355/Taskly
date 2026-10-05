from dataclasses import dataclass
from typing import Callable

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.utils import escape_markup

from domain.enums.task_status import TaskStatus
from presentation.kivy.formatting import describe_time
from presentation.kivy.task_view import TaskView
from presentation.kivy.widgets import make_button, make_label


@dataclass(frozen=True)
class TaskActions:
    complete: Callable[[TaskView], None]
    cancel: Callable[[TaskView], None]
    restart: Callable[[TaskView], None]
    edit: Callable[[TaskView], None]
    delete: Callable[[TaskView], None]


class TaskList(ScrollView):
    def __init__(self, actions: TaskActions, **kwargs):
        super().__init__(**kwargs)
        self._actions = actions
        self._box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self._box.bind(minimum_height=self._box.setter("height"))
        self.add_widget(self._box)

    def show(self, tasks: list[TaskView]):
        self._box.clear_widgets()
        if not tasks:
            self._box.add_widget(make_label("No tasks"))
        for task in tasks:
            self._box.add_widget(self._row(task))

    def _row(self, task: TaskView) -> BoxLayout:
        row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(6))
        row.add_widget(self._summary(task))
        for text, action in self._buttons(task):
            row.add_widget(make_button(
                text,
                lambda handler=action: handler(task),
                size_hint_x=None,
                width=dp(90),
                height=dp(56),
            ))
        return row

    def _buttons(self, task: TaskView):
        if task.status is TaskStatus.PENDING:
            return [
                ("Done", self._actions.complete),
                ("Cancel", self._actions.cancel),
                ("Edit", self._actions.edit),
            ]
        return [
            ("Restart", self._actions.restart),
            ("Delete", self._actions.delete),
        ]

    @staticmethod
    def _summary(task: TaskView):
        overdue = "  [color=ff5555]overdue[/color]" if task.is_overdue else ""
        status = "" if task.status is TaskStatus.PENDING else f"  ({task.status.value})"
        text = (
            f"[b]{escape_markup(task.title)}[/b]{overdue}{status}\n"
            f"{describe_time(task.start_at, task.end_at)}  |  {task.priority.value}"
        )
        return make_label(text, markup=True, size_hint_y=1)