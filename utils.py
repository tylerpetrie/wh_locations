import customtkinter as ctk

def center_and_size_toplevel(toplevel_window, base_width, base_height):
    """
    Centers a toplevel window and sets its size based on a base size
    and the current screen's DPI scaling factor.
    """
    try:
        # Assumes the app instance is passed and available
        scaling_factor = toplevel_window.app.scaling_factor
        master = toplevel_window.app
    except AttributeError:
        # Fallback if the app instance isn't found
        scaling_factor = ctk.ScalingTracker.get_window_scaling(toplevel_window)
        master = toplevel_window.master

    width = int(base_width * scaling_factor)
    height = int(base_height * scaling_factor)
    
    # Center relative to the master window (usually the main app)
    master_x = master.winfo_x()
    master_y = master.winfo_y()
    master_width = master.winfo_width()
    master_height = master.winfo_height()

    x = master_x + (master_width // 2) - (width // 2)
    y = master_y + (master_height // 2) - (height // 2)
    
    toplevel_window.geometry(f"{width}x{height}+{x}+{y}")