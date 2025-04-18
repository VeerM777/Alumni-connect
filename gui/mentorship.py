import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from email.message import EmailMessage
from utils.config import send_email

def request_mentorship(user):
    window = tk.Toplevel()
    window.title("Request Mentorship")
    window.geometry("600x400")
    window.resizable(False, False)

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("SELECT id, full_name, batch, branch FROM alumni")
    alumni = cursor.fetchall()
    if not alumni:
        messagebox.showinfo("No Alumni", "No alumni found. Please register alumni first.")
        window.destroy()
        return

    ttk.Label(window, text="Select Alumni Mentor:", font=("Segoe UI", 12)).pack(pady=10)
    alumni_combo = ttk.Combobox(window, state="readonly", width=50)
    alumni_combo['values'] = [f"{a[1]} ({a[2]}, {a[3]}) [ID:{a[0]}]" for a in alumni]
    alumni_combo.pack(pady=5)

    ttk.Label(window, text="Your Name:", font=("Segoe UI", 10)).pack(pady=10)
    student_entry = ttk.Entry(window, width=40)
    student_entry.pack(pady=5)

    ttk.Label(window, text="Your Message:", font=("Segoe UI", 10)).pack(pady=10)
    message_entry = tk.Text(window, width=50, height=5)
    message_entry.pack(pady=5)

    def send_request():
        idx = alumni_combo.current()
        if idx == -1 or not student_entry.get().strip() or not message_entry.get("1.0", tk.END).strip():
            messagebox.showwarning("Input Error", "Please fill all fields and select a mentor.")
            return
        mentor_id = alumni[idx][0]
        student_name = student_entry.get().strip()
        msg = message_entry.get("1.0", tk.END).strip()
        cursor.execute("INSERT INTO mentorship_requests (mentor_id, student_name, message) VALUES (?, ?, ?)",
                       (mentor_id, student_name, msg))
        conn.commit()
        cursor.execute("SELECT email FROM users WHERE username=(SELECT phone FROM alumni WHERE id=?)", (mentor_id,))
        mentor_email = cursor.fetchone()
        if mentor_email and mentor_email[0]:
            success, message = send_email(
                from_email=user['email'],
                to_email=mentor_email[0],
                subject="Mentorship Request",
                message=f"{student_name} has requested mentorship:\n\n{msg}"
            )
            if not success:
                messagebox.showwarning("Email Error", f"Could not send email: {message}")
        messagebox.showinfo("Request Sent", "Your mentorship request has been sent.")
        window.destroy()

    ttk.Button(window, text="Send Request", command=send_request).pack(pady=20)
    window.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), window.destroy()))