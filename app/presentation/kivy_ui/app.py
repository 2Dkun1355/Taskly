from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView

from application.queries.list_tasks import TaskSection
from domain.exceptions import DomainException
from domain.enums import TaskPriority, TaskStatus
from presentation.kivy_ui import theme
from presentation.kivy_ui.screens.sidebar import Sidebar
from presentation.kivy_ui.screens.task_form import TaskForm
from presentation.kivy_ui.screens.task_row import TaskRow
from presentation.kivy_ui.services.task_service import TaskService
from presentation.kivy_ui.services.task_controller import TaskController
from presentation.kivy_ui.formatting import PRIORITY_LABELS, SECTION_LABELS, status_label
from presentation.kivy_ui.widgets import Card, ChoiceBar, LabelText, Modal, SearchField, UiButton, confirm, message

HINTS = {
    TaskSection.ALL_ACTIVE: "Усі активні завдання",
    TaskSection.TODAY: "Початок або кінець сьогодні",
    TaskSection.UPCOMING: "Активні завдання з майбутньою датою",
    TaskSection.ARCHIVE: "Неактивні завдання",
}
EMPTY = {
    TaskSection.ALL_ACTIVE: "Активних завдань немає",
    TaskSection.TODAY: "На сьогодні завдань немає",
    TaskSection.UPCOMING: "Майбутніх завдань немає",
    TaskSection.ARCHIVE: "Архів порожній",
}


