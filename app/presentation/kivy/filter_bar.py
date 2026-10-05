from dataclasses import dataclass
from typing import Callable, Optional

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton

from domain.enums.task_status import TaskStatus


@dataclass(frozen=True)
class TaskFilter:
    label: str
    status: Optional[TaskStatus] = None
    only_overdue: bool = False


FILTERS = [
    TaskFilter("Active", TaskStatus.PENDING),
    TaskFilter("Done", TaskStatus.COMPLETED),
    TaskFilter("Cancelled", TaskStatus.CANCELLED),
]


class FilterBar(BoxLayout):
    def __init__(self, on_change: Callable[[TaskFilter], None], **kwargs):
        super().__init__(size_hint_y=None, height=dp(40), spacing=dp(6), **kwargs)
        for index, task_filter in enumerate(FILTERS):
            button = ToggleButton(
                text=task_filter.label,
                group="task-filter",
                allow_no_selection=False,
                state="down" if index == 0 else "normal",
            )
            button.bind(on_release=lambda _, f=task_filter: on_change(f))
            self.add_widget(button)