import deal_with_db as db
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib
import datetime
import time
import threading
from multiprocessing import Process

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "MK@SQL",
    "database": "TaskReminder",
}

#function for password hashing
def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

# GUI Application Class
class Main(tk.Tk):
    
    
    
    
 
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.title("Login App")
        self.geometry("1000x800")
        self.username = None  # To store the logged-in user's username
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.show_login_screen()


    def trigger_task_update(self):
        """Run task loading in a background thread."""
        
        print("thread task")
        
        threading.Thread(target=self.load_tasks, daemon=True).start()

    def trigger_reminder_update(self):
        """Run reminder loading in a background thread."""
        threading.Thread(target=self.load_reminders, daemon=True).start()
        
    def load_reminders(self):
        """Load reminders from the database."""
        
        self.after(0,self._load_reminders)
        
                
    def _load_reminders(self):
        """Load tasks from the database."""
        self.reminders_list.delete(0, tk.END)
        try:
                    
                    reminders = db.get_user_reminders(self.connection, self.user_id)
                    for reminder in reminders:
                        self.reminders_list.insert(tk.END, f"{reminder[0]} - {reminder[1]}-{reminder[2]}")
        except Exception as e:
                print(f"Error loading reminders: {e}")
       

    def load_tasks(self):
    
        self.after(0,self._load_tasks)
        
    def _load_tasks(self):
        """Load tasks from the database."""
        
        self.tasks_list.delete(0, tk.END)
        
        try:
                tasks = db.get_user_tasks(self.connection, self.user_id)
                for task in tasks:
                    self.tasks_list.insert(tk.END, f"{task[0]} - {task[1]} - {task[2]} - {task[3]}")
        except Exception as e:
                print(f"Error loading tasks: {e}")

    def add_task(self, title, description, priority, status, due_date, dialog):
        """Add a new task to the database."""
       
        if not title:
                messagebox.showerror("Error", "Title is required.")
                return

        is_valid, result = self.validate_date(due_date)
        if not is_valid:
                messagebox.showerror("Error", result)
                return
        with self.lock:    
            try:
                
                    db.add_task(
                        self.connection,
                        user_id=self.user_id,
                        title=title,
                        description=description,
                        priority=priority,
                        status=status,
                        due_date=result.strftime("%Y-%m-%d"),
                    )
                    messagebox.showinfo("Success", "Task added successfully.")
                    dialog.destroy()  # Close the dialog after success
                    self.trigger_task_update()  # Load tasks in a background thread
            except Exception as e:
                    messagebox.showerror("Error", f"Failed to add task: {e}")
            self.lock.release

    def delete_selected_task(self):
        """Delete the selected task."""
        try:
            selected_task = self.tasks_list.get(self.tasks_list.curselection())
            task_title = selected_task.split(" - ")[0]  # Extract task title
            with self.lock:
                 db.delete_task(self.connection, self.user_id, task_title) # Call DB deletion
            self.lock.release
            messagebox.showinfo("Success", "Task deleted successfully.")
            self.trigger_task_update()  # Refresh tasks in the background
            self.trigger_reminder_update()  # Refresh reminders in the background
        except IndexError:
            messagebox.showerror("Error", "No task selected.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete task: {e}")

    def add_reminder(self, task_title, reminder_time, dialog):
        """Add a new reminder for the selected task."""
        if not task_title or not reminder_time:
            messagebox.showerror("Error", "Task title and reminder time are required.")
            return

        # Validate the reminder datetime
        is_valid, result = self.validate_datetime(reminder_time)
        if not is_valid:
            messagebox.showerror("Error", result)
            return
        with self.lock:
            try:
                db.add_reminder(
                    self.connection,
                    user_id=self.user_id,
                    task_title=task_title,
                    reminder_time=result.strftime("%Y-%m-%d %H:%M"),  # Format datetime for storage
                    is_sent=False,
                )
                messagebox.showinfo("Success", "Reminder added successfully.")
                dialog.destroy()  # Close the dialog after success
                self.trigger_reminder_update()# Reload reminders in the background
                print("reminders reloades")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add reminder: {e}")
        self.lock.release
    def validate_date(self, date_string, allow_past=False):
        """Validate the date format and check if it's in the future."""
        try:
            date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d")
            if not allow_past and date_obj.date() < datetime.datetime.now().date():
                return False, "Date cannot be in the past."
            return True, date_obj
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."

    def validate_datetime(self, datetime_string):
        """Validate the datetime format and check if it's in the future."""
        try:
            datetime_obj = datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M")
            if datetime_obj <= datetime.datetime.now():
                return False, "Date and time must be in the future."
            return True, datetime_obj
        except ValueError:
            return False, "Invalid datetime format. Use YYYY-MM-DD HH:MM."

    # Additional methods for login, registration, and GUI initialization remain unchanged.
        
    def start_reminder_thread(self):
        """Start the reminder checking thread."""
        self.stop_event.clear()  # Clear the stop event
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()
              
    def perform_reminder_update_to_be_sent(self, task_title):
        """Perform the update of the selected reminder."""
        
        # Update the reminder in the database
        
        db.update_reminder(
                    self.connection,
                    user_id=self.user_id,
                    task_title=task_title,
                    is_sent=True  # Mark the reminder as sent
            )

        self.load_reminders()  # Reload reminders to update the list in the GUI
           
      
    def check_reminders(self):
        """Periodically check for due reminders and display notifications."""
        print("Starting reminder check thread")
        while not self.stop_event.is_set():  # Check if the stop event is set
            try:
                if not hasattr(self, 'user_id') or not self.user_id:
                    print("User  ID is not set. Reminder check skipped.")
                    time.sleep(5)
                    continue

                current_time = datetime.datetime.now()
                print(f"Checking reminders at {current_time}")

                
                reminders = db.get_user_reminders(connection=self.connection, user_id=self.user_id)

                for reminder in reminders:
                    task_title, reminder_time, is_sent = reminder[:3]
                    print(f"Reminder found: {task_title} at {reminder_time}, is_sent: {is_sent}")

                    if isinstance(reminder_time, str):
                        reminder_time = datetime.datetime.strptime(reminder_time, "%Y-%m-%d %H:%M")

                    if reminder_time <= current_time and not is_sent:
                        self.show_notification(task_title, reminder_time)
                        self.perform_reminder_update_to_be_sent(task_title=task_title)

            except Exception as e:
                print(f"Error in check_reminders: {e}")

            time.sleep(5)

    def show_notification(self, task_title, reminder_time):
        """Display a notification for a due reminder."""
        self.after(0, lambda: messagebox.showinfo(
            "Reminder Notification",
            f"Task: {task_title}\nReminder Time: {reminder_time}"
        ))
        
    def show_login_screen(self):
        """Display the login screen."""
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Login", font=("TkDefaultFont", 20)).pack(pady=10)

        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self, font=("TkDefaultFont", 12))
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self, font=("TkDefaultFont", 12), show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self, text="Login", command=self.login_user).pack(pady=10)
        ttk.Button(self, text="Register", command=self.show_register_screen).pack(pady=5)

    def show_register_screen(self):
        """Display the registration screen."""
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Register", font=("TkDefaultFont", 20)).pack(pady=10)

        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self, font=("TkDefaultFont", 12))
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self, font=("TkDefaultFont", 12), show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self, text="Register", command=self.register_user).pack(pady=10)
        ttk.Button(self, text="Back to Login", command=self.show_login_screen).pack(pady=5)

    def show_home_screen(self):
        """Display the home screen after successful login."""
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text=f"Welcome, {self.username}!", font=("TkDefaultFont", 20)).pack(pady=10)

        # Reminders Section
        tk.Label(self, text="Reminders:", font=("TkDefaultFont", 14)).pack(pady=5)
        self.reminders_list = tk.Listbox(self, height=5)
        self.reminders_list.pack(pady=5, fill=tk.BOTH, expand=True)
        self.trigger_reminder_update()

        # Reminder Buttons
        ttk.Button(self, text="Add Reminder", command=self.add_reminder_dialog).pack(pady=5)
        ttk.Button(self, text="Delete Selected Reminder", command=self.delete_selected_reminder).pack(pady=5)
        ttk.Button(self, text="Update Selected reminder", command=self.update_selected_reminder).pack(pady=5)

        # Tasks Section
        tk.Label(self, text="Tasks:", font=("TkDefaultFont", 14)).pack(pady=5)
        self.tasks_list = tk.Listbox(self, height=5)
        self.tasks_list.pack(pady=5, fill=tk.BOTH, expand=True)
        self.load_tasks()
        
        #Task buttons
        ttk.Button(self, text="Add Task", command=self.add_task_dialog).pack(pady=5)
        ttk.Button(self, text="Add Task to Reminders", command=self.add_reminder_dialog).pack(pady=5)
        ttk.Button(self, text="Update Selected Task", command=self.update_selected_task).pack(pady=5)
        ttk.Button(self, text="Delete Selected Task", command=self.delete_selected_task).pack(pady=5)
        ttk.Button(self, text="Logout", command=self.logout).pack(pady=10)
 

    def update_selected_reminder(self):
            """Update the selected reminder."""
            try:
                # Get the selected reminder index
                selected_index = self.reminders_list.curselection()
                if not selected_index:
                    messagebox.showerror("Error", "No reminder selected.")
                    return

                # Retrieve the reminder details
                selected_reminder = self.reminders_list.get(selected_index[0])
                task_title = selected_reminder.split(" - ")[0]  # Extract task title
                old_reminder_time = selected_reminder.split(" - ")[1].split("-")[0].strip()

                # Open update dialog
                dialog = tk.Toplevel(self)
                dialog.title("Update Reminder")
                dialog.geometry("300x200")

                tk.Label(dialog, text=f"Task: {task_title}", font=("TkDefaultFont", 12)).pack(pady=10)

                tk.Label(dialog, text="New Reminder Time (YYYY-MM-DD HH:MM):").pack(pady=5)
                new_reminder_time_entry = ttk.Entry(dialog)
                new_reminder_time_entry.insert(0, old_reminder_time)  # Pre-fill with existing reminder time
                new_reminder_time_entry.pack(pady=5)

                ttk.Button(
                    dialog,
                    text="Update Reminder",
                    command=lambda: self.perform_reminder_update(
                        task_title,
                        new_reminder_time_entry.get(),
                        dialog
                    )
                ).pack(pady=10)

            except IndexError:
                messagebox.showerror("Error", "No reminder selected.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load reminder details: {e}")

                    
                    
 

    def add_reminder_dialog(self):
        """Display a dialog box to add a reminder for a selected task."""
        # Check if a task is selected
        selected_task_index = self.tasks_list.curselection()
        if not selected_task_index:
            messagebox.showerror("Error", "Please select a task to add a reminder.")
            return

        # Get the selected task title
        selected_task = self.tasks_list.get(selected_task_index[0])
        task_title = selected_task.split(" - ")[0]  # Extract task title

        # Create dialog for adding reminder
        dialog = tk.Toplevel(self)
        dialog.title("Add Reminder")
        dialog.geometry("300x200")

        tk.Label(dialog, text=f"Task: {task_title}", font=("TkDefaultFont", 12)).pack(pady=10)
        tk.Label(dialog, text="Reminder Time (YYYY-MM-DD HH:MM):").pack(pady=5)
        reminder_time_entry = ttk.Entry(dialog)
        reminder_time_entry.pack(pady=5)

        ttk.Button(
            dialog,
            text="Add Reminder",
            command=lambda: self.add_reminder(
                task_title,  # Use the selected task title
                reminder_time_entry.get(),
                dialog
            )
        ).pack(pady=10)
        
        
    def perform_reminder_update(self, task_title, new_reminder_time, dialog):
        """Perform the update of the selected reminder."""
        if not task_title or not new_reminder_time:
            messagebox.showerror("Error", "Task title and new reminder time are required.")
            return

    # Validate the new reminder time
        is_valid, result = self.validate_datetime(new_reminder_time)
        if not is_valid:
            messagebox.showerror("Error", result)
            return
        with self.lock:
            try:
                # Update the reminder in the database
                db.update_reminder(
                    self.connection,
                    user_id=self.user_id,
                    task_title=task_title,
                    reminder_time=result.strftime("%Y-%m-%d %H:%M"),  # Format datetime for storage
                    is_sent=True  # Reset is_sent for the updated reminder
                )
                messagebox.showinfo("Success", "Reminder updated successfully.")
                dialog.destroy()  # Close the dialog after success
                self.load_reminders()  # Reload reminders to update the list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update reminder: {e}")
        self.lock.release                 
    def add_task_dialog(self):
        status="pending"
        """Display a dialog box to add a new task."""
        dialog = tk.Toplevel(self)
        dialog.title("Add Task")
        dialog.geometry("300x600")

        tk.Label(dialog, text="Title:").pack(pady=5)
        title_entry = ttk.Entry(dialog)
        title_entry.pack(pady=5)

        tk.Label(dialog, text="Description:").pack(pady=5)
        description_entry = tk.Text(dialog, height=5)
        description_entry.pack(pady=5)

        tk.Label(dialog, text="Priority:").pack(pady=5)
        priority_combobox = ttk.Combobox(dialog, values=["Low", "Medium", "High"])
        priority_combobox.pack(pady=5)



        tk.Label(dialog, text="Due Date (YYYY-MM-DD):").pack(pady=5)
        due_date_entry = ttk.Entry(dialog)
        due_date_entry.pack(pady=5)

        ttk.Button(
            dialog,  # Use dialog as the parent, not self
            text="Add Task",
            command=lambda: self.add_task(
                title_entry.get(),
                description_entry.get("1.0", tk.END).strip(),
                priority_combobox.get(),
                status,
                due_date_entry.get(),
                dialog  # Pass dialog for closing after adding
            )
        ).pack(pady=10)

    def logout(self):
        """Logout the user and return to the login screen."""
        self.stop_event.set()  # Signal the reminder thread to stop
        if hasattr(self, 'reminder_thread'):
         self.reminder_thread.join()  # Wait for the thread to finish
        self.username = None
        self.show_login_screen()

        
        

    def login_user(self):
        """Authenticate the user using the database."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Check if username or password fields are empty
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        try:
            # Hash the entered password and validate it in the database
            password_hash = hash_password(password)
            user_id = db.is_user_in_db(self.connection, username, password_hash)

            if user_id:
                self.username = username  # Store username
                self.user_id = user_id  # Store user_id for session management
                self.start_reminder_thread()  # Start the reminder thread
                self.show_home_screen()  # Show the main home screen
            else:
                messagebox.showerror("Error", "Invalid username or password.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")
    def register_user(self):
        """Register a new user in the database."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Check for empty fields
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        # Check if the username already exists in the database
        if db.get_user_id(self.connection, username):
            messagebox.showerror("Error", "Username already exists.")
            return

        try:
            # Hash the password and add the user to the database
            password_hash = hash_password(password)
            db.add_user(self.connection, username, password_hash)
            messagebox.showinfo("Success", "Registration successful.")
            self.show_login_screen()  # Go back to the login screen
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    
    def add_reminder(self, task_title, reminder_time, dialog):
    
        """Add a new reminder for the selected task."""
        if not task_title or not reminder_time:
            messagebox.showerror("Error", "Task title and reminder time are required.")
            return

        # Validate the reminder datetime
        is_valid, result = self.validate_datetime(reminder_time)
        if not is_valid:
            messagebox.showerror("Error", result)
            return
        with self.lock:
            try:
                db.add_reminder(
                    self.connection,
                    user_id=self.user_id,
                    task_title=task_title,
                    reminder_time=result.strftime("%Y-%m-%d %H:%M"),  # Format datetime for storage
                    is_sent=False,
                )
                messagebox.showinfo("Success", "Reminder added successfully.")
                dialog.destroy()  # Close the dialog after success
                self.trigger_reminder_update()  # Reload reminders to update the list
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add reminder: {e}")
            self.lock.release
            
    def update_selected_task(self):
        """Update the selected task."""
        try:
            # Get the selected task index
            selected_index = self.tasks_list.curselection()
            if not selected_index:
                messagebox.showerror("Error", "No task selected.")
                return

            # Retrieve the task title
            selected_task = self.tasks_list.get(selected_index[0])
            task_title = selected_task.split(" - ")[0]  # Extract task title
        except IndexError:
            messagebox.showerror("Error", "No task selected.")
            return

        

        # Open update dialog
        dialog = tk.Toplevel(self)
        dialog.title("Update Task")
        dialog.geometry("300x400")

        tk.Label(dialog, text="New Title:").pack(pady=5)
        title_entry = ttk.Entry(dialog)
        title_entry.insert(0, task_title)  # Pre-fill with existing title
        title_entry.pack(pady=5)

        tk.Label(dialog, text="New Description:").pack(pady=5)
        description_entry = tk.Text(dialog, height=5)
        description_entry.pack(pady=5)

        tk.Label(dialog, text="New Priority:").pack(pady=5)
        priority_combobox = ttk.Combobox(dialog, values=["Low", "Medium", "High"])
        priority_combobox.pack(pady=5)

        tk.Label(dialog, text="New Status:").pack(pady=5)
        status_combobox = ttk.Combobox(dialog, values=["Pending", "Overdue", "Completed"])
        status_combobox.pack(pady=5)

        tk.Label(dialog, text="New Due Date (YYYY-MM-DD):").pack(pady=5)
        due_date_entry = ttk.Entry(dialog)
        due_date_entry.pack(pady=5)

        ttk.Button(
            dialog,
            text="Update Task",
            command=lambda: self.perform_task_update(
                task_title,  # Original title
                title_entry.get(),
                description_entry.get("1.0", tk.END).strip(),
                priority_combobox.get(),
                status_combobox.get(),
                due_date_entry.get(),
                dialog
            )
        ).pack(pady=10)

    def perform_task_update(self, old_title, new_title, description, priority, status, due_date, dialog):
        """Perform the update of the selected task."""
        if not new_title or not old_title:
            messagebox.showerror("Error", "Task title is required.")
            return
        with self.lock:
            try:
                db.update_task(
                    self.connection,
                    user_id=self.user_id,
                    old_title=old_title,
                    title=new_title,
                    description=description,
                    priority=priority,
                    status=status,
                    due_date=due_date
                )
                messagebox.showinfo("Success", "Task updated successfully.")
                dialog.destroy()  # Close the dialog after success
                self.trigger_task_update() # Reload tasks to update the list
                self.trigger_reminder_update()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update task: {e}")
        self.lock.release
    
    def delete_selected_reminder(self):
            """Delete the selected reminder."""
            try:
                selected_reminder = self.reminders_list.get(self.reminders_list.curselection())
                task_title = selected_reminder.split(" - ")[0]  # Extract task title
                with self.lock:
                    db.delete_reminder(self.connection, self.user_id, task_title)  # Call DB deletion
                self.lock.release
                messagebox.showinfo("Success", "Reminder deleted successfully.")
                self.trigger_reminder_update()  # Refresh reminder list
            except IndexError:
                messagebox.showerror("Error", "No reminder selected.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete reminder: {e}")

def run_app():
    try:
        connection = mysql.connector.connect(**db_config)
        app = Main(connection)
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")


# Main Application
if __name__ == "__main__":
    processes = []
    number_of_windows=input('enter the number of windows')
    for i in range(int(number_of_windows)):  # Number of instances you want to run
        process = Process(target=run_app)
        process.start()
        processes.append(process)

    # Optionally, wait for all processes to complete
    for process in processes:
        process.join()