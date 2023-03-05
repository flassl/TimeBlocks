from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from app.utility.db_utility import get_task_amount_for_date
from app.widgets.calendar_day_item import *


class CalendarCard(MDCard):
    def __init__(self, date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date = date
        self.fill_card_with_items()

    def go_to_planer(self):
        root = MDApp.get_running_app().root
        root.ids.calendar_display.show_planer_date(self.date)

    def fill_card_with_items(self):
        item_count = get_task_amount_for_date(self.date)[0]
        for item_index in range(item_count):
            day_item = CalendarDayItem()
            self.ids.list.add_widget(day_item)
