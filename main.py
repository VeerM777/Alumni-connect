import tkinter as tk
from gui.alumni_form import show_alumni_form
from gui.event_form import show_event_form
from gui.view_alumni import show_alumni_list
from gui.view_events import show_event_list
from gui.search_alumni import search_alumni
from utils.export_csv import export_alumni_to_csv
from dashboard import create_dashboard

def main():
   
    create_dashboard()  
    
if __name__ == "__main__":
    main()
