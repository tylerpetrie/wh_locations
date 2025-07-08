import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from utils import center_and_size_toplevel

class BatchSummaryOptionsWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance, callback):
        super().__init__(master)
        self.app = app_instance
        self.callback = callback

        self.title("Batch Summary Options")
        # self.geometry("450x300")
        self.transient(master)
        self.grab_set()

        # --- Define fonts and standard heights ---
        self.label_font = self.app.get_font(size=14)
        self.entry_font = self.app.get_font(size=14)
        self.button_font = self.app.get_font(size=14)
        self.info_font = self.app.get_font(size=12, slant="italic")
        self.entry_height = self.app.get_scaled_size(35)
        self.button_height = self.app.get_scaled_size(35)

        # --- Store input values ---
        self.sku_var = tk.StringVar()
        self.batch_var = tk.StringVar()

        # --- Main Frame ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=self.app.get_scaled_padding(20), padx=self.app.get_scaled_padding(20), fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1)

        row_num = 0

        title_label = ctk.CTkLabel(main_frame, text="Batch Summary by SKU or Batch", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=row_num, column=0, columnspan=2, pady=self.app.get_scaled_padding((0, 15)))
        row_num += 1

        # SKU Input
        ctk.CTkLabel(main_frame, text="Search by SKU:", font=self.label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding((0,10)), pady=self.app.get_scaled_padding(5), sticky="e")
        self.sku_entry = ctk.CTkEntry(main_frame, textvariable=self.sku_var, 
                                      font=self.entry_font, height=self.entry_height,
                                      placeholder_text="Enter SKU (leave blank if searching by Batch)")
        self.sku_entry.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="ew")
        row_num += 1

        # Batch Input
        ctk.CTkLabel(main_frame, text="Search by Batch:", font=self.label_font, anchor="e").grid(
            row=row_num, column=0, padx=self.app.get_scaled_padding((0,10)), pady=self.app.get_scaled_padding(5), sticky="e")
        self.batch_entry = ctk.CTkEntry(main_frame, textvariable=self.batch_var,
                                        font=self.entry_font, height=self.entry_height,
                                        placeholder_text="Enter Batch (leave blank if searching by SKU)")
        self.batch_entry.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="ew")
        row_num += 1
        
        # Instructional Label
        instruction_label = ctk.CTkLabel(main_frame, text="Please enter a value in ONE field only.", 
                                         font=self.info_font, text_color="gray50")
        instruction_label.grid(row=row_num, column=0, columnspan=2, pady=self.app.get_scaled_padding((5,10)))
        row_num +=1

        # --- Buttons ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=self.app.get_scaled_padding((10,15)), fill="x", padx=self.app.get_scaled_padding(20))
        button_frame.grid_columnconfigure((0,1), weight=1)

        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")

        self.run_button = ctk.CTkButton(
            button_frame, text="Run Report", command=self.on_run_report,
            font=self.button_font, height=self.button_height,
            fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext, 
            border_color="black", border_width=self.app.get_scaled_size(1)
        )
        self.run_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), sticky="e")

        self.cancel_button = ctk.CTkButton(
            button_frame, text="Cancel", command=self.destroy,
            font=self.button_font, height=self.button_height,
            fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext, 
            border_color="black", border_width=1
        )
        self.cancel_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(10), sticky="w")

        self.bind("<Escape>", lambda event: self.destroy())
        self.sku_entry.bind("<Return>", lambda event: self.batch_entry.focus_set() if not self.sku_var.get() else self.on_run_report())
        self.batch_entry.bind("<Return>", lambda event: self.on_run_report())

        self.lift()
        self.focus_set()
        self.sku_entry.focus_set()

        center_and_size_toplevel(self, base_width=450, base_height=300)

    def on_run_report(self):
        sku_term = self.sku_var.get().strip().upper()
        batch_term = self.batch_var.get().strip()

        if sku_term and batch_term:
            messagebox.showerror("Input Error", "Please enter a value for EITHER SKU or Batch, not both.", parent=self)
            return
        if not sku_term and not batch_term:
            messagebox.showerror("Input Error", "Please enter either an SKU or a Batch number to search.", parent=self)
            return

        search_criteria = {}
        if sku_term:
            search_criteria['type'] = 'sku'
            search_criteria['term'] = sku_term
        elif batch_term:
            search_criteria['type'] = 'batch'
            search_criteria['term'] = batch_term
        
        self.destroy()
        self.callback(search_criteria)