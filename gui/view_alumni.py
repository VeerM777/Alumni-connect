import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def show_alumni_list(parent=None):
    def load_data():
        listbox.delete(0, tk.END)
        cursor.execute("SELECT full_name, batch, branch, phone, linkedin, job_title, company FROM alumni")
        rows = cursor.fetchall()

        if not rows:
            listbox.insert(tk.END, "No alumni records found.")
        else:
            for row in rows:
                formatted = f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} @ {row[6]}"
                listbox.insert(tk.END, formatted)

    def delete_selected():
        selected = listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an alumni record to delete.")
            return
        
        selected_text = listbox.get(selected[0])
        parts = selected_text.split('|')
        if len(parts) < 4:
            messagebox.showerror("Invalid Record", "Selected record can't be identified.")
            return
        
        full_name = parts[0].strip()
        phone = parts[3].strip()

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete:\n{full_name} ({phone})?")
        if confirm:
            cursor.execute("DELETE FROM alumni WHERE full_name = ? AND phone = ?", (full_name, phone))
            conn.commit()
            load_data()
            messagebox.showinfo("Deleted", f"Record for {full_name} has been deleted.")

    window = tk.Toplevel(parent)
    window.title("Alumni List")
    window.geometry("700x450")
    window.resizable(False, False)

    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    title_label = ttk.Label(main_frame, text="Alumni List", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)

    frame = ttk.Frame(main_frame)
    frame.pack(fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 10), width=80, height=15, selectmode=tk.SINGLE)
    listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.config(command=listbox.yview)

    # Delete Button
    delete_btn = ttk.Button(main_frame, text="Delete Selected", command=delete_selected)
    delete_btn.pack(pady=10)

    # DB connection
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    load_data()

    window.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), window.destroy()))
