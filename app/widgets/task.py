from kivy.animation import Animation
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from app.utility.db_utility import *
from app.utility.utility import *
from kivymd.app import MDApp
from kivy.clock import Clock
from .positioning_hint import *
import math




class Task(MDCard):
    def __init__(self, id, task_type, active, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.task_id = id
        self.active = active
        self.task_type = task_type
    timer = None
    movement_tick = None
    current_touch_position = None
    positioning_hint = None
    task_menu = None
    menu_showing = False
    close_menu_timer = None
    stretching = False
    dragging = False
    fab_is_deleting = False
    deleted = False

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
            rotate_Widget(fab, 0)

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

        self.dragging = False
        return super().on_touch_up(touch)

    def on_touch_move(self, touch, *args):
        self.current_touch_position = touch.pos

        fab = MDApp.get_running_app().root.ids.planer_display.ids.fab.children[0]

        def scale_fab(delta):
            fab.size = (fab.size[0] + delta, fab.size[1] + delta)
            fab.pos = (fab.pos[0] - delta / 2, fab.pos[1] - delta / 2)

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
            rotate_Widget(fab, 45)

        def recreate_in_root():
            self.deleted = False
            temp = self
            self.parent.remove_widget(self)
            root_parent.add_widget(temp)
            self.elevation = 4
            self.follow_touch(0)

        def show_positioning_hint():
            self.positioning_hint = PositioningHint()
            self.positioning_hint.height = self.height
            screen_manager = MDApp.get_running_app().root.ids.planer_display.screen_manager
            active_planer_screen_name = screen_manager.current
            self.active_planer_day = screen_manager.get_screen(active_planer_screen_name).children[0]
            self.active_planer_day.ids.planer_float_layout.add_widget(self.positioning_hint)

        recreate_in_root()
        show_positioning_hint()

    def follow_touch(self, dt):
        if self.current_touch_position:
            touch_pos = [self.current_touch_position[0] - self.width / 3, self.current_touch_position[1] - self.height / 2]
            self.pos = touch_pos
            if self.positioning_hint:
                self.positioning_hint.pos =\
                    [50, calculate_snapping_point(self.active_planer_day,
                                                  self.current_touch_position[1] - self.height / 2)]

    def show_menu(self):
        # ToDo: fade in animation
        def close_menu(dt):
            if self.task_menu:
                self.remove_widget(self.task_menu)
                self.menu_showing = False
            # ToDo: fade away animation
            pass
        if self.close_menu_timer:
            self.close_menu_timer.cancel()
        self.close_menu_timer = Clock.schedule_once(close_menu, 2)
        if not self.task_menu:
            self.task_menu = TaskMenu()
        if not self.menu_showing:
            self.add_widget(self.task_menu)
            label = self.ids.content
            self.remove_widget(label)
            self.add_widget(label)
            self.menu_showing = True


class TaskMenu(MDBoxLayout):
    expand_button = None
    stretch_start_y = None
    start_pos = None
    start_height = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expand_button = self.ids.expand_button

    def start_expansion(self, touch):
        self.parent.stretching = True
        self.stretch_start_y = touch.pos[1]
        self.start_pos = self.parent.pos[1]
        self.start_height = self.parent.height
        print("touch staerted at:" + str(touch.pos[1]))
        self.parent.timer.cancel()
        self.parent.close_menu_timer.cancel()
        if self.parent.positioning_hint:
            self.parent.parent.remove_widget(self.parent.positioning_hint)
        print("stretching")

    def end_expansion(self):
        if self.parent:
            if self.parent.stretching:
                self.parent.stretching = False
                self.parent.menu_showing = False
                self.parent.remove_widget(self)
                self.stretch_start_y = None
                self.start_pos = None
                self.start_height = None
                print("not stretching anymore")

    def on_touch_move(self, touch):
        if self.stretch_start_y:
            delta_y = self.stretch_start_y - touch.pos[1]
            if self.start_height + delta_y > item_height:
                delta_blocks = math.floor(delta_y / item_height)
                self.parent.pos[1] = self.start_pos - delta_blocks * item_height
                self.parent.size[1] = self.start_height + delta_blocks * item_height

                print(self.parent.size[1])

        return super().on_touch_move(touch)


class ExpandButton(MDIconButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.md_bg_color = MDApp.get_running_app().theme_cls.primary_color
            self.parent.start_expansion(touch)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.parent.end_expansion()
        self.md_bg_color = [0, 0, 0, 0]
        return super().on_touch_up(touch)



