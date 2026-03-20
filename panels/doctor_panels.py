# panels/doctor_panels.py
import tkinter as tk
from tkinter import ttk, messagebox

import config
import data_manager
import utils

def show_view_doctors_panel(app):
    """Displays the 'View All Doctors' panel."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["view_doctors"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="View Doctors", font=("Segoe UI", 12, "bold"), fg="#303f9f", bg=panel_bg).pack(pady=(10, 15))

    tree_frame = tk.Frame(app.side_panel, bg=panel_bg)
    tree_frame.pack(expand=True, fill="both", padx=15, pady=5)

    # Use columns from config
    doc_tree = ttk.Treeview(tree_frame, columns=config.DOCTOR_COLS, show="headings", style="Treeview")

    # Configure headings and columns
    doc_tree.heading("Name", text="Name"); doc_tree.column("Name", width=100, stretch=tk.YES) # Wider name
    doc_tree.heading("Specialty", text="Specialty"); doc_tree.column("Specialty", width=100, stretch=tk.YES)
    doc_tree.heading("Qualification", text="Qual."); doc_tree.column("Qualification", width=75, stretch=tk.YES, anchor='center')
    doc_tree.heading("Contact", text="Contact"); doc_tree.column("Contact", width=95, stretch=tk.YES)
    doc_tree.heading("Price", text="Price"); doc_tree.column("Price", width=50, stretch=tk.NO, anchor='e') # Wider price

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=doc_tree.yview, style="Vertical.TScrollbar")
    doc_tree.configure(yscrollcommand=vsb.set)

    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    doc_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    # Load and display doctors
    doctors = data_manager.load_doctors_local()
    doctors.sort(key=lambda d: d.get("name", "").lower()) # Sort by name

    for doc in doctors:
        # Ensure values match the order in config.DOCTOR_COLS
        values = (
            doc.get('name', ''),
            doc.get('specialty', ''),
            doc.get('qualification', ''),
            doc.get('contact', ''),
            f"{doc.get('price', 0.0):.2f}" # Format price
        )
        doc_tree.insert("", "end", values=values)

    tk.Button(app.side_panel, text="Close", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)


def show_add_doctor_panel(app):
    """Displays the 'Add New Doctor' panel."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["add_doctor"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Add New Doctor", font=("Segoe UI", 14, "bold"), fg="#558b2f", bg=panel_bg).pack(pady=(10, 15))
    form_frame = tk.Frame(app.side_panel, bg=panel_bg); form_frame.pack(fill=tk.X, padx=20)

    fields = ["Name", "Specialty", "Qualification", "Contact", "Price"]
    entries = {}
    for i, field in enumerate(fields):
        tk.Label(form_frame, text=field + ":", bg=panel_bg, fg="#689f38", font=("Segoe UI", 10, "bold"), anchor="w").grid(row=i, column=0, sticky="w", pady=3)
        entry = tk.Entry(form_frame, bg="#dcedc8", fg="#222", font=("Segoe UI", 10), width=35)
        entry.grid(row=i, column=1, sticky="ew", pady=3)
        entries[field.lower()] = entry # Use lowercase key

    form_frame.columnconfigure(1, weight=1)
    entries["name"].focus_set() # Focus on the first field

    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=(5,0), fill=tk.X, padx=20)

    def submit_add():
        app._show_panel_message("", "black", panel_bg) # Clear message
        doctors = data_manager.load_doctors_local()

        # Get and validate data
        name = utils.title_case(entries["name"].get().strip())
        specialty = utils.title_case(entries["specialty"].get().strip())
        qualification = entries["qualification"].get().strip().upper()
        contact = entries["contact"].get().strip()
        price_str = entries["price"].get().strip()

        if not name: app._show_panel_message("Error: Doctor Name cannot be empty.", "red", panel_bg); return
        # Check for duplicate name (case-insensitive)
        if any(d.get("name", "").lower() == name.lower() for d in doctors):
            app._show_panel_message(f"Error: Doctor Name '{name}' already exists.", "red", panel_bg); return
        if not specialty: app._show_panel_message("Error: Doctor Specialty cannot be empty.", "red", panel_bg); return
        if not qualification: app._show_panel_message("Error: Doctor Qualification cannot be empty.", "red", panel_bg); return
        if not contact: app._show_panel_message("Error: Doctor Contact cannot be empty.", "red", panel_bg); return

        try:
            price = float(price_str)
            if price < 0: raise ValueError("Price cannot be negative")
        except ValueError:
            app._show_panel_message("Error: Please enter a valid non-negative price.", "red", panel_bg); return

        # Add and save
        new_doctor = {"name": name, "specialty": specialty, "qualification": qualification, "contact": contact, "price": price}
        doctors.append(new_doctor)
        data_manager.save_doctors_local(doctors)

        # Show success
        app._clear_side_panel(); success_bg = config.PANEL_COLORS["success"]
        app.side_panel.configure(bg=success_bg)
        tk.Label(app.side_panel, text="Success!", font=("Segoe UI", 14, "bold"), fg="green", bg=success_bg).pack(pady=20)
        tk.Label(app.side_panel, text=f"Doctor '{name}' added.", font=("Segoe UI", 10), bg=success_bg).pack(pady=5)
        tk.Button(app.side_panel, text="OK", command=app.show_default_side_panel, bg="#43a047", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

    # Buttons
    button_bar = tk.Frame(app.side_panel, bg=panel_bg); button_bar.pack(pady=10, fill=tk.X, padx=20, side=tk.BOTTOM)
    tk.Button(button_bar, text="Add Doctor", command=submit_add, bg="#43a047", fg="white", activebackground="#66bb6a", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, expand=True, padx=5)
    tk.Button(button_bar, text="Cancel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT, expand=True, padx=5)


def show_remove_doctor_panel(app):
    """Displays the 'Remove Doctor' panel."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["remove_doctor"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Remove Doctor", font=("Segoe UI", 14, "bold"), fg="#ff8f00", bg=panel_bg).pack(pady=(10, 15))
    input_frame = tk.Frame(app.side_panel, bg=panel_bg); input_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
    tk.Label(input_frame, text="Enter Doctor Name to Remove:", font=("Segoe UI", 10, "bold"), bg=panel_bg, fg="#ffb300").pack(side=tk.LEFT, padx=(0, 5))
    doc_name_entry = tk.Entry(input_frame, font=("Segoe UI", 10), bg="#ffecb3", width=25)
    doc_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True); doc_name_entry.focus_set()

    button_frame = tk.Frame(app.side_panel, bg=panel_bg); button_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
    remove_button = tk.Button(button_frame, text="Remove Doctor", command=lambda: submit_remove(), bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold"))
    remove_button.pack(pady=5)
    doc_name_entry.bind("<Return>", lambda event: submit_remove()) # Bind Enter key

    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=5, padx=20, fill=tk.X)

    def submit_remove():
        app._show_panel_message("", "black", panel_bg) # Clear message
        doc_name_to_remove = doc_name_entry.get().strip()
        if not doc_name_to_remove:
            app._show_panel_message("Please enter a Doctor Name.", "red", panel_bg); return

        doctors = data_manager.load_doctors_local()
        initial_len = len(doctors)
        # Filter out the doctor (case-insensitive comparison)
        doctors_after_removal = [d for d in doctors if d.get("name", "").lower() != doc_name_to_remove.lower()]

        if len(doctors_after_removal) == initial_len:
            app._show_panel_message(f"Doctor Name '{doc_name_to_remove}' not found.", "red", panel_bg)
        else:
            # Save the updated list
            data_manager.save_doctors_local(doctors_after_removal)
            # Show success message
            app._clear_side_panel(); success_bg = config.PANEL_COLORS["success"]
            app.side_panel.configure(bg=success_bg)
            tk.Label(app.side_panel, text="Success!", font=("Segoe UI", 14, "bold"), fg="green", bg=success_bg).pack(pady=20)
            tk.Label(app.side_panel, text=f"Doctor '{doc_name_to_remove}' removed.", font=("Segoe UI", 10), bg=success_bg).pack(pady=5)
            tk.Button(app.side_panel, text="OK", command=app.show_default_side_panel, bg="#43a047", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

    tk.Button(app.side_panel, text="Cancel", command=app.show_default_side_panel, bg="#757575", fg="white", activebackground="#9e9e9e", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)


def show_update_doctor_panel(app):
    """Displays the initial 'Update Doctor' panel (search part)."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["update_doctor"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Update Doctor", font=("Segoe UI", 14, "bold"), fg="#ad1457", bg=panel_bg).pack(pady=(10, 15))
    input_frame = tk.Frame(app.side_panel, bg=panel_bg); input_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
    tk.Label(input_frame, text="Enter Doctor Name to Update:", font=("Segoe UI", 10, "bold"), bg=panel_bg, fg="#d81b60").pack(side=tk.LEFT, padx=(0, 5))
    doc_name_entry = tk.Entry(input_frame, font=("Segoe UI", 10), bg="#fce4ec", width=25)
    doc_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True); doc_name_entry.focus_set()

    button_frame = tk.Frame(app.side_panel, bg=panel_bg); button_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
    find_button = tk.Button(button_frame, text="Find Doctor", command=lambda: find_doctor_and_proceed(), bg="#f06292", fg="white", activebackground="#f48fb1", font=("Segoe UI", 10, "bold"))
    find_button.pack(pady=5)
    doc_name_entry.bind("<Return>", lambda event: find_doctor_and_proceed()) # Bind Enter key

    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=5, padx=20, fill=tk.X)

    def find_doctor_and_proceed():
        app._show_panel_message("", "black", panel_bg) # Clear message
        doc_name = doc_name_entry.get().strip()
        if not doc_name:
            app._show_panel_message("Please enter a Doctor Name.", "red", panel_bg); return

        # Find doctor (case-insensitive)
        doctor_to_update = next((d for d in data_manager.load_doctors_local() if d.get("name", "").lower() == doc_name.lower()), None)

        if doctor_to_update is None:
            app._show_panel_message(f"Doctor Name '{doc_name}' not found.", "red", panel_bg)
        else:
            # If found, display the update form
            _display_update_doctor_form(app, doctor_to_update)

    tk.Button(app.side_panel, text="Cancel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)


def _display_update_doctor_form(app, doctor_dict):
    """Helper function to display the form for updating a specific doctor."""
    original_name = doctor_dict.get("name", "") # Store original name for lookup
    panel_bg = config.PANEL_COLORS["update_doctor"]
    app._clear_side_panel() # Clear the search widgets
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text=f"Update Doctor: {original_name}", font=("Segoe UI", 14, "bold"), fg="#ad1457", bg=panel_bg).pack(pady=(10, 15))
    form_frame = tk.Frame(app.side_panel, bg=panel_bg); form_frame.pack(fill=tk.X, padx=20)

    fields = ["Name", "Specialty", "Qualification", "Contact", "Price"]
    entries = {} # Use StringVars to hold current values
    for i, field in enumerate(fields):
        tk.Label(form_frame, text=field + ":", bg=panel_bg, fg="#d81b60", font=("Segoe UI", 10, "bold"), anchor="w").grid(row=i, column=0, sticky="w", pady=3)
        key = field.lower()
        current_value = doctor_dict.get(key, '')
        # Format price specifically
        if key == "price":
            current_value = f"{doctor_dict.get('price', 0.0):.2f}"

        entry_var = tk.StringVar(value=current_value)
        entries[key] = entry_var # Store the StringVar
        entry = tk.Entry(form_frame, textvariable=entry_var, bg="#fce4ec", fg="#222", font=("Segoe UI", 10), width=35)
        entry.grid(row=i, column=1, sticky="ew", pady=3)

    form_frame.columnconfigure(1, weight=1)
    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=(5,0), fill=tk.X, padx=20)

    def submit_update():
        app._show_panel_message("", "black", panel_bg) # Clear message

        # Get updated values from StringVars
        updated_name = utils.title_case(entries["name"].get().strip())
        updated_specialty = utils.title_case(entries["specialty"].get().strip())
        updated_qualification = entries["qualification"].get().strip().upper()
        updated_contact = entries["contact"].get().strip()
        updated_price_str = entries["price"].get().strip()

        # Validation
        if not updated_name: app._show_panel_message("Error: Doctor Name cannot be empty.", "red", panel_bg); return
        if not updated_specialty: app._show_panel_message("Error: Doctor Specialty cannot be empty.", "red", panel_bg); return
        if not updated_qualification: app._show_panel_message("Error: Doctor Qualification cannot be empty.", "red", panel_bg); return
        if not updated_contact: app._show_panel_message("Error: Doctor Contact cannot be empty.", "red", panel_bg); return
        try:
            updated_price = float(updated_price_str)
            if updated_price < 0: raise ValueError("Price cannot be negative")
        except ValueError:
            app._show_panel_message("Error: Please enter a valid non-negative price.", "red", panel_bg); return

        doctors = data_manager.load_doctors_local()
        updated = False
        found_index = -1

        # Find the index of the original doctor and check for name conflicts
        for i, doc in enumerate(doctors):
            doc_name_lower = doc.get("name", "").lower()
            if doc_name_lower == original_name.lower():
                found_index = i
            # Check if the *new* name conflicts with *another* doctor
            elif doc_name_lower == updated_name.lower() and original_name.lower() != updated_name.lower():
                app._show_panel_message(f"Error: Another doctor with the name '{updated_name}' already exists.", "red", panel_bg)
                return

        if found_index != -1:
            # Update the doctor's details in the list
            doctors[found_index] = {
                "name": updated_name,
                "specialty": updated_specialty,
                "qualification": updated_qualification,
                "contact": updated_contact,
                "price": updated_price
            }
            updated = True
        else:
            # Should not happen if we came from the search, but handle defensively
            app._show_panel_message(f"Error: Could not find original doctor '{original_name}' to update.", "red", panel_bg)
            return

        if updated:
            data_manager.save_doctors_local(doctors)
            # Show success message
            app._clear_side_panel(); success_bg = config.PANEL_COLORS["success"]
            app.side_panel.configure(bg=success_bg)
            tk.Label(app.side_panel, text="Success!", font=("Segoe UI", 14, "bold"), fg="green", bg=success_bg).pack(pady=20)
            tk.Label(app.side_panel, text=f"Doctor '{updated_name}' (originally '{original_name}') updated.", font=("Segoe UI", 10), bg=success_bg).pack(pady=5)
            tk.Button(app.side_panel, text="OK", command=app.show_default_side_panel, bg="#43a047", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

    # Buttons
    button_bar = tk.Frame(app.side_panel, bg=panel_bg); button_bar.pack(pady=10, fill=tk.X, padx=20, side=tk.BOTTOM)
    tk.Button(button_bar, text="Update Doctor", command=submit_update, bg="#f06292", fg="white", activebackground="#f48fb1", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, expand=True, padx=5)
    # Changed Cancel button to go back to the initial update search panel
    tk.Button(button_bar, text="Cancel", command=lambda: show_update_doctor_panel(app), bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT, expand=True, padx=5)

