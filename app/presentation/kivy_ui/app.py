from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView

from presentation.kivy_ui import theme
from presentation.kivy_ui.screens.task_form import TaskForm
from presentation.kivy_ui.screens.sidebar import Sidebar
from presentation.kivy_ui.screens.task_list import TaskList
from presentation.kivy_ui.services.task_service import (
    ARCHIVE_SECTION,
    SECTION_ALL,
    SECTION_ARCHIVE,
    SECTION_INBOX,
    SECTION_OVERDUE,
    SECTION_TODAY,
    SECTION_UPCOMING,
    SECTIONS,
    TaskService,
)
from presentation.kivy_ui.widgets import (
    Card,
    Field,
    FlatButton,
    Segmented,
    Text,
    confirm,
    show_message,
)

SECTION_TITLES = dict((*SECTIONS, ARCHIVE_SECTION))

SECTION_HINTS = {
    SECTION_ALL: "Усі активні завдання, що чекають виконання.",
    SECTION_TODAY: "Усе, що заплановано на сьогодні.",
    SECTION_OVERDUE: "Активні завдання з минулим дедлайном.",
    SECTION_UPCOMING: "Заплановане на наступні сім днів.",
    SECTION_INBOX: "Завдання без дати. Розплануйте їх, коли буде час.",
    SECTION_ARCHIVE: "Виконані, невиконані та скасовані. Їх можна відновити.",
}

EMPTY_STATES = {
    SECTION_ALL: "Активних завдань немає",
    SECTION_TODAY: "На сьогодні нічого немає",
    SECTION_OVERDUE: "Прострочених завдань немає",
    SECTION_UPCOMING: "Найближчих завдань немає",
    SECTION_INBOX: "Завдань без дати немає",
    SECTION_ARCHIVE: "Архів порожній",
}


