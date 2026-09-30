import sqlite3
from types import SimpleNamespace


DATABASE_FILE = "fitbuddy.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def row_to_object(row):
    """
    Convert a SQLite Row into an object so routes.py
    can use attributes such as user.username.
    """
    if row is None:
        return None

    return SimpleNamespace(**dict(row))


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            age INTEGER NOT NULL,
            weight REAL NOT NULL,
            goal TEXT NOT NULL,
            intensity TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            original_plan TEXT NOT NULL,
            updated_plan TEXT,
            nutrition_tip TEXT,
            feedback TEXT,
            plan_type TEXT DEFAULT 'original',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    connection.commit()
    connection.close()


def save_user(
    user_id,
    username,
    age,
    weight,
    goal,
    intensity
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users
        (
            user_id,
            username,
            age,
            weight,
            goal,
            intensity
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        username,
        age,
        weight,
        goal,
        intensity
    ))

    connection.commit()
    connection.close()

    return get_user(user_id)


def get_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()

    connection.close()

    return row_to_object(row)


def get_all_users():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [row_to_object(row) for row in rows]


def save_plan(
    user_id,
    original_plan,
    nutrition_tip,
    plan_type="original",
    feedback=None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO plans
        (
            user_id,
            original_plan,
            updated_plan,
            nutrition_tip,
            feedback,
            plan_type
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        original_plan,
        None,
        nutrition_tip,
        feedback,
        plan_type
    ))

    plan_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return get_plan(user_id)


def get_plan(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM plans
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))

    row = cursor.fetchone()

    connection.close()

    return row_to_object(row)


def get_original_plan(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM plans
        WHERE user_id = ?
        AND plan_type = 'original'
        ORDER BY id ASC
        LIMIT 1
    """, (user_id,))

    row = cursor.fetchone()

    connection.close()

    return row_to_object(row)


def get_all_plans():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM plans
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [row_to_object(row) for row in rows]


def update_plan(
    user_id,
    updated_plan,
    feedback=None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM plans
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))

    row = cursor.fetchone()

    if row is None:
        connection.close()
        return None

    plan_id = row["id"]

    cursor.execute("""
        UPDATE plans
        SET
            updated_plan = ?,
            feedback = ?,
            plan_type = 'updated'
        WHERE id = ?
    """, (
        updated_plan,
        feedback,
        plan_id
    ))

    connection.commit()
    connection.close()

    return get_plan(user_id)


def delete_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM plans
        WHERE user_id = ?
    """, (user_id,))

    cursor.execute("""
        DELETE FROM users
        WHERE user_id = ?
    """, (user_id,))

    connection.commit()
    connection.close()


# Create database/tables when this file is imported
init_database()