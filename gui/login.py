import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from gui.register import register_user
import hashlib

def login_window(on_success):
    def attempt_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Enter both username and password.")
            return
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        # Hash the password the same way as in register
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT username, role, email FROM users WHERE username=? AND password=?", 
                      (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        if user:
            window.destroy()
            on_success({"username": user[0], "role": user[1], "email": user[2]})
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    window = tk.Tk()
    window.title("Login")
    window.geometry("350x250")
    window.resizable(False, False)

    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(main_frame, text="Username (SAP ID or Email):").pack(pady=5)
    username_entry = ttk.Entry(main_frame, width=30)
    username_entry.pack(pady=5)

    ttk.Label(main_frame, text="Password:").pack(pady=5)
    password_entry = ttk.Entry(main_frame, width=30, show="*")
    password_entry.pack(pady=5)

    ttk.Button(main_frame, text="Login", command=attempt_login).pack(pady=10)
    ttk.Button(main_frame, text="Register", command=register_user).pack(pady=5)

    window.mainloop()