class TasklyApp(App):
    """Графічний інтерфейс Taskly."""

    title = "Taskly"

    def __init__(self, mediator, **kwargs):
        super().__init__(**kwargs)
        self._service = TaskService(mediator)
        self._tasks = []
        self._section = SECTION_ALL
        self._search = ""
        self._archive_status = "all"
        self._sidebar = None
        self._title_label = None
        self._hint_label = None
        self._list = None
        self._toast = None
        self._toast_text = None

    # Побудова вікна

    def build(self):
        from kivy.core.window import Window

        Window.clearcolor = theme.BG
        Window.minimum_width = 900
        Window.minimum_height = 600
        Window.size = (1100, 720)

        root = FloatLayout()

        main = BoxLayout(orientation="horizontal")
        main.add_widget(self._build_sidebar())
        main.add_widget(self._build_content())
        root.add_widget(main)
        root.add_widget(self._build_toast())

        Clock.schedule_once(lambda *_: self.refresh(), 0)
        return root

    def _build_sidebar(self):
        self._sidebar = Sidebar(SECTIONS, ARCHIVE_SECTION, self._select_section)
        return self._sidebar

    def _build_content(self):
        content = BoxLayout(
            orientation="vertical",
            padding=(dp(32), dp(26), dp(24), dp(20)),
            spacing=dp(16),
        )

        header = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(12))

        titles = BoxLayout(orientation="vertical")
        self._title_label = Text(font_size="26sp", bold=True,
                                 size_hint_y=None, height=dp(34))
        self._hint_label = Text(font_size="13sp", color=theme.MUTED,
                                size_hint_y=None, height=dp(20))
        titles.add_widget(self._title_label)
        titles.add_widget(self._hint_label)
        header.add_widget(titles)

        add_button = FlatButton(
            text="+  Нове завдання",
            bg_color=theme.ACCENT,
            bold=True,
            size_hint=(None, None),
            size=(dp(180), dp(44)),
            pos_hint={"center_y": 0.5},
        )
        add_button.bind(on_release=lambda *_: self._open_form())
        header.add_widget(add_button)
        content.add_widget(header)

        search = Field(hint="Пошук за назвою…")
        search.input.bind(text=self._on_search)
        content.add_widget(search)

        self._archive_filters = Segmented(
            (("all", "Усі"), ("completed", "Виконані"),
             ("not_completed", "Не виконані"), ("cancelled", "Скасовані")),
            "all",
        )
        self._archive_filters.height = 0
        self._archive_filters.opacity = 0
        self._archive_filters.disabled = True
        self._archive_filters.bind(value=self._on_archive_filter)
        content.add_widget(self._archive_filters)

        self._list = TaskList(
            state_of=self._service.state_of,
            on_edit=self._open_form,
            on_delete=self._confirm_delete,
            on_action=self._run_action,
        )

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(5),
            scroll_type=["bars", "content"],
        )
        scroll.add_widget(self._list)
        content.add_widget(scroll)
        return content

    def _build_toast(self):
        self._toast = Card(
            bg_color=theme.SURFACE_ALT,
            size_hint=(None, None),
            size=(dp(360), dp(46)),
            pos_hint={"center_x": 0.5, "y": 0.04},
            padding=(dp(16), 0),
            opacity=0,
        )
        self._toast_text = Text(font_size="13sp", halign="center")
        self._toast.add_widget(self._toast_text)
        return self._toast

    def _show_toast(self, message):
        """Коротке повідомлення внизу вікна, що саме зникає."""
        self._toast_text.text = message
        Animation.cancel_all(self._toast)
        self._toast.opacity = 0
        animation = (
            Animation(opacity=1, d=0.15)
            + Animation(opacity=1, d=2.0)
            + Animation(opacity=0, d=0.4)
        )
        animation.start(self._toast)

    # Оновлення вмісту

    def refresh(self):
        """Перезавантажує завдання та перемальовує екран."""
        try:
            self._tasks = self._service.load_tasks()
        except Exception as error:
            show_message("Не вдалося завантажити завдання", str(error) or "Невідома помилка")
            return
        self._render()

    def _render(self):
        counts = {
            key: 0 if key == SECTION_ARCHIVE else self._service.count(self._tasks, key)
            for key, _ in (*SECTIONS, ARCHIVE_SECTION)
        }
        self._sidebar.update(self._section, counts)

        self._title_label.text = SECTION_TITLES[self._section]
        self._hint_label.text = SECTION_HINTS[self._section]
        is_archive = self._section == SECTION_ARCHIVE
        self._archive_filters.height = dp(40) if is_archive else 0
        self._archive_filters.opacity = 1 if is_archive else 0
        self._archive_filters.disabled = not is_archive

        tasks = self._service.select(
            self._tasks,
            self._section,
            self._search,
            self._archive_status if is_archive else "all",
        )

        self._list.show(tasks, EMPTY_STATES[self._section], self._search)

    def _select_section(self, section):
        self._section = section
        self._render()

    def _on_search(self, _, value):
        self._search = value
        self._render()

    def _on_archive_filter(self, _, value):
        self._archive_status = value
        self._render()

    # Дії

    def _open_form(self, task=None):
        TaskForm(on_save=self._save_task, task=task).open()

    def _save_task(self, task, title, description, priority, start_at, end_at):
        """Зберігає завдання. Винятки обробляє форма й показує їх користувачу."""
        if task is None:
            self._service.create_task(title, description, priority, start_at, end_at)
            message = "Завдання створено"
        else:
            self._service.edit_task(task, title, description, priority, start_at, end_at)
            message = "Зміни збережено"

        self.refresh()
        self._show_toast(message)

    def _run_action(self, task, action, message):
        if action == "cancel":
            self._confirm_cancel(task)
            return
        actions = {
            "complete": self._service.complete,
            "not_completed": self._service.mark_not_completed,
            "restart": self._service.restart,
        }
        self._run(actions[action], task, message)

    def _confirm_cancel(self, task):
        confirm(
            "Скасувати завдання?",
            f"«{task.title.value}» потрапить в архів. Його можна буде відновити.",
            "Скасувати завдання",
            lambda: self._run(self._service.cancel, task, "Завдання скасовано"),
            danger=True,
        )

    def _confirm_delete(self, task):
        confirm(
            "Видалити завдання?",
            f"«{task.title.value}» буде видалено назавжди. Цю дію не можна скасувати.",
            "Видалити",
            lambda: self._run(self._service.delete, task, "Завдання видалено"),
            danger=True,
        )

    def _run(self, action, task, message):
        """Виконує дію над завданням, оновлює екран і показує повідомлення."""
        try:
            action(task)
        except Exception as error:
            show_message("Не вдалося виконати дію", str(error) or "Невідома помилка")
            return

        self.refresh()
        self._show_toast(message)
