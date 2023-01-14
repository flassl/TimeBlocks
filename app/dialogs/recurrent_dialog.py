from kivy.graphics.svg import Window
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar

from app.utility.db_utility import *

content = None


class RecurrentDialogContent(MDBoxLayout):
    selected = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_selected(self, selected):
        self.selected = selected
        print(selected.text)


class RecurrentDialog(MDDialog):
    def __init__(self, **kwargs):
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
        self.open()

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
            unit_str = self.content.selected.text
        else:
            # animate buttons to show that they need to be selected
            test_boolean = False

        if test_boolean:
            save_recurrent(1, datetime.today(), 0, 0, text, 0, 1, period, unit_str, [0.2, 0.2, 0.2, 0.2], [0.8, 0.8, 0.8, 0.8])
            print("recurrent task added: " + self.content.ids.text_field_name.text)
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


