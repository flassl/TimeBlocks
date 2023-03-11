from app.dialogs.task_popup import *
from app.dialogs.recurrent_dialog import *
from kivy.core.window import Window
from app.utility.db_utility import *
from kivy.animation import Animation
from kivy.utils import rgba
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from app.utility.db_utility import *
from app.utility.utility import *
from kivymd.app import MDApp
from kivy.clock import Clock
from .positioning_hint import *
import math

from ..dialogs.event_dialog import EventDialog


class Task(MDCard):
    def __init__(self, id, task_type, active, done, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.task_id = id
        self.active = active
        self.task_type = task_type
        self.done = done
        if self.done:
            self.check_button = CheckButton()
            self.check_button.icon = "check-circle"

            def update_check_button(dt):
                self.check_button.children[0].color = [0.5, 0.8, 0, 1]
                self.checked = True

            Clock.schedule_once(update_check_button, 0.1)
            self.ids.check_layout.add_widget(self.check_button)
    timer = None
    movement_tick = None
    current_touch_position = None
    positioning_hint = None
    task_menu = None
    options_showing = False
    close_menu_timer = None
    stretching = False
    dragging = False
    fab_is_deleting = False
    deleted = False
    check_button = None
    checked = False
    delete_button = None
    expand_button = None
    edit_button = None

    scroll_handler = None
    scroll_factor = 0

    active_planer_day = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.timer = Clock.schedule_once(self.on_long_press, 0.3)
        self.current_touch_position = touch.pos
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        fab = MDApp.get_running_app().root.ids.planer_display.ids.fab.children[0]

        if self.timer:
            self.timer.cancel()
        if self.movement_tick:
            self.movement_tick.cancel()

        if self.task_type == 2:
            fab.children[0].icon = "plus"
        else:
            rotate_widget(fab, 0)

        if self.dragging:
            if fab.collide_point(*touch.pos):
                if self.task_type == 2:
                    # ToDo: delete event
                    pass
                elif self.task_type == 0:
                    de_activate_to_do(self.task_id, 0, 0, 0)
                elif self.task_type == 1:
                    de_activate_recurrent(self.task_id, 0, 0, 0, datetime.now())
                self.deleted = True
                self.positioning_hint.parent.remove_widget(self.positioning_hint)
                self.parent.remove_widget(self)
                remove_planer(self.task_id, self.task_type)
                fab.size = (fab.size[0] -10, fab.size[1] -10)
                fab.pos = (fab.pos[0] + 10 / 2, fab.pos[1] + 10 / 2)


        def recreate_in_planer():
            temp = self
            self.parent.remove_widget(self)
            self.active_planer_day.ids.planer_float_layout.add_widget(temp)
            self.elevation = 0

        if self.dragging and not self.deleted:
            current_planer_date = MDApp.get_running_app().root.ids.planer_display.displayed_date
            recreate_in_planer()
            self.pos = [50, calculate_snapping_point(self.active_planer_day,
                                                  self.current_touch_position[1] - self.height / 2)]
            if self.active == 0:
                save_planer(self.task_type, self.task_id, MDApp.get_running_app().root.ids.planer_display.displayed_date)
            if self.task_type == 0:
                de_activate_to_do(self.task_id, 1, 0, self.top)
                update_task(self.task_id, current_planer_date,
                            self.ids.content.text, self.top, 1)
            if self.task_type == 1:
                de_activate_recurrent(self.task_id, 1, 0, self.top, current_planer_date)
            self.active = 1
            MDApp.get_running_app().root.ids.planer_display.create_time_wall()
            self.opacity = 1

        self.dragging = False
        Clock.unschedule(self.scroll_handler)
        return super().on_touch_up(touch)

    def on_touch_move(self, touch, *args):
        self.current_touch_position = touch.pos

        fab = MDApp.get_running_app().root.ids.planer_display.ids.fab.children[0]

        def scale_fab(delta):
            fab.size = (fab.size[0] + delta, fab.size[1] + delta)
            fab.pos = (fab.pos[0] - delta / 2, fab.pos[1] - delta / 2)

        def set_scroll_factor():
            max_height = Window.size[1]
            if touch.pos[1] < max_height / 5:
                speed = (1 - (touch.pos[1] / (max_height / 5)))
                self.scroll_factor = - 0.01 * speed
            elif touch.pos[1] > max_height * 0.75:
                speed = ((touch.pos[1] - max_height * 0.75) / (max_height * 0.25))
                self.scroll_factor = 0.01 * speed
            else:
                self.scroll_factor = 0

        if self.dragging:
            if fab.collide_point(*touch.pos):
                if not self.fab_is_deleting:
                    self.fab_is_deleting = True
                    fab.size_hint = (None, None)
                    scale_fab(10)

            else:
                if self.fab_is_deleting:
                    self.fab_is_deleting = False
                    fab.children[0].size_hint = (None, None)
                    scale_fab(-10)

            set_scroll_factor()

        return super().on_touch_move(touch, *args)

    def on_long_press(self, dt):
        fab = MDApp.get_running_app().root.ids.planer_display.ids.fab.children[0]

        self.dragging = True
        self.movement_tick = Clock.schedule_interval(self.follow_touch, 0.01)
        root = MDApp.get_running_app().root
        root_parent = root.ids.planer_display
        root.ids.navigation_drawer.set_state("close")

        if self.task_type == 2:
            fab.children[0].icon = "delete-outline"
        else:
            rotate_widget(fab, 45)

        def recreate_in_root():
            self.deleted = False
            temp = self
            self.parent.remove_widget(self)
            root_parent.add_widget(temp)
            self.elevation = 4
            self.follow_touch(0)
            self.opacity = 0.5

        def show_positioning_hint():
            self.positioning_hint = PositioningHint()
            self.positioning_hint.height = self.height
            screen_manager = MDApp.get_running_app().root.ids.planer_display.screen_manager
            active_planer_screen_name = screen_manager.current
            self.active_planer_day = screen_manager.get_screen(active_planer_screen_name).children[0]
            self.active_planer_day.ids.planer_float_layout.add_widget(self.positioning_hint)

        recreate_in_root()
        show_positioning_hint()
        if self.options_showing:
            print("options showing")
            self.hide_options(0)

        self.scroll_handler = Clock.schedule_interval(self.handle_scroll, 0.03)
        print(self.scroll_handler)

    def handle_scroll(self, dt):
        if not self.active_planer_day:
            screen_manager = MDApp.get_running_app().root.ids.planer_display.screen_manager
            active_planer_screen_name = screen_manager.current
            self.active_planer_day = screen_manager.get_screen(active_planer_screen_name).children[0]
        self.active_planer_day.scroll_y += self.scroll_factor

    def follow_touch(self, dt):
        if self.current_touch_position:
            touch_pos = [self.current_touch_position[0] - self.width / 3, self.current_touch_position[1] - self.height / 2]
            self.pos = touch_pos
            if self.positioning_hint:
                self.positioning_hint.pos =\
                    [50, calculate_snapping_point(self.active_planer_day,
                                                  self.current_touch_position[1] - self.height / 2)]

    def delete_task(self, *args):
        remove_from_db(self.task_id, self.task_type)
        self.parent.remove_widget(self)

    def show_options(self):
        def show_menu():
            if not self.task_menu:
                self.task_menu = TaskMenu()
                if self.active == 1:
                    self.expand_button = ExpandButton()
                    self.task_menu.add_widget(self.expand_button)
                self.edit_button = EditButton()
                self.task_menu.add_widget(self.edit_button)
            if not self.options_showing:
                if self.task_menu:
                    self.ids.menu_layout.add_widget(self.task_menu)

        def show_check_button():
            if not self.check_button:
                self.check_button = CheckButton()
            if not self.options_showing:
                self.ids.check_layout.add_widget(self.check_button)

        def show_delete_button():
            if not self.delete_button:
                self.delete_button = MDIconButton(
                icon="delete-outline",
                size_hint=(None, None),
                icon_size="15sp",
                pos_hint={"center_x": .5, "center_y": .5},
                on_release=self.delete_task
                )
            if not self.options_showing:
                self.ids.check_layout.add_widget(self.delete_button)

        def hide_list_menu():
            planer_display = MDApp.get_running_app().root.ids.planer_display
            button_task = planer_display.ids.list_button_task
            button_recurrent = planer_display.ids.list_button_recurrent
            button_event = planer_display.ids.list_button_event

            animation = Animation(pos_hint={"center_x": 1.2}, duration=0.3, transition="in_cubic")
            animation.start(button_task)
            animation.start(button_recurrent)
            animation.start(button_event)

        # ToDo: fade in animation

        hide_list_menu()
        show_menu()
        if self.active == 1:
            if not self.done:
                show_check_button()
        else:
            show_delete_button()
        if self.close_menu_timer:
            self.close_menu_timer.cancel()
        self.close_menu_timer = Clock.schedule_once(self.hide_options, 2)
        self.options_showing = True

    def hide_options(self, dt):
        def hide_menu():
            if self.active == 0:
                if self.expand_button:
                    self.task_menu.remove_widget(self.expand_button)
                pass
            elif self.task_menu and self.task_menu.parent:
                self.task_menu.parent.remove_widget(self.task_menu)
            # ToDo: fade away animation

        def hide_check_button():
            if self.check_button.parent and self.check_button:
                self.check_button.parent.remove_widget(self.check_button)

        def show_list_menu():
            planer_display = MDApp.get_running_app().root.ids.planer_display
            button_task = planer_display.ids.list_button_task
            button_recurrent = planer_display.ids.list_button_recurrent
            button_event = planer_display.ids.list_button_event

            animation = Animation(pos_hint={"center_x": 0.92}, duration=0.3, transition="in_cubic")
            animation.start(button_task)
            animation.start(button_recurrent)
            animation.start(button_event)

        self.options_showing = False

        show_list_menu()
        hide_menu()
        if self.active == 1:
            if not self.done:
                hide_check_button()

    def toggle_check(self, *args):
        def save_in_db():
            if self.task_type == 0:
                de_activate_to_do(self.task_id, self.active, self.done, self.top)
            if self.task_type == 1:
                de_activate_recurrent(self.task_id, self.active, self.done, self.top, datetime.now())
            if self.task_type == 2:
                # ToDo: implement for event
                pass

        def save_entry():
            save_recurrent_entry(datetime.now(),self.task_id)

        def delete_entry():
            delete_recurrent_entry(self.task_id)

        def check_task():

            self.check_button.icon = "check-circle"
            self.check_button.children[0].color = [0.5, 0.8, 0, 1]
            self.done = 1
            save_in_db()
            save_recurrent_entry(datetime.now(), self.task_id)

        def uncheck_task():
            self.check_button.icon = "check-circle-outline"
            self.check_button.children[0].color = [1, 1, 1, 1]
            self.done = 0
            save_in_db()
            delete_recurrent_entry(self.task_id)

        self.checked = not self.checked
        if self.checked:
            check_task()
        else:
            uncheck_task()
        if self.close_menu_timer:
            self.close_menu_timer.cancel()
        self.close_menu_timer = Clock.schedule_once(self.hide_options, 2)

    def edit(self):

        if self.task_type == 0:
            task = get_task(self.task_id, self.task_type)
            print(task)
            dialog = TaskPopup(self.task_id, [task[5], task[6]])
        if self.task_type == 1:
            task = get_task(self.task_id, self.task_type)
            print(self.task_id, self.task_type, task)
            dialog = RecurrentDialog(self.task_id, [task[5], task[8], task[9], task[6]])
        if self.task_type == 2:
            dialog = EventDialog(self)


class TaskMenu(MDBoxLayout):
    expand_button = None
    stretch_start_y = None
    start_pos = None
    start_height = None
    parent_task = None
    scroll_factor = 0
    new_height_in_blocks = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(self.set_variables, 0.1)

    def set_variables(self, dt):
        self.parent_task = self.parent.parent

    def start_expansion(self, touch):
        self.parent_task.stretching = True
        self.stretch_start_y = touch.pos[1]
        self.start_pos = self.parent_task.pos[1]
        self.start_height = self.parent_task.height
        self.parent_task.timer.cancel()
        self.parent_task.close_menu_timer.cancel()
        if self.parent_task.positioning_hint:
            self.parent_task.parent.remove_widget(self.parent_task.positioning_hint)

    def end_expansion(self):
        if self.parent_task:
            if self.parent_task.stretching:
                self.parent_task.stretching = False
                self.parent_task.options_showing = False
                self.new_height_in_blocks = self.parent_task.size[1]/30
                update_task_duration(self.parent.parent.task_id, self.new_height_in_blocks)
                self.parent_task.hide_options(0)
                self.stretch_start_y = None
                self.start_pos = None
                self.start_height = None

    def on_touch_move(self, touch):
        if self.stretch_start_y:
            delta_y = self.stretch_start_y - touch.pos[1]
            if self.start_height + delta_y > item_height:
                delta_blocks = math.floor(delta_y / item_height)
                self.parent_task.pos[1] = self.start_pos - delta_blocks * item_height
                self.parent_task.size[1] = self.start_height + delta_blocks * item_height

        def set_scroll_factor():
            max_height = Window.size[1]
            touch_pos_y = self.to_window(*touch.pos)[1]
            if touch_pos_y < max_height / 5:
                speed = (1 - (touch_pos_y / (max_height / 5)))
                self.scroll_factor = - 0.01 * speed
            elif touch_pos_y > max_height * 0.75:
                speed = ((touch_pos_y - max_height * 0.75) / (max_height * 0.25))
                self.scroll_factor = 0.01 * speed
            else:
                self.scroll_factor = 0
        set_scroll_factor()
        return super().on_touch_move(touch)


class ExpandButton(MDIconButton):

    scroll_handler = None
    active_planer_day = None

    def __init__(self, *args, **kwargs):
        super().__init__(
            icon="arrow-expand-down",
            icon_size="10sp",
            pos_hint={"center_x": .5, "center_y": .5},
            *args,
            **kwargs
        )

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.md_bg_color = MDApp.get_running_app().theme_cls.primary_color
            self.parent.start_expansion(touch)

        if not self.active_planer_day:
            screen_manager = MDApp.get_running_app().root.ids.planer_display.screen_manager
            active_planer_screen_name = screen_manager.current
            self.active_planer_day = screen_manager.get_screen(active_planer_screen_name).children[0]
        self.scroll_handler = Clock.schedule_interval(self.handle_scroll, 0.03)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.parent.end_expansion()
        self.md_bg_color = [0, 0, 0, 0]
        Clock.unschedule(self.scroll_handler)
        return super().on_touch_up(touch)

    def handle_scroll(self, dt):
        self.active_planer_day.scroll_y += self.parent.scroll_factor
        pass


class EditButton(MDIconButton):

    def __init__(self, *args, **kwargs):
        super().__init__(
            icon="pencil-outline",
            icon_size="10sp",
            pos_hint={"center_x": .5, "center_y": .5},
            *args,
            **kwargs
        )


class CheckButton(MDIconButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

