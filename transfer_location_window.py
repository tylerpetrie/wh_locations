import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from utils import center_and_size_toplevel

class TransferLocationWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance

        self.title("Transfer Location Contents")
        # self.geometry("450x300")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # --- Define fonts ---
        self.label_font = self.app.get_font(size=14, weight="bold")
        self.entry_font = self.app.get_font(size=14)
        self.button_font = self.app.get_font(size=14, weight="bold")
        self.entry_height = self.app.get_scaled_size(35)
        self.button_height = self.app.get_scaled_size(35)

        # --- Main content frame ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=self.app.get_scaled_padding(20), padx=self.app.get_scaled_padding(20), fill="both", expand=True)

        self.main_frame.grid_columnconfigure(1, weight=1)

        # --- From Location ---
        row_num = 0
        ctk.CTkLabel(self.main_frame, text="From Location:", font=self.label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding((0,10)), pady=self.app.get_scaled_padding(10), sticky="e")
        self.from_location_entry = ctk.CTkEntry(
            self.main_frame, 
            font=self.entry_font,
            height=self.entry_height,
            width=self.app.get_scaled_size(150),
            placeholder_text="e.g., A001"
        )
        self.from_location_entry.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(10), sticky="ew")
        row_num += 1

        # --- To Location ---
        ctk.CTkLabel(self.main_frame, text="To Location:", font=self.label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding((0,10)), pady=self.app.get_scaled_padding(10), sticky="e")
        self.to_location_entry = ctk.CTkEntry(
            self.main_frame, 
            font=self.entry_font,
            height=self.entry_height,
            width=self.app.get_scaled_size(150),
            placeholder_text="e.g., B002"
        )
        self.to_location_entry.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(10), sticky="ew")
        row_num += 1

        # --- Action Buttons ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=self.app.get_scaled_padding((10, 20)), padx=self.app.get_scaled_padding(20), fill="x")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        self.transfer_button = ctk.CTkButton(
            button_frame, 
            text="Execute Transfer", 
            command=self.initiate_transfer,
            font=self.button_font,
            height=self.button_height,
            fg_color=positive_fg, 
            hover_color=positive_hover, 
            text_color=positive_text,
            text_color_disabled=positive_dtext,
            border_color="black",
            border_width=self.app.get_scaled_size(1)
        )
        self.transfer_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(5), sticky="e")

        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")
        self.cancel_button = ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            command=self.destroy,
            font=self.button_font,
            height=self.button_height,
	        fg_color=destructive_fg, 
            hover_color=destructive_hover, 
            text_color=destructive_text, 
            text_color_disabled=destructive_dtext, 
            border_color="black", 
            border_width=self.app.get_scaled_size(1)
        )
        self.cancel_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(5), sticky="w")

        # Bind Escape key to close
        self.bind("<Escape>", lambda event: self.destroy())

        # Bind Enter key to initiate_transfer
        self.from_location_entry.bind("<Return>", lambda event: self.to_location_entry.focus_set()) 
        self.to_location_entry.bind("<Return>", lambda event: self.initiate_transfer())

        # Set initial focus
        self.from_location_entry.focus_set()
        self.lift()

        center_and_size_toplevel(self, base_width=450, base_height=250)

    def validate_location_code(self, location_code):
        """ Basic validation for location code format. """
        if not location_code: return False
        return True

    def initiate_transfer(self):
        from_loc = self.from_location_entry.get().strip().upper()
        to_loc = self.to_location_entry.get().strip().upper()

        if not self.validate_location_code(from_loc):
            messagebox.showerror("Input Error", "Please enter a valid 'From Location'.", parent=self)
            self.from_location_entry.focus_set()
            return
        
        if not self.validate_location_code(to_loc):
            messagebox.showerror("Input Error", "Please enter a valid 'To Location'.", parent=self)
            self.to_location_entry.focus_set()
            return

        if from_loc == to_loc:
            messagebox.showerror("Input Error", "'From' and 'To' locations cannot be the same.", parent=self)
            return

        print(f"TransferWindow: Requesting transfer from {from_loc} to {to_loc}")
        
        # --- Call the App's core transfer logic method --- #
        result = self.app.execute_location_transfer(from_loc, to_loc)
        
        if result is True:
            messagebox.showinfo("Success", f"Transfer from {from_loc} to {to_loc} completed successfully.", 
                                parent=self.master)
            self.destroy()
        elif isinstance(result, str):
            if "cancelled by user" in result.lower() or "has no stock" in result.lower():
                 messagebox.showinfo("Information", result, parent=self)
            else:
                 messagebox.showerror("Transfer Error", result, parent=self)
        else:
           messagebox.showerror("Transfer Error", "An unexpected issue occurred during transfer.", parent=self)
