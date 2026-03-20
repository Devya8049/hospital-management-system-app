# panels/billing_panels.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import config
import data_manager
import utils

def show_generate_bill_panel(app):
    """Displays the initial 'Generate Bill' panel (search part)."""
    app._clear_side_panel()
    panel_bg = config.PANEL_COLORS["generate_bill"]
    app.side_panel.configure(bg=panel_bg)

    tk.Label(app.side_panel, text="Generate Patient Bill", font=("Segoe UI", 14, "bold"), fg="#e65100", bg=panel_bg).pack(pady=(10, 15))
    search_frame = tk.Frame(app.side_panel, bg=panel_bg); search_frame.pack(fill=tk.X, padx=20)
    tk.Label(search_frame, text="Enter Patient ID:", font=("Segoe UI", 10, "bold"), bg=panel_bg, fg="#ef6c00").pack(side=tk.LEFT, padx=(0, 5))
    pid_entry = tk.Entry(search_frame, font=("Segoe UI", 10), bg="#fff3e0", width=20)
    pid_entry.pack(side=tk.LEFT, padx=5); pid_entry.focus_set()
    search_button = tk.Button(search_frame, text="Generate Bill", command=lambda: find_and_generate_bill(), bg="#d84315", fg="white", activebackground="#ff8a65", font=("Segoe UI", 10, "bold"))
    search_button.pack(side=tk.LEFT, padx=5)
    pid_entry.bind("<Return>", lambda event: find_and_generate_bill()) # Bind Enter key

    # Use message_frame for results/errors
    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)

    def find_and_generate_bill():
        # Clear previous bill display or error message
        for widget in app.message_frame.winfo_children(): widget.destroy()
        app.message_frame.configure(bg=panel_bg) # Reset background

        pid = pid_entry.get().strip()
        if not pid:
            _display_billing_message(app, "Please enter a Patient ID.", "red", panel_bg)
            return

        patient = next((p for p in data_manager.load_patients() if p.get("id") == pid), None)
        if patient:
            generate_bill(app, patient) # Pass app instance
        else:
            _display_billing_message(app, "Patient Not Found.", "red", panel_bg)

    tk.Button(app.side_panel, text="Close Panel", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)


def generate_bill(app, patient):
    """Calculates and displays the bill for a given patient."""
    panel_bg = config.PANEL_COLORS["generate_bill"]

    # --- Data Validation ---
    if not patient or not isinstance(patient, dict) or 'id' not in patient:
        _show_billing_error(app, "Invalid patient data provided for billing.")
        return

    # --- Find Patient Index and Current Data ---
    patients = data_manager.load_patients()
    patient_index = next((i for i, p in enumerate(patients) if p.get("id") == patient["id"]), -1)

    if patient_index == -1:
        _show_billing_error(app, f"Patient ID {patient['id']} not found in current records.")
        return

    current_patient_data = patients[patient_index] # Use the latest data from file

    # --- Calculate Costs ---
    # Doctor Cost
    doctor_name = current_patient_data.get("doctor", "Not Assigned").strip()
    doctors = data_manager.load_doctors_local()
    doc_price = config.DEFAULT_DOCTOR_PRICE # Default if not found or assigned
    if doctor_name != "Not Assigned":
        found_doctor = next((d for d in doctors if d.get("name", "").strip().lower() == doctor_name.lower()), None)
        if found_doctor:
            try:
                doc_price = float(found_doctor.get("price", config.DEFAULT_DOCTOR_PRICE))
            except (ValueError, TypeError):
                print(f"Warning: Using default price for doctor {doctor_name} due to invalid stored price.")
                doc_price = config.DEFAULT_DOCTOR_PRICE

    # Medicine Cost
    med_price = _calculate_medicines_cost(app, current_patient_data) # Pass app for simpledialog parent

    # Hospital Charge
    hospital_extra = config.DEFAULT_HOSPITAL_CHARGE

    # Total Bill
    total_bill = doc_price + med_price + hospital_extra

    # --- Update Patient Record ---
    patients[patient_index]["bill"] = f"{total_bill:.2f}"
    data_manager.save_patients(patients)
    app.refresh_table() # Update the main treeview

    # --- Display Bill ---
    # Clear the search input area and display the bill in message_frame
    app._clear_side_panel()
    app.side_panel.configure(bg=panel_bg)
    app.message_frame = tk.Frame(app.side_panel, bg=panel_bg); app.message_frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)

    bill_display_bg = "#ffe0b2" # Slightly darker orange for bill details
    app.message_frame.configure(bg=bill_display_bg)

    tk.Label(app.message_frame, text="Bill Generated", font=("Segoe UI", 14, "bold"), fg="#e65100", bg=bill_display_bg).pack(pady=10)

    bill_details_frame = tk.Frame(app.message_frame, bg="#fff8e1", bd=1, relief=tk.SOLID) # Even lighter for text area
    bill_details_frame.pack(pady=10, padx=5, fill=tk.X)

    details = [
        (f"Patient: {current_patient_data.get('name', '')} (ID: {current_patient_data.get('id', '')})", "bold"),
        (f"Doctor Charges ({doctor_name}): {doc_price:.2f}", "normal"),
        (f"Medicine Charges: {med_price:.2f}", "normal"),
        (f"Hospital Charges: {hospital_extra:.2f}", "normal"),
    ]

    for text, weight in details:
        tk.Label(bill_details_frame, text=text, font=("Segoe UI", 10, weight), bg="#fff8e1", anchor="w").pack(fill=tk.X, padx=5, pady=2)

    tk.Frame(bill_details_frame, height=1, bg="grey").pack(fill=tk.X, padx=5, pady=3) # Separator
    tk.Label(bill_details_frame, text=f"Total Bill: {total_bill:.2f}", font=("Segoe UI", 11, "bold"), bg="#fff8e1", anchor="w").pack(fill=tk.X, padx=5, pady=3)

    # Add Close button at the bottom of the main side panel
    tk.Button(app.side_panel, text="Close Bill View", command=app.show_default_side_panel, bg="#c62828", fg="white", activebackground="#ef5350", font=("Segoe UI", 10, "bold")).pack(side=tk.BOTTOM, pady=10)