class TasklyApp(App):
    title = "Taskly"

    def __init__(self, mediator, **kwargs):
        super().__init__(**kwargs)
        self._service = TaskService(mediator)
        self._controller = TaskController(self._service)

    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = theme.BG
        Window.minimum_width, Window.minimum_height = 900, 600
        Window.size = 1100, 720

        root = FloatLayout()
        main = BoxLayout(orientation="horizontal")
        self._sidebar = Sidebar(
            tuple(TaskSection),
            self._controller.section,
            self._select_section,
        )
        main.add_widget(self._sidebar)
        content = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(12))
        content.add_widget(self._header())
        content.add_widget(self._filters())
        self._tasks = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self._tasks.bind(minimum_height=self._tasks.setter("height"))
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(5))
        scroll.add_widget(self._tasks)
        content.add_widget(scroll)
        main.add_widget(content)
        root.add_widget(main)
        root.add_widget(self._toast())
        Clock.schedule_once(lambda *_: self.refresh(), 0)
        return root

    def _header(self):
        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        title = BoxLayout(orientation="vertical")
        self._title = LabelText(text="Taskly", font_size="24sp", bold=True, size_hint_y=None, height=dp(30))
        self._hint = LabelText(color=theme.MUTED, font_size="12sp", size_hint_y=None, height=dp(18))
        title.add_widget(self._title)
        title.add_widget(self._hint)
        row.add_widget(title)
        self._primary_button = UiButton(background=theme.ACCENT, size_hint=(None, None), size=(dp(150), dp(40)), pos_hint={"center_y": .5})
        self._primary_button.bind(on_release=lambda *_: self._primary_action())
        row.add_widget(self._primary_button)
        return row

    def _filters(self):
        panel = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(40), spacing=dp(6))
        search_row = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        self._search_field = SearchField(hint_text="Пошук за назвою…")
        self._search_field.bind(text=lambda _, value: self._search_changed(value))
        search_row.add_widget(self._search_field)
        filter_button = UiButton(
            text="Фільтри",
            background=theme.PANEL,
            color=theme.TEXT,
            size_hint_x=None,
            width=dp(100),
        )
        filter_button.bind(on_release=lambda *_: self._open_filters())
        search_row.add_widget(filter_button)
        panel.add_widget(search_row)
        return panel

    def _toast(self):
        self._toast_card = Card(size_hint=(None, None), size=(dp(330), dp(42)), pos_hint={"center_x": .5, "y": .03}, padding=dp(12), opacity=0)
        self._toast_label = LabelText(halign="center", font_size="12sp")
        self._toast_card.add_widget(self._toast_label)
        return self._toast_card

    def refresh(self):
        controller = self._controller
        try:
            controller.refresh()
            is_archive = controller.section is TaskSection.ARCHIVE
            self._title.text = SECTION_LABELS[controller.section]
            self._hint.text = HINTS[controller.section]
            self._primary_button.text = "Очистити архів" if is_archive else "+  Нова задача"
            self._show()
        except (DomainException, ValueError, OSError) as error:
            message("Не вдалося завантажити завдання", str(error) or "Невідома помилка")

    def _show(self):
        self._tasks.clear_widgets()
        tasks = self._controller.visible_tasks()
        if not tasks:
            self._tasks.add_widget(LabelText(
                text=EMPTY[self._controller.section],
                halign="center",
                size_hint_y=None,
                height=dp(160),
            ))
            return
        for task in tasks:
            self._tasks.add_widget(TaskRow(task, self._open_form, self._delete, self._action))

    def _select_section(self, section):
        self._controller.select_section(section)
        self._sidebar.update(section)
        self.refresh()

    def _search_changed(self, value):
        self._controller.set_search(value)
        self._show()

    def _priority_changed(self, value):
        self._controller.set_pending_priority(value)

    def _archive_changed(self, value):
        self._controller.set_pending_archive_status(value)

    def _open_form(self, task=None):
        TaskForm(self._save, task).open()

    def _open_filters(self):
        controller = self._controller
        controller.begin_filter_edit()
        is_archive = controller.section is TaskSection.ARCHIVE
        modal = Modal("Фільтри", size=(dp(430), dp(350 if is_archive else 290)))
        modal.body.add_widget(LabelText(text="Пріоритет", color=theme.MUTED, size_hint_y=None, height=dp(22)))
        priority = ChoiceBar(
            (("all", "Усі"), *(tuple((item.name, PRIORITY_LABELS[item]) for item in TaskPriority))),
            controller.pending_priority.name if controller.pending_priority else "all",
            self._priority_changed,
        )
        modal.body.add_widget(priority)
        if is_archive:
            modal.body.add_widget(LabelText(text="Статус", color=theme.MUTED, size_hint_y=None, height=dp(22)))
            archive = ChoiceBar(
                (("all", "Усі"), *(
                    tuple(
                        (item.value, status_label(item))
                        for item in (
                            TaskStatus.COMPLETED,
                            TaskStatus.NOT_COMPLETED,
                            TaskStatus.CANCELLED,
                        )
                    )
                )),
                controller.pending_archive_status.value if controller.pending_archive_status else "all",
                self._archive_changed,
            )
            modal.body.add_widget(archive)
        reset = UiButton(text="Скинути")
        close = UiButton(text="Готово", background=theme.ACCENT)
        reset.bind(on_release=lambda *_: self._reset_filters(modal))
        close.bind(on_release=lambda *_: self._apply_filters(modal))
        modal.footer.add_widget(reset)
        modal.footer.add_widget(close)
        modal.open()

    def _apply_filters(self, modal):
        self._controller.apply_filters()
        modal.dismiss()
        self.refresh()

    def _reset_filters(self, modal):
        self._controller.reset_filters()
        modal.dismiss()
        self.refresh()

    def _primary_action(self):
        if self._controller.section is TaskSection.ARCHIVE:
            confirm(
                "Очистити архів?",
                "Усі архівні завдання буде видалено назавжди.",
                "Очистити",
                self._clear_archive,
                danger=True,
            )
            return
        self._open_form()

    def _clear_archive(self):
        try:
            count = self._service.clear_archive()
        except (DomainException, ValueError, OSError) as error:
            message("Не вдалося очистити архів", str(error) or "Невідома помилка")
            return
        self.refresh()
        self._notify(f"Архів очищено: {count}")

    def _save(self, task, title, description, priority, start, end):
        if task is None:
            self._service.create_task(title, description, priority, start, end)
            text = "Завдання створено"
        else:
            self._service.edit_task(task, title, description, priority, start, end)
            text = "Зміни збережено"
        self.refresh()
        self._notify(text)

    def _action(self, task, action, _message):
        if action == "cancel":
            confirm("Скасувати завдання?", f"«{task.title.value}» потрапить в архів.", "Скасувати", lambda: self._run(self._service.cancel, task))
            return
        actions = {
            "complete": self._service.complete,
            "not_completed": self._service.mark_not_completed,
            "restart": self._service.restart,
        }
        self._run(actions[action], task)

    def _delete(self, task):
        confirm("Видалити завдання?", f"«{task.title.value}» буде видалено назавжди.", "Видалити", lambda: self._run(self._service.delete, task), danger=True)

    def _run(self, action, task):
        try:
            action(task)
        except (DomainException, ValueError, OSError) as error:
            message("Не вдалося виконати дію", str(error) or "Невідома помилка")
            return
        self.refresh()
        self._notify("Зміни збережено")

    def _notify(self, text):
        self._toast_label.text = text
        self._toast_card.opacity = 1
        Animation(opacity=0, d=1.8).start(self._toast_card)