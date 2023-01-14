from App.Widgets.calendar_card import *
from App.Templates.calendar_month import *
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import MDApp
import calendar
from kivy.clock import Clock
from functools import partial
from datetime import date, timedelta


class CalendarDisplay(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(partial(self.fill_calendar, date.today()), 0.1)

    def fill_calendar(self, day_in_month, dt):

        def fill_month(calendar_month):
            days_in_month = calendar.monthrange(day_in_month.year, month)[1]
            first_day_in_month = day_in_month - timedelta(days=day_in_month.day - 1)
            for previous_month_day in range(first_day_in_month.weekday()):
                # toDO: set the respective nr as header for this cards
                calendar_card = CalendarCard(date.today())
                calendar_card.ids.header.text = " "
                calendar_month.ids.grid.add_widget(calendar_card)
            for day in range(days_in_month):
                calendar_card = CalendarCard(date(day_in_month.year, day_in_month.month, day + 1))
                calendar_card.ids.header.text = str(day + 1)
                calendar_month.ids.grid.add_widget(calendar_card)

        def inflate_month(month):
            calendar_month = CalendarMonth()
            if day_in_month.month == month:
                fill_month(calendar_month)
            self.ids.swiper.add_widget(calendar_month)

        self.ids.header.text = day_in_month.strftime("%B") + "   " + str(day_in_month.year)
        for month in range(1, 12):
            inflate_month(month)

    def on_shown(self):
        # animate the icon button popping out from the right
        pass

    def back_to_planer(self):
        root = MDApp.get_running_app().root
        screen_manager = root.ids.screen_manager
        screen_manager.switch_to(root.ids.planer_display_screen, direction="up", duration=1)

    def show_planer_date(self, date):
        root = MDApp.get_running_app().root
        root.ids.planer_display.show_tasks(date, 0)
        self.back_to_planer()
