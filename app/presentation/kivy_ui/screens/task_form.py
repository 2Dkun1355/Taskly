"""Форма створення та редагування завдання."""

from datetime import date, datetime, timedelta

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from domain.exceptions import ValidationException
from presentation.kivy_ui import theme
from presentation.kivy_ui.widgets import Field, FlatButton, ModalCard, Segmented, Text

_DATE_FORMATS = ("%d.%m.%Y", "%d.%m.%y")
_QUICK_DAYS = (("Сьогодні", 0), ("Завтра", 1), ("Через тиждень", 7))


class DateTimeField(BoxLayout):
    """Дата (ДД.ММ.РРРР) і час (ГГ:ХХ) із кнопками швидкого вибору дня.

    Якщо дату вказано, а час порожній, береться час за замовчуванням.
    Повністю порожнє поле означає, що дати немає.
    """

    def __init__(self, caption, default_time, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(102),
            spacing=dp(6),
            **kwargs,
        )
        self._caption = caption
        self._default_time = default_time

        self._caption_label = Text(
            text=caption,
            font_size="12sp",
            color=theme.MUTED,
            size_hint_y=None,
            height=dp(18),
        )
        self.add_widget(self._caption_label)

        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self._date = Field(hint="ДД.ММ.РРРР")
        self._time = Field(hint=default_time, size_hint_x=None, width=dp(100))
        row.add_widget(self._date)
        row.add_widget(self._time)
        self.add_widget(row)

        quick = BoxLayout(size_hint_y=None, height=dp(28), spacing=dp(6))
        for label, offset in _QUICK_DAYS:
            button = FlatButton(
                text=label,
                font_size="11sp",
                bg_color=theme.FIELD,
                color=theme.MUTED,
                size_hint_x=None,
                width=dp(104),
            )
            button.bind(on_release=lambda *_, days=offset: self._set_day(days))
            quick.add_widget(button)
        quick.add_widget(Widget())
        self.add_widget(quick)

    def set_caption(self, caption):
        """Змінює підпис поля, наприклад «Дедлайн» або «Кінець»."""
        self._caption = caption
        self._caption_label.text = caption

    def set_value(self, value):
        """Записує момент часу в поля, у локальному часі."""
        if value is None:
            self._date.text = ""
            self._time.text = ""
            return
        local = value.astimezone()
        self._date.text = local.strftime("%d.%m.%Y")
        self._time.text = local.strftime("%H:%M")

    def value(self):
        """Повертає datetime з часовим поясом або None, якщо поле порожнє."""
        date_text = self._date.text.strip()
        time_text = self._time.text.strip()

        if not date_text and not time_text:
            return None
        if not date_text:
            raise ValidationException(f"{self._caption}: вкажіть дату")

        day = self._parse_date(date_text)
        moment = self._parse_time(time_text or self._default_time)
        # Наївний час трактується як локальний.
        return datetime.combine(day, moment).astimezone()

    def _set_day(self, offset):
        day = date.today() + timedelta(days=offset)
        self._date.text = day.strftime("%d.%m.%Y")

    def _parse_date(self, text):
        for pattern in _DATE_FORMATS:
            try:
                return datetime.strptime(text, pattern).date()
            except ValueError:
                continue
        raise ValidationException(
            f"{self._caption}: некоректна дата «{text}», потрібен формат ДД.ММ.РРРР"
        )

    def _parse_time(self, text):
        try:
            return datetime.strptime(text, "%H:%M").time()
        except ValueError:
            raise ValidationException(
                f"{self._caption}: некоректний час «{text}», потрібен формат ГГ:ХХ"
            ) from None


