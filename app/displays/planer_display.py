from main import *
from app.widgets.time_wall import *


class PlanerDisplay(MDFloatLayout):
    displayed_date = datetime.now().date()

    screen_manager = None
    active_planer_screen_name = None
    active_planer_day = None
    time_wall = None

    def __init__(self, **kwargs):
        super(PlanerDisplay, self).__init__(**kwargs)
        self.dialog = None
        Clock.schedule_once(self._set_variables, 0.1)
        Clock.schedule_once(self._add_labels, 0.1)
        Clock.schedule_once(partial(self.show_tasks, date.today()), 0.1)
        Clock.schedule_interval(self.update_time_wall, 60)

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
        date_start_timestamp = datetime.combine(planer_date, time(0, 0, 0)).timestamp()
        date_end = datetime.combine(planer_date, time(0, 0, 0)) + timedelta(hours=23, minutes=59, seconds=59)
        date_end_timestamp = date_end.timestamp()
        cursor.execute(f"SELECT * FROM PlanerTasks WHERE planed_date_timestamp BETWEEN '{date_start_timestamp}' AND "
                       f"'{date_end_timestamp}'")
        planer_tasks_db = cursor.fetchall()
        connection.commit()
        self.active_planer_day.ids.planer_float_layout.clear_widgets()

        def add_to_planer_from_table(table_name):
            cursor.execute(f"SELECT * FROM {table_name} WHERE task_reference = '{row[2]}'")
            connection.commit()
            task_values = cursor.fetchone()
            # if task_values[4] == 1:
            #   load_checked_task(task_values[5], task_values[6], task_values[7], task_values[2])
            # else:
            event_data_index_displacement = 0
            if row[1] == 2:
                event_data_index_displacement = - 1
            new_task = Task(task_values[0], task_values[1], 1, task_values[4 + event_data_index_displacement])
            height = task_values[7 + event_data_index_displacement] * 30
            new_task.size = (new_task.size[0], height)
            new_task.ids.content.text = task_values[5 + event_data_index_displacement]
            new_task.top = task_values[6 + event_data_index_displacement]
            new_task.pos = [50, new_task.pos[1]]
            self.active_planer_day.ids.planer_float_layout.add_widget(new_task)
            # planer_task_list.append(new_task)

        for row in planer_tasks_db:
            if row[1] == 0:
                add_to_planer_from_table("ToDoTasks")
            if row[1] == 1:
                add_to_planer_from_table("RecurrentTasks")
            if row[1] == 2:
                add_to_planer_from_table("EventTasks")

        if planer_date == date.today():
            self.create_time_wall()
            Clock.schedule_once(self.smooth_scroll_to_time, 0.8)

    def create_time_wall(self):
        if self.displayed_date == date.today():
            if self.time_wall and self.time_wall.parent:
                self.time_wall.parent.remove_widget(self.time_wall)
            self.time_wall = TimeWall()
            self.active_planer_day.ids.planer_float_layout.add_widget(self.time_wall)
            self.update_time_wall(0)

    def smooth_scroll_to_time(self, dt):
        current_time = datetime.now()
        current_hour = current_time.hour - 5
        current_minute = current_time.minute
        day_progress = 1 - ((current_hour * 4 + current_minute / 15) / (displayed_hours * 4))
        scroll_animation = Animation(scroll_y=day_progress, duration=0.8, transition="out_back")
        scroll_animation.start(self.active_planer_day)

    def update_time_wall(self, dt):
        if self.time_wall:
            current_time = datetime.now()
            self.time_wall.pos[1] = calculate_true_top_from_time(current_time)

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
            self.dialog = TaskPopup(-1, [])
        elif pressed_icon == fab_icons.get("recurrent"):
            fab.close_stack()
            self.dialog = RecurrentDialog(-1, [])

        elif pressed_icon == fab_icons.get("event"):
            fab.close_stack()
            self.dialog = EventDialog(None)

    def show_task_list(self):
        load_tasks_to_list(0)
        navigation_drawer = MDApp.get_running_app().root.ids.navigation_drawer
        navigation_drawer_content = MDApp.get_running_app().root.ids.navigation_drawer_content
        deactivate_passed_tasks()
        navigation_drawer_content.load_tasks_to_list(0)
        navigation_drawer.set_state("open")
        navigation_drawer_content.display_task_type = 0
        navigation_drawer_content.ids.drawer_title.text = "To Do:"

    def show_recurrent_list(self):
        load_tasks_to_list(1)
        navigation_drawer = MDApp.get_running_app().root.ids.navigation_drawer
        navigation_drawer_content = MDApp.get_running_app().root.ids.navigation_drawer_content
        navigation_drawer_content.load_tasks_to_list(1)
        self.show_tasks(self.displayed_date, 0)
        navigation_drawer.set_state("open")
        navigation_drawer_content.display_task_type = 1
        navigation_drawer_content.ids.drawer_title.text = "Recurring Tasks:"


    def show_calendar(self):
        root = MDApp.get_running_app().root
        screen_manager = root.ids.screen_manager
        if screen_manager and root.ids.calendar_screen:
            screen_manager.on_complete = root.ids.calendar_display.on_shown()
            screen_manager.switch_to(root.ids.calendar_screen, direction="down", duration="1")
            screen_manager.current = "calendar"





