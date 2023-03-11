from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from app.utility.db_utility import *
from app.utility.utility import *
from .custom_task_dialog import *


class TaskPopup(CustomTaskDialog):
    def __init__(self, task_id, input_data, **kwargs):
        super(TaskPopup, self).__init__(radius=[10, 10, 10, 10], **kwargs)
        Clock.schedule_once(self._set_focus, 0.3)
        self.task_id = task_id
        self.input_data = input_data
        self.open()
        Clock.schedule_once(self.fill_input_from_data, 0.1)

    def fill_input_from_data(self, dt):
        if self.task_id != -1:
            print(self.input_data[0])
            self.ids.task_text_input.text = self.input_data[0]

    def add_task(self):
        text_input_field = self.ids.task_text_input
        if got_filled(text_input_field):
            if self.task_id == -1:
                print("task added: " + text_input_field.text)
                save_task(0, datetime.now(), 0, 0, text_input_field.text, 0, 1)
            else:
                print("task updated: " + text_input_field.text)
                update_task(self.task_id, datetime.now(), text_input_field.text, self.input_data[1])
                planner_display = MDApp.get_running_app().root.ids.planer_display
                planner_display.show_tasks(planner_display.displayed_date, 0)
            super(TaskPopup, self).update_drawer(0)
            self.dismiss()


    def _set_focus(self, dt):
        self.ids.task_text_input.focused = True