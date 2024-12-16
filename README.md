# Task-Reminder-App
A multithreaded reminder application with a GUI that supports concurrent reminders. The app allows users to add, edit, or remove tasks and reminders, ensuring thread safety while avoiding deadlocks and UI hanging. Perfect for organizing tasks efficiently with robust performance.

## How to Use
1. **Download MySQL Server and Workbench**
   - Install **MySQL Server** and **MySQL Workbench** (version 8.0.40 recommended) from the [official MySQL website](https://dev.mysql.com/downloads/installer/).
   - Start the MySQL server and ensure it is running.

2. **Set Up the Database**
   - Locate the `TaskReminder-db.sql` file in the project directory.
   - Open MySQL Workbench and run the `TaskReminder-db.sql` script to create the database and its associated tables.

3. **Configure Database Connection in `deal_with_db.py`**
   - Open the `deal_with_db.py` file in a text editor or IDE.
   - Update the `username` and `password` variables with your MySQL credentials:
     ```python
     db_config = {
         "host": "localhost",
         "user": "root",             # Insert Your username
         "password": "MK@SQL",       # Insert Your password
         "database": "TaskReminder"
     }
     ```

4. **Configure Database Connection in `Gui.py`**
   - Similarly, open the `Gui.py` file and update the `username` and `password` variables to match your MySQL credentials:
     ```python
     db_config = {
         "host": "localhost",
         "user": "root",             # Insert Your username
         "password": "MK@SQL",       # Insert Your password
         "database": "TaskReminder"
     }
     ```

5. **Run the Application**
   - After completing the configurations, run the `Gui.py` file to start the Task Reminder application:
     ```bash
     python Gui.py
     ```
   - The GUI will open, allowing you to add, edit, remove, and manage reminders.
