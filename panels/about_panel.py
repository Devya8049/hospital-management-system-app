# panels/about_panel.py
import tkinter as tk
from tkinter import ttk

import config
import data_manager # To load about text

def show_about_panel(app):
    """Displays the 'About' information panel."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["about"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="About EMPOWER HOSPITAL", font=("Segoe UI", 14, "bold"), fg="#4e342e", bg=panel_bg).pack(pady=(10, 15))

    about_text = data_manager.load_about_text() # Load text using data_manager

    # Frame for Text and Scrollbar
    text_frame = tk.Frame(app.side_panel, bg="#d7ccc8", bd=1, relief=tk.SOLID) # Slightly darker bg
    text_frame.pack(expand=True, fill="both", padx=20, pady=10)

    about_text_widget = tk.Text(text_frame, wrap="word", font=("Segoe UI", 10), bg="#efebe9", fg="#3e2723", bd=0, height=15) # Match panel bg
    about_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=about_text_widget.yview)
    about_text_widget.config(yscrollcommand=about_scrollbar.set)

    about_text_widget.insert("1.0", about_text)
    about_text_widget.config(state="disabled") # Make read-only

    about_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    about_text_widget.pack(side=tk.LEFT, expand=True, fill="both", padx=5, pady=5)

    tk.Button(app.side_panel, text="Close", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)

