# c:\Users\devya\OneDrive\Desktop\Empower Hospital\panels\patient_panels.py

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

import config
import data_manager
import utils
# Import other panel modules ONLY if needed (e.g., for navigating between panels)
from . import assignment_panels # To call _display_medicine_options
# from . import billing_panels    # To call generate_bill (if needed directly, though unlikely)

def show_add_patient_panel(app):
    """Displays the 'Add New Patient' panel."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["add_patient"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Add New Patient", font=("Segoe UI", 14, "bold"), fg="#1b5e20", bg=panel_bg).pack(pady=(10, 15))
    form_frame = tk.Frame(app.side_panel, bg=panel_bg); form_frame.pack(fill=tk.X, padx=20)

    fields = ["Patient ID", "Name", "Age", "Gender", f"Phone Number ({config.PHONE_DIGITS} digits)", "Address", "Email"]
    entries = {}
    for i, field in enumerate(fields):
        tk.Label(form_frame, text=field + ":", bg=panel_bg, fg="#2e7d32", font=("Segoe UI", 10, "bold"), anchor="w").grid(row=i, column=0, sticky="w", pady=2)
        # Determine key for entries dict
        key = "id" if field == "Patient ID" else \
              "contact" if "Phone" in field else \
              "address" if "Address" in field else \
              "email" if "Email" in field else \
              field.lower()
        entry = tk.Entry(form_frame, bg="#e8f5e9", fg="#222", font=("Segoe UI", 10), width=35)
        entry.grid(row=i, column=1, sticky="ew", pady=2)
        entries[key] = entry
        if key == "id": entry.focus_set() # Focus on Patient ID

    # Disease Selection
    tk.Label(form_frame, text="Disease:", bg=panel_bg, fg="#2e7d32", font=("Segoe UI", 10, "bold"), anchor="w").grid(row=len(fields), column=0, sticky="w", pady=(10, 2))
    # Combine auto-assign keys with common diseases, remove duplicates, sort, add 'Other'
    auto_keys = [k.capitalize() for k in config.AUTO_ASSIGN_MEDS.keys()]
    common_diseases_base = ["Fever", "Cold", "Headache", "Cough", "Hypertension", "Diabetes", "Asthma", "Allergy", "Stomach Pain", "Back Pain"]
    all_disease_options = sorted(list(set(auto_keys + common_diseases_base))) + ["Other"]

    disease_var = tk.StringVar(value=all_disease_options[0])
    disease_menu = ttk.OptionMenu(form_frame, disease_var, all_disease_options[0], *all_disease_options)
    disease_menu.grid(row=len(fields), column=1, sticky="ew", pady=2)
    tk.Label(form_frame, text="If 'Other', specify:", bg=panel_bg, fg="#2e7d32", font=("Segoe UI", 9), anchor="w").grid(row=len(fields)+1, column=0, sticky="w", pady=2)
    custom_disease_entry = tk.Entry(form_frame, bg="#e8f5e9", fg="#222", font=("Segoe UI", 10), width=35)
    custom_disease_entry.grid(row=len(fields)+1, column=1, sticky="ew", pady=2)

    form_frame.columnconfigure(1, weight=1)
    # Ensure message_frame is created (will be used by _show_panel_message)
    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg)
    # Pack it below the form, above the bottom buttons
    app.message_frame.pack(pady=(5,0), fill=tk.X, padx=20, side=tk.BOTTOM)


    def submit():
        # Find the actual button bar to pack message frame before it
        button_bar = None
        for w in reversed(app.side_panel.winfo_children()):
            if isinstance(w, tk.Frame) and any(isinstance(child, tk.Button) for child in w.winfo_children()):
                pack_info = w.pack_info()
                if pack_info.get('side') == tk.BOTTOM:
                    button_bar = w
                    break
        if button_bar:
            app.message_frame.pack_configure(before=button_bar) # Repack message frame correctly

        app._show_panel_message("", "black", panel_bg) # Clear message
        patients = data_manager.load_patients()

        # --- Get and Validate Inputs ---
        new_patient_id = entries["id"].get().strip()
        if not new_patient_id: app._show_panel_message("Error: Patient ID cannot be empty.", "red", panel_bg); return
        if any(p.get("id") == new_patient_id for p in patients):
            app._show_panel_message(f"Error: Patient ID '{new_patient_id}' already exists.", "red", panel_bg); return

        name = utils.title_case(entries["name"].get().strip())
        if not name: app._show_panel_message("Error: Patient Name cannot be empty.", "red", panel_bg); return

        age_str = entries["age"].get().strip()
        try:
            age = int(age_str)
            if age <= 0: raise ValueError("Age must be positive")
        except ValueError:
            app._show_panel_message("Error: Please enter a valid positive age.", "red", panel_bg); return

        gender = utils.title_case(entries["gender"].get().strip())
        if not gender: app._show_panel_message("Error: Gender cannot be empty.", "red", panel_bg); return

        contact = entries["contact"].get().strip()
        if not (contact.isdigit() and len(contact) == config.PHONE_DIGITS):
            app._show_panel_message(f"Error: Phone number must be {config.PHONE_DIGITS} digits.", "red", panel_bg); return

        address = entries["address"].get().strip() or "N/A"
        email = entries["email"].get().strip() or "N/A"

        selected_disease = disease_var.get()
        disease = utils.title_case(custom_disease_entry.get().strip()) if selected_disease == "Other" else selected_disease
        if not disease: app._show_panel_message("Error: Please select or specify a disease.", "red", panel_bg); return

        # --- Auto-assign medicines ---
        assigned_medicines = ""; disease_lower = disease.lower()
        if disease_lower in config.AUTO_ASSIGN_MEDS:
            assigned_medicines = ", ".join(config.AUTO_ASSIGN_MEDS[disease_lower])

        # --- Create and Save Patient ---
        new_patient = {
            "id": new_patient_id,
            "name": name,
            "age": age_str,
            "gender": gender,
            "disease": disease,
            "doctor": "Not Assigned",
            "bill": "0.00",
            "appointment_time": "-",
            "medicines": assigned_medicines,
            "contact": contact,
            "address": address,
            "email": email
        }
        patients.append(new_patient)
        data_manager.save_patients(patients)
        app.refresh_table()

        # --- Post-Save Actions ---
        if not assigned_medicines:
            app._show_panel_message("Patient added. Please assign medicines.", "blue", panel_bg)
            # Need to find the *saved* patient dict to pass
            # Reload patients to ensure we have the exact object structure if needed elsewhere
            saved_patient = next((p for p in data_manager.load_patients() if p.get("id") == new_patient_id), None)
            if saved_patient:
                # Call the function from assignment_panels to display medicine options
                assignment_panels._display_medicine_options(app, saved_patient)
            else:
                # This should ideally not happen
                messagebox.showerror("Error", f"Could not re-find patient {new_patient_id} after saving.", parent=app)
                app.show_default_side_panel()
        else:
            # Show success message if meds were auto-assigned
            app._clear_side_panel(); success_bg = config.PANEL_COLORS["success"]
            app.side_panel.configure(bg=success_bg)
            tk.Label(app.side_panel, text="Success!", font=("Segoe UI", 14, "bold"), fg="green", bg=success_bg).pack(pady=20)
            tk.Label(app.side_panel, text=f"Patient '{new_patient['name']}' added.", font=("Segoe UI", 10), bg=success_bg).pack(pady=5)
            tk.Label(app.side_panel, text=f"Auto-assigned medicines: {assigned_medicines}", font=("Segoe UI", 9, "italic"), bg=success_bg).pack(pady=2)
            tk.Button(app.side_panel, text="OK", command=app.show_default_side_panel, bg="#43a047", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)

    # --- Buttons ---
    # Create the button bar *after* the message frame so it appears at the very bottom
    button_bar = tk.Frame(app.side_panel, bg=panel_bg)
    button_bar.pack(pady=10, fill=tk.X, padx=20, side=tk.BOTTOM)
    tk.Button(button_bar, text="Add Patient", command=submit, bg="#43a047", fg="white", activebackground="#66bb6a", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, expand=True, padx=5)
    tk.Button(button_bar, text="Cancel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT, expand=True, padx=5)

    # Ensure message frame is packed before the button bar initially
    app.message_frame.pack_configure(before=button_bar)


def show_search_panel(app):
    """Displays the 'Search Patient' panel."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["search_patient"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Search Patient", font=("Segoe UI", 14, "bold"), fg="#0277bd", bg=panel_bg).pack(pady=(10, 15))
    search_frame = tk.Frame(app.side_panel, bg=panel_bg); search_frame.pack(fill=tk.X, padx=20)
    tk.Label(search_frame, text="Enter Patient ID:", font=("Segoe UI", 10, "bold"), bg=panel_bg, fg="#0288d1").pack(side=tk.LEFT, padx=(0, 5))
    pid_entry = tk.Entry(search_frame, font=("Segoe UI", 10), bg="#e1f5fe", width=20); pid_entry.pack(side=tk.LEFT, padx=5); pid_entry.focus_set()
    search_button = tk.Button(search_frame, text="Search", command=lambda: perform_search(), bg="#039be5", fg="white", activebackground="#4fc3f7", font=("Segoe UI", 10, "bold")); search_button.pack(side=tk.LEFT, padx=5)
    pid_entry.bind("<Return>", lambda event: perform_search()) # Bind Enter key

    result_frame = tk.Frame(app.side_panel, bg=panel_bg); result_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)

    def perform_search():
        # Clear previous results
        for widget in result_frame.winfo_children(): widget.destroy()
        pid = pid_entry.get().strip()
        if not pid:
            tk.Label(result_frame, text="Please enter a Patient ID.", font=("Segoe UI", 10, "italic"), fg="red", bg=panel_bg).pack()
            return

        patient = next((p for p in data_manager.load_patients() if p.get("id") == pid), None)

        if patient:
            result_frame.configure(bg="#b3e5fc") # Slightly darker blue for result area
            tk.Label(result_frame, text="Patient Details", font=("Segoe UI", 12, "bold"), bg="#b3e5fc", fg="#01579b").pack(pady=5)
            # Define the order and labels for display
            display_fields = [
                ("Patient ID", "id"), ("Name", "name"), ("Age", "age"), ("Gender", "gender"),
                ("Disease", "disease"), ("Assigned Doctor", "doctor"), ("Current Bill", "bill"),
                ("Appointment Time", "appointment_time"), ("Assigned Medicines", "medicines"),
                ("Phone", "contact"), ("Address", "address"), ("Email", "email")
            ]
            info_lines = []
            for label, key in display_fields:
                value = patient.get(key, 'N/A')
                if key == "bill" and value:
                    try: value = f"{float(value):.2f}"
                    except ValueError: pass # Keep original if not float
                elif not value: # Handle empty strings for optional fields
                    value = "N/A"
                info_lines.append(f"{label}: {value}")

            info = "\n".join(info_lines)

            details_text = tk.Text(result_frame, font=("Segoe UI", 10), bg="#e1f5fe", fg="#222", wrap="word", bd=0, height=14, relief=tk.FLAT)
            details_text.insert("1.0", info)
            details_text.configure(state="disabled") # Make read-only
            details_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        else:
            result_frame.configure(bg=panel_bg) # Reset background if not found
            tk.Label(result_frame, text="Patient Not Found.", font=("Segoe UI", 10, "bold"), fg="red", bg=panel_bg).pack(pady=10)

    tk.Button(app.side_panel, text="Close Panel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)


def show_patient_report_panel(app):
    """Displays the initial panel to search for a patient to generate a report."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["patient_report"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Patient Report", font=("Segoe UI", 14, "bold"), fg="#f57f17", bg=panel_bg).pack(pady=(10, 15))
    input_frame = tk.Frame(app.side_panel, bg=panel_bg); input_frame.pack(fill=tk.X, padx=20, pady=10)
    tk.Label(input_frame, text="Enter Patient ID:", font=("Segoe UI", 10, "bold"), bg=panel_bg, fg="#f9a825").pack(side=tk.LEFT, padx=(0, 5))
    pid_entry = tk.Entry(input_frame, font=("Segoe UI", 10), bg="#fffde7", width=20); pid_entry.pack(side=tk.LEFT, padx=5); pid_entry.focus_set()
    proceed_button = tk.Button(input_frame, text="Show Report", command=lambda: find_patient_and_proceed(), bg="#fbc02d", fg="#424242", activebackground="#fff176", font=("Segoe UI", 10, "bold")); proceed_button.pack(side=tk.LEFT, padx=5)
    pid_entry.bind("<Return>", lambda event: find_patient_and_proceed())

    # Ensure message_frame is created for potential error messages
    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg)
    app.message_frame.pack(pady=5, padx=20, fill=tk.X)

    def find_patient_and_proceed():
        # Find the actual button bar to pack message frame before it
        button_bar = None
        for w in reversed(app.side_panel.winfo_children()):
             if isinstance(w, tk.Button) and w.cget('text') == "Cancel": # Find the cancel button
                 button_bar = w.master # Get its parent frame
                 break
        if button_bar:
            app.message_frame.pack_configure(before=button_bar) # Repack message frame correctly

        app._show_panel_message("", "black", panel_bg) # Clear previous messages
        pid = pid_entry.get().strip()
        if not pid:
            app._show_panel_message("Please enter a Patient ID.", "red", panel_bg); return

        patient = next((p for p in data_manager.load_patients() if p.get("id") == pid), None)
        if not patient:
            app._show_panel_message("Patient Not Found.", "red", panel_bg); return

        # If patient found, display the report (clears the input fields)
        _display_patient_report(app, patient)

    # Create the button bar *after* the message frame so it appears at the very bottom
    button_bar = tk.Frame(app.side_panel, bg=panel_bg)
    button_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(5, 10)) # Pack button bar at bottom
    tk.Button(button_bar, text="Cancel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack() # Simple cancel button

    # Ensure message frame is packed before the button bar initially
    app.message_frame.pack_configure(before=button_bar)


def _display_patient_report(app, patient):
    """Helper function to display the actual report content."""
    app._clear_side_panel() # Clear the input fields etc.
    panel_bg = config.PANEL_COLORS["patient_report"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Patient Report", font=("Segoe UI", 14, "bold"), fg="#f57f17", bg=panel_bg).pack(pady=(10, 5))
    now = datetime.datetime.now().strftime("Generated: %d-%m-%Y %H:%M:%S")
    tk.Label(app.side_panel, text=now, font=("Segoe UI", 9, "italic"), fg="#f9a825", bg=panel_bg).pack(pady=(0, 10))

    # --- Container Frame for Canvas and Scrollbar ---
    report_area_frame = tk.Frame(app.side_panel, bg=panel_bg)
    # Pack this frame to fill available space, leaving room for buttons at the bottom
    report_area_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 5))

    # Canvas and Scrollbar for potentially long reports
    report_canvas = tk.Canvas(report_area_frame, bg="#fff9c4", bd=1, relief=tk.SOLID, highlightthickness=0) # Slightly darker bg
    report_scrollbar = ttk.Scrollbar(report_area_frame, orient="vertical", command=report_canvas.yview)
    report_frame = tk.Frame(report_canvas, bg="#fff9c4") # Match canvas bg

    # Binding to resize scrollregion and inner frame width
    report_frame.bind("<Configure>", lambda e: report_canvas.configure(scrollregion=report_canvas.bbox("all")))
    report_canvas_window = report_canvas.create_window((0, 0), window=report_frame, anchor="nw")
    # Update inner frame width when canvas width changes
    report_canvas.bind("<Configure>", lambda e: report_canvas.itemconfig(report_canvas_window, width=e.width))

    report_canvas.configure(yscrollcommand=report_scrollbar.set)

    # Pack canvas and scrollbar inside the container frame
    report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    report_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # --- Populate Report Content ---
    # Fields to display in the report
    fields_to_display = [
        ("Patient ID", "id"), ("Name", "name"), ("Age", "age"), ("Gender", "gender"),
        ("Phone", "contact"), ("Address", "address"), ("Email", "email"),
        ("Disease", "disease"), ("Assigned Doctor", "doctor"),
        ("Appointment Time", "appointment_time"), ("Assigned Medicines", "medicines"),
        ("Current Bill", "bill")
    ]

    for i, (label, key) in enumerate(fields_to_display):
        value = patient.get(key, "N/A")
        if not value: value = "N/A" # Ensure empty strings become N/A
        if key == "medicines" and value == "N/A": value = "None"
        if key == "bill" and value != "N/A":
            try: value = f"{float(value):.2f}" # Format bill
            except ValueError: pass # Keep original if not float

        # Label widget for field name
        lbl = tk.Label(report_frame, text=f"{label}:", font=("Segoe UI", 10, "bold"),
                       bg="#fff9c4", fg="#f57f17", anchor="nw", width=16, justify="left", wraplength=120) # Allow label wrapping
        lbl.grid(row=i, column=0, sticky="nw", padx=5, pady=3)

        # Text widget for value (allows wrapping and selection)
        val_text = tk.Text(report_frame, font=("Segoe UI", 10), bg="#fffde7", fg="#222",
                           wrap="word", height=1, bd=0, relief="flat", padx=2, pady=1)
        val_text.insert("1.0", value)
        val_text.configure(state="disabled") # Read-only
        val_text.grid(row=i, column=1, sticky="nsew", padx=5, pady=3)

        # Adjust height based on content immediately after ensuring layout is calculated
        val_text.update_idletasks()
        utils.adjust_text_height(val_text)

    report_frame.columnconfigure(1, weight=1) # Allow value column to expand

    # Adjust canvas scroll region after content is added and heights adjusted
    report_frame.update_idletasks()
    report_canvas.configure(scrollregion=report_canvas.bbox("all"))
    # report_canvas.itemconfig(report_canvas_window, width=report_canvas.winfo_width()) # Ensure inner frame fills canvas width initially

    # --- Add Edit and Close Buttons ---
    button_frame = tk.Frame(app.side_panel, bg=panel_bg)
    # Place button frame below the report_area_frame using pack with side=BOTTOM
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(5, 10))

    edit_button = tk.Button(button_frame, text="Edit Patient",
                            # Pass the current patient data to the edit form function
                            command=lambda p=patient: _display_patient_edit_form(app, p),
                            bg="#ffb300", fg="black", activebackground="#ffe082", font=("Segoe UI", 10, "bold"))
    edit_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X) # Place Edit on the left

    close_button = tk.Button(button_frame, text="Close Report", command=app.show_default_side_panel,
                             bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold"))
    close_button.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X) # Place Close on the right


def _display_patient_edit_form(app, patient):
    """Displays an editable form pre-filled with patient data."""
    print(f"DEBUG: Entering _display_patient_edit_form for patient ID: {patient.get('id')}") # <-- DEBUG PRINT
    app._clear_side_panel()
    # Use a distinct color for editing
    panel_bg = config.PANEL_COLORS.get("update_doctor", "#fce4ec") # Use update_doctor color or fallback
    app.side_panel.configure(bg=panel_bg)

    original_patient_id = patient.get('id', '') # Store original ID

    tk.Label(app.side_panel, text=f"Edit Patient: {patient.get('name', '')}", font=("Segoe UI", 14, "bold"), fg="#ad1457", bg=panel_bg).pack(pady=(10, 15))
    form_frame = tk.Frame(app.side_panel, bg=panel_bg); form_frame.pack(fill=tk.X, padx=20)

    # --- Form Fields ---
    # Use StringVars to easily get/set values
    entry_vars = {}
    fields_to_edit = ["Name", "Age", "Gender", f"Phone Number ({config.PHONE_DIGITS} digits)", "Address", "Email"]
    # Map display names to dictionary keys
    key_map = {
        "Name": "name", "Age": "age", "Gender": "gender",
        f"Phone Number ({config.PHONE_DIGITS} digits)": "contact",
        "Address": "address", "Email": "email"
    }

    # Patient ID (Read-only)
    tk.Label(form_frame, text="Patient ID:", bg=panel_bg, fg="#ad1457", font=("Segoe UI", 10, "bold"), anchor="w").grid(row=0, column=0, sticky="w", pady=2)
    id_label = tk.Label(form_frame, text=original_patient_id, bg="#e0e0e0", fg="#555555", font=("Segoe UI", 10), relief=tk.SUNKEN, anchor="w", padx=2)
    id_label.grid(row=0, column=1, sticky="ew", pady=2)

    # Editable Fields
    row_offset = 1
    for i, field_name in enumerate(fields_to_edit):
        key = key_map[field_name]
        tk.Label(form_frame, text=field_name + ":", bg=panel_bg, fg="#ad1457", font=("Segoe UI", 10, "bold"), anchor="w").grid(row=i + row_offset, column=0, sticky="w", pady=2)
        var = tk.StringVar(value=patient.get(key, ''))
        entry_vars[key] = var
        entry = tk.Entry(form_frame, textvariable=var, bg="#fce4ec", fg="#222", font=("Segoe UI", 10), width=35)
        entry.grid(row=i + row_offset, column=1, sticky="ew", pady=2)
        if key == "name": entry.focus_set() # Focus on name field

    # Disease Field (Handle OptionMenu + Custom Entry) - Make consistent with add_patient
    disease_row = len(fields_to_edit) + row_offset
    tk.Label(form_frame, text="Disease:", bg=panel_bg, fg="#ad1457", font=("Segoe UI", 10, "bold"), anchor="w").grid(row=disease_row, column=0, sticky="w", pady=(10, 2))

    # Combine auto-assign keys with common diseases, remove duplicates, sort, add 'Other'
    auto_keys = [k.capitalize() for k in config.AUTO_ASSIGN_MEDS.keys()]
    common_diseases_base = ["Fever", "Cold", "Headache", "Cough", "Hypertension", "Diabetes", "Asthma", "Allergy", "Stomach pain", "Back pain"]
    all_disease_options = sorted(list(set(auto_keys + common_diseases_base))) + ["Other"]

    current_disease = patient.get('disease', '')
    custom_disease_value = ""
    initial_disease_selection = all_disease_options[0] # Default

    if current_disease in all_disease_options:
        initial_disease_selection = current_disease
    elif current_disease: # If it's not in the list, assume it's custom
        initial_disease_selection = "Other"
        custom_disease_value = current_disease

    disease_var = tk.StringVar(value=initial_disease_selection)
    entry_vars['disease_option'] = disease_var # Store the option menu variable

    disease_menu = ttk.OptionMenu(form_frame, disease_var, initial_disease_selection, *all_disease_options)
    disease_menu.grid(row=disease_row, column=1, sticky="ew", pady=2)

    tk.Label(form_frame, text="If 'Other', specify:", bg=panel_bg, fg="#ad1457", font=("Segoe UI", 9), anchor="w").grid(row=disease_row + 1, column=0, sticky="w", pady=2)
    custom_disease_var = tk.StringVar(value=custom_disease_value)
    entry_vars['disease_custom'] = custom_disease_var # Store the custom entry variable
    custom_disease_entry = tk.Entry(form_frame, textvariable=custom_disease_var, bg="#fce4ec", fg="#222", font=("Segoe UI", 10), width=35)
    custom_disease_entry.grid(row=disease_row + 1, column=1, sticky="ew", pady=2)

    form_frame.columnconfigure(1, weight=1)

    # Ensure message_frame is created for potential messages
    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg)
    # Pack it below the form, above the bottom buttons
    app.message_frame.pack(pady=(5,0), fill=tk.X, padx=20, side=tk.BOTTOM)


    # --- Save Changes Logic ---
    def save_changes():
        # Find the actual button bar to pack message frame before it
        button_bar = None
        for w in reversed(app.side_panel.winfo_children()):
            if isinstance(w, tk.Frame) and any(isinstance(child, tk.Button) for child in w.winfo_children()):
                pack_info = w.pack_info()
                if pack_info.get('side') == tk.BOTTOM:
                    button_bar = w
                    break
        if button_bar:
            app.message_frame.pack_configure(before=button_bar) # Repack message frame correctly

        app._show_panel_message("", "black", panel_bg) # Clear message

        # Get updated values from StringVars
        updated_data = {}
        for key, var in entry_vars.items():
            # Skip the disease helper vars for now
            if key not in ['disease_option', 'disease_custom']:
                updated_data[key] = var.get().strip()

        # Determine final disease
        selected_disease_option = entry_vars['disease_option'].get()
        custom_disease_text = entry_vars['disease_custom'].get().strip()
        if selected_disease_option == "Other":
            updated_data['disease'] = utils.title_case(custom_disease_text)
        else:
            updated_data['disease'] = selected_disease_option # Already title cased from list

        # --- Validation (similar to add patient) ---
        if not updated_data.get('disease'):
            app._show_panel_message("Error: Please select or specify a disease.", "red", panel_bg); return

        contact = updated_data.get('contact', '')
        if not (contact.isdigit() and len(contact) == config.PHONE_DIGITS):
            app._show_panel_message(f"Error: Phone number must be {config.PHONE_DIGITS} digits.", "red", panel_bg); return

        age_str = updated_data.get('age', '')
        try:
            age = int(age_str)
            if age <= 0: raise ValueError("Age must be positive")
        except ValueError:
            app._show_panel_message("Error: Please enter a valid positive age.", "red", panel_bg); return

        name = utils.title_case(updated_data.get('name', ''))
        if not name:
             app._show_panel_message("Error: Patient Name cannot be empty.", "red", panel_bg); return

        gender = utils.title_case(updated_data.get('gender', ''))
        if not gender:
             app._show_panel_message("Error: Gender cannot be empty.", "red", panel_bg); return

        address = updated_data.get('address', '') or "N/A"
        email = updated_data.get('email', '') or "N/A"

        # --- Update and Save ---
        patients = data_manager.load_patients()
        found_index = next((i for i, p in enumerate(patients) if p.get("id") == original_patient_id), -1)

        if found_index != -1:
            # Update the patient dictionary IN PLACE in the list
            patients[found_index]['name'] = name
            patients[found_index]['age'] = age_str
            patients[found_index]['gender'] = gender
            patients[found_index]['contact'] = contact
            patients[found_index]['address'] = address
            patients[found_index]['email'] = email
            patients[found_index]['disease'] = updated_data['disease']
            # Other fields like doctor, bill, medicines, appointment_time are NOT changed here

            data_manager.save_patients(patients)
            app.refresh_table()

            # Show success message and return to report view
            app._show_panel_message("Patient details updated successfully.", "green", panel_bg)
            # Get the fully updated patient data to display in the report
            updated_patient_data = patients[found_index]
            # Use 'after' to delay going back slightly, letting user see the message
            app.after(1500, lambda: _display_patient_report(app, updated_patient_data))

        else:
            # Should not happen if we came from the report, but handle defensively
            app._show_panel_message(f"Error: Could not find patient with ID {original_patient_id} to update.", "red", panel_bg)
            app.after(1500, app.show_default_side_panel)


    # --- Cancel Edit Logic ---
    def cancel_edit():
        # Simply go back to the report view using the original patient data
        _display_patient_report(app, patient)

    # --- Buttons ---
    # Create the button bar *after* the message frame so it appears at the very bottom
    button_bar = tk.Frame(app.side_panel, bg=panel_bg)
    button_bar.pack(pady=10, fill=tk.X, padx=20, side=tk.BOTTOM)
    tk.Button(button_bar, text="Save Changes", command=save_changes, bg="#43a047", fg="white", activebackground="#66bb6a", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, expand=True, padx=5)
    tk.Button(button_bar, text="Cancel", command=cancel_edit, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT, expand=True, padx=5)

    # Ensure message frame is packed before the button bar initially
    app.message_frame.pack_configure(before=button_bar)

    print("DEBUG: Finished setting up edit form.") # <-- DEBUG PRINT
