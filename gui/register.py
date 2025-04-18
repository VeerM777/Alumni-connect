import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib

def register_user():
    def submit():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        email = email_entry.get().strip()
        role = role_var.get()
        if not username or not password or not email or not role:
            messagebox.showwarning("Input Error", "All fields are required!")
            return
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        try:
            # Hash the password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                           (username, hashed_password, email, role))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
            window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            conn.close()

    window = tk.Toplevel()
    window.title("Register")
    window.geometry("350x350")
    window.resizable(False, False)

    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(main_frame, text="Username (SAP ID or Email):").pack(pady=5)
    username_entry = ttk.Entry(main_frame, width=30)
    username_entry.pack(pady=5)

    ttk.Label(main_frame, text="Password:").pack(pady=5)
    password_entry = ttk.Entry(main_frame, width=30, show="*")
    password_entry.pack(pady=5)

    ttk.Label(main_frame, text="Email:").pack(pady=5)
    email_entry = ttk.Entry(main_frame, width=30)
    email_entry.pack(pady=5)

    ttk.Label(main_frame, text="Role:").pack(pady=5)
    role_var = tk.StringVar(value="student")
    role_combo = ttk.Combobox(main_frame, textvariable=role_var, state="readonly", width=27)
    role_combo['values'] = ("student", "teacher")
    role_combo.pack(pady=5)

    ttk.Button(main_frame, text="Register", command=submit).pack(pady=15)