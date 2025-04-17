# utils/export_csv.py
import sqlite3
import csv
from tkinter import messagebox

def export_alumni_to_csv(filename="alumni_export.csv"):
    try:
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alumni")
        rows = cursor.fetchall()
        headers = [description[0] for description in cursor.description]
        conn.close()

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        messagebox.showinfo("Export Success", f"Data exported to {filename} successfully.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))
