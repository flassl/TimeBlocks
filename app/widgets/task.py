from kivymd.uix.card import MDCard
from app.utility.db_utility import *
from app.utility.utility import *
from kivymd.app import MDApp
from kivy.clock import Clock
from .positioning_hint import *

dragging = False


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

    active_planer_day = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.timer = Clock.schedule_once(self.on_long_press, 0.3)
        self.current_touch_position = touch.pos
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        global dragging

        if self.timer:
            self.timer.cancel()
        if self.movement_tick:
            self.movement_tick.cancel()

        def recreate_in_planer():
            temp = self
            self.parent.remove_widget(self)
            self.active_planer_day.ids.planer_float_layout.add_widget(temp)
            self.elevation = 0
        if dragging:
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
        pass