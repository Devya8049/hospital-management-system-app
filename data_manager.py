# data_manager.py
import os
from tkinter import messagebox, simpledialog
import config
import utils # For title_case

# --- Patient Data Functions ---
def load_patients():
    patients = []
    try:
        with open(config.PATIENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                parts = line.strip().split('|')
                # Expecting 12 parts now based on save_patients
                if len(parts) >= 8: # Keep minimum check, but use get for safety
                    patient = {
                        "id": parts[0].strip(),
                        "name": utils.title_case(parts[1].strip()),
                        "age": parts[2].strip(),
                        "gender": utils.title_case(parts[3].strip()),
                        "disease": utils.title_case(parts[4].strip()),
                        "doctor": utils.title_case(parts[5].strip()),
                        "bill": parts[6].strip(),
                        "appointment_time": parts[7].strip(),
                        "medicines": parts[8].strip() if len(parts) >= 9 else "",
                        "contact": parts[9].strip() if len(parts) >= 10 else "",
                        "address": parts[10].strip() if len(parts) >= 11 else "",
                        "email": parts[11].strip() if len(parts) >= 12 else "",
                    }
                    patients.append(patient)
                else:
                    print(f"Warning: Skipping malformed line in {os.path.basename(config.PATIENTS_FILE)}: {line.strip()}")
    except FileNotFoundError:
        print(f"Warning: {config.PATIENTS_FILE} not found. Creating.")
        # Create the file if it doesn't exist
        try:
            with open(config.PATIENTS_FILE, "w", encoding="utf-8") as f: pass
        except Exception as e:
            messagebox.showerror("Error", f"Could not create {os.path.basename(config.PATIENTS_FILE)}\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not load {os.path.basename(config.PATIENTS_FILE)}\n{e}")
    return patients

def save_patients(patients):
    try:
        with open(config.PATIENTS_FILE, "w", encoding="utf-8") as f:
            for p in patients:
                # Ensure all expected keys exist using .get() with defaults
                f.write(
                    f"{p.get('id','')}|{p.get('name','')}|{p.get('age','')}|{p.get('gender','')}|"
                    f"{p.get('disease','')}|{p.get('doctor','')}|{p.get('bill','0.00')}|"
                    f"{p.get('appointment_time','-')}|{p.get('medicines','')}|{p.get('contact','')}|"
                    f"{p.get('address','')}|{p.get('email','')}\n"
                )
    except Exception as e:
        messagebox.showerror("Error", f"Could not save {os.path.basename(config.PATIENTS_FILE)}\n{e}")

# --- Medicine Data Functions ---
def load_medicine_prices():
    prices = {}
    try:
        with open(config.MEDICINES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    name, price_str = line.strip().split("|", 1)
                    try:
                        prices[name.strip()] = float(price_str.strip())
                    except ValueError:
                        print(f"Warning: Skipping invalid price for medicine '{name.strip()}' in {os.path.basename(config.MEDICINES_FILE)}")
    except FileNotFoundError:
        print(f"Warning: {config.MEDICINES_FILE} not found. Creating with defaults.")
        default_prices = {
            "Paracetamol": 10.0, "Ibuprofen": 15.0, "Amoxicillin": 25.0, "Cetirizine": 12.0, "Azithromycin": 30.0,
            "Metformin": 18.0, "Amlodipine": 20.0, "Omeprazole": 22.0, "Atorvastatin": 28.0, "Salbutamol": 16.0,
            "Dolo 650": 14.0, "Pantoprazole": 19.0, "Levocetirizine": 13.0, "Ciprofloxacin": 27.0, "Diclofenac": 17.0,
            "Ranitidine": 11.0, "Losartan": 21.0, "Montelukast": 23.0, "Dexamethasone": 26.0, "Clopidogrel": 29.0,
            "Ambroxol": 15.0
        }
        save_medicine_prices(default_prices) # Save defaults if file not found
        return default_prices
    except Exception as e:
         messagebox.showerror("Error", f"Could not load {os.path.basename(config.MEDICINES_FILE)}\n{e}")
         return {}
    return prices

def save_medicine_prices(prices):
    try:
        with open(config.MEDICINES_FILE, "w", encoding="utf-8") as f:
            # Sort by name before saving for consistency
            for name, price in sorted(prices.items()):
                f.write(f"{name}|{price:.2f}\n") # Save with 2 decimal places
    except Exception as e:
        messagebox.showerror("Error", f"Could not save {os.path.basename(config.MEDICINES_FILE)}\n{e}")

# --- Doctor Data Functions ---
def load_doctors_local():
    """Loads doctors from doctors.txt (format: name|specialty|qualification|contact|price)"""
    doctors = []
    try:
        with open(config.DOCTORS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                parts = line.strip().split('|')
                if len(parts) == 5:
                    try:
                        doctors.append({
                            "name": utils.title_case(parts[0].strip()),
                            "specialty": utils.title_case(parts[1].strip()),
                            "qualification": parts[2].strip().upper(),
                            "contact": parts[3].strip(),
                            "price": float(parts[4].strip())
                        })
                    except ValueError:
                         print(f"Warning: Skipping line due to invalid price in {os.path.basename(config.DOCTORS_FILE)}: {line.strip()}")
                    except IndexError:
                         print(f"Warning: Skipping line due to unexpected format (IndexError) in {os.path.basename(config.DOCTORS_FILE)}: {line.strip()}")
                else:
                     print(f"Warning: Skipping malformed line (expected 5 parts) in {os.path.basename(config.DOCTORS_FILE)}: {line.strip()}")
    except FileNotFoundError:
        print(f"Warning: {config.DOCTORS_FILE} not found. Creating.")
        try:
            with open(config.DOCTORS_FILE, "w", encoding="utf-8") as f: pass
        except Exception as e:
            messagebox.showerror("Error", f"Could not create {os.path.basename(config.DOCTORS_FILE)}\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not load {os.path.basename(config.DOCTORS_FILE)}\n{e}")
    return doctors

def save_doctors_local(doctors_list):
    """Saves doctors to doctors.txt in the format: name|specialty|qualification|contact|price"""
    try:
        with open(config.DOCTORS_FILE, "w", encoding="utf-8") as f:
            # Sort by name before saving for consistency
            for doc in sorted(doctors_list, key=lambda d: d.get('name', '')):
                name = doc.get('name','Unknown Doctor')
                specialty = doc.get('specialty','N/A')
                qualification = doc.get('qualification', 'N/A')
                contact = doc.get('contact', 'N/A')
                price = doc.get('price', 0.0)
                f.write(f"{name}|{specialty}|{qualification}|{contact}|{price:.2f}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save {os.path.basename(config.DOCTORS_FILE)}\n{e}")

# --- About Data Function ---
def load_about_text():
    try:
        with open(config.ABOUT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {config.ABOUT_FILE} not found. Creating.")
        default_text = "Welcome to EMPOWER HOSPITAL Management System.\n\nDeveloped by [Your Name/Group].\n\nVersion 1.0"
        try:
            with open(config.ABOUT_FILE, "w", encoding="utf-8") as f:
                f.write(default_text)
            return default_text
        except Exception as e_create:
             messagebox.showerror("Error", f"Could not create or read {os.path.basename(config.ABOUT_FILE)}\n{e_create}")
             return f"Error loading about info: {e_create}"
    except Exception as e:
        messagebox.showerror("Error", f"Could not load {os.path.basename(config.ABOUT_FILE)}\n{e}")
        return f"Error loading about info: {e}"