class TaskForm(ModalCard):
    """Форма створення (task=None) або редагування завдання.

    on_save отримує: завдання або None, назву, опис, ключ пріоритету
    (LOW, MEDIUM, HIGH), початок і кінець (datetime з поясом або None).
    Якщо on_save кидає виняток, його текст показується у формі.
    """

    def __init__(self, on_save, task=None, **kwargs):
        super().__init__(
            "Редагувати завдання" if task else "Нове завдання",
            width=540,
            height=700,
            auto_dismiss=False,
            **kwargs,
        )
        self._on_save = on_save
        self._task = task

        self._build_fields()
        self._build_footer()

        if task is not None:
            self._fill(task)
        self._update_mode()

    def on_open(self):
        Clock.schedule_once(lambda *_: setattr(self._title.input, "focus", True), 0.1)

    def _build_fields(self):
        grid = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=(0, 0, dp(10), 0),
        )
        grid.bind(minimum_height=grid.setter("height"))

        grid.add_widget(self._caption("Назва *"))
        self._title = Field(hint="Що потрібно зробити?")
        grid.add_widget(self._title)

        grid.add_widget(self._caption("Опис"))
        self._description = Field(
            hint="Подробиці (необов'язково)",
            multiline=True,
            height=76,
        )
        grid.add_widget(self._description)

        grid.add_widget(self._caption("Пріоритет"))
        self._priority = Segmented(
            (("LOW", "Низький"), ("MEDIUM", "Середній"), ("HIGH", "Високий")),
            "LOW",
        )
        grid.add_widget(self._priority)

        grid.add_widget(self._caption("Коли"))
        self._mode = Segmented(
            (("none", "Без дати"), ("deadline", "Дедлайн"), ("interval", "Інтервал")),
            "none",
        )
        grid.add_widget(self._mode)

        # Поля дат додаються в цей контейнер лише коли потрібні, тому
        # невидимі елементи ніколи не перекривають кнопки вище.
        self._start = DateTimeField("Початок", "09:00")
        self._end = DateTimeField("Дедлайн", "18:00")
        self._dates = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        self._dates.bind(minimum_height=self._dates.setter("height"))
        grid.add_widget(self._dates)

        self._mode.bind(value=lambda *_: self._update_mode())

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4),
            scroll_type=["bars", "content"],
        )
        scroll.add_widget(grid)
        self.body.add_widget(scroll)

    def _build_footer(self):
        self._error = Text(
            text="",
            font_size="12sp",
            color=theme.RED,
            shorten=False,
            size_hint_y=None,
            height=dp(34),
        )
        self.body.add_widget(self._error)

        buttons = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel = FlatButton(text="Скасувати", bg_color=theme.SURFACE_ALT)
        save = FlatButton(text="Зберегти", bg_color=theme.ACCENT, bold=True)
        cancel.bind(on_release=lambda *_: self.dismiss())
        save.bind(on_release=self._save)
        buttons.add_widget(cancel)
        buttons.add_widget(save)
        self.body.add_widget(buttons)

    @staticmethod
    def _caption(text):
        return Text(
            text=text,
            font_size="12sp",
            color=theme.MUTED,
            size_hint_y=None,
            height=dp(20),
        )

    def _fill(self, task):
        """Заповнює форму даними завдання при редагуванні."""
        self._title.text = task.title.value
        self._description.text = task.description.value if task.description else ""
        self._priority.value = task.priority.name

        start_at, end_at = task.schedule.start_at, task.schedule.end_at
        if start_at is not None and end_at is not None:
            self._mode.value = "interval"
        elif end_at is not None:
            self._mode.value = "deadline"
        else:
            self._mode.value = "none"

        self._start.set_value(start_at)
        self._end.set_value(end_at)

    def _update_mode(self):
        """Показує лише ті поля дат, які потрібні для обраного режиму."""
        mode = self._mode.value
        self._dates.clear_widgets()

        if mode == "interval":
            self._dates.add_widget(self._start)
        if mode in ("deadline", "interval"):
            self._end.set_caption("Дедлайн" if mode == "deadline" else "Кінець")
            self._dates.add_widget(self._end)

    def _read_schedule(self):
        """Читає початок і кінець із полів залежно від режиму."""
        mode = self._mode.value
        if mode == "none":
            return None, None

        end_at = self._end.value()
        if end_at is None:
            raise ValidationException(
                "Вкажіть дедлайн" if mode == "deadline" else "Вкажіть кінець"
            )
        if mode == "deadline":
            return None, end_at

        start_at = self._start.value()
        if start_at is None:
            raise ValidationException("Вкажіть початок")
        return start_at, end_at

    def _save(self, *_):
        try:
            title = self._title.text.strip()
            if not title:
                raise ValidationException("Вкажіть назву завдання")

            start_at, end_at = self._read_schedule()
            self._on_save(
                self._task,
                title,
                self._description.text.strip(),
                self._priority.value,
                start_at,
                end_at,
            )
        except Exception as error:
            self._error.text = str(error) or "Сталася невідома помилка"
            return

        self.dismiss()
