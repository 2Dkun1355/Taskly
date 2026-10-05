from typing import Callable, Optional

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from domain.enums.task_priority import TaskPriority
from presentation.kivy.formatting import INPUT_HINT, format_input, parse_time
from presentation.kivy.task_view import TaskData, TaskView
from presentation.kivy.widgets import make_button, make_label


class TaskForm:
    def __init__(
        self,
        heading: str,
        task: Optional[TaskView],
        on_submit: Callable[[TaskData], Optional[str]],
        on_delete: Optional[Callable[[], Optional[str]]] = None,
    ):
        self._on_submit = on_submit
        self._on_delete = on_delete
        self._delete_armed = False

        self._title = self._input("Title", task.title if task else "")
        self._description = TextInput(
            text=(task.description or "") if task else "",
            hint_text="Description (optional)",
            size_hint_y=None,
            height=dp(80),
        )
        self._priority = Spinner(
            text=(task.priority if task else TaskPriority.MEDIUM).value,
            values=[priority.value for priority in TaskPriority],
            size_hint_y=None,
            height=dp(40),
        )
        self._start = self._input(INPUT_HINT, format_input(task.start_at if task else None))
        self._end = self._input(INPUT_HINT, format_input(task.end_at if task else None))
        self._error = make_label("")

        self._popup = Popup(
            title=heading,
            content=self._build(),
            size_hint=(None, None),
            size=(dp(480), dp(560)),
            auto_dismiss=False,
        )

    def open(self):
        self._popup.open()

    def _build(self) -> BoxLayout:
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))
        content.add_widget(make_label("Title"))
        content.add_widget(self._title)
        content.add_widget(make_label("Description"))
        content.add_widget(self._description)
        content.add_widget(make_label("Priority"))
        content.add_widget(self._priority)
        content.add_widget(make_label("Starts (optional)"))
        content.add_widget(self._start)
        content.add_widget(make_label("Ends (optional)"))
        content.add_widget(self._end)
        content.add_widget(self._error)

        buttons = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        if self._on_delete is not None:
            self._delete_button = make_button("Delete", self._delete)
            buttons.add_widget(self._delete_button)
        buttons.add_widget(make_button("Cancel", self._popup_dismiss))
        buttons.add_widget(make_button("Save", self._submit))
        content.add_widget(buttons)
        return content

    def _submit(self):
        try:
            data = TaskData(
                title=self._title.text,
                description=self._description.text.strip() or None,
                priority=TaskPriority(self._priority.text),
                start_at=parse_time(self._start.text),
                end_at=parse_time(self._end.text),
            )
        except ValueError as error:
            self._error.text = str(error)
            return

        message = self._on_submit(data)
        if message is None:
            self._popup.dismiss()
        else:
            self._error.text = message

    def _delete(self):
        if not self._delete_armed:
            self._delete_armed = True
            self._delete_button.text = "Sure?"
            return

        message = self._on_delete()
        if message is None:
            self._popup.dismiss()
        else:
            self._error.text = message

    def _popup_dismiss(self):
        self._popup.dismiss()

    @staticmethod
    def _input(hint: str, value: str) -> TextInput:
        return TextInput(
            text=value,
            hint_text=hint,
            multiline=False,
            write_tab=False,
            size_hint_y=None,
            height=dp(40),
        )