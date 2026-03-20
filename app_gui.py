# app_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, PanedWindow
import datetime
from PIL import Image, ImageTk
import os

# Import project modules
import config
import data_manager
import utils
from panels import ( # Import panel modules
    patient_panels,
    doctor_panels,
    assignment_panels,
    billing_panels,
    about_panel
)

class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🏥 EMPOWER HOSPITAL")
        self.state('zoomed')

        # --- Animated Background Colors ---
        # ... (bg_colors list remains the same) ...
        self.bg_colors = [
            "#f3f7fa", "#e1f5fe", "#ffe0b2", "#f8bbd0", "#c8e6c9", "#fff9c4", "#d1c4e9", "#b2dfdb",
            "#ffd6e0", "#b3e5fc", "#ffecb3", "#c5e1a5", "#ffccbc", "#e6ee9c", "#f48fb1", "#b2ebf2",
            "#e0f7fa", "#fce4ec", "#f1f8e9", "#fffde7", "#e8eaf6", "#efebe9", "#eceff1", "#f3e5f5",
            "#e8f5e9", "#fff3e0", "#fbe9e7", "#e1f5fe", "#e0f2f1", "#f9fbe7", "#fce4ec", "#ede7f6",
            "#f0f4c3", "#dcedc8", "#c5cae9", "#bbdefb", "#b2ebf2", "#b2dfdb", "#ffecb3", "#ffe0b2",
            "#ffccbc", "#f8bbd0", "#e1bee7", "#d7ccc8", "#cfd8dc", "#f5f5f5", "#fafafa", "#eeeeee",
            "#fbc02d", "#ff7043", "#81d4fa", "#aed581", "#ffb74d", "#ce93d8", "#fff176", "#ff8a65",
            "#f06292", "#9575cd", "#4dd0e1", "#ffb300", "#aed581", "#ff8a65", "#ba68c8", "#ffd54f",
            "#4fc3f7", "#4db6ac", "#81c784", "#a1887f", "#90a4ae", "#7986cb", "#64b5f6", "#ff8f00",
            "#ffca28", "#ffee58", "#d4e157", "#9ccc65", "#66bb6a", "#26a69a", "#26c6da", "#29b6f6",
            "#7e57c2", "#ab47bc", "#ec407a", "#ef5350", "#ff7043", "#ffa726", "#ffee58", "#66bb6a",
        ]
        self.current_bg = 0
        self.configure(bg=self.bg_colors[self.current_bg])

        # --- Main Layout ---
        self.border_frame = tk.Frame(self, bg="#ef5350", bd=7, relief=tk.RIDGE)
        self.border_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.outer_paned_window = PanedWindow(self.border_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5, bg="#FFFDD0")
        self.outer_paned_window.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # --- Logo Loading (Moved here to be accessible by default panel) ---
        self.logo_photo = None # Initialize attribute
        try:
            logo_image = Image.open(config.LOGO_FILE)
            logo_width = 150 # Keep the size used in the sidebar
            aspect_ratio = logo_image.height / logo_image.width
            logo_height = int(logo_width * aspect_ratio)
            logo_image = logo_image.resize((logo_width, logo_height), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
        except Exception as e:
            print(f"Logo Loading Error: {e}")
            # Fallback handled later if self.logo_photo is None

        # --- Setup UI Components ---
        self._setup_sidebar() # Sidebar setup now uses self.logo_photo if available
        self._setup_main_area()

        # --- Datetime Label ---
        self.datetime_label = tk.Label(self.border_frame, font=("Segoe UI", 10, "bold"), bg="#FEC5E5", fg="#0d47a1")
        self.datetime_label.pack(fill=tk.X, side=tk.BOTTOM)
        self.update_datetime()

        # Start background animation
        self.animate_bg()

        # Load initial data into table
        self.refresh_table()
        # Show default content in side panel
        self.show_default_side_panel()


    def _setup_sidebar(self):
        """Creates the left sidebar with logo and buttons."""
        self.button_sidebar_frame = tk.Frame(self.outer_paned_window, width=170, bg="#B2AC88", relief=tk.RAISED, bd=2)
        self.button_sidebar_frame.pack_propagate(False)
        self.outer_paned_window.add(self.button_sidebar_frame, stretch="never")

        # --- Logo ---
        # Use the pre-loaded self.logo_photo
        if self.logo_photo:
            logo_label = tk.Label(self.button_sidebar_frame, image=self.logo_photo, bg="#228B22")
            logo_label.pack(pady=(15, 15), padx=10)
        else: # Fallback if loading failed
            logo_label = tk.Label(self.button_sidebar_frame, text="🏥", font=("Segoe UI Emoji", 40), fg="white", bg="#4B0082")
            logo_label.pack(pady=(15, 15), padx=10)

        # --- Buttons ---
        # ... (button setup remains the same) ...
        sidebar_btn_style = {
            "fg": "white", "activeforeground": "#1976d2", "font": ("Segoe UI", 10, "bold"),
            "bd": 1, "relief": tk.RAISED, "cursor": "hand2", "padx": 6, "pady": 5, "anchor": "w"
        }
        button_width = 18 # Not strictly needed with fill=tk.X

        # Button definitions using lambda to pass `self` (the app instance) to panel functions
        buttons_data = [
            ("➕ Add Patient", lambda: patient_panels.show_add_patient_panel(self), "#43a047", "#a5d6a7"),
            ("🔍 Search Patient", lambda: patient_panels.show_search_panel(self), "#039be5", "#81d4fa"),
            ("🩺 Assign Doctor", lambda: assignment_panels.show_assign_doctor_panel(self), "#8e24aa", "#ce93d8"),
            ("💊 Assign Medicines", lambda: assignment_panels.show_assign_medicines_panel(self), "#009688", "#80cbc4"),
            ("📄 Patient Report", lambda: patient_panels.show_patient_report_panel(self), "#fbc02d", "#fff59d"),
            ("💳 Generate Bill", lambda: billing_panels.show_generate_bill_panel(self), "#d84315", "#ffab91"),
            ("🔄 Refresh List", self.refresh_table, "#1976d2", "#90caf9"),
        ]

        for text, command, bg, active_bg in buttons_data:
            tk.Button(self.button_sidebar_frame, text=text, width=button_width, command=command,
                      bg=bg, activebackground=active_bg, **sidebar_btn_style).pack(side=tk.TOP, fill=tk.X, padx=8, pady=2 if text != "➕ Add Patient" else (10, 2))

        # --- Doctor Menu Button ---
        doctor_menu_btn = tk.Menubutton(self.button_sidebar_frame, text="👨‍⚕️ Doctor Menu", width=button_width,
                                        bg="#3949ab", activebackground="#9fa8da", **sidebar_btn_style, direction="right")
        doctor_menu = tk.Menu(doctor_menu_btn, tearoff=0, bg="#e3f2fd", fg="#222", font=("Segoe UI Emoji", 10, "bold"))
        doctor_menu.add_command(label="👁️ View All Doctors", command=lambda: doctor_panels.show_view_doctors_panel(self))
        doctor_menu.add_command(label="➕ Add Doctor", command=lambda: doctor_panels.show_add_doctor_panel(self))
        doctor_menu.add_command(label="➖ Remove Doctor", command=lambda: doctor_panels.show_remove_doctor_panel(self))
        doctor_menu.add_command(label="✏️ Update Doctor", command=lambda: doctor_panels.show_update_doctor_panel(self))
        doctor_menu_btn.config(menu=doctor_menu)
        doctor_menu_btn.pack(side=tk.TOP, fill=tk.X, padx=8, pady=2)

        # --- Bottom Buttons ---
        tk.Button(self.button_sidebar_frame, text="⏻ Exit", width=button_width, command=self.destroy,
                  bg="#c62828", activebackground="#ef9a9a", **sidebar_btn_style).pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(2, 8))
        tk.Button(self.button_sidebar_frame, text="❗ About", width=button_width, command=lambda: about_panel.show_about_panel(self),
                  bg="#00acc1", activebackground="#80deea", **sidebar_btn_style).pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=2)


    def _setup_main_area(self):
        """Sets up the right side including the side panel and treeview area."""
        # ... (Inner PanedWindow, Side Panel, Main Area Frame setup remains the same) ...
        # --- Inner PanedWindow (Right Pane of Outer PanedWindow) ---
        self.paned_window = PanedWindow(self.outer_paned_window, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=6, bg="#E6E6FA")
        self.outer_paned_window.add(self.paned_window, stretch="always")

        # --- Side Panel (Left Pane of Inner PanedWindow) ---
        self.side_panel = tk.Frame(self.paned_window, width=470, bg=config.PANEL_COLORS["default"], relief=tk.SUNKEN, bd=2)
        self.side_panel.pack_propagate(False)
        self.paned_window.add(self.side_panel, stretch="never")
        # self.show_default_side_panel() # Called after __init__ finishes

        # --- Main Area Frame (Right Pane of Inner PanedWindow) ---
        self.main_area_frame = tk.Frame(self.paned_window, bg="#E6E6FA")
        self.paned_window.add(self.main_area_frame, stretch="always")

        # --- Watermark ---
        # ... (Watermark setup remains the same) ...
        self.tree_bg_watermark_img = None
        self.watermark_label = None
        try:
            bg_watermark_pil = Image.open(config.WATERMARK_FILE)
            watermark_size = (350, 350)
            bg_watermark_pil = bg_watermark_pil.resize(watermark_size, Image.LANCZOS)
            if bg_watermark_pil.mode != 'RGBA': bg_watermark_pil = bg_watermark_pil.convert('RGBA')
            alpha = 30
            bg_watermark_pil.putalpha(alpha)
            self.tree_bg_watermark_img = ImageTk.PhotoImage(bg_watermark_pil)
            self.watermark_label = tk.Label(self.main_area_frame, image=self.tree_bg_watermark_img, bg=self.main_area_frame['bg'])
            self.watermark_label.image = self.tree_bg_watermark_img # Keep reference
            self.watermark_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Treeview Watermark error: {e}")


        # --- Treeview Styling ---
        # ... (Treeview styling remains the same) ...
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#9DC183", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", background="#FFFDD0", fieldbackground="#FFFDD0", foreground="#222", rowheight=26, font=("Segoe UI", 9))
        style.map("Treeview", background=[('selected', '#2ECC71')])
        style.configure("Vertical.TScrollbar", gripcount=0, background="#FADADD", darkcolor="#4B0082", lightcolor="#40E0D0", troughcolor="#E09F3E", bordercolor="#FF7F50", arrowcolor="white")


        # --- Treeview and Scrollbar ---
        # ... (Treeview and Scrollbar setup remains the same) ...
        vsb = ttk.Scrollbar(self.main_area_frame, orient="vertical", style="Vertical.TScrollbar")
        self.tree = ttk.Treeview(self.main_area_frame, columns=config.PATIENT_COLS, show="headings", yscrollcommand=vsb.set, style="Treeview")
        vsb.config(command=self.tree.yview)

        # --- Configure Treeview Columns ---
        for col in config.PATIENT_COLS:
            self.tree.heading(col, text=col)
            col_width = 100 # Default
            if col == "Bill": col_width = 70
            elif col == "Age": col_width = 60
            elif col in ["Name", "Appointment Time"]: col_width = 140
            self.tree.column(col, width=col_width, stretch=tk.NO, minwidth=40)

        # --- Place Treeview and Scrollbar using grid ---
        self.main_area_frame.grid_rowconfigure(0, weight=1)
        self.main_area_frame.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')


        # --- Lower the watermark ---
        if self.watermark_label:
            self.watermark_label.lower(self.tree)


    # --- Core GUI Utility Methods ---
    def _clear_side_panel(self):
        """Removes all widgets from the side panel and resets background."""
        for widget in self.side_panel.winfo_children():
            widget.destroy()
        self.side_panel.configure(bg=config.PANEL_COLORS["default"])

    def _show_panel_message(self, text, color, bg_color="#FF7F50"):
        """Helper to display temporary messages in the side panel's message_frame."""
        # ... (remains the same) ...
        if hasattr(self, 'message_frame') and self.message_frame.winfo_exists():
            for widget in self.message_frame.winfo_children(): widget.destroy()
            self.message_frame.configure(bg=bg_color) # Match panel bg
            msg_label = tk.Label(self.message_frame, text=text, fg=color, bg=bg_color, font=("Segoe UI", 9, "italic"))
            msg_label.pack(pady=2)
        else:
            print(f"Panel Message ({color}): {text}") # Print to console


    def show_default_side_panel(self):
        """Displays the initial content (including logo) in the side panel."""
        self._clear_side_panel()
        panel_bg = config.PANEL_COLORS["default"]
        self.side_panel.configure(bg=panel_bg) # Ensure default color

        tk.Label(self.side_panel, text="🏥 EMPOWER HOSPITAL", font=("Segoe UI", 16, "bold"), fg="#2ECC71", bg=panel_bg).pack(pady=(20, 10)) # Adjust padding

        # --- Add Logo to Default Panel ---
        if self.logo_photo:
            # Create a label for the logo in the side panel
            side_logo_label = tk.Label(self.side_panel, image=self.logo_photo, bg=panel_bg)
            # IMPORTANT: Keep a reference to the image to prevent garbage collection
            side_logo_label.image = self.logo_photo
            side_logo_label.pack(pady=(10, 15)) # Add some padding around the logo
        else:
            # Optional: Add a text fallback if logo failed to load
            tk.Label(self.side_panel, text="🏥", font=("Segoe UI Emoji", 50), fg="#1976d2", bg=panel_bg).pack(pady=(10, 15))


        tk.Label(self.side_panel, text="Welcome to ", font=("Segoe UI", 15, "bold"), fg="#40E0D0", bg=panel_bg, wraplength=350).pack(pady=10)
        tk.Label(self.side_panel, text="🏥 EMPOWER Hospital \n\t Life Saving Hospital", font=("Segoe UI", 16, "bold"), fg="#004d4d", bg=panel_bg, wraplength=350).pack(pady=10)
        tk.Label(self.side_panel, text="Health is wealth, and health is life. \n\t We are here to help you and your family.", font=("Segoe UI", 10, "italic"), fg="#191970", bg=panel_bg, wraplength=350).pack(pady=10)

    def animate_bg(self):
        """Cycles through background colors for the main window."""
        # ... (remains the same) ...
        self.current_bg = (self.current_bg + 1) % len(self.bg_colors)
        new_bg_color = self.bg_colors[self.current_bg]
        try:
            if self.winfo_exists():
                self.configure(bg=new_bg_color)
                self.after(1200, self.animate_bg) # Schedule next change
        except tk.TclError:
            print("Info: Main window closed, stopping background animation.")


    def update_datetime(self):
        """Updates the date and time label at the bottom."""
        # ... (remains the same) ...
        now = datetime.datetime.now().strftime("Date And Time: %d-%m-%Y %H:%M:%S")
        try:
            if self.datetime_label.winfo_exists():
                self.datetime_label.config(text=now)
                self.after(1000, self.update_datetime) # Schedule next update
        except tk.TclError:
            print("Info: Datetime label destroyed, stopping update.")


    def refresh_table(self):
        """Clears and reloads the patient data in the main Treeview."""
        # ... (remains the same) ...
        if not hasattr(self, 'tree') or not self.tree.winfo_exists():
            print("Warning: Attempted to refresh table, but treeview doesn't exist.")
            return

        # Clear existing items
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Load and sort patients
        patients = data_manager.load_patients()
        try:
            # Sort primarily by ID (numeric if possible)
            patients.sort(key=lambda p: int(p.get("id", "0")))
        except ValueError:
             # Fallback sort if ID is not purely numeric
             patients.sort(key=lambda p: p.get("id", "0"))

        # Insert data
        for p in patients:
            # Ensure the order matches config.PATIENT_COLS
            row_values = []
            key_map = { # Map Treeview column names to patient dict keys
                "Patient ID": "id",
                "Name": "name",
                "Age": "age",
                "Gender": "gender",
                "Disease": "disease",
                "Doctor": "doctor",
                "Bill": "bill",
                "Appointment Time": "appointment_time"
            }
            for col_name in config.PATIENT_COLS:
                patient_key = key_map.get(col_name)
                if patient_key:
                    value = p.get(patient_key, '')
                    # Format bill specifically
                    if col_name == "Bill" and value:
                        try: value = f"{float(value):.2f}"
                        except ValueError: pass # Keep original if not float
                    row_values.append(value)
                else:
                    row_values.append('') # Should not happen if key_map is correct

            if self.tree.winfo_exists():
                self.tree.insert("", "end", values=row_values)

        # Ensure watermark is behind the tree
        if self.watermark_label and self.watermark_label.winfo_exists() and self.tree.winfo_exists():
             self.watermark_label.lower(self.tree)

    # Note: Panel display functions are imported and called via button commands.
