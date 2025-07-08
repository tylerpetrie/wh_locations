import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import datetime
import calendar
import pyodbc
from utils import center_and_size_toplevel

class UpdateNewWindow(ctk.CTkToplevel):
    field_keys = [
        'SKU', 'Brand', 'Description', 'ShelfLocation', 'Barcode',
        'Batch', 'ExpiryDate', 'Quantity', 'UnitsPerCarton',
        'Notes', 'IsDangerousGood', 'DG_UN_Number', 'IsAdhoc',
        'IsQuarantined', 'IsFirst'
    ]
    lsi_derived_fields_keys = ['Brand', 'Description', 'ShelfLocation', 'Barcode']
    disabled_lsi_field_text_color = "gray60"

    def __init__(self, master, app_instance, mode, location_code, existing_data=None, source_view='location'):
        super().__init__(master)
        self.app = app_instance
        self.mode = mode
        self.location_code = location_code
        self.existing_data = existing_data
        self.stock_item_id = existing_data.get('StockItemID') if existing_data else None
        self.source_view = source_view 
        
        if self.mode == 'update': self.title(f"Update Item in {self.location_code}")
        else: self.title(f"Add New Item to {self.location_code}")
        # self.geometry("750x600"); self.resizable(False, False); self.transient(master); self.grab_set()

        self.label_font = self.app.get_font(size=14, weight="bold") # Label Font Size
        self.data_font = self.app.get_font(size=14) # Data font size
        self.total_font = self.app.get_font(size=18, weight="bold") # Total qty size
        self.entry_height = self.app.get_scaled_size(35) # Define a standard height for entries
        self.checkbox_font = self.app.get_font(size=13) # Font for checkboxes
        self.button_font = self.app.get_font(size=14, weight="bold") # button Font

        self.entries = {}

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=self.app.get_scaled_padding((10,0)), padx=self.app.get_scaled_padding(20), fill="both", expand=True)
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(side="bottom", pady=self.app.get_scaled_padding((5, 10)), padx=self.app.get_scaled_padding(20), fill="x", expand=False)
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # -- BUTTON COLORS
        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        neutral_fg, neutral_hover, neutral_text, neutral_dtext = self.app.get_button_color_config("neutral")
        warning_fg, warning_hover, warning_text, warning_dtext = self.app.get_button_color_config("warning")
        standard_fg, standard_hover, standard_text, standard_dtext = self.app.get_button_color_config("standard")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")
        
        # --- SAVE BUTTON ---
        self.save_button = ctk.CTkButton(self.button_frame, text="SAVE", width=self.app.get_scaled_size(120), command=self.save_item, 
                                         fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext, 
                                         border_color="black", border_width=self.app.get_scaled_size(1),
                                         height=self.entry_height, font=self.button_font)
        self.save_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="e")

        # --- CANCEL BUTTON  ---
        self.cancel_button = ctk.CTkButton(self.button_frame, text="CANCEL", width=self.app.get_scaled_size(120), command=self.destroy, 
                                           fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext, 
                                           border_color="black", border_width=self.app.get_scaled_size(1), 
                                           height=self.entry_height, font=self.button_font)
        self.cancel_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="w")

        row_num = 0

        self.main_frame.grid_columnconfigure(1, weight=1)

        # SKU
        ctk.CTkLabel(self.main_frame, text="SKU:", font=self.label_font, anchor="e").grid(row=row_num, column=0, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(5), sticky="e")
        sku_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        sku_frame.grid(row=row_num, column=1, columnspan=2, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="ew")
        sku_frame.grid_columnconfigure(0, weight=1)
        self.entries['SKU'] = ctk.CTkEntry(sku_frame, font=self.data_font, height=self.entry_height)
        self.entries['SKU'].grid(row=0, column=0, sticky="ew")
        self.entries['SKU'].bind("<Return>", self.trigger_lsi_search)
        # --- LSI SEARCH BUTTON ("standard")
        self.lsi_search_button = ctk.CTkButton(sku_frame, text="Search LSI", width=self.app.get_scaled_size(100), command=self.trigger_lsi_search, 
                                               fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext, 
                                               height=self.entry_height, font=self.button_font)
        self.lsi_search_button.grid(row=0, column=1, padx=self.app.get_scaled_padding((10, 0)))

        row_num += 1

        # LSI Populated Fields
        for field_key in self.lsi_derived_fields_keys:
            ctk.CTkLabel(self.main_frame, text=f"{field_key}:", font=self.label_font, anchor="e").grid(row=row_num, column=0, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(5), sticky="e")
            self.entries[field_key] = ctk.CTkEntry(self.main_frame, font=self.data_font, height=self.entry_height)
            self.entries[field_key].grid(row=row_num, column=1, columnspan=2, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="ew")
            row_num += 1

        # Status Flags Row
        status_flags_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        status_flags_frame.grid(row=row_num, column=0, columnspan=3, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding((5,10)), sticky="ew")
        # DG | UN Label | UN Entry | Quarantine | Use First | Adhoc | LSI Miss Warning
        
        col_idx = 0
        # IsDangerousGood CheckBox
        self.entries['IsDangerousGood'] = ctk.CTkCheckBox(status_flags_frame, text="DG", 
                                                          font=self.checkbox_font,
                                                          command=self.on_status_flags_change)
        self.entries['IsDangerousGood'].grid(row=0, column=col_idx, padx=self.app.get_scaled_padding((0, 2)), pady=self.app.get_scaled_padding(2), sticky="w")
        col_idx += 1

        # DG UN Number Label and Entry
        ctk.CTkLabel(status_flags_frame, text="UN:", font=self.label_font).grid(row=0, column=col_idx, padx=self.app.get_scaled_padding((0,2)), pady=self.app.get_scaled_padding(2), sticky="w")
        col_idx += 1
        self.entries['DG_UN_Number'] = ctk.CTkEntry(status_flags_frame, font=self.data_font, width=self.app.get_scaled_size(70), height=self.entry_height)
        self.entries['DG_UN_Number'].grid(row=0, column=col_idx, padx=self.app.get_scaled_padding((0, 10)), pady=self.app.get_scaled_padding(2), sticky="w")
        col_idx += 1

        # IsQuarantined CheckBox
        self.entries['IsQuarantined'] = ctk.CTkCheckBox(status_flags_frame, text="Quarantined", 
                                                        font=self.checkbox_font,
                                                        command=self.on_status_flags_change)
        self.entries['IsQuarantined'].grid(row=0, column=col_idx, padx=self.app.get_scaled_padding((5, 5)), pady=self.app.get_scaled_padding(2), sticky="w")
        col_idx += 1

        # IsFirst (Use First) CheckBox
        self.entries['IsFirst'] = ctk.CTkCheckBox(status_flags_frame, text="Use First", 
                                                  font=self.checkbox_font,
                                                  command=self.on_status_flags_change)
        self.entries['IsFirst'].grid(row=0, column=col_idx, padx=self.app.get_scaled_padding((5, 10)), pady=self.app.get_scaled_padding(2), sticky="w")
        col_idx += 1
        
        # IsAdhoc CheckBox
        self.entries['IsAdhoc'] = ctk.CTkCheckBox(status_flags_frame, text="Adhoc",
                                                  font=self.checkbox_font, 
                                                  command=self.on_status_flags_change)
        self.entries['IsAdhoc'].grid(row=0, column=col_idx, padx=self.app.get_scaled_padding((5, 0)), pady=self.app.get_scaled_padding(2), sticky="w")
        col_idx += 1
        
        # LSI Miss Warning Label
        self.adhoc_lsi_warning_label = ctk.CTkLabel(status_flags_frame, text="SKU Missing",
                                                    text_color="orange", font=self.checkbox_font)

        row_num += 1
        
        # Batch, Expiry
        ctk.CTkLabel(self.main_frame, text="Batch:", font=self.label_font, anchor="e").grid(row=row_num, column=0, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(5), sticky="e")
        self.entries['Batch'] = ctk.CTkEntry(self.main_frame, font=self.data_font, height=self.entry_height)
        self.entries['Batch'].grid(row=row_num, column=1, columnspan=2, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="ew"); row_num += 1
        ctk.CTkLabel(self.main_frame, text="Expiry:", font=self.label_font, anchor="e").grid(row=row_num, column=0, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(5), sticky="e")
        self.entries['ExpiryDate'] = ctk.CTkEntry(self.main_frame, font=self.data_font, placeholder_text="MM/YYYY", height=self.entry_height)
        self.entries['ExpiryDate'].grid(row=row_num, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="w"); row_num += 1

        # Quantity Section
        ctk.CTkLabel(self.main_frame, text="Quantity:", font=self.label_font, anchor="ne").grid(row=row_num, column=0, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(5), sticky="ne")
        qty_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        qty_frame.grid(row=row_num, column=1, columnspan=2, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="ew")
        qty_frame.grid_columnconfigure((1, 3, 5), weight=0); qty_frame.grid_columnconfigure(7, weight=1)
        ctk.CTkLabel(qty_frame, text="CTNs:", font=self.label_font).grid(row=0, column=0, padx=self.app.get_scaled_padding((0,2)), pady=self.app.get_scaled_padding(2))
        self.entry_qty_cartons = ctk.CTkEntry(qty_frame, font=self.data_font, width=self.app.get_scaled_size(70), justify="right", height=self.entry_height)
        self.entry_qty_cartons.grid(row=0, column=1, padx=self.app.get_scaled_padding((0,10)), pady=self.app.get_scaled_padding(2)); self.entry_qty_cartons.bind("<KeyRelease>", self.calculate_total_qty)
        ctk.CTkLabel(qty_frame, text="Units/CTN:", font=self.label_font).grid(row=0, column=2, padx=self.app.get_scaled_padding((0,2)), pady=self.app.get_scaled_padding(2))
        self.entries['UnitsPerCarton'] = ctk.CTkEntry(qty_frame, font=self.data_font, width=self.app.get_scaled_size(70), justify="right", height=self.entry_height)
        self.entries['UnitsPerCarton'].grid(row=0, column=3, padx=self.app.get_scaled_padding((0,10)), pady=self.app.get_scaled_padding(2)); self.entries['UnitsPerCarton'].bind("<KeyRelease>", self.calculate_total_qty)
        ctk.CTkLabel(qty_frame, text="Loose:", font=self.label_font).grid(row=0, column=4, padx=self.app.get_scaled_padding((0,2)), pady=self.app.get_scaled_padding(2))
        self.entry_qty_loose = ctk.CTkEntry(qty_frame, font=self.data_font, width=self.app.get_scaled_size(70), justify="right", height=self.entry_height)
        self.entry_qty_loose.grid(row=0, column=5, padx=self.app.get_scaled_padding((0,15)), pady=self.app.get_scaled_padding(2)); self.entry_qty_loose.bind("<KeyRelease>", self.calculate_total_qty)
        ctk.CTkLabel(qty_frame, text="TOTAL:", font=self.total_font, anchor='e').grid(row=0, column=6, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(2), sticky="e")
        self.entries['Quantity'] = ctk.CTkLabel(qty_frame, text="0", font=self.total_font, anchor='w')
        self.entries['Quantity'].grid(row=0, column=7, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(2), sticky="w"); row_num += 1

        # Notes
        ctk.CTkLabel(self.main_frame, text="Notes:", font=self.label_font, anchor="ne").grid(row=row_num, column=0, padx=self.app.get_scaled_padding((0,5)), pady=self.app.get_scaled_padding(5), sticky="ne")
        self.entries['Notes'] = ctk.CTkTextbox(self.main_frame, font=self.data_font, height=self.app.get_scaled_size(100), wrap="word")
        self.entries['Notes'].grid(row=row_num, column=1, columnspan=2, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="nsew")
        self.main_frame.grid_rowconfigure(row_num, weight=1)
        
        if self.mode == 'update' and self.existing_data: self.populate_fields_for_update()
        self.update_field_visual_states()
        
        # self.center_window(master); 
        self.bind("<Escape>", self._handle_escape_key); self.protocol("WM_DELETE_WINDOW", self._handle_window_close)
        if self.mode == 'new': self.entries['SKU'].focus_set()
        elif self.save_button: self.save_button.focus_set()

        center_and_size_toplevel(self, base_width=750, base_height=600)

        self.lift()
        self.focus_set()
        self.grab_set()

    def _handle_escape_key(self, event=None): self.destroy()
    def _handle_window_close(self, event=None): self.destroy()
    
    def center_window(self, master):
        if not (master and master.winfo_viewable()):
            self.update_idletasks(); w = self.winfo_width(); h = self.winfo_height(); sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
            x = (sw//2)-(w//2); y = (sh//2)-(h//2)
            if w>0 and h>0: self.geometry(f'{w}x{h}+{x}+{y}')
            return
        mx=master.winfo_x(); my=master.winfo_y(); mw=master.winfo_width(); mh=master.winfo_height()
        self.update_idletasks(); w=self.winfo_width(); h=self.winfo_height()
        x=mx+(mw//2)-(w//2); y=my+(mh//2)-(h//2)
        if w>0 and h>0: self.geometry(f'{w}x{h}+{x}+{y}')


    def populate_fields_for_update(self):
        if not (self.mode == 'update' and self.existing_data): return
        for key, value in self.existing_data.items():
            if key in self.entries:
                widget = self.entries[key]
                if key == 'ExpiryDate':
                    disp_val = datetime.datetime.strptime(value, '%Y-%m-%d').strftime('%m/%Y') if value else ""
                    widget.delete(0, tk.END); widget.insert(0, disp_val)
                elif isinstance(widget, ctk.CTkEntry): widget.delete(0, tk.END); widget.insert(0, str(value) if value is not None else "")
                elif isinstance(widget, ctk.CTkCheckBox): widget.select() if value == 1 else widget.deselect()
                elif isinstance(widget, ctk.CTkTextbox): widget.delete("1.0", tk.END); widget.insert("1.0", str(value) if value is not None else "")
        
        qty, per = self.existing_data.get('Quantity', 0), self.existing_data.get('UnitsPerCarton')
        if per and per > 0:
            self.entry_qty_cartons.insert(0, str(qty//per)); self.entry_qty_loose.insert(0, str(qty%per))
        else:
            self.entry_qty_cartons.insert(0, "0"); self.entry_qty_loose.insert(0, str(qty))
        self.calculate_total_qty()

    def update_field_visual_states(self):
        is_adhoc = self.entries['IsAdhoc'].get() == 1
        is_dg_checked = self.entries['IsDangerousGood'].get() == 1
        is_quarantined_checked = self.entries['IsQuarantined'].get() == 1
        is_first_checked = self.entries['IsFirst'].get() == 1
        
        print(f"DEBUG: update_field_visual_states - adhoc={is_adhoc}, dg={is_dg_checked}, quarantined={is_quarantined_checked}, first={is_first_checked}")
        default_text_color = self.entries['SKU'].cget("text_color")

        # --- LSI-derived text fields (Brand, Desc, ShelfLoc, Barcode) ---
        state_for_lsi_fields = "normal" if is_adhoc else "disabled"
        print(f"DEBUG: Setting LSI fields state to: {state_for_lsi_fields}")
        color_for_lsi_fields = default_text_color if is_adhoc else self.disabled_lsi_field_text_color
        for key in self.lsi_derived_fields_keys: # ['Brand', 'Description', 'ShelfLocation', 'Barcode']
            if key in self.entries:
                widget = self.entries[key]
                widget.configure(state=state_for_lsi_fields, text_color=color_for_lsi_fields)
        
        # --- UnitsPerCarton: Always editable state, visual style optionally based on Adhoc ---
        self.entries['UnitsPerCarton'].configure(state="normal", text_color=default_text_color)

        # --- DG Checkbox: Editability depends ONLY on Adhoc ---
        state_for_dg_check = "normal" if is_adhoc else "disabled"
        self.entries['IsDangerousGood'].configure(state=state_for_dg_check)
        
        # --- DG UN Number: Editability depends on Adhoc AND DG checkbox being checked ---
        can_edit_dg_un = is_adhoc and is_dg_checked
        state_for_dg_un = "normal" if can_edit_dg_un else "disabled"
        color_for_dg_un = default_text_color if can_edit_dg_un else self.disabled_lsi_field_text_color
        
        self.entries['DG_UN_Number'].configure(state=state_for_dg_un, text_color=color_for_dg_un)
        if not is_dg_checked:
            if self.entries['DG_UN_Number'].cget('state') == "disabled":
                self.entries['DG_UN_Number'].configure(state="normal")
                self.entries['DG_UN_Number'].delete(0, tk.END)
                self.entries['DG_UN_Number'].configure(state="disabled")
            else:
                self.entries['DG_UN_Number'].delete(0, tk.END)

        # --- IsQuarantined and IsFirst Checkboxes (Mutually Exclusive Logic) ---
        if is_quarantined_checked:
            self.entries['IsFirst'].deselect()
            self.entries['IsFirst'].configure(state="disabled")
            self.entries['IsQuarantined'].configure(state="normal")
        elif is_first_checked:
            self.entries['IsQuarantined'].deselect()
            self.entries['IsQuarantined'].configure(state="disabled")
            self.entries['IsFirst'].configure(state="normal")
        else:
            self.entries['IsQuarantined'].configure(state="normal")
            self.entries['IsFirst'].configure(state="normal")

        # --- SKU field and LSI Search button ---
        if self.mode == 'update':
            self.entries['SKU'].configure(state="disabled", text_color=self.disabled_lsi_field_text_color)
            self.lsi_search_button.configure(state="disabled")
        else:
            self.entries['SKU'].configure(state="normal", text_color=default_text_color)
            self.lsi_search_button.configure(state="normal")

    def on_status_flags_change(self):
        print(f"DEBUG: on_status_flags_change called")
        self.update_field_visual_states()

    def calculate_total_qty(self, event=None):
        try:
            cartons = int(self.entry_qty_cartons.get() or 0)
            per = int(self.entries['UnitsPerCarton'].get() or 0) if self.entries['UnitsPerCarton'].get() else 0
            loose = int(self.entry_qty_loose.get() or 0)
            for entry, val in [(self.entry_qty_cartons, cartons), (self.entries['UnitsPerCarton'], per), (self.entry_qty_loose, loose)]:
                if val < 0: entry.delete(0, tk.END); entry.insert(0, "0");
            cartons=max(0,cartons); per=max(0,per); loose=max(0,loose)
            self.entries['Quantity'].configure(text=str((cartons * per) + loose))
        except ValueError: self.entries['Quantity'].configure(text="Error")

    def trigger_lsi_search(self, event=None):
        sku = self.entries['SKU'].get().strip().upper()
        if not sku: 
            messagebox.showinfo("SKU Search", "Please enter an SKU.", parent=self)
            return

        print(f"DEBUG: trigger_lsi_search - Searching LSI for SKU: {sku}")
        lsi_data = self.app.fetch_lsi_data(sku)
        
        # Ensure warning label exists before trying to grid_remove
        if hasattr(self, 'adhoc_lsi_warning_label'):
            self.adhoc_lsi_warning_label.grid_remove()

        # --- Always ensure fields are in normal state before attempting to populate ---
        fields_to_enable = self.lsi_derived_fields_keys + ['DG_UN_Number', 'UnitsPerCarton', 'IsDangerousGood', 'IsQuarantined', 'IsFirst']
        for key in fields_to_enable:
            if key in self.entries:
                self.entries[key].configure(state="normal") 

        # --- Process LSI Result ---
        if lsi_data:
            print(f"DEBUG: trigger_lsi_search - LSI data found for {sku}")
            self.entries['IsAdhoc'].deselect()

            # Populate LSI-derived text fields
            for key in self.lsi_derived_fields_keys: # ['Brand', 'Description', 'ShelfLocation', 'Barcode']
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, lsi_data.get(key, ''))
            
            # Populate UnitsPerCarton
            self.entries['UnitsPerCarton'].delete(0, tk.END)
            units_val = lsi_data.get('UnitsPerCarton') # Could be None or integer
            self.entries['UnitsPerCarton'].insert(0, str(units_val) if units_val is not None else '')

            # Populate DG Checkbox
            if lsi_data.get('IsDangerousGood', 0) == 1: 
                self.entries['IsDangerousGood'].select()
            else: 
                self.entries['IsDangerousGood'].deselect()
                
            # Populate DG UN Number (handling None)
            self.entries['DG_UN_Number'].delete(0, tk.END)
            dg_un_val = lsi_data.get('DG_UN_Number')
            self.entries['DG_UN_Number'].insert(0, str(dg_un_val) if dg_un_val is not None else '') 

        else:
            print(f"DEBUG: trigger_lsi_search - LSI data NOT found for {sku}")
            if self.entries['IsAdhoc'].get() == 0:
                print("DEBUG: trigger_lsi_search - Adhoc not checked, clearing LSI fields.")
                for key_to_clear in self.lsi_derived_fields_keys + ['DG_UN_Number', 'UnitsPerCarton']: 
                     if key_to_clear in self.entries: 
                         self.entries[key_to_clear].delete(0,tk.END)
                if 'IsDangerousGood' in self.entries: 
                    self.entries['IsDangerousGood'].deselect()
            else:
                 print("DEBUG: trigger_lsi_search - Adhoc IS checked, leaving fields as is.")
            
            if hasattr(self, 'adhoc_lsi_warning_label'):
                self.adhoc_lsi_warning_label.grid(row=0, column=5, padx=self.app.get_scaled_padding((2,0)), sticky="w")
                
            messagebox.showwarning("SKU Not Found", f"SKU '{sku}' not found in LSI.", parent=self)

        # --- Update field visual states (enabled/disabled/color) based on current Adhoc status ---
        self.update_field_visual_states() 
        # --- Recalculate total quantity ---
        self.calculate_total_qty() 

    def save_item(self):
        item_data = {}
        for key in self.field_keys:
            if key in self.entries:
                widget = self.entries[key]
                if isinstance(widget, ctk.CTkEntry): item_data[key] = widget.get().strip()
                elif isinstance(widget, ctk.CTkCheckBox): item_data[key] = widget.get() # Gets 0 or 1
                elif isinstance(widget, ctk.CTkTextbox): item_data[key] = widget.get("1.0", tk.END).strip()
                elif isinstance(widget, ctk.CTkLabel) and key == 'Quantity': # For the Qty display label
                    try: item_data[key] = int(widget.cget("text"))
                    except ValueError: messagebox.showerror("Input Error", "Invalid Total Quantity.", parent=self); return
        
        # Ensure IsAdhoc is from the checkbox
        item_data['IsAdhoc'] = self.entries['IsAdhoc'].get()
        item_data['IsQuarantined'] = self.entries['IsQuarantined'].get()
        item_data['IsFirst'] = self.entries['IsFirst'].get()

        # Mutual exclusivity check before saving (belt and braces)
        if item_data['IsQuarantined'] == 1 and item_data['IsFirst'] == 1:
            messagebox.showerror("Input Error", "An item cannot be both 'Quarantined' and 'Use First'. Please uncheck one.", parent=self)
            return

        # Validate and process UnitsPerCarton
        try:
            per_text = item_data.get('UnitsPerCarton', '')
            item_data['UnitsPerCarton'] = int(per_text) if per_text and per_text.strip() else None
            if item_data.get('UnitsPerCarton') is not None and item_data['UnitsPerCarton'] < 0:
                item_data['UnitsPerCarton'] = 0
        except ValueError:
            messagebox.showerror("Input Error", "Invalid 'Units Per Carton'. Must be a number.", parent=self); return
        
        # Validate SKU
        if not item_data.get('SKU'):
            messagebox.showerror("Input Error", "SKU is required.", parent=self); return
        
        # Validate and format ExpiryDate
        expiry_db_str = None
        expiry_input = item_data.get('ExpiryDate', '')
        if expiry_input:
            try:
                exp_month, exp_year = map(int, expiry_input.split('/'))
                if not (1 <= exp_month <= 12 and 1900 < exp_year < 2999): raise ValueError("Invalid month/year range")
                last_day = calendar.monthrange(exp_year, exp_month)[1]
                expiry_date_obj = datetime.date(exp_year, exp_month, last_day)
                expiry_db_str = expiry_date_obj.strftime('%Y-%m-%d')
            except Exception as e:
                messagebox.showerror("Input Error", "Invalid Expiry Date. Please use MM/YYYY format.", parent=self); return
        
        # Process Dangerous Goods
        dg_un_number_val = item_data.get('DG_UN_Number', "")
        is_dg_checked_val = self.entries['IsDangerousGood'].get() == 1
        is_dg_flag_to_save = 1 if is_dg_checked_val and dg_un_number_val and dg_un_number_val.strip() else 0
        actual_dg_un_to_store = dg_un_number_val.strip() if dg_un_number_val and dg_un_number_val.strip() else None
        now_str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        user_name = self.app.current_username if self.app and hasattr(self.app, 'current_username') else "Unknown"
        is_quarantined_val = self.entries['IsQuarantined'].get()
        is_first_val = self.entries['IsFirst'].get()

        # Prepare data for SQL using DB column names as keys where possible
        sql_data = {
            'LocationName': self.location_code,
            'SKU': item_data.get('SKU'),
            'Brand': item_data.get('Brand'),
            'Description': item_data.get('Description'),
            'ShelfLocation': item_data.get('ShelfLocation'),
            'IsDangerousGood': is_dg_flag_to_save,
            'Barcode': item_data.get('Barcode'),
            'Batch': item_data.get('Batch'),
            'ExpiryDate': expiry_db_str,
            'Quantity': item_data.get('Quantity', 0),
            'UnitsPerCarton': item_data.get('UnitsPerCarton'),
            'Notes': item_data.get('Notes'),
            'LastUpdatedBy': user_name,
            'LastUpdatedDate': now_str,
            'IsAdhoc': item_data.get('IsAdhoc'),
            'DG_UN_NUMBER': actual_dg_un_to_store,
            'IsQuarantined': is_quarantined_val,
            'IsFirst': is_first_val
        }

        if not self.app or not self.app.conn:
            messagebox.showerror("Database Error", "Database connection is not available.", parent=self); return
        
        cursor = self.app.conn.cursor()
        try:
            if self.mode == 'new':
                # --- Check if location needs DateFirstStocked updated --- #
                needs_date_update = False
                try:
                    cursor.execute("SELECT DateFirstStocked FROM dbo.Locations WHERE LocationName = ?", (self.location_code,))
                    result = cursor.fetchone()
                    if result and result.DateFirstStocked is None:
                        needs_date_update = True
                except Exception as check_err:
                    print(f"Warning: Could not check DateFirstStocked for {self.location_code}: {check_err}")

                # --- Perform INSERT into StockItems ---
                cols_ordered = ['LocationName', 'SKU', 'Brand', 'Description', 'ShelfLocation', 'IsDangerousGood', 'Barcode', 'Batch', 'ExpiryDate', 'Quantity', 'UnitsPerCarton', 'Notes', 'LastUpdatedBy', 'LastUpdatedDate', 'IsAdhoc', 'DG_UN_NUMBER', 'IsQuarantined', 'IsFirst']
                placeholders = ', '.join(['?'] * len(cols_ordered))
                sql_insert = f"INSERT INTO dbo.StockItems ({', '.join(cols_ordered)}) VALUES ({placeholders})"
                params_tuple_insert = tuple(sql_data.get(col) for col in cols_ordered)
                cursor.execute(sql_insert, params_tuple_insert)

                cursor.execute("SELECT @@IDENTITY AS NewID;")
                new_stock_item_id = cursor.fetchone().NewID

                print(f"DEBUG: Inserted StockItem for {self.location_code}, new ID: {new_stock_item_id}")


                # --- DateFirstStocked if needed ---
                if needs_date_update:
                    try:
                        sql_update_loc = "UPDATE Locations SET DateFirstStocked = ? WHERE LocationName = ?"
                        cursor.execute(sql_update_loc, (sql_data['LastUpdatedDate'], self.location_code))
                        print(f"DEBUG: Updated DateFirstStocked for {self.location_code}")
                    except Exception as update_err:
                        print(f"Warning: Failed to update DateFirstStocked for {self.location_code}: {update_err}")
                
                # --- Log 'CREATE' to StockItemHistory ---
                if new_stock_item_id and self.app.current_user_id is not None:
                    history_notes = f"New item created in location {sql_data['LocationName']}."
                    sql_history_create = """
                        INSERT INTO dbo.StockItemHistory 
                            (StockItemID, ChangeTimestamp, UserID, ChangeType, LocationName, SKU, Notes)
                        VALUES (?, ?, ?, 'CREATE', ?, ?, ?)
                    """
                    history_params_create = (
                        new_stock_item_id,
                        sql_data['LastUpdatedDate'],
                        self.app.current_user_id,
                        sql_data['LocationName'],
                        sql_data['SKU'],
                        history_notes
                    )
                    cursor.execute(sql_history_create, history_params_create)
                    print(f"DEBUG: Logged CREATE history for StockItemID {new_stock_item_id}")
                else:
                    if not new_stock_item_id: print("Warning: Could not get new_stock_item_id for history logging.")
                    if self.app.current_user_id is None: print("Warning: current_user_id is None, cannot log history accurately.")

            elif self.mode == 'update' and self.stock_item_id:
                update_data = sql_data.copy()
                update_data.pop('LocationName', None); update_data.pop('SKU', None)
                db_cols_map = {'Brand':'Brand', 'Description':'Description', 'ShelfLocation':'ShelfLocation', 'Barcode':'Barcode', 'Batch':'Batch', 'ExpiryDate':'ExpiryDate', 'Quantity':'Quantity', 'UnitsPerCarton':'UnitsPerCarton', 'Notes':'Notes', 'IsDangerousGood':'IsDangerousGood', 'DG_UN_NUMBER':'DG_UN_NUMBER', 'IsAdhoc':'IsAdhoc', 'IsQuarantined':'IsQuarantined', 'IsFirst':'IsFirst', 'LastUpdatedBy':'LastUpdatedBy', 'LastUpdatedDate':'LastUpdatedDate'}
                set_clause_parts = []; params_list = []
                for col_name, value in update_data.items():
                    db_col = db_cols_map.get(col_name)
                    if db_col:
                        set_clause_parts.append(f"{db_col} = ?")
                        params_list.append(value)
                set_clause = ', '.join(set_clause_parts)
                sql_update = f"UPDATE dbo.StockItems SET {set_clause} WHERE StockItemID = ?"
                params_tuple_update = tuple(params_list) + (self.stock_item_id,)
                cursor.execute(sql_update, params_tuple_update)
                print(f"DEBUG: Updated StockItemID {self.stock_item_id}")

                # --- Log Update to StockItemHistory ---
                if self.app.current_user_id is not None:
                    history_notes_update = f"Item details updated for SKU {sql_data['SKU']} in {sql_data['LocationName']}."
                    sql_history_update = """
                        INSERT INTO dbo.StockItemHistory
                            (StockItemID, ChangeTimestamp, UserID, ChangeType, LocationName, SKU, FieldName, Notes)
                        VALUES (?, ?, ?, 'UPDATE', ?, ?, 'RECORD_UPDATE', ?)
                    """
                    history_params_update = (
                        self.stock_item_id,
                        sql_data['LastUpdatedDate'],
                        self.app.current_user_id,
                        sql_data['LocationName'],
                        sql_data['SKU'],
                        history_notes_update
                    )
                    cursor.execute(sql_history_update, history_params_update)
                    print(f"DEBUG: Logged generic UPDATE history for StockItemID {self.stock_item_id}")

            # --- Commit Transaction ---
            self.app.conn.commit()
            messagebox.showinfo("Success", f"Item {self.mode} successful.", parent=self.master)
            if self.source_view == 'sku' and self.mode == 'update':
                sku_to_refresh = self.entries['SKU'].get() 
                if sku_to_refresh and hasattr(self.app, 'navigate_to_sku_results'):
                    print(f"UpdateNew: Requesting SKU results refresh for {sku_to_refresh}")
                    self.app.navigate_to_sku_results(sku_to_refresh)
                else:
                    if hasattr(self.app, 'refresh_location_results'): self.app.refresh_location_results(self.location_code)
            elif hasattr(self.app, 'refresh_location_results'):
                self.app.refresh_location_results(self.location_code)
            
            self.destroy()

        except pyodbc.Error as e:
            if self.app.conn: self.app.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to save item: {e}", parent=self)
        except Exception as e:
            if self.app.conn: self.app.conn.rollback()
            sql_str = sql_data if 'sql' in locals() else 'N/A'
            params_str = params_tuple_update if 'params_tuple' in locals() else 'N/A'
            messagebox.showerror("Error", f"An unexpected error occurred during save: {e}\nSQL: {sql_str}\nParams: {params_str}", parent=self)