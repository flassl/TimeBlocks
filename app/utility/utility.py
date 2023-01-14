item_height = 30


def calculate_snapping_point(planer_scroll_view, touch_pos_y):
    top = planer_scroll_view.to_local(50, touch_pos_y)[1]
    difference = top % item_height
    if difference >= item_height / 2:
        snapped_top = top + (item_height - difference)
    else:
        snapped_top = top - difference
    return snapped_top
