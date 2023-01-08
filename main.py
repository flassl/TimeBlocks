from utility import *
from db_utility import *
from calendar_display import *
from calendar_card import *
from calendar_month import *
from planer_day import *
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
from kivy.uix.screenmanager import FadeTransition
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
from datetime import datetime, timedelta
from functools import partial


item_height = 30
start_hour = 5
displayed_hours = 24 - start_hour
font_size = window_width//30

dragging = False

planer_task_list = []


def load_tasks_to_list():
    tasks = get_list_tasks()
    scroll_view = MDApp.get_running_app().root.ids.navigation_drawer_content.ids.stack_layout
    scroll_view.clear_widgets()
    for task in tasks:
        new_task = Task(task[0], task[3])
        new_task.ids.content.text = task[5]
        scroll_view.add_widget(new_task)


class TimeBlocks(MDScreen):
    def __init__(self, **kwargs):
        super(TimeBlocks, self).__init__(**kwargs)


class PlanerDisplay(MDFloatLayout):
    displayed_date = datetime.now().date()

    screen_manager = None
    active_planer_screen_name = None
    active_planer_day = None

    def __init__(self, **kwargs):
        super(PlanerDisplay, self).__init__(**kwargs)
        self.dialog = None
        Clock.schedule_once(self._set_variables, 0.1)
        Clock.schedule_once(self._add_labels, 0.1)
        Clock.schedule_once(partial(self.show_tasks, date.today()), 0.1)

    def _set_variables(self, dt):
        self.screen_manager = self.ids.screen_manager
        self.active_planer_screen_name = self.screen_manager.current
        self.active_planer_day = self.screen_manager.get_screen(self.active_planer_screen_name).children[0]

    def _add_labels(self, dt):
        time_display_font_size = font_size * 0.8
        half_space_widget = MDLabel(text="    ",
                                  size_hint_y=None, font_size=time_display_font_size, height=item_height / 2)
        self.active_planer_day.ids.time_display.add_widget(half_space_widget)
        for h in range(0, displayed_hours):
            hour = start_hour + h
            string_hour = "{:02d}".format(hour)
            for m in range(0, 4):
                minute = m * 15
                string_minute = "{:02d}".format(minute)
#
                if m == 0:
                    label = MDLabel(text=" " + string_hour + ":" + string_minute,
                                  size_hint_y=None, font_size=time_display_font_size, height=item_height)
                elif m == 2:
                    label = MDLabel(text="    :" + string_minute,
                                  size_hint_y=None, font_size=time_display_font_size * 0.8, height=item_height)
                else:
                    label = MDLabel(text="     ",
                                  size_hint_y=None, font_size=time_display_font_size, height=item_height)
