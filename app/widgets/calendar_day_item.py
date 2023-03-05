from kivy.graphics import Color, RoundedRectangle
from kivymd.uix.widget import Widget
from kivymd.app import MDApp


class CalendarDayItem(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)