def _calculate_medicines_cost(app, patient):
    """Calculates total cost of assigned medicines, prompting for missing prices."""
    prices = data_manager.load_medicine_prices()
    updated_prices = False
    med_price_total = 0.0
    missing_prices_meds = []

    assigned_meds_str = patient.get("medicines", "")
    if assigned_meds_str:
        assigned_meds = [med.strip() for med in assigned_meds_str.split(",") if med.strip()]
        for med_name in assigned_meds:
            # Clean up name just in case (e.g., remove price if accidentally included)
            clean_med_name = med_name.split(":")[0].strip()

            if clean_med_name in prices:
                med_price_total += prices[clean_med_name]
            else:
                # Prompt user for price if missing
                price = simpledialog.askfloat("New Medicine Price",
                                              f"Price not found for '{clean_med_name}'.\nEnter price (or 0 to skip):",
                                              parent=app, minvalue=0.0) # Use app as parent
                if price is not None and price > 0:
                    prices[clean_med_name] = price
                    med_price_total += price
                    updated_prices = True
                else:
                    # If user cancels or enters 0, count as 0 and note it
                    missing_prices_meds.append(clean_med_name)
                    med_price_total += 0.0
                    print(f"Info: Price for '{clean_med_name}' set to 0 for this bill.")

    # Save prices if any new ones were added via the dialog
    if updated_prices:
        data_manager.save_medicine_prices(prices)

    # Show a single warning for all missing/skipped prices at the end
    if missing_prices_meds:
        messagebox.showwarning("Missing Prices",
                               f"Could not find/set prices for: {', '.join(missing_prices_meds)}. "
                               "They were counted as 0.00 in the bill.",
                               parent=app) # Use app as parent

    return med_price_total


def _display_billing_message(app, text, color, bg_color):
    """Helper to show messages specifically in the billing panel's message_frame."""
    if hasattr(app, 'message_frame') and app.message_frame.winfo_exists():
        # Clear previous content
        for widget in app.message_frame.winfo_children(): widget.destroy()
        app.message_frame.configure(bg=bg_color) # Ensure correct background
        msg_label = tk.Label(app.message_frame, text=text, fg=color, bg=bg_color, font=("Segoe UI", 10, "italic"))
        msg_label.pack(pady=10)
    else:
        # Fallback if message_frame is somehow missing
        messagebox.showinfo("Billing Info", text, parent=app) if color != "red" else messagebox.showerror("Billing Error", text, parent=app)


def _show_billing_error(app, message):
    """Displays an error message in a consistent way for billing failures."""
    try:
        app._clear_side_panel()
        error_bg = config.PANEL_COLORS["error"]
        app.side_panel.configure(bg=error_bg)
        tk.Label(app.side_panel, text="Billing Error", font=("Segoe UI", 14, "bold"), fg="red", bg=error_bg).pack(pady=10)
        tk.Label(app.side_panel, text=message, font=("Segoe UI", 10), bg=error_bg).pack(pady=5, padx=10)
        # Provide a way back to the initial billing panel or default
        tk.Button(app.side_panel, text="Try Again", command=lambda: show_generate_bill_panel(app), bg="#c62828", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)
    except tk.TclError:
        # Fallback if GUI elements are already destroyed
        messagebox.showerror("Billing Error", message, parent=app)
