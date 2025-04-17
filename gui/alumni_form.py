import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def save_alumni(data):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            batch TEXT,
            branch TEXT,
            phone TEXT,
            linkedin TEXT,
            job_title TEXT,
            company TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO alumni (full_name, batch, branch, phone, linkedin, job_title, company)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Alumni registered successfully!")

def show_alumni_form():
    window = tk.Toplevel()
    window.title("Register Alumni")
    window.geometry("450x400")
    window.resizable(False, False)

    # Main frame
    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Alumni Registration Form", font=("Segoe UI", 16, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    fields = ["Full Name", "Batch", "Branch", "Phone", "LinkedIn", "Job Title", "Company"]
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

        if not values[3].isdigit() or len(values[3]) < 10:
            messagebox.showwarning("Invalid Phone", "Please enter a valid phone number.")
            return

        if not values[4].startswith("http"):
            messagebox.showwarning("Invalid LinkedIn", "Please enter a valid LinkedIn URL.")
            return

        save_alumni(values)
        window.destroy()

    submit_btn = ttk.Button(main_frame, text="Submit", command=submit)
    submit_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)

