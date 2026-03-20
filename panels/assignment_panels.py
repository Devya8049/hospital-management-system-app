# panels/assignment_panels.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime

import config
import data_manager
import utils
# Import other panels if needed for navigation
from . import billing_panels # To call generate_bill after assigning meds

def show_assign_doctor_panel(app):
    """Displays the initial 'Assign Doctor' panel (search part)."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["assign_doctor"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Assign Doctor", font=("Segoe UI", 14, "bold"), fg="#6a1b9a", bg=panel_bg).pack(pady=(10, 15))
    input_frame = tk.Frame(app.side_panel, bg=panel_bg); input_frame.pack(fill=tk.X, padx=20, pady=10)
    tk.Label(input_frame, text="Enter Patient ID:", font=("Segoe UI", 10, "bold"), bg=panel_bg, fg="#8e24aa").pack(side=tk.LEFT, padx=(0, 5))
    pid_entry = tk.Entry(input_frame, font=("Segoe UI", 10), bg="#f3e5f5", width=20)
    pid_entry.pack(side=tk.LEFT, padx=5); pid_entry.focus_set()
    proceed_button = tk.Button(input_frame, text="Find Patient", command=lambda: find_patient_and_proceed(), bg="#8e24aa", fg="white", activebackground="#ba68c8", font=("Segoe UI", 10, "bold"))
    proceed_button.pack(side=tk.LEFT, padx=5)
    pid_entry.bind("<Return>", lambda event: find_patient_and_proceed()) # Bind Enter key

    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=5, padx=20, fill=tk.X)

    def find_patient_and_proceed():
        app._show_panel_message("", "black", panel_bg) # Clear message
        pid = pid_entry.get().strip()
        if not pid:
            app._show_panel_message("Please enter a Patient ID.", "red", panel_bg); return

        patients = data_manager.load_patients()
        # Find patient index
        patient_index = next((i for i, p in enumerate(patients) if p.get("id") == pid), -1)

        if patient_index == -1:
            app._show_panel_message("Patient Not Found.", "red", panel_bg); return

        # If found, display doctor options
        _display_doctor_options(app, patients, patient_index)

    tk.Button(app.side_panel, text="Cancel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)


def _display_doctor_options(app, patients, patient_index):
    """Helper to show available doctors and handle assignment."""
    p = patients[patient_index]
    panel_bg = config.PANEL_COLORS["assign_doctor"]

    # Validate Age
    try:
        age = int(p.get("age", -1))
        if age < 0: raise ValueError("Invalid age")
    except ValueError:
        app._clear_side_panel(); error_bg = config.PANEL_COLORS["error"]
        app.side_panel.configure(bg=error_bg)
        tk.Label(app.side_panel, text="Error", font=("Segoe UI", 14, "bold"), fg="red", bg=error_bg).pack(pady=10)
        tk.Label(app.side_panel, text=f"Invalid age ('{p.get('age', '')}') for patient {p.get('name', '')} (ID: {p.get('id', '')}).", font=("Segoe UI", 10), bg=error_bg).pack(pady=5, padx=10)
        # Provide a way back to the search panel
        tk.Button(app.side_panel, text="Back", command=lambda: show_assign_doctor_panel(app), bg="#c62828", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)
        return

    now = datetime.datetime.now()
    hour = now.hour

    # --- Night Shift Assignment ---
    if config.NIGHT_SHIFT_START_HOUR <= hour or hour < config.NIGHT_SHIFT_END_HOUR:
        doctors_data = data_manager.load_doctors_local()
        # Find Dr. Prasad (case-insensitive)
        night_doctor = next((d for d in doctors_data if d.get('name','').lower() == 'dr.prasad'), None)
        doctor_name = night_doctor['name'] if night_doctor else "Dr.Prasad" # Fallback name

        patients[patient_index]["doctor"] = doctor_name
        patients[patient_index]["appointment_time"] = now.strftime("%d-%m-%Y %H:%M:%S")
        data_manager.save_patients(patients)
        app.refresh_table()

        # Show confirmation
        app._clear_side_panel(); app.side_panel.configure(bg=panel_bg)
        tk.Label(app.side_panel, text="Doctor Assigned (Night Shift)", font=("Segoe UI", 12, "bold"), fg="#6a1b9a", bg=panel_bg).pack(pady=10)
        info_bg = "#e1bee7" # Slightly darker purple
        tk.Label(app.side_panel, text=f"Patient: {p.get('name', '')} (ID: {p.get('id', '')})\nAssigned: {doctor_name}",
                 font=("Segoe UI", 10), bg=info_bg, justify="left").pack(pady=10, padx=20, fill="x")
        tk.Button(app.side_panel, text="OK", command=app.show_default_side_panel, bg="#8e24aa", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)
        return

    # --- Daytime Doctor Assignment ---
    app._clear_side_panel(); app.side_panel.configure(bg=panel_bg)
    tk.Label(app.side_panel, text=f"Assign Doctor to {p.get('name', '')}", font=("Segoe UI", 14, "bold"), fg="#6a1b9a", bg=panel_bg).pack(pady=(10, 5))
    tk.Label(app.side_panel, text=f"(ID: {p.get('id', '')}, Age: {age}, Gender: {p.get('gender', '')})", font=("Segoe UI", 9), fg="#8e24aa", bg=panel_bg).pack(pady=(0, 15))

    is_female = p.get("gender", "").strip().lower() == "female"
    doctors_data = data_manager.load_doctors_local()
    available_options = [] # List of doctor names
    display_lines = []     # List of strings for display
    num = 1

    # Filter doctors based on specialty and patient gender/age
    for d in doctors_data:
        specialty_lower = d.get("specialty", "").lower()
        is_gynecologist = "gynecologist" in specialty_lower

        # Skip gynecologist if patient is not female or too young
        if is_gynecologist and not (is_female and age > 12):
            continue
        # Skip Dr. Prasad during daytime
        if d.get('name','').lower() == 'dr.prasad':
            continue

        display_lines.append(f"{num}. {d.get('name', '')} ({d.get('specialty', '')})")
        available_options.append(d.get("name", ''))
        num += 1

    if not available_options:
        tk.Label(app.side_panel, text="No suitable doctors available.", font=("Segoe UI", 10, "bold"), fg="red", bg=panel_bg).pack(pady=10)
        tk.Button(app.side_panel, text="Close", command=app.show_default_side_panel, bg="#c62828", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)
        return

    # Display options
    options_frame = tk.Frame(app.side_panel, bg="#e1bee7"); options_frame.pack(pady=10, padx=20, fill=tk.X) # Slightly darker bg
    tk.Label(options_frame, text="Available Doctors:", font=("Segoe UI", 11, "bold"), bg="#e1bee7", fg="#4a148c").pack(anchor="w")
    tk.Label(options_frame, text="\n".join(display_lines), font=("Segoe UI", 10), bg="#e1bee7", fg="#222", justify="left").pack(anchor="w", pady=(5, 10))

    # Input for choice
    input_frame = tk.Frame(app.side_panel, bg=panel_bg); input_frame.pack(pady=5, padx=20, fill=tk.X)
    tk.Label(input_frame, text="Enter choice number:", font=("Segoe UI", 10), bg=panel_bg).pack(side=tk.LEFT)
    choice_var = tk.StringVar()
    entry = tk.Entry(input_frame, textvariable=choice_var, font=("Segoe UI", 10), bg="#f3e5f5", width=5)
    entry.pack(side=tk.LEFT, padx=5); entry.focus_set()

    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=5, padx=20, fill=tk.X)

    def submit_doctor():
        app._show_panel_message("", "black", panel_bg) # Clear message
        try:
            choice_idx = int(choice_var.get()) - 1 # Adjust for 0-based index
        except ValueError:
            app._show_panel_message("Invalid choice. Enter a number.", "red", panel_bg); return

        if not (0 <= choice_idx < len(available_options)):
            app._show_panel_message("Invalid doctor choice number.", "red", panel_bg); return

        selected_doctor_name = available_options[choice_idx]
        patients[patient_index]["doctor"] = selected_doctor_name
        patients[patient_index]["appointment_time"] = now.strftime("%d-%m-%Y %H:%M:%S")
        data_manager.save_patients(patients)
        app.refresh_table()

        # Show success
        app._clear_side_panel(); success_bg = config.PANEL_COLORS["success"]
        app.side_panel.configure(bg=success_bg)
        tk.Label(app.side_panel, text="Success!", font=("Segoe UI", 14, "bold"), fg="green", bg=success_bg).pack(pady=20)
        tk.Label(app.side_panel, text=f"Doctor '{selected_doctor_name}' assigned to {p.get('name', '')}.", font=("Segoe UI", 10), bg=success_bg).pack(pady=5)
        tk.Button(app.side_panel, text="OK", command=app.show_default_side_panel, bg="#8e24aa", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

    # Buttons
    button_bar = tk.Frame(app.side_panel, bg=panel_bg); button_bar.pack(pady=15, fill=tk.X, padx=20, side=tk.BOTTOM)
    tk.Button(button_bar, text="Assign Doctor", command=submit_doctor, bg="#8e24aa", fg="white", activebackground="#ba68c8", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, expand=True, padx=5)
    tk.Button(button_bar, text="Cancel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT, expand=True, padx=5)
    entry.bind("<Return>", lambda event: submit_doctor()) # Bind Enter key


def show_assign_medicines_panel(app):
    """Displays the initial 'Assign Medicines' panel (search part)."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["assign_medicines"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Assign Medicines", font=("Segoe UI", 14, "bold"), fg="#00695c", bg=panel_bg).pack(pady=(10, 15))
    input_frame = tk.Frame(app.side_panel, bg=panel_bg); input_frame.pack(fill=tk.X, padx=20, pady=10)
    tk.Label(input_frame, text="Enter Patient ID:", font=("Segoe UI", 10, "bold"), bg=panel_bg, fg="#00796b").pack(side=tk.LEFT, padx=(0, 5))
    pid_entry = tk.Entry(input_frame, font=("Segoe UI", 10), bg="#e0f2f1", width=20)
    pid_entry.pack(side=tk.LEFT, padx=5); pid_entry.focus_set()
    proceed_button = tk.Button(input_frame, text="Find Patient", command=lambda: find_patient_and_proceed(), bg="#009688", fg="white", activebackground="#4db6ac", font=("Segoe UI", 10, "bold"))
    proceed_button.pack(side=tk.LEFT, padx=5)
    pid_entry.bind("<Return>", lambda event: find_patient_and_proceed()) # Bind Enter key

    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=5, padx=20, fill=tk.X)

    def find_patient_and_proceed():
        app._show_panel_message("", "black", panel_bg) # Clear message
        pid = pid_entry.get().strip()
        if not pid:
            app._show_panel_message("Please enter a Patient ID.", "red", panel_bg); return

        patient = next((p for p in data_manager.load_patients() if p.get("id") == pid), None)
        if not patient:
            app._show_panel_message("Patient Not Found.", "red", panel_bg); return

        # If found, display medicine options
        _display_medicine_options(app, patient)

    tk.Button(app.side_panel, text="Cancel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)


def _display_medicine_options(app, patient):
    """Helper to show medicine listbox and handle assignment."""
    # Basic validation of input
    if not isinstance(patient, dict) or 'id' not in patient:
         messagebox.showerror("Error", "Invalid patient data passed to assign medicines.", parent=app)
         app.show_default_side_panel()
         return

    panel_bg = config.PANEL_COLORS["assign_medicines"]
    app._clear_side_panel(); app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text=f"Assign Medicines to {patient.get('name', 'Unknown')}", font=("Segoe UI", 14, "bold"), fg="#00695c", bg=panel_bg).pack(pady=(10, 5))
    tk.Label(app.side_panel, text=f"(ID: {patient['id']})", font=("Segoe UI", 9), fg="#00796b", bg=panel_bg).pack(pady=(0, 10))

    # Load available medicines
    file_prices = data_manager.load_medicine_prices()
    common_meds = sorted(list(file_prices.keys())) # Sort alphabetically

    # Listbox for selection
    tk.Label(app.side_panel, text="Select from list:", font=("Segoe UI", 10), bg=panel_bg).pack(anchor="w", padx=20)
    listbox_frame = tk.Frame(app.side_panel, bg=panel_bg)
    listbox_frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, font=("Segoe UI", 10), bg="#b2dfdb", fg="#222", height=10, exportselection=False) # Slightly darker bg
    list_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
    listbox.config(yscrollcommand=list_scrollbar.set)

    # Populate listbox and pre-select current meds
    current_assigned_meds = [m.strip() for m in patient.get("medicines", "").split(',') if m.strip()]
    for idx, med in enumerate(common_meds):
        listbox.insert(tk.END, med)
        if med in current_assigned_meds:
            listbox.selection_set(idx)

    list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Custom entry
    tk.Label(app.side_panel, text="Or enter custom medicines (comma separated):", bg=panel_bg, fg="#00796b", font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(10, 0))
    custom_entry = tk.Entry(app.side_panel, bg="#e0f2f1", fg="#222", font=("Segoe UI", 10))
    custom_entry.pack(padx=20, pady=5, fill=tk.X)
    tk.Label(app.side_panel, text="(Optional: Use Name:Price for new items, e.g., Aspirin:15)", bg=panel_bg, fg="#00796b", font=("Segoe UI", 8)).pack(anchor="w", padx=20)

    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=5, padx=20, fill=tk.X)

    def submit_medicines():
        app._show_panel_message("", "black", panel_bg) # Clear message

        # Get selected items from listbox
        selected_meds = [listbox.get(i) for i in listbox.curselection()]

        # Process custom entries
        custom_meds = []
        new_prices_added = False
        local_file_prices = data_manager.load_medicine_prices() # Load fresh copy for updates

        for entry in custom_entry.get().split(","):
            entry = entry.strip()
            if not entry: continue

            med_name = entry
            price = None
            if ":" in entry:
                try:
                    name_part, price_part = entry.split(":", 1)
                    med_name = name_part.strip()
                    price = float(price_part.strip())
                    if price < 0: raise ValueError("Price cannot be negative")
                except ValueError:
                    app._show_panel_message(f"Invalid price format for '{entry}'. Price not added.", "orange", panel_bg)
                    price = None # Reset price if format is bad

            if med_name:
                custom_meds.append(med_name)
                # Add new price to local dict if valid and not already present
                if price is not None and med_name not in local_file_prices:
                    local_file_prices[med_name] = price
                    new_prices_added = True

        # Save updated prices if any new ones were added
        if new_prices_added:
            data_manager.save_medicine_prices(local_file_prices)

        # Combine, remove duplicates, and sort
        all_assigned_meds = sorted(list(set(selected_meds + custom_meds)))

        if not all_assigned_meds:
            app._show_panel_message("No medicines selected or entered.", "red", panel_bg); return

        assigned_meds_str = ", ".join(all_assigned_meds)

        # Save updated patient data
        current_patients = data_manager.load_patients()
        p_index_to_save = next((i for i, p_item in enumerate(current_patients) if p_item.get('id') == patient['id']), -1)

        if p_index_to_save != -1:
             current_patients[p_index_to_save]["medicines"] = assigned_meds_str
             data_manager.save_patients(current_patients)
             app.refresh_table()

             # Show success and option to generate bill
             app._clear_side_panel(); success_bg = config.PANEL_COLORS["success"]
             app.side_panel.configure(bg=success_bg)
             tk.Label(app.side_panel, text="Medicines Assigned!", font=("Segoe UI", 14, "bold"), fg="green", bg=success_bg).pack(pady=20)
             tk.Label(app.side_panel, text=f"Assigned to {patient['name']}:\n{assigned_meds_str}",
                      font=("Segoe UI", 10), bg=success_bg, wraplength=350).pack(pady=5)

             # Get the fully updated patient data for the bill generation
             updated_patient_for_bill = current_patients[p_index_to_save]
             tk.Button(app.side_panel, text="Generate Bill Now",
                       command=lambda p=updated_patient_for_bill: billing_panels.generate_bill(app, p), # Pass app and patient
                       bg="#d84315", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)
             tk.Button(app.side_panel, text="Close Panel", command=app.show_default_side_panel,
                       bg="#009688", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=5)
        else:
             # Should not happen if patient was found initially
             app._show_panel_message("Error: Could not find patient to save medicines.", "red", panel_bg)

    # Buttons
    button_bar = tk.Frame(app.side_panel, bg=panel_bg); button_bar.pack(pady=15, fill=tk.X, padx=20, side=tk.BOTTOM)
    tk.Button(button_bar, text="Assign & Proceed to Bill", command=submit_medicines, bg="#009688", fg="white", activebackground="#4db6ac", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, expand=True, padx=5)
    tk.Button(button_bar, text="Cancel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT, expand=True, padx=5)

