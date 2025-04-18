import tkinter as tk
from tkinter import ttk

# Import functions for each section
from gui.alumni_form import show_alumni_form
from gui.event_form import show_event_form
from gui.search_alumni import search_alumni
from gui.view_alumni import show_alumni_list
from gui.view_events import show_event_list
from gui.update_alumni import update_alumni
from gui.invite_alumni import invite_alumni
from gui.mentorship import request_mentorship
from utils.export_csv import export_alumni_to_csv

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

def create_dashboard(user):
    window = tk.Tk()
    window.title("Alumni Connect Portal - Dashboard")
    window.geometry("600x450")  # Slightly taller for more buttons
    window.resizable(False, False)

    main_frame = ttk.Frame(window, padding=20)
    main_frame.pack(fill="both", expand=True)

    title_label = ttk.Label(main_frame, text=f"Alumni Connect Dashboard ({user['role'].capitalize()})", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=10)

    # Common features (visible to all users)
    ttk.Button(main_frame, text="Search Alumni", width=30, command=open_search_alumni).pack(pady=5)
    ttk.Button(main_frame, text="View Alumni List", width=30, command=open_view_alumni).pack(pady=5)
    ttk.Button(main_frame, text="View Events", width=30, command=open_view_events).pack(pady=5)
    ttk.Button(main_frame, text="Export Alumni Data to CSV", width=30, command=export_alumni_to_csv).pack(pady=5)

    # Teacher-only features
    if user["role"] == "teacher":
        ttk.Button(main_frame, text="Register Alumni", width=30, command=open_alumni_form).pack(pady=5)
        ttk.Button(main_frame, text="Create Event", width=30, command=open_event_form).pack(pady=5)
        ttk.Button(main_frame, text="Update Alumni Career Info", width=30, command=update_alumni).pack(pady=5)
        ttk.Button(main_frame, text="Invite Alumni to Event", width=30, command=lambda: invite_alumni(user)).pack(pady=5)
    
    # Student-only features
    if user["role"] == "student":
        ttk.Button(main_frame, text="Request Mentorship", width=30, command=lambda: request_mentorship(user)).pack(pady=5)

    # Logout button
    def logout():
        window.destroy()
        from gui.login import login_window
        login_window(lambda user: create_dashboard(user))
        
    ttk.Button(main_frame, text="Logout", width=30, command=logout).pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    # This is just for testing - should not be called directly
    create_dashboard({"username": "test", "role": "teacher", "email": "test@example.com"})
