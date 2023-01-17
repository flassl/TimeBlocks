from kivymd.uix.boxlayout import MDBoxLayout
from app.dialogs.task_popup import *
from app.dialogs.recurrent_dialog import *
from app.utility.utility import *
from app.widgets.task import *


class NavigationDrawerContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super(NavigationDrawerContent, self).__init__(**kwargs)
        self.dialog = None
        self.display_task_type = None

    def add_task(self):
        print(self.display_task_type)

        if self.display_task_type == 0:
            self.dialog = TaskPopup(-1, [])

        if self.display_task_type == 1:
            self.dialog = RecurrentDialog(-1, [])


    def load_tasks_to_list(self, task_type):
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
