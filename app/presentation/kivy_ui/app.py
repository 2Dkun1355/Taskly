from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from presentation.kivy_ui import theme
from presentation.kivy_ui.formatting import (
    PRIORITY_LABELS,
    STATE_LABELS,
    format_schedule,
    today_caption,
)
from presentation.kivy_ui.screens.task_form import TaskForm
from presentation.kivy_ui.services.task_service import (
    ARCHIVE_SECTION,
    SECTION_ALL,
    SECTION_ARCHIVE,
    SECTION_INBOX,
    SECTION_LATER,
    SECTION_TODAY,
    SECTION_TOMORROW,
    SECTIONS,
    TaskService,
)
from presentation.kivy_ui.widgets import (
    Card,
    Chip,
    Field,
    FlatButton,
    IconButton,
    NavItem,
    Text,
    confirm,
    show_message,
)

SECTION_TITLES = dict((*SECTIONS, ARCHIVE_SECTION))

SECTION_HINTS = {
    SECTION_TODAY: "Усе, що заплановано на сьогодні.",
    SECTION_TOMORROW: "Те, що чекає на вас завтра.",
    SECTION_LATER: "Завдання з датою, яка не припадає на сьогодні чи завтра.",
    SECTION_INBOX: "Завдання без дати. Розплануйте їх, коли буде час.",
    SECTION_ALL: "Усі завдання, що чекають виконання.",
    SECTION_ARCHIVE: "Виконані, невиконані та скасовані. Їх можна відновити.",
}

EMPTY_STATES = {
    SECTION_TODAY: "На сьогодні нічого немає",
    SECTION_TOMORROW: "На завтра нічого немає",
    SECTION_LATER: "Завдань на майбутнє немає",
    SECTION_INBOX: "Завдань без дати немає",
    SECTION_ALL: "Активних завдань немає",
    SECTION_ARCHIVE: "Архів порожній",
}


