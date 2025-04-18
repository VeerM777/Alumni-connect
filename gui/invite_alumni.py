import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from email.message import EmailMessage
from utils.config import send_email

def invite_alumni(user):
    window = tk.Toplevel()
    window.title("Invite Alumni to Event")
    window.geometry("600x500")
    window.resizable(False, False)

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Fetch events
    cursor.execute("SELECT id, title, date FROM events")
    events = cursor.fetchall()
    if not events:
        messagebox.showinfo("No Events", "No events found. Please create an event first.")
        window.destroy()
        return

    # Fetch alumni
    cursor.execute("SELECT id, full_name, batch FROM alumni")
    alumni = cursor.fetchall()
    if not alumni:
        messagebox.showinfo("No Alumni", "No alumni found. Please register alumni first.")
        window.destroy()
        return

    ttk.Label(window, text="Select Event:", font=("Segoe UI", 12)).pack(pady=10)
    event_var = tk.StringVar()
    event_combo = ttk.Combobox(window, textvariable=event_var, state="readonly", width=50)
    event_combo['values'] = [f"{e[1]} on {e[2]} (ID:{e[0]})" for e in events]
    event_combo.pack(pady=5)

    ttk.Label(window, text="Select Alumni to Invite:", font=("Segoe UI", 12)).pack(pady=10)
    alumni_listbox = tk.Listbox(window, selectmode=tk.MULTIPLE, width=60, height=15)
    for a in alumni:
        alumni_listbox.insert(tk.END, f"{a[1]} ({a[2]}) [ID:{a[0]}]")
    alumni_listbox.pack(pady=5)

    def send_invites():
        event_idx = event_combo.current()
        if event_idx == -1:
            messagebox.showwarning("Select Event", "Please select an event.")
            return
        selected_indices = alumni_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Select Alumni", "Please select at least one alumni.")
            return
        event_id = events[event_idx][0]
        alumni_ids = [alumni[i][0] for i in selected_indices]
        for aid in alumni_ids:
            cursor.execute("INSERT INTO invitations (alumni_id, event_id) VALUES (?, ?)", (aid, event_id))
            # Fetch alumni email
            cursor.execute("SELECT email FROM users WHERE username=(SELECT phone FROM alumni WHERE id=?)", (aid,))
            alumni_email = cursor.fetchone()
            if alumni_email and alumni_email[0]:
                success, message = send_email(
                    from_email=user['email'],
                    to_email=alumni_email[0],
                    subject=f"Invitation to Event: {events[event_idx][1]}",
                    message=f"You are invited to the event '{events[event_idx][1]}' on {events[event_idx][2]}."
                )
                if not success:
                    messagebox.showwarning("Email Error", f"Could not send email: {message}")
        conn.commit()
        messagebox.showinfo("Invitations Sent", "Selected alumni have been invited to the event.")
        window.destroy()

    ttk.Button(window, text="Send Invitations", command=send_invites).pack(pady=20)
    window.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), window.destroy()))