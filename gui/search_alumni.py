import tkinter as tk
from tkinter import ttk
import sqlite3

def search_alumni():
    def perform_search():
        keyword = search_entry.get()
        listbox.delete(0, tk.END)

        if not keyword:
            listbox.insert(tk.END, "Enter a search term.")
            return

        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        query = f"""
        SELECT full_name, batch, branch, company FROM alumni
        WHERE batch LIKE ? OR branch LIKE ? OR company LIKE ?
        """
        keyword_wild = f"%{keyword}%"
        cursor.execute(query, (keyword_wild, keyword_wild, keyword_wild))
        results = cursor.fetchall()
        conn.close()

        if results:
            for r in results:
                listbox.insert(tk.END, f"{r[0]} | Batch: {r[1]} | {r[2]} @ {r[3]}")
        else:
            listbox.insert(tk.END, "No matching alumni found.")

    win = tk.Toplevel()
    win.title("Search Alumni")
    win.geometry("600x400")
    win.resizable(False, False)

    # Main frame
    main_frame = ttk.Frame(win, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Search Alumni by Batch, Branch, or Company", font=("Segoe UI", 14, "bold"))
    title_label.pack(pady=10)

    # Search Entry
    search_entry = ttk.Entry(main_frame, width=50, font=("Segoe UI", 10))
    search_entry.pack(pady=5)

    # Search Button
    search_button = ttk.Button(main_frame, text="Search", command=perform_search)
    search_button.pack(pady=10)

    # Results Listbox
    listbox = tk.Listbox(main_frame, width=80, height=10, font=("Segoe UI", 10), selectmode=tk.SINGLE)
    listbox.pack(fill="both", expand=True, padx=10, pady=10)

