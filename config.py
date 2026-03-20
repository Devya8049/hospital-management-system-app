# config.py
import os
import sys # Import sys

# --- Function to determine the correct base path ---
def get_base_path():
    """ Get the base path for data files, handling PyInstaller's temp folder. """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle (frozen)
        # sys._MEIPASS is the temporary folder where PyInstaller unpacks data
        # We want files relative to the *executable*, not the temp folder,
        # so we get the directory of the executable.
        # However, for data files added with --add-data 'source;.',
        # they will often be placed alongside the executable OR in _MEIPASS
        # depending on onefile vs one-dir mode.
        # Let's assume they are placed relative to the executable's dir for simplicity,
        # or directly in _MEIPASS if using --add-data 'source;dest_folder_in_bundle'.
        # A safe bet for files added with ';.' is often sys._MEIPASS itself
        # or os.path.dirname(sys.executable) if they are copied next to it.
        # Let's try _MEIPASS first as it's common for --add-data.
        # If using one-dir mode, files added with ';.' might be in the main dir.
        # A more robust approach might be needed depending on the exact PyInstaller command.
        # For simplicity with '--add-data "file;."' let's try _MEIPASS
        # If that fails, try the executable's directory.
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
        # print(f"Running bundled, base path: {base_path}") # Debug print
    else:
        # Running as a normal Python script
        base_path = os.path.dirname(os.path.abspath(__file__))
        # print(f"Running script, base path: {base_path}") # Debug print
    return base_path

# --- Use the function to define file paths ---
BASE_DIR = get_base_path() # Use the function here

PATIENTS_FILE = os.path.join(BASE_DIR, "patients.txt")
ABOUT_FILE = os.path.join(BASE_DIR, "about.txt")
MEDICINES_FILE = os.path.join(BASE_DIR, "medicines.txt")
DOCTORS_FILE = os.path.join(BASE_DIR, "doctors.txt")
LOGO_FILE = os.path.join(BASE_DIR, "logo.png")
WATERMARK_FILE = os.path.join(BASE_DIR, "watermark.png")

# --- Auto-Assign Medicines Dictionary ---
# ... (rest of your config remains the same) ...
AUTO_ASSIGN_MEDS = {
    "fever": ["Paracetamol", "Dolo 650"],
    "cold": ["Cetirizine", "Levocetirizine"],
    "headache": ["Ibuprofen", "Paracetamol"],
    "cough": ["Salbutamol", "Ambroxol"],
    "stomach pain": ["Ranitidine", "Omeprazole"],
    "allergy": ["Cetirizine", "Montelukast"],
    "hypertension": ["Amlodipine", "Losartan"],
    "diabetes": ["Metformin"],
    "back pain": ["Ibuprofen", "Paracetamol"],
    "skin rash": ["Hydrocortisone", "Calamine lotion"],
    "asthma": ["Salbutamol", "Budesonide"],
    "anxiety": ["Sertraline", "Escitalopram"],
    "depression": ["Fluoxetine", "Sertraline"],
    "insomnia": ["Zolpidem", "Melatonin"],
    "nausea": ["Ondansetron", "Metoclopramide"],
    "vomiting": ["Ondansetron", "Domperidone"],
    "diarrhea": ["Loperamide", "Oral rehydration salts"],
    "constipation": ["Lactulose", "Polyethylene glycol"],
    "acidity": ["Omeprazole", "Ranitidine"],
    "gastritis": ["Omeprazole", "Sucralfate"],
    "ulcer": ["Omeprazole", "Sucralfate"],
    "arthritis": ["Ibuprofen", "Naproxen"],
    "gout": ["Allopurinol", "Colchicine"],
    "migraine": ["Sumatriptan", "Ibuprofen"],
    "insomnia": ["Zolpidem", "Melatonin"],
    "anemia": ["Ferrous sulfate", "Folic acid"],
    "thyroid": ["Levothyroxine", "Methimazole"],
    "cholesterol": ["Atorvastatin", "Simvastatin"],
    "heart disease": ["Aspirin", "Clopidogrel"],
    "stroke": ["Aspirin", "Clopidogrel"],
    "seizures": ["Phenytoin", "Carbamazepine"],
    "Parkinson's": ["Levodopa", "Carbidopa"],
    "Alzheimer's": ["Donepezil", "Rivastigmine"],
    "bacterial infection": ["Amoxicillin", "Azithromycin"],
    "viral infection": ["Oseltamivir", "Acyclovir"],
    "fungal infection": ["Fluconazole", "Clotrimazole"],
    "parasitic infection": ["Metronidazole", "Ivermectin"],
    "UTI": ["Nitrofurantoin", "Ciprofloxacin"],
    "kidney stones": ["Tamsulosin", "Hydrochlorothiazide"],
    # ... your dictionary ...
}

# --- Panel Background Colors ---
PANEL_COLORS = {
    "default": "#E6E6FA",            # Lavender
    "add_patient": "#e8f5e9",        # Light Green
    "search_patient": "#e1f5fe",     # Light Blue
    "assign_doctor": "#f3e5f5",      # Light Purple
    "assign_medicines": "#e0f2f1",   # Light Teal/Cyan
    "patient_report": "#fffde7",     # Light Yellow
    "generate_bill": "#fff3e0",      # Light Orange
    "about": "#efebe9",              # Light Brown/Beige
    "view_doctors": "#e8eaf6",       # Light Indigo
    "add_doctor": "#dcedc8",         # Another Light Green
    "remove_doctor": "#ffecb3",      # Light Amber
    "update_doctor": "#fce4ec",      # Light Pink
    "error": "#ffcdd2",              # Light Red (for error states if needed)
    "success": "#c8e6c9",            # Light Green (for success states if needed)
    # ... your dictionary ...
}

# --- Treeview Columns ---
PATIENT_COLS = ["Patient ID", "Name", "Age", "Gender", "Disease", "Doctor", "Bill", "Appointment Time"]
DOCTOR_COLS = ["Name", "Specialty", "Qualification", "Contact", "Price"]

# --- Other Constants ---
NIGHT_SHIFT_START_HOUR = 22
NIGHT_SHIFT_END_HOUR = 7
DEFAULT_HOSPITAL_CHARGE = 100.0
DEFAULT_DOCTOR_PRICE = 500.0
PHONE_DIGITS = 12
