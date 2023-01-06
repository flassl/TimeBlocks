from utility import *
from db_utility import *
from kivy.core.window import Window
from kivy.metrics import dp
window_width = dp(360)
window_height = dp(780)
Window.size = (window_width, window_height)
Window.top = 100
##Window.left = -1200
from kivy.graphics import Ellipse, Color, Line, Rectangle
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard, MDCardSwipe, MDCardSwipeFrontBox, MDCardSwipeLayerBox
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivy.properties import ObjectProperty
from kivy.animation import Animation
from datetime import datetime
from functools import partial


item_height = 30
start_hour = 5
displayed_hours = 24 - start_hour
font_size = window_width//30

dragging = False


def load_tasks_to_list():
    tasks = get_list_tasks()
    scroll_view = MDApp.get_running_app().root.ids.navigation_drawer_content.ids.stack_layout
    scroll_view.clear_widgets()
    for task in tasks:
        new_task = Task()
        new_task.ids.content.text = task[5]
        scroll_view.add_widget(new_task)


class TimeBlocks(MDScreen):
    def __init__(self, **kwargs):
        super(TimeBlocks, self).__init__(**kwargs)


class PlanerDisplay(MDFloatLayout):
    displayed_date = datetime.now().date()

    def __init__(self, **kwargs):
        super(PlanerDisplay, self).__init__(**kwargs)
        self.dialog = None
        Clock.schedule_once(self._add_labels, 0.1)

    def _add_labels(self, dt):
        time_display_font_size = font_size * 0.8
        half_space_widget = MDLabel(text="    ",
                                  size_hint_y=None, font_size=time_display_font_size, height=item_height / 2)
        self.ids.time_display.add_widget(half_space_widget)
        for h in range(0, displayed_hours):
            hour = start_hour + h
            string_hour = "{:02d}".format(hour)
            for m in range(0, 4):
                minute = m * 15
                string_minute = "{:02d}".format(minute)
#
                if m == 0:
                    label = MDLabel(text=string_hour + ":" + string_minute,
                                  size_hint_y=None, font_size=time_display_font_size, height=item_height)
                elif m == 2:
                    label = MDLabel(text="    :" + string_minute,
                                  size_hint_y=None, font_size=time_display_font_size * 0.8, height=item_height)
                else:
                    label = MDLabel(text="     ",
                                  size_hint_y=None, font_size=time_display_font_size, height=item_height)
#
                self.ids.time_display.add_widget(label)
        half_space_widget_end = MDLabel(text=" ",
                                      size_hint_y=None, font_size=time_display_font_size, height=item_height / 2)
        self.width = 30
        self.ids.time_display.add_widget(half_space_widget_end)
        self.ids.time_display.height = displayed_hours * 4 * item_height + item_height / 2
        self.ids.date_text.text = self.displayed_date.strftime("%A, %d/%m/%Y")

    def fab_callback(self, instance):
        pressed_icon = instance.icon
        fab = self.ids.fab

        if pressed_icon == "text-short":
            print("you pressed " + instance.icon)
            fab.close_stack()
            self.dialog = TaskPopup()
            self.dialog.open()
        elif pressed_icon == "calendar-clock":
            print("you pressed " + instance.icon)
        else:
            print("you pressed " + instance.icon)

    def show_task_list(self):
        load_tasks_to_list()
        MDApp.get_running_app().root.ids.navigation_drawer.set_state("open")


class TaskPopup(MDDialog):
    def __init__(self, **kwargs):
        super(TaskPopup, self).__init__(radius=[10, 10, 10, 10], **kwargs)
        Clock.schedule_once(self._set_focus, 0.3)

    def add_task(self):
        print("task added: " + self.ids.task_text_input.text)
        self.dismiss()
        save_task(0, datetime.now(), 0, 0, self.ids.task_text_input.text, 0, 1)

    def _set_focus(self, dt):
        self.ids.task_text_input.focused = True


class Task(MDCard):
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)

    timer = None
    movement_tick = None
    current_touch_position = None
    positioning_hint = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.timer = Clock.schedule_once(self.on_long_press, 0.3)
        self.current_touch_position = touch.pos
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        global dragging
        dragging = False

        if self.timer:
            self.timer.cancel()
        if self.movement_tick:
            self.movement_tick.cancel()

        return super().on_touch_up(touch)

    def on_touch_move(self, touch, *args):
        self.current_touch_position = touch.pos
        return super().on_touch_move(touch, *args)

    def on_long_press(self, dt):
        global dragging
        dragging = True
        self.movement_tick = Clock.schedule_interval(self.follow_touch, 0.01)
        root = MDApp.get_running_app().root
        root_parent = root.ids.planer_display
        root.ids.navigation_drawer.set_state("close")

        def recreate_in_root():
            temp = self
            self.parent.remove_widget(self)
            root_parent.add_widget(temp)
            self.elevation = 4
            self.follow_touch(0)

        def show_positioning_hint():
            self.positioning_hint = PositioningHint()
            self.positioning_hint.height = self.height
            root.ids.planer_display.ids.planer_float_layout.add_widget(self.positioning_hint)

        recreate_in_root()
        show_positioning_hint()

    def follow_touch(self, dt):
        if self.current_touch_position:
            touch_pos = [self.current_touch_position[0], self.current_touch_position[1] - self.height / 2]
            self.pos = touch_pos
            if self.positioning_hint:
                self.positioning_hint.pos =\
                    [50, calculate_snapping_point(MDApp.get_running_app().root.ids.planer_display.ids.planer_scroll_view,
                                                  self.current_touch_position[1] - self.height / 2)]
        pass


class PositioningHint(Widget):
    def __init__(self, **kwargs):
        super(PositioningHint, self).__init__(size_hint=(1, None), **kwargs)
        with self.canvas:
            Color(.3, .3, .3, .3)
            self.rectangle = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rectangle)
        self.bind(size=self.update_rectangle)

    def update_rectangle(self, *args):
        self.rectangle.pos = self.pos
        self.rectangle.size = self.size


class NavigationDrawerContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super(NavigationDrawerContent, self).__init__(**kwargs)


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


