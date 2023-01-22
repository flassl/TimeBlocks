from .custom_task_dialog import *
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock


class EventDialogContent(MDBoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save_date_picker, on_cancel=self.on_cancel_date_picker)
        date_dialog.open()

    def on_save_date_picker(self, *args):
        pass

    def on_cancel_date_picker(self, *args):
        pass

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_save_time_picker, on_cancel=self.on_cancel_time_picker)
        time_dialog.open()

    def on_save_time_picker(self):
        pass

    def on_cancel_time_picker(self):
        pass

    def show_dropdown(self):
        pass


class EventDialog(CustomTaskDialog):
    def __init__(self, task_id, input_data, **kwargs):
        self.content = EventDialogContent()
        super().__init__(
            type="custom",
            content_cls=self.content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=MDApp.get_running_app().theme_cls.primary_color,
                    on_release=self.dismiss
                ),
                MDFlatButton(
                    id="button_save",
                    text="SAVE",
                    theme_text_color="Custom",
                    text_color=MDApp.get_running_app().theme_cls.primary_color,
                    on_release=self.add_task

              ),
            ],
            **kwargs)
        self.task_id = task_id
        self.input_data = input_data
        self.open()
        Clock.schedule_once(self.fill_input_from_data, 0.1)

    def fill_input_from_data(self, dt):
        pass

    def add_task(self):
        pass