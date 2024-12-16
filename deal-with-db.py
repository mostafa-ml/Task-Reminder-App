import mysql.connector    # pip install mysql-connector-python
import datetime

db_config = {
    "host": "localhost",
    "user": "root",             # Insert Your username
    "password": "MK@SQL",       # Insert Your password
    "database": "TaskReminder"
}

priority = ('High', 'Medium', 'Low')
status = ('Pending', 'Completed', 'Overdue')

def add_user(connection, username, password_hash):
    cursor = connection.cursor()
    query = "INSERT INTO Users (username, password_hash) VALUES (%s, %s)"
    values = (username, password_hash)
    try:
        cursor.execute(query, values)
        connection.commit()
        print('User added successfully')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        cursor.close()

def delete_user(connection, username, password_hash):
    cursor = connection.cursor()
    query = "DELETE FROM users WHERE username = %s AND password_hash = %s"
    values = (username, password_hash)
    try:
        cursor.execute(query, values)
        connection.commit()
        if cursor.rowcount > 0:
            print(f'User `{username}` deleted successfully')
        else:
            print('Incorrect username or password')
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

def update_user(connection, old_username, old_password_hash, new_username=None, new_password_hash=None):
    cursor = connection.cursor()
    attributes = {'username':new_username, 'password_hash':new_password_hash}
    query = "UPDATE Users SET"
    values = []
    for attr, val in attributes.items():
        if val:
            query += f" {attr} = %s,"
            values.append(val)
    if len(values) == 0:
        print('There are no changes to update!')
        return
    query = query.rstrip(',')
    query += " WHERE username = %s AND password_hash = %s"
    values.append(old_username)
    values.append(old_password_hash)
    try:
        cursor.execute(query, tuple(values))
        connection.commit()
        if cursor.rowcount > 0:
            print('User updated successfully')
        else:
            print('Incorrect username/password or there are no changes')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        cursor.close()

def is_user_in_db(connection, username, password_hash):
    """Return the user_id if the user exists in the database otherwise return None"""
    cursor = connection.cursor()
    query = "SELECT user_id FROM users WHERE username = %s AND password_hash = %s"
    values = (username, password_hash)
    try:
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result[0] if result else result
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()

def get_user_id(connection, username):
    """Return the user_id if the user exists in the database otherwise return None"""
    cursor = connection.cursor()
    query = "SELECT user_id FROM users WHERE username = %s"
    values = (username,)
    try:
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result[0] if result else result
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()

def add_task(connection, user_id, title, description, priority, status, due_date):
    cursor = connection.cursor()
    query = "INSERT INTO Tasks (user_id, title, description, priority, status, due_date) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (user_id, title, description, priority, status, due_date)
    try:
        cursor.execute(query, values)
        connection.commit()
        print('Task added successfully')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        cursor.close()

def delete_task(connection, user_id, title):
    cursor = connection.cursor()
    query = "DELETE FROM Tasks WHERE user_id = %s AND title = %s"
    values = (user_id, title)
    try:
        cursor.execute(query, values)
        connection.commit()
        if cursor.rowcount > 0:
            print(f'Task with title {title} deleted successfully')
        else:
            print(f'Task title is wrong')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        cursor.close()

def update_task(connection, user_id, old_title, title=None, description=None, priority=None, status=None, due_date=None):
    cursor = connection.cursor()
    attributes = {'title':title, 'description':description, 'priority':priority, 'status':status, 'due_date':due_date}
    query = "UPDATE Tasks SET"
    values = []
    for attr, val in attributes.items():
        if val:
            query += f" {attr} = %s,"
            values.append(val)
    if len(values) == 0:
        print('No fields to update.')
        return
    query = query.rstrip(',')
    query += " WHERE user_id = %s AND title = %s"
    values.append(user_id)
    values.append(old_title)
    try:
        cursor.execute(query, tuple(values))
        connection.commit()
        if cursor.rowcount > 0:
            print('Task updated successfully')
        else:
            print('Task title is wrong or there are no changes')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        cursor.close()

def get_task_id(connection, user_id, title):
    cursor = connection.cursor()
    query = "SELECT task_id FROM tasks WHERE user_id = %s AND title = %s"
    values = (user_id, title)
    try:
        cursor.execute(query, values)
        res = cursor.fetchone()
        return res[0] if res else res
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()

