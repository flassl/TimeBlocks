from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from app.utility.db_utility import *
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
        if self.task_id == -1:
            print("task added: " + self.ids.task_text_input.text)
            save_task(0, datetime.now(), 0, 0, self.ids.task_text_input.text, 0, 1)
        else:
            print("task updated: " + self.ids.task_text_input.text)
            update_task(self.task_id, datetime.now(), self.ids.task_text_input.text, self.input_data[1], 1)
        super(TaskPopup, self).update_drawer(0)
        self.dismiss()


    def _set_focus(self, dt):
        self.ids.task_text_input.focused = True