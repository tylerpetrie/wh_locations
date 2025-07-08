import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, font as tkfont
from tkinter import messagebox
import datetime

class SKUResultsFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance, searched_sku, sku_lsi_data, stock_data):
        super().__init__(master, fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.app = app_instance
        self.searched_sku = searched_sku
        self.sku_lsi_data = sku_lsi_data
        self.stock_data = stock_data

        # --- Define fonts ---
        self.header_label_font = self.app.get_font(size=14, weight="bold")
        self.header_data_font = self.app.get_font(size=14)
        self.notes_font = self.app.get_font(size=13)
        self.total_qty_font = self.app.get_font(size=15, weight="bold")
        self.location_count_font = self.app.get_font(size=14)
        self.sku_display_font = self.app.get_font(size=40, weight="bold")
        self.button_font = self.app.get_font(size=14, weight="bold")
        self.button_height = self.app.get_scaled_size(35)
        self.tree_font_family = "Segoi UI"
        self.tree_font_size = 11

        # --- Configure Main Frame Grid ---
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)

        # --- Top Section (Header: SKU Display | Details | Notes) ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="nsew", padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((10, 5)))
        self.top_frame.grid_columnconfigure(0, weight=0)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(2, weight=0, minsize=self.app.get_scaled_size(200))
        self.top_frame.grid_rowconfigure(0, weight=0)

        # --- Column 0: Large SKU Display ---
        self.sku_display_frame = ctk.CTkFrame(self.top_frame, border_width=self.app.get_scaled_size(2), width=self.app.get_scaled_size(180))
        self.sku_display_frame.grid(row=0, column=0, padx=self.app.get_scaled_padding((10, 15)), pady=self.app.get_scaled_padding(5), sticky="ns"); self.sku_display_frame.grid_propagate(False)
        self.sku_display_frame.grid_rowconfigure(0, weight=1); self.sku_display_frame.grid_columnconfigure(0, weight=1)
        sku_parts = self.searched_sku.split('-', 1)
        if len(sku_parts) == 2:
            display_sku_text = f"{sku_parts[0]}-\n{sku_parts[1]}"
        else:
            display_sku_text = self.searched_sku
        self.sku_display_label = ctk.CTkLabel(self.sku_display_frame, text=display_sku_text, font=self.sku_display_font, anchor="center")
        self.sku_display_label.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="nsew")

        # --- Column 1: Main Header Details (LSI + Aggregates) ---
        self.header_details_frame = ctk.CTkFrame(self.top_frame)
        self.header_details_frame.grid(row=0, column=1, sticky="nsew", padx=self.app.get_scaled_padding((0, 15)), pady=self.app.get_scaled_padding(5))
        label_col_width = self.app.get_scaled_size(95)
        self.header_details_frame.grid_columnconfigure(0, weight=0, minsize=self.app.get_scaled_size(label_col_width))
        self.header_details_frame.grid_columnconfigure(1, weight=1)
        self.header_details_frame.grid_columnconfigure(2, weight=0, minsize=self.app.get_scaled_size(label_col_width))
        self.header_details_frame.grid_columnconfigure(3, weight=1)

        # Header data background color
        try: current_mode = ctk.get_appearance_mode(); bg_col = "#3A3A3A" if current_mode == "Dark" else "#E5E5E5"
        except: bg_col = "#E5E5E5"
        hdr_padx = self.app.get_scaled_padding((5, 10)); hdr_pady = self.app.get_scaled_padding((2, 6))

        # Get LSI details or use placeholders
        brand = self.sku_lsi_data.get('Brand', 'N/A') if self.sku_lsi_data else 'N/A'
        desc = self.sku_lsi_data.get('Description', 'N/A') if self.sku_lsi_data else 'N/A'
        barcode = self.sku_lsi_data.get('Barcode', 'N/A') if self.sku_lsi_data else 'N/A'
        shelfloc = self.sku_lsi_data.get('ShelfLocation', 'N/A') if self.sku_lsi_data else 'N/A'
        is_dg = self.sku_lsi_data.get('IsDangerousGood', 0) if self.sku_lsi_data else 0
        dg_un = self.sku_lsi_data.get('DG_UN_Number') if self.sku_lsi_data else None
        dg_display = f"YES ({dg_un})" if is_dg and dg_un else ("YES" if is_dg else "NO")

        # Calculate Aggregates (will be updated in populate_table)
        self.total_quantity = 0
        self.location_count = 0

        # Create Header Labels
        r = 0
        ctk.CTkLabel(self.header_details_frame, text="BRAND:", anchor="e", font=self.header_label_font).grid(row=r, column=0, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_brand_label = ctk.CTkLabel(self.header_details_frame, text=brand, anchor="w", font=self.header_data_font, fg_color=bg_col, corner_radius=3)
        self.header_brand_label.grid(row=r, column=1, padx=hdr_padx, pady=hdr_pady, sticky="ew")
        ctk.CTkLabel(self.header_details_frame, text="BARCODE:", anchor="e", font=self.header_label_font).grid(row=r, column=2, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_barcode_label = ctk.CTkLabel(self.header_details_frame, text=barcode, anchor="w", font=self.header_data_font, fg_color=bg_col, corner_radius=3)
        self.header_barcode_label.grid(row=r, column=3, padx=hdr_padx, pady=hdr_pady, sticky="ew"); r+=1

        ctk.CTkLabel(self.header_details_frame, text="DESCRIPTION:", anchor="e", font=self.header_label_font).grid(row=r, column=0, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_desc_label = ctk.CTkLabel(self.header_details_frame, text=desc, anchor="w", justify="left", font=self.header_data_font, fg_color=bg_col, corner_radius=3, wraplength=500)
        self.header_desc_label.grid(row=r, column=1, columnspan=3, padx=hdr_padx, pady=hdr_pady, sticky="ew"); r+=1

        ctk.CTkLabel(self.header_details_frame, text="LSI SHELFLOC:", anchor="e", font=self.header_label_font).grid(row=r, column=0, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_lsishelfloc_label = ctk.CTkLabel(self.header_details_frame, text=shelfloc, anchor="w", font=self.header_data_font, fg_color=bg_col, corner_radius=3)
        self.header_lsishelfloc_label.grid(row=r, column=1, padx=hdr_padx, pady=hdr_pady, sticky="ew")
        ctk.CTkLabel(self.header_details_frame, text="DG STATUS:", anchor="e", font=self.header_label_font).grid(row=r, column=2, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_dg_label = ctk.CTkLabel(self.header_details_frame, text=dg_display, anchor="w", font=self.header_data_font, fg_color=bg_col, corner_radius=3)
        self.header_dg_label.grid(row=r, column=3, padx=hdr_padx, pady=hdr_pady, sticky="ew"); r+=1

        # Oldest/Newest Expiry and Associated Batch Row 1
        ctk.CTkLabel(self.header_details_frame, text="EARLIEST EXP:", anchor="e", font=self.header_label_font).grid(row=r, column=0, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_oldest_expiry_label = ctk.CTkLabel(self.header_details_frame, text="N/A", anchor="w", font=self.header_data_font, fg_color=bg_col, corner_radius=3)
        self.header_oldest_expiry_label.grid(row=r, column=1, padx=hdr_padx, pady=hdr_pady, sticky="ew")
        
        ctk.CTkLabel(self.header_details_frame, text="Batch:", anchor="e", font=self.header_label_font).grid(row=r, column=2, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e") 
        self.header_oldest_expiry_batch_label = ctk.CTkLabel(self.header_details_frame, text="N/A", anchor="w", font=self.header_data_font, fg_color=bg_col, corner_radius=3) 
        self.header_oldest_expiry_batch_label.grid(row=r, column=3, padx=hdr_padx, pady=hdr_pady, sticky="ew"); r+=1


        # Oldest/Newest Expiry and Associated Batch Row 2
        ctk.CTkLabel(self.header_details_frame, text="LATEST EXP:", anchor="e", font=self.header_label_font).grid(row=r, column=0, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_newest_expiry_label = ctk.CTkLabel(self.header_details_frame, text="N/A", anchor="w", font=self.header_data_font, fg_color=bg_col, corner_radius=3)
        self.header_newest_expiry_label.grid(row=r, column=1, padx=hdr_padx, pady=hdr_pady, sticky="ew")

        ctk.CTkLabel(self.header_details_frame, text="Batch:", anchor="e", font=self.header_label_font).grid(row=r, column=2, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_newest_expiry_batch_label = ctk.CTkLabel(self.header_details_frame, text="N/A", anchor="w", font=self.header_data_font, fg_color=bg_col, corner_radius=3) 
        self.header_newest_expiry_batch_label.grid(row=r, column=3, padx=hdr_padx, pady=hdr_pady, sticky="ew"); r+=1
        
        # Aggregate Info Row
        ctk.CTkLabel(self.header_details_frame, text="TOTAL QTY:", anchor="e", font=self.header_label_font).grid(row=r, column=0, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_total_qty_label = ctk.CTkLabel(self.header_details_frame, text="0", anchor="w", font=self.total_qty_font)
        self.header_total_qty_label.grid(row=r, column=1, padx=hdr_padx, pady=hdr_pady, sticky="w")
        ctk.CTkLabel(self.header_details_frame, text="LOCATIONS:", anchor="e", font=self.header_label_font).grid(row=r, column=2, padx=self.app.get_scaled_padding((10,2)), pady=hdr_pady, sticky="e")
        self.header_location_count_label = ctk.CTkLabel(self.header_details_frame, text="0", anchor="w", font=self.location_count_font)
        self.header_location_count_label.grid(row=r, column=3, padx=hdr_padx, pady=hdr_pady, sticky="w"); r+=1

        # --- Column 2: Notes Panel ---
        self.notes_display_frame = ctk.CTkFrame(self.top_frame, border_width=self.app.get_scaled_size(1))
        self.notes_display_frame.grid(row=0, column=2, padx=self.app.get_scaled_padding((0, 10)), pady=self.app.get_scaled_padding(5), sticky="nsew")
        self.notes_display_frame.grid_columnconfigure(0, weight=1); self.notes_display_frame.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(self.notes_display_frame, text="SELECTED ITEM DETAILS:", anchor="w", font=self.header_label_font).grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding((5,0)), sticky="ew")
        self.selected_item_status_label = ctk.CTkLabel(self.notes_display_frame, text="", font=self.header_data_font, anchor="w")
        self.selected_item_status_label.grid(row=1, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding((0,5)), sticky="ew")
        self.notes_display_text = ctk.CTkTextbox(self.notes_display_frame, wrap="word", font=self.notes_font, state="disabled", border_width=self.app.get_scaled_size(0), fg_color=self.notes_display_frame.cget('fg_color')) # Read-only Textbox
        self.notes_display_text.grid(row=2, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding((0,5)), sticky="nsew")


        # --- Middle Row: Stock Items Table ---
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(5))
        self.table_frame.grid_rowconfigure(0, weight=1); self.table_frame.grid_columnconfigure(0, weight=1)

        # Treeview Setup
        style = ttk.Style(); style.map('Treeview', background=[('selected', '#A9CCE3')], foreground=[('selected', 'black')])
        style.configure("Treeview.Heading", font=self.app.get_treeview_font(size=self.tree_font_size + 1, weight="bold")) 
        style.configure("Treeview", rowheight=self.app.get_scaled_size(int(self.tree_font_size * 2.2)), font=self.app.get_treeview_font(size=self.tree_font_size))
        self.tree = ttk.Treeview(self.table_frame, style="Treeview", show='headings', selectmode='browse')
        # Columns: LOCATION | QUANTITY | CTNS | BATCH | EXPIRY | UPDATED BY | UPDATED DATE |DATE FIRST STOCKED |  NOTES
        self.columns = ('location', 'quantity', 'ctns', 'batch', 'expiry', 'updated_by', 'updated_date', 'date_first_stocked', 'notes')
        self.tree['columns'] = self.columns
        self.tree.heading('location', text='BIN')
        self.tree.heading('quantity', text='QTY')
        self.tree.heading('ctns', text='CTNS')
        self.tree.heading('batch', text='BATCH')
        self.tree.heading('expiry', text='EXP')
        self.tree.heading('updated_by', text='UPD BY')
        self.tree.heading('updated_date', text='UPD DATE')
        self.tree.heading('date_first_stocked', text='FIRST STOCKED')
        self.tree.heading('notes', text='NOTES')

        self.tree.column('#0', width=self.app.get_scaled_size(0), stretch=tk.NO)
        self.tree.column('location', width=self.app.get_scaled_size(70), anchor=tk.W, stretch=tk.NO)
        self.tree.column('quantity', width=self.app.get_scaled_size(70), anchor=tk.E, stretch=tk.NO)
        self.tree.column('ctns', width=self.app.get_scaled_size(70), anchor=tk.E, stretch=tk.NO)
        self.tree.column('batch', width=self.app.get_scaled_size(120), anchor=tk.W, stretch=tk.NO)
        self.tree.column('expiry', width=self.app.get_scaled_size(80), anchor=tk.CENTER, stretch=tk.NO)
        self.tree.column('updated_by', width=self.app.get_scaled_size(130), anchor=tk.W, stretch=tk.NO)
        self.tree.column('updated_date', width=self.app.get_scaled_size(150), anchor=tk.W, stretch=tk.NO)
        self.tree.column('date_first_stocked', width=self.app.get_scaled_size(150), anchor=tk.W, stretch=tk.NO)
        self.tree.column('notes', width=self.app.get_scaled_size(200), anchor=tk.W, stretch=tk.YES)

        # Scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview); vsb.grid(row=0, column=1, sticky='ns')
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview); hsb.grid(row=1, column=0, sticky='ew')
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')

        # --- Treeview Tags ---
        self.tree.tag_configure('quarantined_row', background='#FADBD8', foreground='black') # Light Red
        self.tree.tag_configure('soonest_expiry', background='#fff7dc', foreground='black') # Yellow
        self.tree.tag_configure('use_first_row', background='#ABEBC6', foreground='black') # Green | Light Purple - #D2B4DE

        # Bindings
        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)
        self.tree.bind('<Delete>', self.request_clear_line)
        self.tree.bind('<Double-1>', self.go_to_selected_location)
        self.tree.bind("<F4>", self.request_update_item)
        self.bind("<F4>", self.request_update_item)

        # Column sorting
        self._last_sort_column = None
        self._last_sort_reverse = False
        for col in self.columns:
            self.tree.heading(col, text=self.tree.heading(col)['text'],
                              command=lambda _col=col: self.sort_column(_col))

        self.populate_table()

        # --- Bottom Row: Buttons ---
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((5, 10)))
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)

        # -- BUTTON COLORS
        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        neutral_fg, neutral_hover, neutral_text, neutral_dtext = self.app.get_button_color_config("destructive")
        warning_fg, warning_hover, warning_text, warning_dtext = self.app.get_button_color_config("warning")
        standard_fg, standard_hover, standard_text, standard_dtext = self.app.get_button_color_config("standard")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")

        # BACK Button (Col 0)
        self.back_button = ctk.CTkButton(self.button_frame, text="BACK", width=self.app.get_scaled_size(120), command=self.go_back,  
                                         fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext, 
                                         font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.back_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="w")

        # UPDATE Button (Col 1)
        self.update_button = ctk.CTkButton(self.button_frame, text="(F4) UPDATE", width=self.app.get_scaled_size(120), command=self.request_update_item,
                                           fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext, 
                                           state="disabled", font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.update_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(5), sticky="")

        # GO TO LOCATION Button (Col 2)
        self.goto_location_button = ctk.CTkButton(self.button_frame, text="GO TO BIN", width=self.app.get_scaled_size(120), command=self.go_to_selected_location,
                                                  fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext, 
                                                  state="disabled", font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.goto_location_button.grid(row=0, column=2, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(5), sticky="")

        # CLEAR LINE Button (Col 3)
        self.clear_line_button = ctk.CTkButton(self.button_frame, text="(DEL) CLEAR LINE", width=self.app.get_scaled_size(120), command=self.request_clear_line,
                                               fg_color=warning_fg, hover_color=warning_hover, text_color=warning_text, text_color_disabled=warning_dtext,
                                               state="disabled", font=self.button_font, height=self.button_height, border_color="black", border_width=self.app.get_scaled_size(1))
        self.clear_line_button.grid(row=0, column=3, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="e")

        # Final Setup
        self.select_first_row()

    # --- Helper Functions ---
    def parse_date_robust(self, date_input):
        if date_input is None or date_input == '': return None
        if isinstance(date_input, (datetime.datetime, datetime.date)): return date_input.date() if isinstance(date_input, datetime.datetime) else date_input
        s = str(date_input).strip()
        if not s: return None
        fmts = ('%Y-%m-%d','%d/%m/%Y','%m/%d/%Y','%Y%m%d','%m/%d/%y','%d-%b-%y','%d-%b-%Y','%Y-%m-%d %H:%M:%S','%d/%m/%Y %H:%M:%S','%m/%d/%Y %H:%M:%S','%d/%m/%Y %I:%M:%S %p')
        for fmt in fmts:
            try: return datetime.datetime.strptime(s, fmt).date()
            except (ValueError, TypeError): pass
        return None

    def format_expiry_display(self, expiry_date_obj):
        return expiry_date_obj.strftime('%m/%Y') if isinstance(expiry_date_obj, datetime.date) else "N/A"

    def format_datetime_display(self, datetime_input):
        if datetime_input is None or str(datetime_input).strip() == '': return "N/A"
        dt_obj = None
        if isinstance(datetime_input, datetime.datetime): dt_obj = datetime_input
        elif isinstance(datetime_input, datetime.date): dt_obj = datetime.datetime.combine(datetime_input, datetime.time.min)
        else:
            s = str(datetime_input).strip()
            if not s: return "N/A"
            fmts = ('%Y-%m-%d %H:%M:%S','%Y-%m-%dT%H:%M:%S','%d/%m/%Y %I:%M:%S %p','%m/%d/%Y %I:%M:%S %p','%d/%m/%Y %H:%M:%S','%m/%d/%Y %H:%M:%S','%d/%m/%Y %H:%M','%m/%d/%Y %H:%M','%Y-%m-%d','%d/%m/%Y','%m/%d/%Y')
            for fmt in fmts:
                try: dt_obj = datetime.datetime.strptime(s, fmt); break
                except (ValueError, TypeError): pass
        if dt_obj: return dt_obj.strftime('%d/%m/%Y %H:%M')
        else: return str(datetime_input)

    def calculate_ctns(self, quantity, units_per_carton):
        """Calculates cartons display, handles None or 0 units_per_carton."""
        if units_per_carton is not None and units_per_carton > 0:
            try:
                return quantity // units_per_carton
            except (TypeError, ValueError):
                return "N/A"
        else:
            return "--"

    # --- Table Population & Interaction ---
    def populate_table(self):
        """ Clears and fills the Treeview, calculates aggregates, finds min/max expiry and associated batches. """
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        self.total_quantity = 0
        locations_found = set()
        earliest_expiry_date = None

        # Variables for header display
        oldest_expiry_obj = None
        newest_expiry_obj = None
        batch_for_oldest_expiry = "N/A"
        batch_for_newest_expiry = "N/A"

        if self.stock_data:
            # --- First Pass: Calculate aggregates and find min/max expiry & batch ---
            for item_row in self.stock_data:
                self.total_quantity += item_row.get('Quantity', 0) or 0
                locations_found.add(item_row.get('LocationName'))

                current_expiry = self.parse_date_robust(item_row.get('ExpiryDate'))
                current_batch = item_row.get('Batch', 'N/A')

                if current_expiry:
                    # For soonest expiry highlighting
                    if earliest_expiry_date is None or current_expiry < earliest_expiry_date:
                        earliest_expiry_date = current_expiry
                    
                    # For header display (oldest expiry and its batch)
                    if oldest_expiry_obj is None or current_expiry < oldest_expiry_obj:
                        oldest_expiry_obj = current_expiry
                        batch_for_oldest_expiry = current_batch
                        
                    # For header display (newest expiry and its batch)
                    if newest_expiry_obj is None or current_expiry > newest_expiry_obj:
                        newest_expiry_obj = current_expiry
                        batch_for_newest_expiry = current_batch

            self.location_count = len(locations_found)

            # --- Update Header Aggregates & Min/Max ---
            self.header_total_qty_label.configure(text=str(self.total_quantity))
            self.header_location_count_label.configure(text=str(self.location_count))
            self.header_oldest_expiry_label.configure(text=self.format_expiry_display(oldest_expiry_obj))
            self.header_newest_expiry_label.configure(text=self.format_expiry_display(newest_expiry_obj))
            self.header_oldest_expiry_batch_label.configure(text=batch_for_oldest_expiry if batch_for_oldest_expiry else "N/A")
            self.header_newest_expiry_batch_label.configure(text=batch_for_newest_expiry if batch_for_newest_expiry else "N/A")

            # --- Second Pass: Insert rows and apply tags ---
            for item_row in self.stock_data:
                item_id = item_row.get('StockItemID')
                if not item_id: continue

                # Format dates
                expiry_date_obj = self.parse_date_robust(item_row.get('ExpiryDate'))
                exp_display = self.format_expiry_display(expiry_date_obj)
                updated_date_display = self.format_datetime_display(item_row.get('LastUpdatedDate'))

                # Calculate CTNS
                qty = item_row.get('Quantity', 0) or 0
                units_per = item_row.get('UnitsPerCarton') # Can be None
                ctns_display = self.calculate_ctns(qty, units_per)

                # Get other values
                location = item_row.get('LocationName', '')
                batch = item_row.get('Batch', '')
                full_notes = item_row.get('Notes', '')
                notes_display = ""
                if full_notes is not None: 
                    if isinstance(full_notes, str): 
                       notes_display = full_notes.split('\n', 1)[0]
                       if '\n' in full_notes: notes_display += "..."
                    else:
                        notes_display = str(full_notes) 
                updated_by = item_row.get('LastUpdatedBy', '')
                first_stocked_display = self.format_datetime_display(item_row.get('DateFirstStocked'))

                tags = []
                if item_row.get('IsQuarantined') == 1:
                    tags.append('quarantined_row')
                elif item_row.get('IsFirst') == 1:
                    tags.append('use_first_row')

                if earliest_expiry_date and expiry_date_obj == earliest_expiry_date:
                    if 'use_first_row' not in tags and 'quarantined_row' not in tags:
                        tags.append('soonest_expiry')

                self.tree.insert('', tk.END, iid=item_id, values=(
                    location, qty, ctns_display, batch, exp_display, updated_by, updated_date_display, first_stocked_display, notes_display
                ), tags=tuple(tags))
        else:
             self.header_total_qty_label.configure(text="0")
             self.header_location_count_label.configure(text="0")
             self.header_oldest_expiry_label.configure(text="N/A")
             self.header_newest_expiry_label.configure(text="N/A")
             self.header_oldest_expiry_batch_label.configure(text="N/A")
             self.header_newest_expiry_batch_label.configure(text="N/A")

    def on_row_select(self, event=None):
        """ Updates buttons and notes panel based on row selection """
        selected_iid = self.get_selected_stock_item_id()
        if selected_iid:
            self.clear_line_button.configure(state="normal")
            self.goto_location_button.configure(state="normal")
            self.update_button.configure(state="normal")
            
            # Update Notes Panel
            selected_data = next((item for item in self.stock_data if item['StockItemID'] == selected_iid), None)
            notes_text = selected_data.get('Notes', '') if selected_data else ''
            self.notes_display_text.configure(state="normal")
            self.notes_display_text.delete("1.0", tk.END)
            self.notes_display_text.insert("1.0", notes_text if notes_text else "")
            self.notes_display_text.configure(state="disabled")
            
            status_text_display = ""
            status_text_color = self.selected_item_status_label.cget("text_color")

            if selected_data:
                if selected_data.get('IsQuarantined') == 1:
                    status_text_display = "STATUS: QUARANTINED"
                    status_text_color = "orange"
                elif selected_data.get('IsFirst') == 1:
                    status_text_display = "STATUS: USE FIRST"
                    status_text_color = "dodgerblue"
            
            self.selected_item_status_label.configure(text=status_text_display, text_color=status_text_color)

        else:
            self.clear_line_button.configure(state="disabled")
            self.goto_location_button.configure(state="disabled")
            self.update_button.configure(state="disabled")
            
            self.notes_display_text.configure(state="normal")
            self.notes_display_text.delete("1.0", tk.END)
            self.notes_display_text.configure(state="disabled")

            self.selected_item_status_label.configure(text="", text_color=self.selected_item_status_label.cget("text_color"))

    def select_first_row(self):
        children = self.tree.get_children()
        if children: self.tree.selection_set(children[0]); self.tree.focus(children[0]); self.tree.focus_set(); self.on_row_select()

    def get_selected_stock_item_id(self):
        selected_items = self.tree.selection()
        return int(selected_items[0]) if selected_items else None

    def get_selected_location(self):
        selected_iid = self.get_selected_stock_item_id()
        if selected_iid:
            selected_data = next((item for item in self.stock_data if item['StockItemID'] == selected_iid), None)
            if selected_data: return selected_data.get('LocationName')
        return None
    
    # Column Sorting
    def sort_column(self, col_id):
        """Sort treeview contents when a column header is clicked."""
        
        # Determine sort direction
        reverse_sort = False
        if col_id == self._last_sort_column:
            reverse_sort = not self._last_sort_reverse
        
        # --- Define how to get the sort key for each column ---
        data_map = {item['StockItemID']: item for item in self.stock_data}
        
        def get_sort_key(item_id):
            item_data = data_map.get(int(item_id))
            if not item_data: return None

            val = None
            if col_id == 'location':           val = item_data.get('LocationName')
            elif col_id == 'quantity':         val = item_data.get('Quantity')
            elif col_id == 'ctns':
                qty_k = item_data.get('Quantity', 0)
                upc_k = item_data.get('UnitsPerCarton')
                val = qty_k // upc_k if upc_k and upc_k > 0 else 0
            elif col_id == 'batch':            val = item_data.get('Batch')
            elif col_id == 'expiry':           val = self.parse_date_robust(item_data.get('ExpiryDate'))
            elif col_id == 'updated_by':       val = item_data.get('LastUpdatedBy')
            elif col_id == 'updated_date':     val = self.parse_date_robust(item_data.get('LastUpdatedDate'))
            elif col_id == 'date_first_stocked': val = self.parse_date_robust(item_data.get('DateFirstStocked'))
            elif col_id == 'notes':            val = item_data.get('Notes')
            else: return None

            # Handle types for comparison
            if isinstance(val, str): return val.lower()
            if isinstance(val, (int, float)): return val
            if isinstance(val, datetime.date): return val
            if val is None:
                if isinstance(get_sort_key(self.tree.get_children()[0] if self.tree.get_children() else None), (datetime.date, int, float)):
                    return datetime.date.min if isinstance(get_sort_key(self.tree.get_children()[0]), datetime.date) else -float('inf')
                else:
                    return ""
            return val

        # --- Get current items and their sort keys ---
        items_to_sort = []
        for item_id_str in self.tree.get_children():
            sort_key = get_sort_key(item_id_str)
            items_to_sort.append((sort_key, item_id_str))

        # --- Sort the items ---
        items_to_sort.sort(key=lambda x: x[0], reverse=reverse_sort)

        # --- Reorder items in the treeview ---
        for index, (sort_key, item_id_str) in enumerate(items_to_sort):
            self.tree.move(item_id_str, '', index)

        # --- Update sorting state for next click ---
        self._last_sort_column = col_id
        self._last_sort_reverse = reverse_sort

    # --- Button Action Handlers ---
    def go_back(self): self.app.show_main_page()

    def request_clear_line(self, event=None):
        selected_iid = self.get_selected_stock_item_id()
        selected_location = self.get_selected_location()
        if selected_iid and selected_location:
            if messagebox.askyesno("Confirm Clear Line", f"Clear SKU {self.searched_sku} from {selected_location}?", parent=self):
                self.app.clear_stock_item_and_refresh_sku_view(selected_iid, self.searched_sku)
        else: messagebox.showwarning("No Selection", "Select line to clear.", parent=self)

    def go_to_selected_location(self, event=None):
        selected_location = self.get_selected_location()
        if selected_location: self.app.navigate_to_location_results(selected_location)
        elif event and event.type == tk.EventType.ButtonPress: messagebox.showwarning("No Selection", "Select line to go to location.", parent=self)
    
    def request_update_item(self, event=None):
        """Gets selected item details and asks the App to open the update window."""
        selected_iid = self.get_selected_stock_item_id()
        selected_location = self.get_selected_location()

        if selected_iid and selected_location:
            print(f"SKUResults: Requesting update for StockItemID: {selected_iid} in location {selected_location}")
            self.app.open_update_new_window(location_code=selected_location, mode='update', stock_item_id=selected_iid, source_view='sku')
        elif event and event.type == tk.EventType.ButtonPress and hasattr(event, 'widget') and event.widget == self.update_button:
            messagebox.showwarning("No Selection", "Please select a line to update.", parent=self)