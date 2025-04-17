import tkinter as tk
from tkinter import ttk

# Import functions for each section
from gui.alumni_form import show_alumni_form
from gui.event_form import show_event_form
from gui.search_alumni import search_alumni
from gui.view_alumni import show_alumni_list
from gui.view_events import show_event_list

def open_alumni_form():
    show_alumni_form()

def open_event_form():
    show_event_form()

def open_search_alumni():
    search_alumni()

def open_view_alumni():
    show_alumni_list()

def open_view_events():
    show_event_list()

def create_dashboard():
    window = tk.Tk()
    window.title("Alumni Connect Portal - Dashboard")
    window.geometry("600x400")
    window.resizable(False, False)

    # Main frame
    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Title label
    title_label = ttk.Label(main_frame, text="Alumni Connect Dashboard", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)

    # Dashboard buttons
    ttk.Button(main_frame, text="Register Alumni", width=30, command=open_alumni_form).pack(pady=5)
    ttk.Button(main_frame, text="Create Event", width=30, command=open_event_form).pack(pady=5)
    ttk.Button(main_frame, text="Search Alumni", width=30, command=open_search_alumni).pack(pady=5)
    ttk.Button(main_frame, text="View Alumni List", width=30, command=open_view_alumni).pack(pady=5)
    ttk.Button(main_frame, text="View Events", width=30, command=open_view_events).pack(pady=5)

    window.mainloop()

if __name__ == "__main__":
    create_dashboard()
