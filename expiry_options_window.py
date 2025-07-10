import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from utils import center_and_size_toplevel


class ExpiryReportOptionsWindow(ctk.CTkToplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.app = master
        self.callback = callback

        self.title("Expiry Report Options")
        # self.geometry("400x400")
        self.transient(master)
        self.grab_set()

        self.label = ctk.CTkLabel(self, text="Show items expiring:", font=self.app.get_font(size=14))
        self.label.pack(pady=self.app.get_scaled_padding(20), padx=self.app.get_scaled_padding(10))

        self.option_type_var = tk.StringVar(value="fixed_6") # Default to 6 months
        self.custom_months_var = tk.StringVar(value="") # For custom input
        self.custom_operator_var = tk.StringVar(value="<") # Default custom operator

        # --- Fixed Radio Buttons ---
        self.radio_6m = ctk.CTkRadioButton(self, text="Within Next 6 Months", variable=self.option_type_var, value="fixed_6", command=self.toggle_custom_input)
        self.radio_6m.pack(pady=self.app.get_scaled_size(5), anchor="w", padx=self.app.get_scaled_padding(50))

        self.radio_12m = ctk.CTkRadioButton(self, text="Within Next 12 Months", variable=self.option_type_var, value="fixed_12", command=self.toggle_custom_input)
        self.radio_12m.pack(pady=self.app.get_scaled_padding(5), anchor="w", padx=self.app.get_scaled_padding(50))

        self.radio_18m = ctk.CTkRadioButton(self, text="Within Next 18 Months", variable=self.option_type_var, value="fixed_18", command=self.toggle_custom_input)
        self.radio_18m.pack(pady=self.app.get_scaled_padding(5), anchor="w", padx=self.app.get_scaled_padding(50))

        # --- Custom Range Radio Button ---
        self.radio_custom = ctk.CTkRadioButton(self, text="Custom Range:", variable=self.option_type_var, value="custom", command=self.toggle_custom_input)
        self.radio_custom.pack(pady=self.app.get_scaled_padding((10,0)), anchor="w", padx=self.app.get_scaled_padding(50))

        # --- Custom Input Frame (initially hidden or disabled) ---
        self.custom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.custom_frame.pack(pady=self.app.get_scaled_padding((0,10)), padx=self.app.get_scaled_padding(50), fill="x")
        self.custom_frame.grid_columnconfigure(1, weight=1)

        self.operator_label = ctk.CTkLabel(self.custom_frame, text="Operator:", font=self.app.get_font(size=12))
        self.operator_label.grid(row=0, column=0, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(5), sticky="w")
        
        self.operator_menu = ctk.CTkOptionMenu(
            self.custom_frame, 
            variable=self.custom_operator_var,
            values=["< (Less than)", "> (Greater than)"],
            width=self.app.get_scaled_size(180)
        )
        self.operator_menu.grid(row=0, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="ew")

        self.months_label = ctk.CTkLabel(self.custom_frame, text="Months:", font=self.app.get_font(size=12))
        self.months_label.grid(row=1, column=0, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(5), sticky="w")
        
        self.custom_months_entry = ctk.CTkEntry(self.custom_frame, textvariable=self.custom_months_var, width=self.app.get_scaled_size(80), placeholder_text="e.g., 3")
        self.custom_months_entry.grid(row=1, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="w")
        
        # Initial state of custom input
        self.toggle_custom_input()

        # --- Action Buttons Frame --- 
        self.action_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_button_frame.pack(pady=self.app.get_scaled_padding(20), fill="x", padx=self.app.get_scaled_padding(50))
        self.action_button_frame.grid_columnconfigure((0,1), weight=1)

        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        self.run_button = ctk.CTkButton(
            self.action_button_frame,
            text="Run Report", 
            command=self.on_run,
            height=self.app.get_scaled_size(35),
            fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext, 
            border_color="black", border_width=self.app.get_scaled_size(1)
        )
        self.run_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="e")

        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")
        self.cancel_button = ctk.CTkButton(
            self.action_button_frame, 
            text="Cancel", 
            command=self.destroy,
            height=self.app.get_scaled_size(35),
            fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext,
            border_color="black", border_width=self.app.get_scaled_size(1)
        )
        self.cancel_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="w")


        self.bind("<Escape>", lambda event: self.destroy())
        self.lift()
        self.focus_set()
        self.radio_6m.focus_set() 
        center_and_size_toplevel(self, base_width=400, base_height=420)

    def toggle_custom_input(self):
        """Enables/disables custom input fields based on radio button selection."""
        if self.option_type_var.get() == "custom":
            self.operator_menu.configure(state="normal")
            self.custom_months_entry.configure(state="normal")
        else:
            self.operator_menu.configure(state="disabled")
            self.custom_months_entry.configure(state="disabled")

    def on_run(self):
        option_choice = self.option_type_var.get()
        report_params = {}

        if option_choice.startswith("fixed_"):
            report_params['months'] = int(option_choice.split("_")[1])
            report_params['operator'] = "<="
        
        elif option_choice == "custom":
            custom_months_str = self.custom_months_var.get().strip()
            if not custom_months_str:
                messagebox.showerror("Input Error", "Please enter the number of months for custom range.", parent=self)
                return
            try:
                custom_months_val = int(custom_months_str)
                if custom_months_val <= 0:
                    messagebox.showerror("Input Error", "Months for custom range must be a positive number.", parent=self)
                    return
                report_params['months'] = custom_months_val
            except ValueError:
                messagebox.showerror("Input Error", "Invalid number for months. Please enter a whole number.", parent=self)
                return
            
            # Get operator from OptionMenu ("< (Less than)" or "> (Greater than)")
            selected_operator_display = self.custom_operator_var.get()
            if "< (Less than)" in selected_operator_display:
                report_params['operator'] = "<"
            elif "> (Greater than)" in selected_operator_display:
                report_params['operator'] = ">"
            else:
                messagebox.showerror("Input Error", "Invalid operator selected.", parent=self)
                return
        else:
            messagebox.showerror("Error", "No report option selected.", parent=self)
            return
            
        self.destroy()
        self.callback(report_params)
