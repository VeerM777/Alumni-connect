import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def show_event_list():
    def load_data():
        listbox.delete(0, tk.END)
        cursor.execute("SELECT title, description, date, time, location FROM events")
        events.clear()
        rows = cursor.fetchall()

        if not rows:
            listbox.insert(tk.END, "No events found.")
        else:
            for row in rows:
                formatted = f"{row[0]} on {row[2]} at {row[3]} | {row[4]} \n  {row[1]}"
                events.append((row[0], row[2], row[3])) 
                listbox.insert(tk.END, formatted)
                listbox.insert(tk.END, "—" * 80)

    def delete_selected():
        selected_index = listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select an event to delete.")
            return

        
        real_index = selected_index[0] // 2
        if real_index >= len(events):
            messagebox.showerror("Invalid Selection", "Unable to identify selected event.")
            return

        title, date, time = events[real_index]
        confirm = messagebox.askyesno("Confirm Deletion", f"Delete the event '{title}' on {date} at {time}?")
        if confirm:
            cursor.execute("DELETE FROM events WHERE title=? AND date=? AND time=?", (title, date, time))
            conn.commit()
            load_data()
            messagebox.showinfo("Deleted", f"Event '{title}' has been deleted.")

    window = tk.Toplevel()
    window.title("Upcoming Events")
    window.geometry("700x450")
    window.resizable(False, False)

    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    title_label = ttk.Label(main_frame, text="Upcoming Events", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)

    frame = ttk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 10), width=80, height=15, selectmode=tk.SINGLE)
    listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.config(command=listbox.yview)

    delete_btn = ttk.Button(main_frame, text="Delete Selected Event", command=delete_selected)
    delete_btn.pack(pady=10)

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    events = [] 

    load_data()

    window.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), window.destroy()))
