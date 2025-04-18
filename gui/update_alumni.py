import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def update_alumni():
    def search():
        phone = phone_entry.get().strip()
        if not phone:
            messagebox.showwarning("Input Error", "Enter phone number to search.")
            return
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, batch, branch, phone, linkedin, job_title, company FROM alumni WHERE phone=?", (phone,))
        row = cursor.fetchone()
        conn.close()
        if row:
            for idx, field in enumerate(fields):
                entries[field].delete(0, tk.END)
                entries[field].insert(0, row[idx])
        else:
            messagebox.showinfo("Not Found", "No alumni found with that phone number.")

    def update():
        values = [entries[field].get().strip() for field in fields]
        if not all(values):
            messagebox.showwarning("Input Error", "All fields are required!")
            return
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE alumni SET full_name=?, batch=?, branch=?, linkedin=?, job_title=?, company=?
            WHERE phone=?
        ''', (values[0], values[1], values[2], values[4], values[5], values[6], values[3]))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Alumni info updated successfully!")

    window = tk.Toplevel()
    window.title("Update Alumni Career Info")
    window.geometry("450x450")
    window.resizable(False, False)

    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(main_frame, text="Enter Phone to Search:", font=("Segoe UI", 10)).grid(row=0, column=0, pady=5, sticky="e")
    phone_entry = ttk.Entry(main_frame, width=30)
    phone_entry.grid(row=0, column=1, pady=5, sticky="w")
    ttk.Button(main_frame, text="Search", command=search).grid(row=0, column=2, padx=5)

    fields = ["Full Name", "Batch", "Branch", "Phone", "LinkedIn", "Job Title", "Company"]
    entries = {}
    for idx, field in enumerate(fields):
        ttk.Label(main_frame, text=field + ":", font=("Segoe UI", 10)).grid(row=idx+1, column=0, sticky="e", padx=10, pady=5)
        entry = ttk.Entry(main_frame, width=30)
        entry.grid(row=idx+1, column=1, pady=5, sticky="w")
        entries[field] = entry

    ttk.Button(main_frame, text="Update", command=update).grid(row=len(fields)+2, column=0, columnspan=2, pady=20)