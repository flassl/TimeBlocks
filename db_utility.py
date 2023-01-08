import sqlite3 as sl
from datetime import datetime, date, time

connection = sl.connect("TimeBlocks.db")
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
            unit_str text NOT NULL,
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
            task_id integer NOT NULL UNIQUE,
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


def save_task(task_type, creation_date, active, done, text, top, duration):
    date_timestamp = datetime.timestamp(creation_date)
    cursor.execute(
        f"INSERT INTO ToDoTasks VALUES(NULL, '{task_type}', '{date_timestamp}',"
        f" '{active}','{done}', '{text}', '{top}', '{duration}')")
    connection.commit()


def update_task(ID, date_update, text, top, duration):
    if isinstance(date_update, date):
        date_update = datetime.combine(date_update, time(0, 0))
    date_update_timestamp = date_update.timestamp()
    cursor.execute(
        f"UPDATE ToDoTasks "
        f"SET "
        f"text = '{text}', "
        f"top = '{top}', "
        f"date_timestamp = '{date_update_timestamp}', "
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


def get_list_tasks():
    cursor.execute("SELECT * FROM ToDoTasks WHERE active = '0' AND done = '0'")
    tasks = cursor.fetchall()
    return tasks

