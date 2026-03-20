# main.py
import tkinter as tk
import os

# Import project modules
import config
import data_manager
import app_gui # Import the main App class

def ensure_files_exist():
    """Checks and creates necessary data files if they don't exist."""
    files_to_check = [
        config.PATIENTS_FILE,
        config.ABOUT_FILE,
        config.MEDICINES_FILE,
        config.DOCTORS_FILE
    ]
    for filename in files_to_check:
         try:
             # Use 'a' mode to create if not exists, without truncating
             # Ensure the directory exists first (optional but good practice)
             os.makedirs(os.path.dirname(filename), exist_ok=True)
             with open(filename, "a", encoding="utf-8") as f: pass
             print(f"Checked/Ensured file: {filename}")
         except Exception as e:
             print(f"Warning: Could not ensure file '{filename}' exists or is accessible. {e}")
             # Optionally, show a critical error message and exit if a file is essential
             # tk.messagebox.showerror("File Error", f"Could not access essential file: {os.path.basename(filename)}\n{e}")
             # return False # Indicate failure
    return True # Indicate success

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting EMPOWER HOSPITAL Application...")

    # 1. Ensure data files exist before loading data or starting GUI
    if not ensure_files_exist():
        print("Exiting due to file access errors.")
        exit() # Stop if essential files can't be created/accessed

    # 2. Pre-load data (optional, but can catch loading errors early)
    print("Pre-loading data...")
    try:
        data_manager.load_medicine_prices()
        data_manager.load_doctors_local()
        data_manager.load_patients() # Load patients too for early checks
        data_manager.load_about_text()
        print("Data pre-loading complete.")
    except Exception as e:
        # Show error message if pre-loading fails
        tk.Tk().withdraw() # Hide the root window for the messagebox
        tk.messagebox.showerror("Data Loading Error", f"Failed to pre-load data:\n{e}")
        print(f"Exiting due to data loading error: {e}")
        exit()

    # 3. Create and run the main application window
    print("Initializing GUI...")
    try:
        app = app_gui.HospitalApp()
        print("Running main loop...")
        app.mainloop()
        print("Application finished.")
    except Exception as e:
         # Catch unexpected GUI errors
         print(f"An unexpected error occurred: {e}")
         # Log the error or show a message
         tk.Tk().withdraw()
         tk.messagebox.showerror("Application Error", f"An unexpected error occurred:\n{e}")

