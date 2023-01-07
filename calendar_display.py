from kivymd.uix.boxlayout import MDBoxLayout
from calendar_card import *
from calendar_month import *
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import MDApp
import calendar
from kivy.clock import Clock
from functools import partial
from datetime import date


class CalendarDisplay(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(partial(self.fill_calendar, date.today()), 0.1)

    def fill_calendar(self, day_in_month, dt):

        def fill_month(calendar_month):
            days_in_month = calendar.monthrange(day_in_month.year, month)[1]
            for day in range(days_in_month):
                days_date =date(day_in_month.year, day_in_month.month, day + 1)
                calendar_card = CalendarCard()
                calendar_card.ids.header.text = str(day + 1)
                calendar_month.ids.grid.add_widget(calendar_card)

        def inflate_month(month):
            calendar_month = CalendarMonth()
            if month == day_in_month.month:
                fill_month(calendar_month)
            self.ids.swiper.add_widget(calendar_month)

        self.ids.header.text = day_in_month.strftime("%B") + "   " + str(day_in_month.year)
        for month in range(1, 12):
            inflate_month(month)

    def on_shown(self):
        # animate the icon button popping out from the right
        pass

    def show_planer(self):
        root = MDApp.get_running_app().root
        screen_manager = root.ids.screen_manager
        screen_manager.switch_to(root.ids.planer_display_screen, direction="up", duration=1)
