import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime

class LocationResultsFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance, location_code, stock_data, location_header_data):
        super().__init__(master, fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.app = app_instance
        self.location_code = location_code
        self.stock_data = stock_data
        self.location_header_data = location_header_data

        # --- Define fonts ---
        self.header_label_font = self.app.get_font(size=14, weight="bold")
        self.header_data_font = self.app.get_font(size=14)
        self.notes_font = self.app.get_font(size=13)
        self.button_font = self.app.get_font(size=14, weight="bold")
        self.button_height = self.app.get_scaled_size(35)
        self.tree_font_family = "Segoe UI"
        self.tree_font_size = 11

        # -- BUTTON COLORS
        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        neutral_fg, neutral_hover, neutral_text, neutral_dtext = self.app.get_button_color_config("destructive")
        warning_fg, warning_hover, warning_text, warning_dtext = self.app.get_button_color_config("warning")
        standard_fg, standard_hover, standard_text, standard_dtext = self.app.get_button_color_config("standard")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")       

        # --- Configure Main Frame Grid ---
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(1, weight=1)

        # --- Top Section (Location + Header + Notes) ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((10, 5)))
        self.top_frame.grid_columnconfigure(0, weight=0); self.top_frame.grid_columnconfigure(1, weight=1); self.top_frame.grid_columnconfigure(2, weight=0, minsize=self.app.get_scaled_size(200))
        self.top_frame.grid_rowconfigure(0, weight=1)

        # --- Box for Large Location Display (Column 0) ---
        self.location_display_frame = ctk.CTkFrame(self.top_frame, border_width=2, width=self.app.get_scaled_size(180))
        self.location_display_frame.grid(row=0, column=0, padx=self.app.get_scaled_padding((10, 15)), pady=self.app.get_scaled_padding(5), sticky="ns"); self.location_display_frame.grid_propagate(False)
        self.location_display_frame.grid_rowconfigure(0, weight=1); self.location_display_frame.grid_columnconfigure(0, weight=1)
        self.location_display_label = ctk.CTkLabel(self.location_display_frame, text=self.location_code, font=ctk.CTkFont(size=48, weight="bold"), anchor="center")
        self.location_display_label.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="nsew")

        # --- Main Header Details Frame (Column 1) - RIGID 4-COLUMN GRID ---
        self.header_frame = ctk.CTkFrame(self.top_frame)
        self.header_frame.grid(row=0, column=1, sticky="nsew", padx=self.app.get_scaled_padding((0, 15)), pady=self.app.get_scaled_padding(5))

        # Configure 4 columns - ALL WEIGHT=0, RELY ON MINSIZE
        label_col_width = self.app.get_scaled_size(95)
        data_col1_width = self.app.get_scaled_size(250)
        data_col2_width = self.app.get_scaled_size(305)
        self.header_frame.grid_columnconfigure(0, weight=0, minsize=label_col_width)
        self.header_frame.grid_columnconfigure(1, weight=0, minsize=data_col1_width)
        self.header_frame.grid_columnconfigure(2, weight=0, minsize=label_col_width)
        self.header_frame.grid_columnconfigure(3, weight=0, minsize=data_col2_width)

        # Define data label background color
        try: current_mode = ctk.get_appearance_mode()
        except: current_mode = "Light"
        data_label_bg = "#3A3A3A" if current_mode == "Dark" else "#E5E5E5"
        grid_padx = (5, 20) # Horizontal padding for data labels in grid
        grid_pady = (1, 5) # Vertical padding (above, below) for data labels in grid

        # --- Row 1: CODE / BRAND ---
        row_num = 0
        ctk.CTkLabel(self.header_frame, text="CODE:", anchor="e", font=self.header_label_font).grid(row=row_num, column=0, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_code_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3)
        self.header_code_label.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew")

        ctk.CTkLabel(self.header_frame, text="BRAND:", anchor="e", font=self.header_label_font).grid(row=row_num, column=2, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_brand_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3) 
        self.header_brand_label.grid(row=row_num, column=3, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew")

        # --- Row 2: DESCRIPTION ---
        row_num += 1
        ctk.CTkLabel(self.header_frame, text="DESCRIPTION:", anchor="e", font=self.header_label_font).grid(row=row_num, column=0, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="ne")
        self.header_desc_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", justify="left", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3, wraplength=550) 
        self.header_desc_label.grid(row=row_num, column=1, columnspan=3, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew")

        # --- Row 3: BATCH / EXPIRY ---
        row_num += 1
        ctk.CTkLabel(self.header_frame, text="BATCH:", anchor="e", font=self.header_label_font).grid(row=row_num, column=0, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_batch_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3) 
        self.header_batch_label.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew") 

        ctk.CTkLabel(self.header_frame, text="EXPIRY:", anchor="e", font=self.header_label_font).grid(row=row_num, column=2, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_expiry_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3) 
        self.header_expiry_label.grid(row=row_num, column=3, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew") 

        # --- Row 4: BARCODE / QTY ---
        row_num += 1
        ctk.CTkLabel(self.header_frame, text="BARCODE:", anchor="e", font=self.header_label_font).grid(row=row_num, column=0, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_barcode_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3) 
        self.header_barcode_label.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew") 

        ctk.CTkLabel(self.header_frame, text="QTY:", anchor="e", font=self.header_label_font).grid(row=row_num, column=2, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_qty_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3)
        self.header_qty_label.grid(row=row_num, column=3, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew") 

        # --- Row 5: SHELFLOC / UPDATED ---
        row_num += 1
        ctk.CTkLabel(self.header_frame, text="SHELFLOC:", anchor="e", font=self.header_label_font).grid(row=row_num, column=0, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_shelfloc_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3) 
        self.header_shelfloc_label.grid(row=row_num, column=1, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew") 

        ctk.CTkLabel(self.header_frame, text="UPDATED:", anchor="e", font=self.header_label_font).grid(row=row_num, column=2, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_lastupdated_label = ctk.CTkLabel(self.header_frame, text="...", anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3) 
        self.header_lastupdated_label.grid(row=row_num, column=3, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew") 

        # --- Row 6: QUARANTINE STATUS ---
        row_num += 1
        # This label will only show text if quarantined, otherwise it will be empty.
        ctk.CTkLabel(self.header_frame, text="STATUS:", anchor="e", font=self.header_label_font).grid(row=row_num, column=0, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        self.header_quarantine_status_label = ctk.CTkLabel(self.header_frame, text="", anchor="w", font=ctk.CTkFont(size=14, weight="bold"), text_color="red")
        self.header_quarantine_status_label.grid(row=row_num, column=1, columnspan=3, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew")

        # Date First Stocked
        ctk.CTkLabel(self.header_frame, text="FIRST STOCKED:", anchor="e", font=self.header_label_font).grid(row=row_num, column=2, padx=self.app.get_scaled_padding((10,2)), pady=self.app.get_scaled_padding(grid_pady), sticky="e")
        first_stocked_val = self.location_header_data.get('DateFirstStocked') if self.location_header_data else None
        first_stocked_display_text = self.format_datetime_display(first_stocked_val) if first_stocked_val else "Never"
        self.header_first_stocked_label = ctk.CTkLabel(self.header_frame, text=first_stocked_display_text, anchor="w", font=self.header_data_font, fg_color=data_label_bg, corner_radius=3)
        self.header_first_stocked_label.grid(row=row_num, column=3, padx=self.app.get_scaled_padding(grid_padx), pady=self.app.get_scaled_padding(grid_pady), sticky="ew")

        # --- Notes Display Frame (Column 2 in top_frame) ---
        self.notes_display_frame = ctk.CTkFrame(self.top_frame, border_width=1)
        self.notes_display_frame.grid(row=0, column=2, padx=self.app.get_scaled_padding((0, 10)), pady=self.app.get_scaled_padding(5), sticky="nsew")
        self.notes_display_frame.grid_columnconfigure(0, weight=1); self.notes_display_frame.grid_rowconfigure(1, weight=1)

        # Static "NOTES:" label
        ctk.CTkLabel(self.notes_display_frame, text="NOTES:", anchor="w", font=self.header_label_font).grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding((5,2)), sticky="ew")

        # Container frame for the actual notes text (for padding/scrolling later if needed)
        notes_data_container = ctk.CTkFrame(self.notes_display_frame, fg_color="transparent")
        notes_data_container.grid(row=1, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding((0,5)), sticky="nsew")
        notes_data_container.grid_columnconfigure(0, weight=1); notes_data_container.grid_rowconfigure(0, weight=1)

        # Create the actual label instance and assign it to self.header_notes_label
        self.header_notes_label = ctk.CTkLabel(notes_data_container, text="...", anchor="nw", justify="left", wraplength=180, font=self.notes_font)

        self.header_notes_label.grid(row=0, column=0, sticky="nsew")

        # --- Middle Row: Stock Items Table ---
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(5))
        self.table_frame.grid_rowconfigure(0, weight=1); self.table_frame.grid_columnconfigure(0, weight=1)

        # --- Treeview Setup ---
        style = ttk.Style(); 
        style.map('Treeview', background=[('selected', '#A9CCE3')], foreground=[('selected', 'black')])
        style.configure("Treeview.Heading", font=self.app.get_treeview_font(size=self.tree_font_size + 1, weight="bold")) 
        style.configure("Treeview", rowheight=self.app.get_scaled_size(int(self.tree_font_size * 2.2)), font=self.app.get_treeview_font(size=self.tree_font_size))
        self.tree = ttk.Treeview(self.table_frame, style="Treeview", show='headings', selectmode='browse')
        columns = ('code', 'description', 'barcode', 'brand', 'shelflocation', 'batch', 'exp', 'qty', 'dg', 'notes')
        self.tree['columns'] = columns
        self.tree.heading('code', text='CODE'); self.tree.heading('description', text='DESCRIPTION'); self.tree.heading('barcode', text='BARCODE'); self.tree.heading('brand', text='BRAND'); self.tree.heading('shelflocation', text='SHELF'); self.tree.heading('batch', text='BATCH'); self.tree.heading('exp', text='EXP'); self.tree.heading('qty', text='QTY'); self.tree.heading('dg', text='DG'); self.tree.heading('notes', text='NOTES')
        self.tree.column('#0', width=self.app.get_scaled_size(0), stretch=tk.NO); self.tree.column('code', width=self.app.get_scaled_size(75), anchor=tk.W, stretch=tk.NO); self.tree.column('description', width=self.app.get_scaled_size(270), anchor=tk.W, stretch=tk.YES); self.tree.column('barcode', width=self.app.get_scaled_size(130), anchor=tk.CENTER, stretch=tk.NO); self.tree.column('brand', width=self.app.get_scaled_size(95), anchor=tk.W, stretch=tk.NO); self.tree.column('shelflocation', width=self.app.get_scaled_size(80), anchor=tk.CENTER, stretch=tk.NO); self.tree.column('batch', width=self.app.get_scaled_size(100), anchor=tk.W, stretch=tk.NO); self.tree.column('exp', width=self.app.get_scaled_size(70), anchor=tk.CENTER, stretch=tk.NO); self.tree.column('qty', width=self.app.get_scaled_size(60), anchor=tk.E, stretch=tk.NO); self.tree.column('dg', width=self.app.get_scaled_size(40), anchor=tk.CENTER, stretch=tk.NO); self.tree.column('notes', width=self.app.get_scaled_size(200), anchor=tk.W, stretch=tk.YES)
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview); vsb.grid(row=0, column=1, sticky='ns')
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview); hsb.grid(row=1, column=0, sticky='ew')
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')

        # --- Bindings and Tags ---
        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)
        self.tree.bind('<Delete>', self.request_clear_line)
        self.tree.bind('<Double-1>', self.update_item)

        # --- Specific Tags (IsFirst / IsQuarantined) ---
        self.tree.tag_configure('quarantined_row', background='#FADBD8', foreground='black') # Light Red
        self.tree.tag_configure('use_first_row', background='#D2B4DE', foreground='black') # Light Purple

        # --- Bind F4 and F5 keys ---
        self.bind("<F4>", self.update_item_fkey) 
        self.bind("<F5>", self.add_new_item_fkey) 
        self.tree.bind("<F4>", self.update_item_fkey)
        self.tree.bind("<F5>", self.add_new_item_fkey)

        # Populate the table
        self.populate_table()

        # --- Bottom Row: Buttons ---
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((5, 10)))
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.back_button = ctk.CTkButton(self.button_frame, text="BACK", width=self.app.get_scaled_size(100), command=self.go_back, 
                                         fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text,
                                         font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.back_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))
        self.update_button = ctk.CTkButton(self.button_frame, text="(F4) UPDATE", width=self.app.get_scaled_size(100), command=self.update_item, state="disabled",
                                           fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext,
                                           font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.update_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))
        self.new_button = ctk.CTkButton(self.button_frame, text="(F5) NEW", width=self.app.get_scaled_size(100), command=self.add_new_item, 
                                        fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext, 
                                        font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.new_button.grid(row=0, column=2, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))
        self.find_sku_button = ctk.CTkButton(self.button_frame, text="SEARCH ITEM", width=self.app.get_scaled_size(120), command=self.go_to_sku_search, state="disabled",
                                             fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext,
                                             font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.find_sku_button.grid(row=0, column=3, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))
        self.clear_all_button = ctk.CTkButton(self.button_frame, text="CLEAR ALL", width=self.app.get_scaled_size(100), command=self.request_clear_all, 
                                              fg_color=warning_fg, hover_color=warning_hover, text_color=warning_text, text_color_disabled=warning_dtext, 
                                              font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.clear_all_button.grid(row=0, column=4, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))
        self.clear_line_button = ctk.CTkButton(self.button_frame, text="(DEL) CLEAR LINE", width=self.app.get_scaled_size(100), command=self.request_clear_line, state="disabled", 
                                              fg_color=warning_fg, hover_color=warning_hover, text_color=warning_text, text_color_disabled=warning_dtext,
                                               font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.clear_line_button.grid(row=0, column=5, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))

        # --- Final Setup ---
        self.select_first_row()

    # --- Helper Functions for Date/Time Parsing & Formatting ---
    def parse_date_robust(self, date_input):
        if date_input is None or date_input == '': return None
        if isinstance(date_input, (datetime.datetime, datetime.date)):
            return date_input.date() if isinstance(date_input, datetime.datetime) else date_input
        date_str_cleaned = str(date_input).strip()
        if not date_str_cleaned: return None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d', '%m/%d/%y', '%d-%b-%y', '%d-%b-%Y',
                    '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %I:%M:%S %p'):
            try: return datetime.datetime.strptime(date_str_cleaned, fmt).date()
            except (ValueError, TypeError): continue
        return None

    def format_expiry_display(self, expiry_date_obj):
        if isinstance(expiry_date_obj, datetime.date): return expiry_date_obj.strftime('%m/%Y')
        return "N/A"

    def format_datetime_display(self, datetime_input):
        if datetime_input is None or str(datetime_input).strip() == '': return "N/A"
        dt_obj = None
        if isinstance(datetime_input, datetime.datetime): dt_obj = datetime_input
        elif isinstance(datetime_input, datetime.date): dt_obj = datetime.datetime.combine(datetime_input, datetime.time.min)
        else:
            datetime_str_cleaned = str(datetime_input).strip()
            if not datetime_str_cleaned: return "N/A"
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y %I:%M:%S %p', '%m/%d/%Y %I:%M:%S %p',
                        '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%m/%d/%Y %H:%M',
                        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                try: dt_obj = datetime.datetime.strptime(datetime_str_cleaned, fmt); break
                except (ValueError, TypeError): continue
        # The block using pandas is now removed
        if dt_obj: return dt_obj.strftime('%d/%m/%Y %H:%M')
        else: return str(datetime_input)

    # --- Table Population & Interaction ---
    def populate_table(self):
        """ Clears and fills the Treeview table with stock_data """

        # --- Explicitly clear all existing items from the tree ---
        try:
            existing_items = self.tree.get_children()
            if existing_items:
                self.tree.delete(*existing_items) 
        except tk.TclError as e:
             print(f"Warning: TclError during tree clear: {e}") 

        # --- Proceed with populating ---
        if self.stock_data:
            for item_row in self.stock_data:
                item_id = item_row.get('StockItemID')
                if not item_id:
                    print(f"Warning: Skipping row insert due to missing StockItemID: {item_row}")
                    continue

                # --- Get and Format Data ---
                
                # Dates
                expiry_date_obj = self.parse_date_robust(item_row.get('ExpiryDate'))
                exp_display = self.format_expiry_display(expiry_date_obj)

                # DG Display
                dg_un_no = item_row.get('DG_UN_Number')
                dg_display = ""
                if dg_un_no: 
                    dg_display = "Gas" if dg_un_no == '1950' else "Liq"

                # Notes (Truncated for Treeview)
                full_notes = item_row.get('Notes')
                notes_display = "" 
                if full_notes is not None: 
                    if isinstance(full_notes, str): 
                       notes_display = full_notes.split('\n', 1)[0]
                       if '\n' in full_notes and len(full_notes) > len(notes_display):
                           notes_display += "..."
                    else: 
                        notes_display = str(full_notes)

                # Other values (handle potential None)
                code = item_row.get('SKU', '') or ''
                description = item_row.get('Description', '') or ''
                barcode = item_row.get('Barcode', '') or ''
                brand = item_row.get('Brand', '') or ''
                shelfloc = item_row.get('ShelfLocation', '') or ''
                batch = item_row.get('Batch', '') or ''
                qty = item_row.get('Quantity', 0) or 0

                # --- Determine Tags ---
                tags_to_apply = []
                if item_row.get('IsQuarantined') == 1:
                    tags_to_apply.append('quarantined_row')
                elif item_row.get('IsFirst') == 1:
                    tags_to_apply.append('use_first_row')
                
                # --- Insert Row ---
                try: 
                    self.tree.insert('', tk.END, iid=item_id, values=(
                        code, description, barcode, brand, shelfloc, batch, exp_display, qty, dg_display, 
                        notes_display 
                    ), tags=tuple(tags_to_apply))
                except tk.TclError as e: 
                     print(f"ERROR: Failed to insert item with iid {item_id} into LocationResults tree: {e}")
                     print(f"       Problematic row data: {item_row}")
                     continue
 

    def on_row_select(self, event=None):
        selected_items = self.tree.selection()
        if selected_items:
            selected_iid = selected_items[0]
            selected_data = next((item for item in self.stock_data if str(item.get('StockItemID')) == str(selected_iid)), None)
            if selected_data:
                self.header_code_label.configure(text=selected_data.get('SKU', '...')); self.header_brand_label.configure(text=selected_data.get('Brand', '...')); self.header_shelfloc_label.configure(text=selected_data.get('ShelfLocation', '...')); self.header_desc_label.configure(text=selected_data.get('Description', '...')); self.header_batch_label.configure(text=selected_data.get('Batch', '...'));
                exp_date_obj = self.parse_date_robust(selected_data.get('ExpiryDate')); self.header_expiry_label.configure(text=self.format_expiry_display(exp_date_obj));
                self.header_qty_label.configure(text=selected_data.get('Quantity', '...')); self.header_barcode_label.configure(text=selected_data.get('Barcode', '...'));
                last_updated_val = selected_data.get('LastUpdatedDate'); last_updated_str = self.format_datetime_display(last_updated_val)
                last_updated_by = selected_data.get('LastUpdatedBy', 'N/A'); self.header_lastupdated_label.configure(text=f"{last_updated_str} by {last_updated_by}")
                notes = selected_data.get('Notes', '...'); self.header_notes_label.configure(text=notes if notes else '...')
                status_text = ""
                status_color = self.header_quarantine_status_label.cget("text_color")

                if selected_data.get('IsQuarantined') == 1:
                    status_text = "QUARANTINED"
                    status_color = "orange"
                elif selected_data.get('IsFirst') == 1:
                    status_text = "USE FIRST"
                    status_color = "dodgerblue"
                
                self.header_quarantine_status_label.configure(text=status_text, text_color=status_color)

                self.clear_line_button.configure(state="normal"); self.update_button.configure(state="normal"); self.find_sku_button.configure(state="normal")
            else:
                 print(f"Warning: Could not find data for selected iid {selected_iid}")
                 self.clear_header()
                 self.disable_selection_buttons()
        else: self.clear_header(); self.disable_selection_buttons()

    def select_first_row(self):
        children = self.tree.get_children()
        if children: self.tree.selection_set(children[0]); self.tree.focus(children[0]); self.tree.focus_set(); self.on_row_select()

    def clear_header(self):
        self.header_code_label.configure(text="..."); self.header_brand_label.configure(text="..."); self.header_shelfloc_label.configure(text="..."); self.header_desc_label.configure(text="..."); self.header_batch_label.configure(text="..."); self.header_expiry_label.configure(text="..."); self.header_qty_label.configure(text="..."); self.header_barcode_label.configure(text="..."); self.header_lastupdated_label.configure(text="..."); self.header_notes_label.configure(text="..."); self.header_quarantine_status_label.configure(text="")


    def disable_selection_buttons(self):
        self.clear_line_button.configure(state="disabled")
        self.update_button.configure(state="disabled")
        self.find_sku_button.configure(state="disabled")

    # --- Get Selected Info ---
    def get_selected_stock_item_id(self):
        selected_items = self.tree.selection()
        try:
            return int(selected_items[0]) if selected_items else None
        except (ValueError, IndexError):
            return None

    def get_selected_sku(self):
        selected_iid = self.get_selected_stock_item_id()
        if selected_iid:
             selected_data = next((item for item in self.stock_data if item.get('StockItemID') == selected_iid), None)
             if selected_data:
                 return selected_data.get('SKU')
        return None

    # --- Button Action Handlers (call App methods) ---
    def go_back(self):
        print("LocationResults: Requesting go back"); self.app.show_main_page()

    def add_new_item(self):
        print(f"LocationResults: Requesting add new item to {self.location_code}"); self.app.open_update_new_window(location_code=self.location_code, mode='new')

    def request_clear_all(self):
        print(f"LocationResults: Requesting clear all for {self.location_code}")
        if messagebox.askyesno("Confirm Clear All", f"Are you sure you want to clear ALL stock items from location {self.location_code}?", parent=self): self.app.clear_all_location(self.location_code)

    def request_clear_line(self, event=None):
        selected_iid = self.get_selected_stock_item_id()
        selected_sku = self.get_selected_sku()
        if selected_iid:
            print(f"LocationResults: Requesting clear line for StockItemID: {selected_iid} (SKU: {selected_sku})")
            if messagebox.askyesno("Confirm Clear Line", f"Are you sure you want to clear SKU '{selected_sku}' from location {self.location_code}?", parent=self):
                 self.app.clear_stock_item(selected_iid, self.location_code)
        else:
            messagebox.showwarning("No Selection", "Please select a line to clear.", parent=self)

    def update_item(self, event=None):
        selected_iid = self.get_selected_stock_item_id()
        if selected_iid:
            print(f"LocationResults: Requesting update for StockItemID: {selected_iid}")
            self.app.open_update_new_window(location_code=self.location_code, mode='update', stock_item_id=selected_iid)
        elif event and event.type == tk.EventType.ButtonPress and hasattr(event, 'widget') and event.widget == self.update_button:
             messagebox.showwarning("No Selection", "Please select a line to update.", parent=self)

    def go_to_sku_search(self):
        """ Gets the selected SKU and asks the app to navigate to the SKU results view. """
        selected_sku = self.get_selected_sku()
        if selected_sku:
            print(f"LocationResults: Requesting SKU results view for SKU: {selected_sku}")
            self.app.navigate_to_sku_results(selected_sku)
        else:
            messagebox.showwarning("No Selection", "Please select an item line to find other locations for its SKU.", parent=self)
    
    def add_new_item_fkey(self, event=None):
        """Handles F5 key press for adding a new item."""
        print("LocationResults: F5 pressed, calling add_new_item")
        self.add_new_item()

    def update_item_fkey(self, event=None):
        """Handles F4 key press for updating an item."""
        print("LocationResults: F4 pressed, calling update_item")
        self.update_item(event=event)