def get_user_tasks(connection, user_id):
    """If the user_id is valid it will return list of tasks each with (title, description, priority, status, due_date)"""
    cursor = connection.cursor()
    query = "SELECT title, description, priority, status, due_date FROM tasks WHERE user_id = %s"
    values = (user_id, )
    try:
        cursor.execute(query, values)
        res = cursor.fetchall()
        return res
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()

def add_reminder(connection, user_id, task_title, reminder_time, is_sent=False):
    cursor = connection.cursor()
    task_id = get_task_id(connection, user_id=user_id, title=task_title)
    if task_id is None:
        print('Incorrect task title or user_id')
        return
    query = "INSERT INTO Reminders (task_id, reminder_time, is_sent) VALUES (%s, %s, %s)"
    values = (task_id, reminder_time, is_sent)
    try:
        cursor.execute(query, values)
        connection.commit()
        print('Reminder added successfully')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        cursor.close()

def delete_reminder(connection, user_id, task_title):
    cursor = connection.cursor()
    task_id = get_task_id(connection, user_id=user_id, title=task_title)
    if task_id is None:
        print('Incorrect task title or user_id')
        return
    query = "DELETE FROM Reminders WHERE task_id = %s"
    values = (task_id,)
    try:
        cursor.execute(query, values)
        connection.commit()
        print(f'Reminder with task title {task_title} deleted successfully')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        cursor.close()

def update_reminder(connection, user_id, task_title, reminder_time=None, is_sent=None):
    cursor = connection.cursor()
    task_id = get_task_id(connection, user_id=user_id, title=task_title)
    if task_id is None:
        print('Incorrect task title or user_id')
        return
    attributes = {'reminder_time':reminder_time, 'is_sent':is_sent}
    query = "UPDATE Reminders SET"
    values = []
    for attr, val in attributes.items():
        if val is not None:
            query += f" {attr} = %s,"
            values.append(val)
    if len(values) == 0:
        print('No fields to update.')
        return
    query = query.rstrip(',')
    query += " WHERE task_id = %s"
    values.append(task_id)
    try:
        cursor.execute(query, tuple(values))
        connection.commit()
        if cursor.rowcount > 0:
            print('Reminder updated successfully')
        else:
            print('There are no changes')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        cursor.close()

def get_user_reminders(connection, user_id):
    cursor = connection.cursor()
    query = "SELECT t.title, r.reminder_time, r.is_sent FROM reminders r JOIN tasks t ON r.task_id = t.task_id WHERE t.user_id = %s"
    values = (user_id,)
    try:
        cursor.execute(query, values)
        reminders = cursor.fetchall()
        return reminders if reminders else None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()

if __name__ == '__main__':
    try:
        connection = mysql.connector.connect(**db_config)
        print("Database connection successful")

        # Add user
        # add_user(connection, 'mostafa', '7777')

        # Delete user
        # delete_user(connection, username='mostafa', password_hash='7777')
        
        # Update user
        # update_user(connection, old_username='mostafa', old_password_hash='7777', new_username=None, new_password_hash=None)

        # is username & password valid => return user_id if valid else: None
        # user_id = is_user_in_db(connection, 'mostafa', '7777')
        # print(user_id)

        # get user id
        # user_id = get_user_id(connection, 'mostafa')
        # print(user_id)

        # Add task
        # add_task(connection, user_id=2, 'Learn Python', 'Learn python in 3 days!', priority[1], status[0], due_date=datetime.datetime.now())

        # Delete task
        # delete_task(connection, user_id=2, title='Learn Python')

        # Update task
        # update_task(connection, user_id=2, old_title='Learn Pythoon', title='Learn Python')

        # get all user tasks
        # user_tasks = get_user_tasks(connection, user_id=2)
        # print(user_tasks)

        # Add reminder
        # add_reminder(connection, user_id=2, task_title='Learn Python', reminder_time=datetime.datetime(2030, 12, 25, 10, 30, 0), is_sent=False)

        # Delete reminder
        # delete_reminder(connection, user_id=2, task_title='Learn Python')

        # Update reminder
        update_reminder(connection, user_id=2, task_title='Learn Python', reminder_time=datetime.datetime.now())

        # get all user reminders
        # user_reminders = get_user_reminders(connection, user_id=2)
        # print(user_reminders)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            connection.close()
