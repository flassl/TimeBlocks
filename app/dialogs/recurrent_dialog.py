from kivy.graphics.svg import Window
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from .custom_task_dialog import *
from kivy.clock import Clock
from app.utility.db_utility import *
from .custom_task_dialog import CustomTaskDialog

content = None


class RecurrentDialogContent(MDBoxLayout):
    selected = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_selected(self, selected):
        self.selected = selected.text
        print(selected.text)


class RecurrentDialog(CustomTaskDialog):
    def __init__(self, task_id, input_data, **kwargs):
        self.content = RecurrentDialogContent()
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
        if self.task_id != -1:
            self.content.ids.text_field_name.text = self.input_data[0]
            self.content.ids.text_field_number.text = str(self.input_data[1])
            self.content.selected = self.input_data[2]
            print(self.content.selected)
            if self.content.selected == "Days":
                self.content.ids.days_button.state = "down"

            if self.content.selected == "Hours":
                self.content.ids.hours_button.state = "down"

            if self.content.selected == "Weeks":
                self.content.ids.weeks_button.state = "down"

    def add_task(self, *args):
        text_field_name = self.content.ids.text_field_name
        text_field_number = self.content.ids.text_field_number
        test_boolean = False
        text = None
        period= None
        unit_str = None

        if text_field_name:
            text = text_field_name.text
            test_boolean = True
        else:
            text_field_name.error = True

        if text_field_number:
            period = text_field_number.text
        else:
            text_field_number.error = True
            test_boolean = False

        if self.content.selected:
            unit_str = self.content.selected
        else:
            # animate buttons to show that they need to be selected
            test_boolean = False

        if test_boolean:
            planer_date = MDApp.get_running_app().root.ids.planer_display.displayed_date
            planer_datetime = datetime.combine(planer_date, datetime.now().time())
            print(self.parent)
            if self.task_id == -1:
                save_recurrent(1, planer_datetime, 0, 0, text, 0, 1, period, unit_str, [0.2, 0.2, 0.2, 0.2], [0.8, 0.8, 0.8, 0.8])
                print("recurrent task added: " + self.content.ids.text_field_name.text)

            else:
                update_recurrent(self.task_id, planer_datetime, self.content.ids.text_field_name.text, self.input_data[3], 1, period, unit_str, [0.2, 0.2, 0.2, 0.2], [0.8, 0.8, 0.8, 0.8])
                print("recurrent task edited: " + self.content.ids.text_field_name.text)
            super(RecurrentDialog, self).update_drawer(1)
            self.dismiss()
        else:
            Snackbar(
                text="Please enter required info",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                                    Window.width - (dp(10) * 2)
                            ) / Window.width
            ).open()


