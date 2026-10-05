from typing import Callable, Optional

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout

from domain.enums.task_status import TaskStatus
from domain.exceptions import DomainException
from presentation.kivy.filter_bar import FILTERS, FilterBar, TaskFilter
from presentation.kivy.task_form import TaskForm
from presentation.kivy.task_gateway import TaskGateway
from presentation.kivy.task_list import TaskActions, TaskList
from presentation.kivy.task_view import TaskData, TaskView
from presentation.kivy.widgets import make_button, make_label, show_error


class TasklyApp(App):
    title = "Taskly"

    def __init__(self, gateway: TaskGateway, **kwargs):
        super().__init__(**kwargs)
        self._gateway = gateway
        self._filter = FILTERS[0]

    def build(self):
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        header = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        header.add_widget(make_label("Taskly", font_size=sp(20), bold=True))
        header.add_widget(make_button("New task", self._new, size_hint_x=None, width=dp(120)))
        root.add_widget(header)

        root.add_widget(FilterBar(self._set_filter))

        self._list = TaskList(TaskActions(
            complete=lambda task: self._change_status(task, TaskStatus.COMPLETED),
            cancel=lambda task: self._change_status(task, TaskStatus.CANCELLED),
            restart=lambda task: self._change_status(task, TaskStatus.PENDING),
            edit=self._edit,
            delete=lambda task: self._run(lambda: self._gateway.delete(task.id)),
        ))
        root.add_widget(self._list)

        self._reload()
        return root

    def _set_filter(self, task_filter: TaskFilter):
        self._filter = task_filter
        self._reload()

    def _reload(self):
        self._list.show(self._gateway.list(self._filter))

    def _run(self, action: Callable[[], None]):
        try:
            action()
        except DomainException as error:
            show_error(str(error))
        self._reload()

    def _change_status(self, task: TaskView, status: TaskStatus):
        self._run(lambda: self._gateway.change_status(task.id, status))

    def _new(self):
        TaskForm("New task", None, self._create).open()

    def _edit(self, task: TaskView):
        TaskForm(
            "Edit task",
            task,
            lambda data: self._update(task.id, data),
            lambda: self._delete(task.id),
        ).open()

    def _create(self, data: TaskData) -> Optional[str]:
        return self._guard(lambda: self._gateway.create(data))

    def _update(self, task_id: str, data: TaskData) -> Optional[str]:
        return self._guard(lambda: self._gateway.update(task_id, data))

    def _delete(self, task_id: str) -> Optional[str]:
        return self._guard(lambda: self._gateway.delete(task_id))

    def _guard(self, action: Callable[[], None]) -> Optional[str]:
        try:
            action()
        except DomainException as error:
            return str(error)
        self._reload()
        return None