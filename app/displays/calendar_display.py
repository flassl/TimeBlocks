from app.widgets.calendar_card import *
from app.utility.utility import *
from app.templates.calendar_month import *
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
import calendar
from kivy.clock import Clock
from functools import partial
from datetime import date, timedelta


class CalendarDisplay(MDFloatLayout):
    screen_manager = None
    active_calendar_screen_name = None
    active_calendar_month = None
    displayed_date_in_month = date(day=1, month=date.today().month, year=date.today().year)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._set_variables, 0.1)
        Clock.schedule_once(partial(self.fill_month, date.today()), 0.1)

    def _set_variables(self, dt):
        self.screen_manager = self.ids.screen_manager
        self.active_calendar_screen_name = self.screen_manager.current
        self.active_calendar_month = self.screen_manager.get_screen(self.active_calendar_screen_name).children[0]

    def fill_month(self, day_in_month, dt):

        days_in_month = calendar.monthrange(day_in_month.year, day_in_month.month)[1]
        first_day_in_month = day_in_month - timedelta(days=day_in_month.day - 1)
        for previous_month_day in range(first_day_in_month.weekday()):
            # toDO: set the respective nr as header for this cards
            calendar_card = CalendarCard(date.today())
            calendar_card.ids.header.text = " "
            self.active_calendar_month.ids.grid.add_widget(calendar_card)
        for day in range(days_in_month):
            calendar_card = CalendarCard(date(day_in_month.year, day_in_month.month, day + 1))
            calendar_card.ids.header.text = str(day + 1)
            self.active_calendar_month.ids.grid.add_widget(calendar_card)
            print(day)

        self.update_header_label()
        pass

    def update_screen_values(self, current_screen):
        self.active_calendar_screen_name = current_screen.name
        self.active_calendar_month = current_screen.children[0]

    def update_header_label(self):
        self.ids.header.text = self.displayed_date_in_month.strftime("%B %Y")

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

    def get_other_screen(self, date_in_month):
        print(self.screen_manager.screens)
        other_screen = None
        for screen in self.screen_manager.screens:
            if self.screen_manager.current != screen.name:
                other_screen = screen
        if other_screen is None:
            screen = MDScreen(name="hola")
            calendar_month = CalendarMonth()
            screen.add_widget(calendar_month)
            other_screen = screen
        self.update_screen_values(other_screen)
        self.displayed_date_in_month = date_in_month
        self.update_header_label()
        if self.displayed_date_in_month != date_in_month:
            self.fill_month(date_in_month, 0)
        return other_screen

    def show_previous(self):
        self.screen_manager.switch_to(
            self.get_other_screen(
                offset_date_by_months(self.displayed_date_in_month, -1)
            ),
            direction="right",
            duration=0.5
        )

    def show_next(self):
        self.screen_manager.switch_to(
            self.get_other_screen(
                offset_date_by_months(self.displayed_date_in_month, 1)
            ),
            direction="left",
            duration=0.5
        )

