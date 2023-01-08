from kivymd.uix.card import MDCard
from kivymd.app import MDApp


class CalendarCard(MDCard):
    def __init__(self, date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date = date

    def go_to_planer(self):
        root = MDApp.get_running_app().root
        root.ids.calendar_display.show_planer_date(self.date)


