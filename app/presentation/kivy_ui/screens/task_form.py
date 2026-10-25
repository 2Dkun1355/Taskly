from datetime import datetime, timedelta

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from domain.exceptions import ValidationException
from presentation.kivy_ui import theme
from presentation.kivy_ui.widgets import ChoiceBar, LabelText, Modal, ScheduleField, SearchField, UiButton


class TaskForm(Modal):
    def __init__(self, on_save, task=None, **kwargs):
        super().__init__("Редагування завдання" if task else "Нове завдання", size=(dp(560), dp(650)), **kwargs)
        self._on_save = on_save
        self._task = task
        self._build()

    def _field(self, hint, value="", multiline=False):
        return SearchField(
            hint_text=hint,
            text=value,
            multiline=multiline,
            size_hint_y=None,
            height=dp(82 if multiline else 42),
        )

    @staticmethod
    def _label(text):
        return LabelText(
            text=text,
            color=theme.MUTED,
            font_size="12sp",
            size_hint_y=None,
            height=dp(18),
        )

    def _build(self):
        self._title = self._field("Назва завдання", self._task.title.value if self._task else "")
        self._description = self._field("Опис (необов'язково)", self._task.description.value if self._task and self._task.description else "", True)
        self._priority = ChoiceBar((("LOW", "Низький"), ("MEDIUM", "Середній"), ("HIGH", "Високий")), self._task.priority.name if self._task else "LOW")
        self._schedule_mode = ChoiceBar(
            (("NONE", "Без дати"), ("DEADLINE", "Кінцевий термін"), ("INTERVAL", "Інтервал")),
            self._initial_schedule_mode(),
            self._schedule_changed,
        )
        self._start = self._schedule_field("Початок", self._task.schedule.start_at if self._task else None)
        self._end = self._schedule_field("Кінець", self._task.schedule.end_at if self._task else None)

        self.body.add_widget(self._label("Назва"))
        self.body.add_widget(self._title)
        self.body.add_widget(self._label("Опис"))
        self.body.add_widget(self._description)
        self.body.add_widget(self._label("Пріоритет"))
        self.body.add_widget(self._priority)
        self.body.add_widget(self._label("Розклад"))
        self.body.add_widget(self._schedule_mode)
        self._schedule_fields = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        schedule = self._schedule_fields
        schedule.add_widget(self._start)
        schedule.add_widget(self._end)
        self.body.add_widget(schedule)
        self._schedule_changed(self._schedule_mode.value)

        self._error = LabelText(text="", color=theme.RED, font_size="12sp", size_hint_y=None, height=dp(28))
        self.body.add_widget(self._error)
        save = UiButton(text="Зберегти", background=theme.GREEN)
        cancel = UiButton(text="Скасувати")
        save.bind(on_release=self._save)
        cancel.bind(on_release=lambda *_: self.dismiss())
        self.footer.add_widget(save)
        self.footer.add_widget(cancel)

    def _initial_schedule_mode(self):
        if not self._task:
            return "NONE"
        if self._task.schedule.start_at is not None:
            return "INTERVAL"
        if self._task.schedule.end_at is not None:
            return "DEADLINE"
        return "NONE"

    def _schedule_changed(self, mode):
        now = datetime.now().astimezone().replace(second=0, microsecond=0)
        if mode == "NONE":
            self._set_schedule_value(self._start, None)
            self._set_schedule_value(self._end, None)
            active = ()
        elif mode == "DEADLINE":
            self._set_schedule_value(self._start, None)
            if not self._end.text.strip():
                self._set_schedule_value(self._end, now + timedelta(hours=1))
            active = (self._end,)
        else:
            if not self._start.text.strip():
                self._set_schedule_value(self._start, now)
            if not self._end.text.strip():
                self._set_schedule_value(self._end, now + timedelta(hours=1))
            active = (self._start, self._end)
        for row in (self._start, self._end):
            enabled = row in active
            row.height = dp(42)
            row.opacity = 1
            row.disabled = not enabled
            row.set_enabled(enabled)

    def _schedule_field(self, label, value):
        return ScheduleField(label, value)

    @staticmethod
    def _parse_schedule(row, label):
        value = row.text.strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, "%d.%m.%Y %H:%M").astimezone()
        except ValueError as error:
            raise ValidationException(f"{label}: формат дд.мм.рррр гг:хх") from error

    @staticmethod
    def _set_schedule_value(row, value):
        row.text = value.strftime("%d.%m.%Y %H:%M") if value else ""

    def _save(self, *_):
        try:
            title = self._title.text.strip()
            if not title:
                raise ValidationException("Вкажіть назву завдання")
            start_at = self._parse_schedule(self._start, "Початок")
            end_at = self._parse_schedule(self._end, "Кінець")
            self._on_save(self._task, title, self._description.text.strip(), self._priority.value, start_at, end_at)
        except (ValidationException, ValueError, OSError) as error:
            self._error.text = str(error)
            return
        self.dismiss()
