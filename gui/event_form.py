import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def save_event(data):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT,
            time TEXT,
            location TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO events (title, description, date, time, location)
        VALUES (?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Event created successfully!")

def show_event_form():
    window = tk.Toplevel()
    window.title("Create Event")
    window.geometry("450x400")
    window.resizable(False, False)

    # Main frame
    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Create Event Form", font=("Segoe UI", 16, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    fields = ["Title", "Description", "Date", "Time", "Location"]
    entries = {}

    for idx, field in enumerate(fields):
        label = ttk.Label(main_frame, text=field + ":", font=("Segoe UI", 10))
        label.grid(row=idx+1, column=0, sticky="e", padx=10, pady=5)

        entry = ttk.Entry(main_frame, width=30)
        entry.grid(row=idx+1, column=1, pady=5, sticky="w")
        entries[field] = entry

    def submit():
        values = [entries[field].get().strip() for field in fields]

        if not all(values):
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        save_event(values)
        window.destroy()

    submit_btn = ttk.Button(main_frame, text="Create Event", command=submit)
    submit_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)

