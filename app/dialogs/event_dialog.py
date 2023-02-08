from kivy.animation import Animation
from app.utility.utility import *
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

from .custom_task_dialog import *
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelLabel
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock



class DropDownContent(MDBoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EventDialogContent(MDBoxLayout):
    time_dialog = None
    date_dialog = None
    drop_down_box = None
    drop_down_box_base_top = None
    repeat_button = None
    repeat_button_pos = None
    repeating_showing = False
    weekday_toggleable = False
    hour = None
    minute = None
    day = None
    month = None
    year = None

    def __init__(self, dialog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog = dialog
        Clock.schedule_once(self.set_values, 0.3)

    def set_values(self, dt):
        self.drop_down_box = self.ids.drop_down_box
        self.repeat_button = self.ids.repeat_button
        self.repeat_button_pos = self.repeat_button.pos

        for button in self.drop_down_box.children:
            button.disabled = True
        widget = Widget()
        with widget.canvas:
            Color(0.12156862745098039, 0.12156862745098039, 0.12156862745098039, 1)
            widget.bg_rect = Rectangle(pos=(self.pos[0] -2, self.repeat_button.pos[1]-25), size=(self.size[0] + 10, 60))
        self.ids.float_layout.add_widget(widget)
        self.repeat_button.parent.remove_widget(self.ids.repeat_button)
        self.ids.float_layout.add_widget(self.repeat_button)
        self.repeat_button.pos = self.repeat_button_pos
        self.drop_down_box_base_top = self.repeat_button.top - 25
        #self.drop_down_box.top = self.drop_down_box_base_top - 20
        self.drop_down_box.pos = self.repeat_button_pos
        self.drop_down_box.pos_hint = {"center_x": .5}

    def fill_values(self, text, hour, minute, day, month, year):
        self.ids.text_field_name.text = text
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month
        self.year = year
        self.update_time_display()
        self.update_date_display()

    def show_date_picker(self):
        self.date_dialog = MDDatePicker()
        self.date_dialog.bind(on_save=self.on_save_date_picker, on_cancel=self.on_cancel_date_picker)
        self.date_dialog.open()

    def on_save_date_picker(self, *args):
        self.day = self.date_dialog.day
        self.month = self.date_dialog.month
        self.year = self.date_dialog.year
        self.update_date_display()

    def update_date_display(self):
        self.ids.date_label.text = str(self.day) + "/" + "%02d" % (self.month) + "/" + str(self.year)[2:4]

    def on_cancel_date_picker(self, *args):
        pass

    def show_time_picker(self):
        self.time_dialog = MDTimePicker(
            primary_color="black",
            accent_color="gray",
            text_button_color="pink",
            line_color="pink",
            input_field_text_color="pink"
        )
        self.time_dialog.bind(on_save=self.on_save_time_picker,
                              on_cancel=self.on_cancel_time_picker,
                              )
        self.time_dialog.open()

    def on_save_time_picker(self, *args):
        self.hour = self.time_dialog.hour
        self.minute = self.time_dialog.minute
        self.update_time_display()

    def update_time_display(self):
        self.ids.time_label.text = str(self.hour) + ":" + str("%02d" % (int(self.minute),))

    def on_cancel_time_picker(self, *args):
        pass

    def toggle_dropdown(self):
        if self.repeating_showing:
            animation = Animation(top=self.drop_down_box_base_top, t='in_cubic', duration=0.5)
            animation.start(self.drop_down_box)
            self.repeating_showing = False
            self.weekday_toggleable = False
            for button in self.drop_down_box.children:
                button.disabled = True
        else:
            animation = Animation(top=self.drop_down_box_base_top - 50, t='out_cubic', duration=0.5)
            animation.start(self.drop_down_box)
            self.repeating_showing = True
            self.weekday_toggleable = True
            for button in self.drop_down_box.children:
                button.disabled = False

    def toggle_weekday(self, day_index):
        if self.weekday_toggleable:
            print(day_index)

    def on_save_task(self, dt):
        event_date = date(day=self.day, month=self.month, year=self.year)
        event_time = time(hour=int(self.hour), minute=int(self.minute))
        event_timestamp = datetime.combine(event_date, event_time).timestamp()
        if self.dialog.task_id == -1:
            save_event(event_timestamp, self.ids.text_field_name.text, calculte_top_from_time(event_time), 1, [0.2, 0.2, 0.2, 0.2], [0.8, 0.8, 0.8, 0.8])
            save_planer(2, cursor.lastrowid, event_timestamp)
            print("saved event: " + self.ids.text_field_name.text)
            pass
        else:
            update_event(self.dialog.task_id, event_timestamp, self.ids.text_field_name.text, calculte_top_from_time(event_time), 1, [0.2, 0.2, 0.2, 0.2], [0.8, 0.8, 0.8, 0.8])
            update_planer(2, self.dialog.task_id, event_timestamp)
            print("updated event: " + self.ids.text_field_name.text)
            pass
        planner_display = MDApp.get_running_app().root.ids.planer_display
        planner_display.show_tasks(planner_display.displayed_date, 0)
        self.dialog.dismiss()
        pass


class EventDialog(CustomTaskDialog):
    def __init__(self, task_widget, **kwargs):
        self.content = EventDialogContent(self)
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
                    on_release=self.content.on_save_task
              ),
            ],
            **kwargs)
        self.open()
        if task_widget != None:
            self.task = task_widget
            self.task_id = task_widget.task_id
            self.task_type = task_widget.task_type
            Clock.schedule_once(self.fill_input_from_data, 0.1)
        else:
            self.task_id = -1

    def fill_input_from_data(self, dt):
        task = get_task(self.task_id, self.task_type)
        task_date = datetime.fromtimestamp(int(task[2]))
        hour = task_date.hour
        minute = task_date.minute
        day = task_date.day
        month = task_date.month
        year = task_date.year
        self.content.fill_values(task[4], hour, minute, day, month, year)
        pass
