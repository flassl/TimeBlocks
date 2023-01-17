from kivymd.uix.dialog import MDDialog
from app.utility.db_utility import *
from kivymd.app import MDApp


class CustomTaskDialog(MDDialog):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_drawer(self, task_id):
        navigation_drawer_content = MDApp.get_running_app().root.ids.navigation_drawer_content
        navigation_drawer_content.load_tasks_to_list(task_id)
