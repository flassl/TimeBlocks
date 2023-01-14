from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from app.utility.db_utility import *


class TaskPopup(MDDialog):
    def __init__(self, **kwargs):
        super(TaskPopup, self).__init__(radius=[10, 10, 10, 10], **kwargs)
        Clock.schedule_once(self._set_focus, 0.3)
        self.open()

    def add_task(self):
        print("task added: " + self.ids.task_text_input.text)
        self.dismiss()
        save_task(0, datetime.now(), 0, 0, self.ids.task_text_input.text, 0, 1)

    def _set_focus(self, dt):
        self.ids.task_text_input.focused = True