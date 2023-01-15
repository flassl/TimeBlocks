from app.widgets.task import *
from app.dialogs.task_popup import *
from app.dialogs.recurrent_dialog import *
from app.displays.calendar_display import *
from app.templates.planer_day import *
from app.templates.navigation_drawer_content import *
from app.displays.planer_display import *
from kivy.core.window import Window
from kivy.metrics import dp
window_width = dp(360)
window_height = dp(780)
Window.size = (window_width, window_height)
Window.top = 100
##Window.left = -1200
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from datetime import datetime, timedelta, date
from functools import partial


item_height = 30
start_hour = 5
displayed_hours = 24 - start_hour
font_size = window_width//30

fab_icons = {"task": "text-short", "recurrent": "cached", "calendar": "calendar"}


planer_task_list = []


def load_tasks_to_list(task_type):
    tasks = get_list_tasks()
    recurrent_tasks = get_list_recurrent()
    scroll_view = MDApp.get_running_app().root.ids.navigation_drawer_content.ids.stack_layout
    scroll_view.clear_widgets()

    def append_task_to_list(task):
        new_task = Task(task[0], task[1], task[3], task[4])
        new_task.ids.content.text = task[5]
        scroll_view.add_widget(new_task)

    if task_type == 0:
        for task in tasks:
            append_task_to_list(task)
    if task_type == 1:
        for task in recurrent_tasks:
            append_task_to_list(task)


class TimeBlocks(MDScreen):
    def __init__(self, **kwargs):
        super(TimeBlocks, self).__init__(**kwargs)


class TimeBlocksApp (MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Pink"
        return Builder.load_file("TimeBlocksLayout.kv")

    def on_start(self):
        # app = MDApp.get_running_app()
        # Window.bind(size=app.root.on_resize)
        Window.softinput_mode = "below_target"
        Window.release_all_keyboards()


if __name__ == '__main__':
    create_db()
    TimeBlocksApp().run()