class TasklyApp(App):
    """Графічний інтерфейс Taskly."""

    title = "Taskly"

    def __init__(self, mediator, **kwargs):
        super().__init__(**kwargs)
        self._service = TaskService(mediator)
        self._tasks = []
        self._section = SECTION_TODAY
        self._search = ""
        self._nav_items = {}
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
        sidebar = Card(
            orientation="vertical",
            size_hint_x=None,
            width=dp(240),
            bg_color=theme.SIDEBAR,
            radius=0,
            padding=(dp(16), dp(24), dp(16), dp(18)),
            spacing=dp(6),
        )

        sidebar.add_widget(
            Text(text="Taskly", font_size="28sp", bold=True,
                 size_hint_y=None, height=dp(44))
        )
        sidebar.add_widget(
            Text(text=today_caption(), font_size="12sp", color=theme.MUTED,
                 size_hint_y=None, height=dp(22))
        )
        sidebar.add_widget(Widget(size_hint_y=None, height=dp(18)))

        for key, label in SECTIONS:
            self._add_nav_item(sidebar, key, label)

        # Порожнє місце відсуває архів у самий низ меню.
        sidebar.add_widget(Widget())
        self._add_nav_item(sidebar, *ARCHIVE_SECTION)
        return sidebar

    def _add_nav_item(self, sidebar, key, label):
        item = NavItem(label)
        item.bind(on_release=lambda _, section=key: self._select_section(section))
        self._nav_items[key] = item
        sidebar.add_widget(item)

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

        self._list = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=(0, dp(2), dp(10), dp(10)),
        )
        self._list.bind(minimum_height=self._list.setter("height"))

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
        for key, item in self._nav_items.items():
            item.selected = key == self._section
            # Лічильник показуємо лише для активних розділів, не для архіву.
            count = 0 if key == SECTION_ARCHIVE else self._service.count(self._tasks, key)
            item.set_count(count)

        self._title_label.text = SECTION_TITLES[self._section]
        self._hint_label.text = SECTION_HINTS[self._section]

        tasks = self._service.select(self._tasks, self._section, self._search)

        self._list.clear_widgets()
        if not tasks:
            self._list.add_widget(self._empty_state())
            return

        for task in tasks:
            self._list.add_widget(self._task_card(task))

    def _select_section(self, section):
        self._section = section
        self._render()

    def _on_search(self, _, value):
        self._search = value
        self._render()

    def _empty_state(self):
        box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(220),
            spacing=dp(6),
            padding=dp(24),
        )
        if self._search.strip():
            title, hint = "Нічого не знайдено", "Спробуйте змінити пошуковий запит."
        else:
            title = EMPTY_STATES[self._section]
            hint = "Натисніть «Нове завдання», щоб додати справу."

        box.add_widget(Text(text=title, font_size="18sp", halign="center"))
        box.add_widget(Text(text=hint, font_size="13sp", color=theme.MUTED, halign="center"))
        return box

    # Картка завдання

    def _task_card(self, task):
        state = self._service.state_of(task)
        priority = task.priority.name
        description = (task.description or "").replace("\n", " ")

        card = Card(
            orientation="vertical",
            size_hint_y=None,
            height=dp(144 if description else 120),
            padding=(dp(28), dp(12), dp(16), dp(12)),
            spacing=dp(4),
            accent_color=(
                theme.PRIORITY_COLORS.get(priority, theme.DIM)
                if task.is_planned else theme.DIM
            ),
        )

        # Верхній рядок: назва, стан і піктограми. Олівець є лише в активних
        # завдань, а урна в усіх, зокрема в архівних.
        top = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        top.add_widget(Text(text=task.title.value, font_size="16sp", bold=True))
        top.add_widget(Chip(text=STATE_LABELS[state], tone=theme.STATE_COLORS[state]))
        if task.is_planned:
            top.add_widget(self._icon_button(
                "edit",
                lambda *_, current=task: self._open_form(current),
            ))
        top.add_widget(self._icon_button(
            "delete",
            lambda *_, current=task: self._confirm_delete(current),
            press_tone=theme.RED,
        ))
        card.add_widget(top)

        if description:
            card.add_widget(
                Text(text=description, font_size="12sp", color=theme.MUTED,
                     size_hint_y=None, height=dp(20))
            )

        meta = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(10))
        meta.add_widget(
            Text(text=format_schedule(task.schedule), font_size="12sp", color=theme.MUTED)
        )
        meta.add_widget(
            Text(
                text=f"Пріоритет: {PRIORITY_LABELS.get(priority, priority).lower()}",
                font_size="12sp",
                color=theme.PRIORITY_COLORS.get(priority, theme.MUTED),
                halign="right",
                size_hint_x=None,
                width=dp(170),
            )
        )
        card.add_widget(meta)

        actions = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        actions.add_widget(Widget())

        if task.is_planned:
            actions.add_widget(self._action_button(
                "Скасувати",
                lambda *_, current=task: self._confirm_cancel(current),
                color=theme.RED,
            ))
            actions.add_widget(self._action_button(
                "Не виконано",
                lambda *_, current=task: self._run(
                    self._service.mark_not_completed, current, "Позначено як невиконане"
                ),
                color=theme.ORANGE,
            ))
            actions.add_widget(self._action_button(
                "Виконано",
                lambda *_, current=task: self._run(
                    self._service.complete, current, "Завдання виконано"
                ),
                bg=theme.GREEN,
                color=theme.WHITE,
            ))
        else:
            actions.add_widget(self._action_button(
                "Відновити",
                lambda *_, current=task: self._run(
                    self._service.restart, current, "Завдання повернуто без дати"
                ),
                bg=theme.ACCENT,
                color=theme.WHITE,
            ))

        card.add_widget(actions)
        return card

    @staticmethod
    def _action_button(text, on_release, bg=theme.SURFACE_ALT, color=theme.TEXT, width=104):
        button = FlatButton(
            text=text,
            bg_color=bg,
            color=color,
            font_size="12sp",
            size_hint=(None, None),
            size=(dp(width), dp(34)),
        )
        button.bind(on_release=on_release)
        return button

    @staticmethod
    def _icon_button(icon, on_release, press_tone=theme.TEXT):
        button = IconButton(
            icon=icon,
            press_tone=press_tone,
            size=(dp(30), dp(30)),
            pos_hint={"center_y": 0.5},
        )
        button.bind(on_release=on_release)
        return button

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