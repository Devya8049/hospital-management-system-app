# utils.py
import tkinter as tk

def title_case(s):
    """Converts a string to title case."""
    if not isinstance(s, str):
        return ""
    return ' '.join([w.capitalize() for w in s.split()])

def adjust_text_height(text_widget):
    """Dynamically adjusts the height of a Text widget based on its content."""
    try:
        if text_widget.winfo_exists():
            # Get the number of lines, ensuring at least 1
            num_lines = max(1, int(text_widget.index('end-1c').split('.')[0]))
            text_widget.configure(height=num_lines)
    except tk.TclError:
        pass # Widget might be destroyed
    except Exception as e:
        print(f"Error adjusting text height: {e}")
