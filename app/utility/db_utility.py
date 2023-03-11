import sqlite3 as sl
from datetime import datetime, date, time, timedelta

connection = sl.connect("../../TimeBlocks.db")
cursor = connection.cursor()


def delete_db():
    cursor.execute("DROP TABLE IF EXISTS ToDoTasks")
    cursor.execute("DROP TABLE IF EXISTS RecurrentTasks")
    cursor.execute("DROP TABLE IF EXISTS PlanerTasks")
    cursor.execute("DROP TABLE IF EXISTS RecurrentTaskEntries")
    cursor.execute("DROP TABLE IF EXISTS EventTasks")
    pass


def create_db():
    # delete_db()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ToDoTasks (
    task_reference integer PRIMARY KEY,
    task_type integer NOT NULL,
    date_timestamp integer NOT NULL,
    active integer NOT NULL,
    done integer DEFAULT '0' NOT NULL,
    text text NOT NULL,
    top real NOT NULL,
    duration integer DEFAULT "1" NOT NULL
    )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RecurrentTasks (
        task_reference integer PRIMARY KEY,
        task_type integer NOT NULL,
        date_timestamp integer NOT NULL,
        active integer NOT NULL,
        done integer DEFAULT '0' NOT NULL,
        text text NOT NULL,
        top real NOT NULL,
        duration integer DEFAULT "1" NOT NULL,
        period integer NOT NULL,
        unit_str text NOT NULL,
        color text NOT NULL,
        font_color text NOT NULL
        )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS RecurrentTaskEntries (
            entry_reference integer PRIMARY KEY,
            date_timestamp integer NOT NULL,
            task_reference integer NOT NULL,
            FOREIGN KEY (task_reference)
                REFERENCES RecurrentTasks (task_reference)
            )
            """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS EventTasks (
            task_reference integer PRIMARY KEY,
            task_type integer NOT NULL,
            date_timestamp integer NOT NULL,
            done integer DEFAULT '0' NOT NULL,
            text text NOT NULL,
            top real NOT NULL,
            duration integer DEFAULT "1" NOT NULL,
            color text NOT NULL,
            font_color text NOT NULL
            )
    """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS PlanerTasks (
            task_reference integer PRIMARY KEY,
            task_type integer NOT NULL,
            task_id integer NOT NULL,
            planed_date_timestamp integer NOT NULL
            )
            """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS Goals (
            goal_reference integer PRIMARY KEY,
            goal_type integer NOT NULL,
            goal integer NOT NULL,
            progress integer NOT NULL,
            goal_name text NOT NULL
            )
            """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS GoalEntries (
            entry_reference integer PRIMARY KEY,
            date integer NOT NULL,
            progress integer NOT NULL,
            reset integer NOT NULL,
            goal_type integer NOT NULL,
            goal_reference integer NOT NULL,
            FOREIGN KEY (goal_reference)
                REFERENCES Goals (goal_reference),
            FOREIGN KEY (goal_type)
                REFERENCES Goals (goal_type)
            )
            """)
    connection.commit()


def remove_from_db(task_id, task_type):
    if task_type == 0:
        remove_task(task_id)
        pass
    if task_type == 1:
        remove_recurrent(task_id)
    if task_type == 2:
        # implement delete events
        pass


def save_task(task_type, creation_date, active, done, text, top, duration):
    date_timestamp = datetime.timestamp(creation_date)
    cursor.execute(
        f"INSERT INTO ToDoTasks VALUES(NULL, '{task_type}', '{date_timestamp}',"
        f" '{active}','{done}', '{text}', '{top}', '{duration}')")
    connection.commit()


def update_task(ID, date_update, text, top):
    if isinstance(date_update, date):
        date_update = datetime.combine(date_update, time(0, 0))
    date_update_timestamp = date_update.timestamp()
    cursor.execute(
        f"UPDATE ToDoTasks "
        f"SET "
        f"text = '{text}', "
        f"top = '{top}', "
        f"date_timestamp = '{date_update_timestamp}' "
        f"WHERE "
        f"task_reference = '{ID}'")
    connection.commit()


def update_task_duration(ID, task_type, duration):
    list_name = get_list_from_task_type(task_type)

    cursor.execute(
        f"UPDATE {list_name} "
        f"SET "
        f"duration = '{duration}' "
        f"WHERE "
        f"task_reference = '{ID}'")
    connection.commit()


def de_activate_to_do(ID, active, done, new_top):
    cursor.execute(
        f"UPDATE ToDoTasks "
        f"SET "
        f"active = '{active}', "
        f"done = '{done}', "
        f"top = '{new_top}' "
        f"WHERE "
        f"task_reference = '{ID}'")
    connection.commit()


def remove_task(ID):
    cursor.execute(
        f"DELETE FROM ToDoTasks "
        f"WHERE task_reference = '{ID}'")
    connection.commit()


def get_task(id, task_type):
    db_name = None
    if task_type == 0:
        db_name = "ToDoTasks"
    if task_type == 1:
        db_name = "RecurrentTasks"
    if task_type == 2:
        db_name = "EventTasks"
    cursor.execute(
        f"SELECT * FROM {db_name} "
        f"WHERE "
        f"task_reference = '{id}' AND "
        f"task_type ='{task_type}'")
    connection.commit()
    return cursor.fetchone()


def save_planer(task_type, task_id, planed_date):
    # if isinstance(planed_date, int) or isinstance(planed_date, float):
        # planed_date = datetime.fromtimestamp(planed_date)
    if isinstance(planed_date, date):
        planed_date = datetime.combine(planed_date, time(0, 0)).timestamp()
    if isinstance(planed_date, datetime):
        planed_date = planed_date.timestamp()

    cursor.execute(
            f"INSERT INTO PlanerTasks VALUES(NULL, '{task_type}', '{task_id}', '{planed_date}')")
    connection.commit()


def remove_planer(ID, task_type):
    cursor.execute(
        f"DELETE FROM PlanerTasks "
        f"WHERE "
        f"task_id = '{ID}' AND "
        f"task_type = '{task_type}'")
    connection.commit()


def update_planer(task_type, task_id, planed_date):
    if isinstance(planed_date, date):
        planed_date = datetime.combine(planed_date, time(0, 0)).timestamp()
    if isinstance(planed_date, datetime):
        planed_date = planed_date.timestamp()
    cursor.execute(
        f"UPDATE PlanerTasks "
        f"SET "
        f"planed_date_timestamp = '{planed_date}' "
        f"WHERE "
        f"task_reference = '{task_id}' "
        f"AND "
        f"task_type = '{task_type}'")
    connection.commit()


def get_list_tasks():
    cursor.execute("SELECT * FROM ToDoTasks WHERE active = '0' AND done = '0'")
    tasks = cursor.fetchall()
    return tasks

def deactivate_passed_tasks():
    date_start_timestamp = datetime.combine(date.today(), time(0, 0, 0)).timestamp()
    cursor.execute(
        f"UPDATE ToDoTasks "
        f"SET "
        f"active = '0' "
        f"WHERE "
        f"date_timestamp < '{date_start_timestamp}'")
    print(cursor.fetchall())
    connection.commit()
    pass


def get_list_recurrent():
    tasks = []
    cursor.execute(f"SELECT * FROM RecurrentTasks WHERE unit_str = 'Days'")
    due_for_date = cursor.fetchall()
    connection.commit()
    for task in due_for_date:
        period = task[8]
        limit_date_start = datetime.combine(date.today(), time(0, 0, 0)) - timedelta(days=period)
        limit_date_start_timestamp = limit_date_start.timestamp()
        limit_date_end = datetime.combine(date.today(), time(0, 0, 0)) - timedelta(days=period - 1)
        limit_date_end_timestamp = limit_date_end.timestamp()
        cursor.execute(f"SELECT * FROM RecurrentTaskEntries WHERE task_reference = {task[0]}"
                       f" ORDER BY date_timestamp DESC LIMIT 1")
        entry = cursor.fetchone()
        connection.commit()
        if isinstance(task[2], str):
            task_date_timestamp = datetime.strptime(task[2], "%Y-%m-%d %H:%M:%S.%f").timestamp()
        else:
            task_date_timestamp = task[2]

        today_start = datetime.combine(date.today(), time(0, 0, 0)).timestamp()
        if task[3] == 0 and task_date_timestamp < today_start:
            tasks.append(task)
        if entry:
            if limit_date_start_timestamp < entry[1] < limit_date_end_timestamp and task[3] < 0:
                tasks.append(task)
        else:
            tasks.append(task)

    cursor.execute(f"SELECT * FROM RecurrentTasks WHERE unit_str = 'Hours'")
    due_for_hour = cursor.fetchall()
    connection.commit()
    for task in due_for_hour:
        period = task[8]
        limit_time = datetime.now() - timedelta(hours=period)
        limit_time_timestamp = limit_time.timestamp()
        cursor.execute(f"SELECT * FROM RecurrentTaskEntries WHERE task_reference = {task[0]}"
                       f" ORDER BY date_timestamp DESC LIMIT 1")
        entry = cursor.fetchone()
        connection.commit()
        if entry:
            if entry[1] < limit_time_timestamp and task[3] < 0:
                tasks.append(task)

    return tasks


def get_all_recurrent_entries():
    cursor.execute(f"SELECT * FROM RecurrentTaskEntries")
    entries = cursor.fetchall()
    connection.commit()
    return entries


def get_all_recurrent_tasks_by_done(done):
    cursor.execute(f"SELECT * FROM RecurrentTasks WHERE done='{done}'")
    entries = cursor.fetchall()
    connection.commit()
    return entries


def get_all_recurrent_tasks_by_done_and_active(done, active):
    cursor.execute(f"SELECT * FROM RecurrentTasks WHERE done='{done}' AND active = '{active}'")
    entries = cursor.fetchall()
    connection.commit()
    return entries


def set_due_recurrent_tasks_to_undone():
    def task_period_to_millis(task_data):
        millis = 0
        period = int(task_data[8])
        unit_str = task_data[9]
        if unit_str == "Hours":
            millis = period * 1000
        if unit_str == "Days":
            millis = period * 1000 * 60 * 60 * 24
        if unit_str == "Weeks":
            millis = period * 1000 * 60 * 60 * 24 * 7

        return millis

    tasks_data = get_all_recurrent_tasks_by_done(1)
    for task_data in tasks_data:
        if task_data:
            entry = get_recurrent_entry(task_data[0])
            if entry:
                elapsed_time_since_check = datetime.now().timestamp() - entry[1]
                if elapsed_time_since_check * 1000 >= task_period_to_millis(task_data):
                    un_redo_recurrent(task_data[0], 0, 0)
                    remove_planer(task_data[0], 1)


def get_all_due_recurrent_tasks():
    set_due_recurrent_tasks_to_undone()
    tasks = get_all_recurrent_tasks_by_done_and_active(0, 0)
    return tasks


def save_recurrent(task_type, creation_date, active, done, text, top_distance, duration,
                   period, unit_str, color, font_color):
    date_timestamp = datetime.timestamp(creation_date)
    cursor.execute(
        f"INSERT INTO RecurrentTasks VALUES(NULL, '{task_type}', '{date_timestamp}', '{active}','{done}',"
        f" '{text}', '{top_distance}', '{duration}', '{period}', '{unit_str}', '{color}', '{font_color}')")
    connection.commit()



def get_recurrent_entry(task_id):
    cursor.execute(f"SELECT * FROM RecurrentTaskEntries WHERE task_reference='{task_id}'")
    entry = cursor.fetchone()
    connection.commit()
    return entry


def save_recurrent_entry(date_now, task_reference):
    timestamp = date_now.timestamp()
    cursor.execute(
        f"INSERT INTO RecurrentTaskEntries VALUES(NULL, '{timestamp}', '{task_reference}')")
    connection.commit()


def delete_recurrent_entry(task_reference):
    cursor.execute(
        f"DELETE FROM RecurrentTaskEntries WHERE task_reference ='{task_reference}'")
    connection.commit()


def update_recurrent(ID, date_update, text, top_distance, period, unit_str, color, font_color):
    if isinstance(date_update, date):
        date_update = datetime.combine(date_update, time(0, 0))
    date_timestamp = datetime.timestamp(date_update)
    cursor.execute(
        f"UPDATE RecurrentTasks "
        f"SET "
        f"text = '{text}', "
        f"top = '{top_distance}', "
        f"date_timestamp = '{date_timestamp}', "
        f"period = '{period}', "
        f"unit_str = '{unit_str}', "
        f"color = '{color}', "
        f"font_color = '{font_color}' "
        f"WHERE "
        f"task_reference = '{ID}'")
    connection.commit()


def de_activate_recurrent(ID, active, done, new_top, update_date):
    if isinstance(update_date, date):
        update_date = datetime.combine(update_date, time(0, 0))
    update_date_timestamp = update_date.timestamp()
    cursor.execute(
        f"UPDATE RecurrentTasks "
        f"SET "
        f"active = '{active}', "
        f"done = '{done}', "
        f"top = '{new_top}', "
        f"date_timestamp = {update_date_timestamp} "
        f"WHERE "
        f"task_reference = '{ID}'")
    connection.commit()


def un_redo_recurrent(ID, done, active):
    cursor.execute(
        f"UPDATE RecurrentTasks "
        f"SET "
        f"done = '{done}', "
        f"active = '{active}' "
        f"WHERE "
        f"task_reference = '{ID}'")
    connection.commit()

def get_list_from_task_type(task_type):
    if task_type == 0:
        return "ToDoTasks"
    if task_type == 1:
        return "RecurrentTasks"
    if task_type == 2:
        return "EventTasks"
#def show_due_recurrent_tasks(dt):
#
#    def show_recurrent(task):
#        app = app.get_running_app()
#        recurrent = app.root.planer.recurrent
#        now = datetime.now()
#        top = recurrent.top - item_height - spacing * 2 - len(recurrent_task_list) * (item_height + spacing)
#        color = tuple(float(s) for s in task[10].strip("[]").split(","))
#        font_color = tuple(float(s) for s in task[11].strip("[]").split(","))
#        new_task = RecurrentTask(task[5], top, task[7], color, font_color,
#                                 task[8], task[9], task[3], now, task[0])
#        de_activate_recurrent(task[0], 1, 0, top, now)
#        recurrent_task_list.append(new_task)
#        recurrent.ids.recurrent_list_display.add_widget(new_task)
#    cursor.execute(f"SELECT * FROM RecurrentTasks WHERE unit_str = 'days'")
#    due_for_date = cursor.fetchall()
#    connection.commit()
#    for task in due_for_date:
#        period = task[8]
#        limit_date_start = datetime.combine(date.today(), time(0, 0, 0)) - timedelta(days=period)
#        limit_date_start_timestamp = limit_date_start.timestamp()
#        limit_date_end = datetime.combine(date.today(), time(0, 0, 0)) - timedelta(days=period - 1)
#        limit_date_end_timestamp = limit_date_end.timestamp()
#        cursor.execute(f"SELECT * FROM RecurrentTaskEntries WHERE task_reference = {task[0]}"
#                       f" ORDER BY date_timestamp DESC LIMIT 1")
#        entry = cursor.fetchone()
#        connection.commit()
#        if isinstance(task[2], str):
#            task_date_timestamp = datetime.strptime(task[2], "%Y-%m-%d %H:%M:%S.%f").timestamp()
#        else:
#            task_date_timestamp = task[2]
#
#        today_start = datetime.combine(date.today(), time(0, 0, 0)).timestamp()
#        if task[3] == 0 and task_date_timestamp < today_start:
#            show_recurrent(task)
#        if entry:
#            if limit_date_start_timestamp < entry[1] < limit_date_end_timestamp and task[3] < 0:
#                show_recurrent(task)
#
#    cursor.execute(f"SELECT * FROM RecurrentTasks WHERE unit_str = 'hours'")
#    due_for_hour = cursor.fetchall()
#    connection.commit()
#    for task in due_for_hour:
#        period = task[8]
#        limit_time = datetime.now() - timedelta(hours=period)
#        limit_time_timestamp = limit_time.timestamp()
#        cursor.execute(f"SELECT * FROM RecurrentTaskEntries WHERE task_reference = {task[0]}"
#                       f" ORDER BY date_timestamp DESC LIMIT 1")
#        entry = cursor.fetchone()
#        connection.commit()
#        if entry:
#            if entry[1] < limit_time_timestamp and task[3] < 0:
#                app = app.get_running_app()
#                recurrent = app.root.planer.recurrent
#                now = datetime.now()
#                top = recurrent.top - item_height - spacing * 2 - len(recurrent_task_list) * (item_height + spacing)
#                color = tuple(float(s) for s in task[10].strip("[]").split(","))
#                font_color = tuple(float(s) for s in task[11].strip("[]").split(","))
#                de_activate_recurrent(task[0], 1, 0, top, now)
#                new_task = RecurrentTask(task[5], top, task[7], color, font_color,
#                                         task[8], task[9], 1,now, task[0])
#                recurrent_task_list.append(new_task)
#                recurrent.ids.recurrent_list_display.add_widget(new_task)


def remove_recurrent(ID):
    cursor.execute(
        f"DELETE FROM RecurrentTasks "
        f"WHERE task_reference = '{ID}'")
    connection.commit()


def save_event(event_timestamp, text, top_distance, duration, color, font_color):
    cursor.execute(
        f"INSERT INTO EventTasks VALUES(NULL, '2', '{event_timestamp}', '0',"
        f" '{text}', '{top_distance}', '{duration}', '{color}', '{font_color}')")
    connection.commit()


def update_event(ID, date_update, text, top_distance, color, font_color):
    if isinstance(date_update, datetime):
        date_update = date_update.timestamp()
    cursor.execute(
        f"UPDATE EventTasks "
        f"SET "
        f"text = '{text}', "
        f"top = '{top_distance}', "
        f"date_timestamp = '{date_update}', "
        f"color = '{color}', "
        f"font_color = '{font_color}' "
        f"WHERE "
        f"task_reference = '{ID}'")
    connection.commit()


def get_task_amount_for_date(date):
    date_start_timestamp = datetime.combine(date, time(0, 0, 0)).timestamp()
    date_end = datetime.combine(date, time(0, 0, 0)) + timedelta(hours=23, minutes=59, seconds=59)
    date_end_timestamp = date_end.timestamp()
    cursor.execute(f"SELECT Count(*) FROM PlanerTasks WHERE planed_date_timestamp BETWEEN '{date_start_timestamp}' AND "
                   f"'{date_end_timestamp}'")
    planer_tasks_db = cursor.fetchone()
    connection.commit()
    return planer_tasks_db