#
                self.active_planer_day.ids.time_display.add_widget(label)
        half_space_widget_end = MDLabel(text=" ", size_hint_y=None, font_size=time_display_font_size,
                                        height=item_height / 2)
        self.width = 30
        self.active_planer_day.ids.time_display.add_widget(half_space_widget_end)
        self.active_planer_day.ids.time_display.height = displayed_hours * 4 * item_height + item_height / 2
        self.ids.date_text.text = self.displayed_date.strftime("%A, %d/%m/%Y")

    def show_tasks(self, planer_date, dt):
        self.displayed_date = planer_date
        self.ids.date_text.text = planer_date.strftime("%A, %d/%m/%Y")
        app = MDApp.get_running_app()
        root = app.root
        date_start_timestamp = datetime.combine(planer_date, time(0, 0, 0)).timestamp()
        date_end = datetime.combine(planer_date, time(0, 0, 0)) + timedelta(hours=23, minutes=59, seconds=59)
        date_end_timestamp = date_end.timestamp()
        cursor.execute(f"SELECT * FROM PlanerTasks WHERE planed_date_timestamp BETWEEN '{date_start_timestamp}' AND "
                       f"'{date_end_timestamp}'")
        planer_tasks_db = cursor.fetchall()
        connection.commit()
        self.active_planer_day.ids.planer_float_layout.clear_widgets()
        for row in planer_tasks_db:
            if row[1] == 0:
                cursor.execute(f"SELECT * FROM ToDoTasks WHERE task_reference = '{row[2]}'")
                connection.commit()
                task_values = cursor.fetchone()
                #if task_values[4] == 1:
                 #   load_checked_task(task_values[5], task_values[6], task_values[7], task_values[2])
                #else:
                new_task = Task(task_values[0], task_values[3])
                new_task.ids.content.text = task_values[5]
                new_task.top = task_values[6]
                new_task.pos = [50, new_task.pos[1]]
                self.active_planer_day.ids.planer_float_layout.add_widget(new_task)
                #planer_task_list.append(new_task

    def update_screen_values(self, current_screen):
        self.active_planer_screen_name = current_screen.name
        self.active_planer_day = current_screen.children[0]

    def fill_screen(self, date):

        print(self.screen_manager.screens)
        screen = MDScreen(name= "hola")
        planer_day = PlanerDay()
        screen.add_widget(planer_day)
        self.update_screen_values(screen)
        self.displayed_date = date
        self._add_labels(0)
        self.show_tasks(self.displayed_date, 0)
        self.screen_manager.add_widget(screen)
        return screen

    def get_other_screen(self, date):
        print(self.screen_manager.screens)
        other_screen = None
        for screen in self.screen_manager.screens:
            if self.screen_manager.current != screen.name:
                other_screen = screen
        if other_screen == None:
            screen = MDScreen(name="hola")
            planer_day = PlanerDay()
            screen.add_widget(planer_day)
            other_screen = screen
        self.update_screen_values(other_screen)
        self.displayed_date = date
        self._add_labels(0)
        self.show_tasks(self.displayed_date, 0)
        return other_screen

    def show_previous(self):
        self.screen_manager.switch_to(self.get_other_screen(self.displayed_date - timedelta(days=1)), direction="right", duration=0.5)

    def show_next(self):
        self.screen_manager.switch_to(self.get_other_screen(self.displayed_date + timedelta(days=1)), direction="left",
                                      duration=0.5)

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

    def show_calendar(self):
        root = MDApp.get_running_app().root
        screen_manager = root.ids.screen_manager
        if screen_manager and root.ids.calendar_screen:
            screen_manager.on_complete = root.ids.calendar_display.on_shown()
            screen_manager.switch_to(root.ids.calendar_screen, direction="down", duration="1")
            screen_manager.current = "calendar"
            root.ids.calendar_display.ids.swiper.set_current(date.today().month - 1)


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
    def __init__(self, id, active, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.task_id = id
        self.active = active

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

        planer_display = MDApp.get_running_app().root.ids.planer_display

        if self.timer:
            self.timer.cancel()
        if self.movement_tick:
            self.movement_tick.cancel()

        def recreate_in_planer():
            temp = self
            self.parent.remove_widget(self)
            planer_display.ids.planer_float_layout.add_widget(temp)
            self.elevation = 0
        if dragging:
            recreate_in_planer()
            self.pos = [50, calculate_snapping_point(MDApp.get_running_app().root.ids.planer_display.ids.planer_scroll_view,
                                                  self.current_touch_position[1] - self.height / 2)]
            if self.active == 0:
                save_planer(0, self.task_id, datetime.now())

            de_activate_to_do(self.task_id, 1, 0, self.top)
            self.active = 1


        dragging = False
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
            MDApp.get_running_app().root.ids.planer_display.ids.planer_float_layout.add_widget(self.positioning_hint)

        recreate_in_root()
        show_positioning_hint()

    def follow_touch(self, dt):
        if self.current_touch_position:
            touch_pos = [self.current_touch_position[0] - self.width / 3, self.current_touch_position[1] - self.height / 2]
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


