import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import datetime
from utils import center_and_size_toplevel 

class AuditHistoryOptionsWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance, callback):
        super().__init__(master)
        self.app = app_instance
        self.callback = callback
        self.title("Audit History Filter Options")
        # self.geometry("500x530")
        self.transient(master)
        self.grab_set()

        # --- Store filter values ---
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()
        self.user_var = tk.StringVar(value="All Users") 
        self.action_type_var = tk.StringVar(value="All Actions")
        self.sku_var = tk.StringVar()
        self.location_var = tk.StringVar()

        # --- Main Frame ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=self.app.get_scaled_padding(20), padx=self.app.get_scaled_padding(20), fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1)

        row_num = 0
        label_font = self.app.get_font(size=13)
        entry_font = self.app.get_font(size=13)
        pady_val = (5, 5)
        padx_label = (0, 10)
        padx_entry = 5

        # --- Title ---
        title_label = ctk.CTkLabel(main_frame, text="Filter Audit Log By:", font=self.app.get_font(size=16, weight="bold"))
        title_label.grid(row=row_num, column=0, columnspan=2, pady=self.app.get_scaled_padding((0, 15)))
        row_num += 1

        # --- Date Range ---
        ctk.CTkLabel(main_frame, text="Date From:", font=label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding(padx_label), pady=self.app.get_scaled_padding(pady_val), sticky="e")
        self.date_from_entry = ctk.CTkEntry(main_frame, textvariable=self.date_from_var, font=entry_font, placeholder_text="DD/MM/YYYY")
        self.date_from_entry.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(padx_entry), pady=self.app.get_scaled_padding(pady_val), sticky="ew")
        row_num += 1

        ctk.CTkLabel(main_frame, text="Date To:", font=label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding(padx_label), pady=self.app.get_scaled_padding(pady_val), sticky="e")
        self.date_to_entry = ctk.CTkEntry(main_frame, textvariable=self.date_to_var, font=entry_font, placeholder_text="DD/MM/YYYY")
        self.date_to_entry.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(padx_entry), pady=self.app.get_scaled_padding(pady_val), sticky="ew")
        row_num += 1
        
        # --- User ---
        ctk.CTkLabel(main_frame, text="User:", font=label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding(padx_label), pady=self.app.get_scaled_padding(pady_val), sticky="e")
        user_options = ["All Users"] + self.fetch_user_names()
        self.user_menu = ctk.CTkOptionMenu(main_frame, variable=self.user_var, values=user_options, font=entry_font)
        self.user_menu.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(padx_entry), pady=self.app.get_scaled_padding(pady_val), sticky="ew")
        row_num += 1

        # --- Action Type ---
        ctk.CTkLabel(main_frame, text="Action Type:", font=label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding(padx_label), pady=self.app.get_scaled_padding(pady_val), sticky="e")
        action_options = ["All Actions"] + self.fetch_distinct_action_types()
        self.action_menu = ctk.CTkOptionMenu(main_frame, variable=self.action_type_var, values=action_options, font=entry_font)
        self.action_menu.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(padx_entry), pady=self.app.get_scaled_padding(pady_val), sticky="ew")
        row_num += 1

        # --- SKU ---
        ctk.CTkLabel(main_frame, text="SKU:", font=label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding(padx_label), pady=self.app.get_scaled_padding(pady_val), sticky="e")
        self.sku_entry = ctk.CTkEntry(main_frame, textvariable=self.sku_var, font=entry_font, placeholder_text="Enter SKU (optional)")
        self.sku_entry.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(padx_entry), pady=self.app.get_scaled_padding(pady_val), sticky="ew")
        row_num += 1
        
        # --- Location ---
        ctk.CTkLabel(main_frame, text="Location:", font=label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding(padx_label), pady=self.app.get_scaled_padding(pady_val), sticky="e")
        self.location_entry = ctk.CTkEntry(main_frame, textvariable=self.location_var, font=entry_font, placeholder_text="Enter Location (optional)")
        self.location_entry.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(padx_entry), pady=self.app.get_scaled_padding(pady_val), sticky="ew")
        row_num += 1

        # --- Buttons ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=self.app.get_scaled_padding((15, 10)), fill="x")
        button_frame.grid_columnconfigure((0,1), weight=1)
        self.button_font = self.app.get_font(size=14, weight="bold")

        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        self.apply_button = ctk.CTkButton(button_frame, text="Apply Filters", command=self.on_apply_filters, height=self.app.get_scaled_size(35),
                                          fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext,
                                          border_color="black", border_width=self.app.get_scaled_size(1))
        self.apply_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), sticky="e")

        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, height=self.app.get_scaled_size(35), 
                                           fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext,
                                           border_color="black", border_width=self.app.get_scaled_size(1))
        self.cancel_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(10), sticky="w")

        self.bind("<Escape>", lambda event: self.destroy())
        self.lift()
        self.focus_set()
        self.date_from_entry.focus_set()

        center_and_size_toplevel(self, base_width=500, base_height=450)

    def fetch_user_names(self):
        """Fetches user names from the database for the dropdown."""
        if not self.app.conn: return []
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT UserName FROM Users ORDER BY UserName")
            users = [row[0] for row in cursor.fetchall()]
            return users
        except Exception as e:
            print(f"Error fetching user names for audit filter: {e}")
            return []

    def fetch_distinct_action_types(self):
        """Fetches distinct ChangeType values from StockItemHistory."""
        if not self.app.conn: return []
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT DISTINCT ChangeType FROM StockItemHistory WHERE ChangeType IS NOT NULL ORDER BY ChangeType")
            actions = [row[0] for row in cursor.fetchall()]
            return actions
        except Exception as e:
            print(f"Error fetching action types for audit filter: {e}")
            return []
            
    def _validate_and_format_date(self, date_str, field_name):
        """Validates DD/MM/YYYY and returns YYYY-MM-DD or None."""
        if not date_str:
            return None
        try:
            dt_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            return dt_obj.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Date Error", f"Invalid format for '{field_name}'. Please use DD/MM/YYYY.", parent=self)
            return "INVALID_DATE_FORMAT"

    def on_apply_filters(self):
        date_from_input = self.date_from_var.get().strip()
        date_to_input = self.date_to_var.get().strip()

        formatted_date_from = self._validate_and_format_date(date_from_input, "Date From")
        if formatted_date_from == "INVALID_DATE_FORMAT": return
        
        formatted_date_to = self._validate_and_format_date(date_to_input, "Date To")
        if formatted_date_to == "INVALID_DATE_FORMAT": return

        if formatted_date_from and formatted_date_to:
            if formatted_date_from > formatted_date_to:
                messagebox.showerror("Date Error", "'Date From' cannot be after 'Date To'.", parent=self)
                return

        filters = {
            'date_from': formatted_date_from,
            'date_to': formatted_date_to,
            'user_name': self.user_var.get() if self.user_var.get() != "All Users" else None,
            'action_type': self.action_type_var.get() if self.action_type_var.get() != "All Actions" else None,
            'sku': self.sku_var.get().strip().upper() or None,
            'location_name': self.location_var.get().strip().upper() or None,
        }
        
        print(f"AuditHistoryOptionsWindow: Applying filters: {filters}")
        self.destroy()
        self.callback(filters)
