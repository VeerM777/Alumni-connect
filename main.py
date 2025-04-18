import tkinter as tk
import sqlite3
import os
from gui.alumni_form import show_alumni_form
from gui.event_form import show_event_form
from gui.view_alumni import show_alumni_list
from gui.view_events import show_event_list
from gui.search_alumni import search_alumni
from utils.export_csv import export_alumni_to_csv
from utils.init_db import init_db
from gui.login import login_window
from dashboard import create_dashboard

def main():
    # Check if database exists and has required tables
    if not os.path.exists("db.sqlite3"):
        init_db()
    else:
        # Check if users table exists
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            init_db()
        conn.close()
            
    def on_login(user):
        create_dashboard(user)
    login_window(on_login)

if __name__ == "__main__":
    main()
