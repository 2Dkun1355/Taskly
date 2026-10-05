from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup


def make_label(text, **kwargs):
    kwargs.setdefault("size_hint_y", None)
    kwargs.setdefault("height", dp(30))
    kwargs.setdefault("halign", "left")
    kwargs.setdefault("valign", "middle")
    label = Label(text=text, **kwargs)
    label.bind(size=lambda widget, size: setattr(widget, "text_size", size))
    return label


def make_button(text, on_press, **kwargs):
    kwargs.setdefault("size_hint_y", None)
    kwargs.setdefault("height", dp(40))
    button = Button(text=text, **kwargs)
    button.bind(on_release=lambda *_: on_press())
    return button


def show_error(message):
    content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
    content.add_widget(Label(text=message))
    popup = Popup(title="Error", content=content, size_hint=(None, None), size=(dp(360), dp(180)))
    content.add_widget(make_button("OK", popup.dismiss))
    popup.open()