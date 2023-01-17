from app.utility.db_utility import *
from kivy.animation import Animation

item_height = 30


def calculate_snapping_point(planer_scroll_view, touch_pos_y):
    top = planer_scroll_view.to_local(50, touch_pos_y)[1]
    difference = top % item_height
    if difference >= item_height / 2:
        snapped_top = top + (item_height - difference)
    else:
        snapped_top = top - difference
    return snapped_top


def offset_date_by_months(input_date, offset):
    calculated_year = input_date.year
    calculated_month = input_date.month + offset
    if calculated_month < 1:
        calculated_year -= 1
        calculated_month = 12
    if calculated_month > 12:
        calculated_year += 1
        calculated_month = 1
    offset_date = date(day=1, month=calculated_month, year=calculated_year)
    return offset_date


def rotate_Widget(widget, angle):
    Animation(rotate_value_angle=angle, d=0.3).start(widget)


