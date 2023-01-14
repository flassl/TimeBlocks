from App.Widgets.task import *
from App.Dialogs.task_popup import *
from App.Dialogs.recurrent_dialog import *
from App.Displays.calendar_display import *
from App.Templates.planer_day import *
from kivy.core.window import Window
from kivy.metrics import dp
window_width = dp(360)
window_height = dp(780)
Window.size = (window_width, window_height)
Window.top = 100
##Window.left = -1200
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from datetime import datetime, timedelta
from functools import partial


item_height = 30
start_hour = 5
displayed_hours = 24 - start_hour
font_size = window_width//30

fab_icons = {"task": "text-short", "recurrent": "cached", "calendar": "calendar"}

dragging = False

planer_task_list = []


def load_tasks_to_list(task_type):
    tasks = get_list_tasks()
    recurrent_tasks = get_list_recurrent()
    scroll_view = MDApp.get_running_app().root.ids.navigation_drawer_content.ids.stack_layout
    scroll_view.clear_widgets()

    def append_task_to_list(task):
        new_task = Task(task[0], task[1], task[3])
        new_task.ids.content.text = task[5]
        scroll_view.add_widget(new_task)

    if task_type == 0:
        for task in tasks:
            append_task_to_list(task)
    if task_type == 1:
        for task in recurrent_tasks:
            append_task_to_list(task)


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
        print(planer_tasks_db)
        connection.commit()
        self.active_planer_day.ids.planer_float_layout.clear_widgets()

        def add_to_planer_from_table(table_name):
            cursor.execute(f"SELECT * FROM {table_name} WHERE task_reference = '{row[2]}'")
            connection.commit()
            task_values = cursor.fetchone()
            # if task_values[4] == 1:
            #   load_checked_task(task_values[5], task_values[6], task_values[7], task_values[2])
            # else:
            new_task = Task(task_values[0], task_values[1], task_values[3])
            new_task.ids.content.text = task_values[5]
            new_task.top = task_values[6]
            new_task.pos = [50, new_task.pos[1]]
            self.active_planer_day.ids.planer_float_layout.add_widget(new_task)
            # planer_task_list.append(new_task)

        for row in planer_tasks_db:
            if row[1] == 0:
                add_to_planer_from_table("ToDoTasks")
            if row[1] == 1:
                add_to_planer_from_table("RecurrentTasks")

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

        if pressed_icon == fab_icons.get("task"):
            fab.close_stack()
            self.dialog = TaskPopup()
        elif pressed_icon == fab_icons.get("recurrent"):
            fab.close_stack()
            self.dialog = RecurrentDialog()
        else:
            pass

    def show_task_list(self):
        load_tasks_to_list(0)
        MDApp.get_running_app().root.ids.navigation_drawer.set_state("open")

    def show_recurrent_list(self):
        load_tasks_to_list(1)
        MDApp.get_running_app().root.ids.navigation_drawer.set_state("open")

    def show_calendar(self):
        root = MDApp.get_running_app().root
        screen_manager = root.ids.screen_manager
        if screen_manager and root.ids.calendar_screen:
            screen_manager.on_complete = root.ids.calendar_display.on_shown()
            screen_manager.switch_to(root.ids.calendar_screen, direction="down", duration="1")
            screen_manager.current = "calendar"
            root.ids.calendar_display.ids.swiper.set_current(date.today().month - 1)


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


