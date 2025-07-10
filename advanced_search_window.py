import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from utils import center_and_size_toplevel

class AdvancedSearchWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.last_search_results = []

        self.title("Advanced Item Search")
        # self.geometry("800x600")
        # self.resizable(False, False) # Allowing resizing might be good for results
        self.transient(master)
        self.grab_set()

        # --- Define fonts ---
        self.label_font = self.app.get_font(size=14, weight="bold")
        self.entry_font = self.app.get_font(size=14)
        self.button_font = self.app.get_font(size=14, weight="bold")
        standard_fg, standard_hover, standard_text, standard_dtext = self.app.get_button_color_config("standard")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")

        self.entry_height = self.app.get_scaled_size(35)
        self.button_height = self.app.get_scaled_size(35)

        self.tree_font_family = "Segoi UI"
        self.tree_font_size = 11

        # --- Configure main grid ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # --- Search Input Frame (Row 0) ---
        search_input_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_input_frame.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="ew")
        search_input_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_input_frame,
            font=self.entry_font,
            height=self.entry_height,
            placeholder_text="Enter search term (SKU, Description, Brand...)"
        )
        self.search_entry.grid(row=0, column=0, padx=self.app.get_scaled_padding((0,10)), pady=self.app.get_scaled_padding(5), sticky="ew")
        self.search_entry.bind("<Return>", self.execute_search)


        self.search_button = ctk.CTkButton(
            search_input_frame,
            text="Search",
            command=self.execute_search,
            font=self.button_font,
            height=self.button_height,
            fg_color=standard_fg,
            hover_color=standard_hover, 
            text_color=standard_text, 
            text_color_disabled=standard_dtext,
            width=self.app.get_scaled_size(120)
        )
        self.search_button.grid(row=0, column=1, pady=self.app.get_scaled_padding(5), sticky="e")

        # --- Results Treeview Frame (Row 1) ---
        tree_frame = ctk.CTkFrame(self)
        tree_frame.grid(row=1, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(5), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.map('Treeview', background=[('selected', '#A9CCE3')], foreground=[('selected', 'black')])
        style.configure("Treeview.Heading", font=self.app.get_treeview_font(size=self.tree_font_size + 1, weight="bold")) 
        style.configure("Treeview", rowheight=self.app.get_scaled_size(int(self.tree_font_size * 2.2)), font=self.app.get_treeview_font(size=self.tree_font_size))
        self.results_tree = ttk.Treeview(tree_frame, style="Treeview", show='headings', selectmode='browse')
        
        # Columns to match data from perform_advanced_lsi_search
        self.columns = ('sku', 'description', 'brand', 'barcode', 'shelflocation') 
        self.results_tree['columns'] = self.columns
        
        self.results_tree.heading('sku', text='SKU')
        self.results_tree.heading('description', text='Description')
        self.results_tree.heading('brand', text='Brand')
        self.results_tree.heading('barcode', text='Barcode')
        self.results_tree.heading('shelflocation', text='ShelfLoc')

        self.results_tree.column('#0', width=self.app.get_scaled_size(0), stretch=tk.NO)
        self.results_tree.column('sku', width=self.app.get_scaled_size(100), anchor=tk.W, stretch=tk.NO)
        self.results_tree.column('description', width=self.app.get_scaled_size(300), anchor=tk.W, stretch=tk.YES)
        self.results_tree.column('brand', width=self.app.get_scaled_size(100), anchor=tk.W, stretch=tk.NO)
        self.results_tree.column('barcode', width=self.app.get_scaled_size(120), anchor=tk.W, stretch=tk.NO)
        self.results_tree.column('shelflocation', width=self.app.get_scaled_size(100), anchor=tk.CENTER, stretch=tk.NO)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.results_tree.xview)
        hsb.grid(row=1, column=0, sticky='ew')
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.results_tree.grid(row=0, column=0, sticky='nsew')

        self.results_tree.bind('<<TreeviewSelect>>', self.on_result_select)
        self.results_tree.bind('<Double-1>', self.view_selected_sku_details)

        # --- Add sorting command to each heading ---
        self._last_sort_column_adv = None
        self._last_sort_reverse_adv = False
        for col_id in self.columns:
            # Get existing text to preserve it
            current_heading_text = self.results_tree.heading(col_id)['text']
            self.results_tree.heading(col_id, text=current_heading_text,
                                      command=lambda _col=col_id: self.sort_column_adv(_col))

        # --- Results Count (Row 2)
        self.results_count_label = ctk.CTkLabel(self, text="Results: 0", font=self.entry_font)
        self.results_count_label.grid(row=2, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((5,0)), sticky="w")

        # --- Action Buttons Frame (Row 3) ---
        action_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_button_frame.grid(row=3, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="ew")
        action_button_frame.grid_columnconfigure(0, weight=1) 
        action_button_frame.grid_columnconfigure(1, weight=0)
        
        self.view_details_button = ctk.CTkButton(
            action_button_frame,
            text="View SKU Details",
            command=self.view_selected_sku_details,
            font=self.button_font,
            height=self.button_height,
            fg_color=standard_fg, 
            hover_color=standard_hover, 
            text_color=standard_text, 
            text_color_disabled=standard_dtext,
            border_color="black", border_width=self.app.get_scaled_size(1),
            state="disabled"
        )
        self.view_details_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="e")

        self.close_button = ctk.CTkButton(
            action_button_frame,
            text="Close",
            command=self.destroy,
            font=self.button_font,
            height=self.button_height,
            fg_color=destructive_fg, 
            hover_color=destructive_hover, 
            text_color=destructive_text,
            border_color="black", border_width=self.app.get_scaled_size(1)
        )
        self.close_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="e")
        
        # --- Final setup calls in __init__ ---
        self.bind("<Escape>", lambda event: self.destroy())
        
        self.on_result_select()
        
        self.search_entry.focus_set()
        self.lift()

        center_and_size_toplevel(self, base_width=800, base_height=600)

    def execute_search(self, event=None):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Input Needed", "Please enter a search term.", parent=self)
            return

        print(f"AdvancedSearchWindow: Executing search for '{search_term}'")
        
        # --- Clear previous results from the tree ---
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)
        
        # --- Reset results count label ---
        if hasattr(self, 'results_count_label'): # Check if label exists
            self.results_count_label.configure(text="Results: 0")
        
        # --- Ensure 'View SKU Details' button is disabled while searching / before results populate ---
        if hasattr(self, 'view_details_button'):
            self.on_result_select() 
            
        # --- Clear previously stored results and perform new search ---
        self.last_search_results = [] 

        if hasattr(self.app, 'perform_advanced_lsi_search'):
            self.last_search_results = self.app.perform_advanced_lsi_search(search_term) 
        else:
            messagebox.showerror("App Error", "Advanced search function not found in main application.", parent=self)
            if hasattr(self, 'view_details_button'): self.on_result_select() 
            return
        
        # --- Populate the treeview with new (potentially sorted) results ---
        self.populate_results_tree(self.last_search_results) 

        if not self.last_search_results:
             messagebox.showinfo("Search Complete", f"No items found matching '{search_term}' in LSI.", parent=self)


    def populate_results_tree(self, results):
        """ Populates the treeview with LSI search results. """        
        count = 0
        if results:
            for item_data in results:
                sku = item_data.get('SKU', '')
                desc = item_data.get('Description', '')
                brand = item_data.get('Brand', '')
                barcode = item_data.get('Barcode', '')
                shelfloc = item_data.get('ShelfLocation', '')
                self.results_tree.insert('', tk.END, 
                                         values=(sku, desc, brand, barcode, shelfloc), 
                                         iid=sku if sku else None) 
                
                count += 1
    
        # --- Update Results Count Label ---
        self.results_count_label.configure(text=f"Results: {count}")   
    
        self.on_result_select()
        
        children = self.results_tree.get_children()
        if children:
            self.results_tree.selection_set(children[0])
            self.results_tree.focus(children[0])

    def on_result_select(self, event=None):
        """ Enables/disables 'View SKU Details' button based on selection. """
        if not hasattr(self, 'view_details_button'):
            print("ERROR in on_result_select: self.view_details_button does not exist!")
            return 

        if self.results_tree.selection():
            self.view_details_button.configure(state="normal")
        else:
            self.view_details_button.configure(state="disabled")


    def view_selected_sku_details(self, event=None):
        selected_items = self.results_tree.selection()
        if not selected_items:
            if event and event.type == tk.EventType.ButtonPress:
                 messagebox.showwarning("No Selection", "Please select an item from the results.", parent=self)
            return
        
        selected_iid = selected_items[0] 
        selected_sku = selected_iid 

        if selected_sku:
            print(f"AdvancedSearchWindow: Navigating to SKU results for: {selected_sku}")
            self.app.navigate_to_sku_results(selected_sku)
            self.destroy() 
        else:
            messagebox.showerror("Error", "Could not determine SKU from selection to view details.", parent=self)
    
    def sort_column_adv(self, col_id):
        """Sorts the advanced search results treeview by a column."""
        if not self.last_search_results:
            return

        reverse_sort = False
        if col_id == self._last_sort_column_adv:
            reverse_sort = not self._last_sort_reverse_adv
        
        def get_sort_key_from_data(item_data):
            val = None
            if col_id == 'sku':           val = item_data.get('SKU')
            elif col_id == 'description': val = item_data.get('Description')
            elif col_id == 'brand':       val = item_data.get('Brand')
            elif col_id == 'barcode':     val = item_data.get('Barcode')
            elif col_id == 'shelflocation': val = item_data.get('ShelfLocation')
            else: return None

            if isinstance(val, str): return val.lower()
            if val is None: return ""
            return val

        try:
            self.last_search_results.sort(key=get_sort_key_from_data, reverse=reverse_sort)
        except TypeError as e:
            print(f"Sorting TypeError (mixed types?): {e} on column {col_id}")
            try:
                self.last_search_results.sort(key=lambda x: str(x.get(col_id.upper(), '')).lower(), reverse=reverse_sort)
                print("Fallback string sort applied.")
            except Exception as e2:
                print(f"Fallback string sort also failed: {e2}")
                return # Can't sort

        # --- Clear and Repopulate the tree with sorted data ---
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)
        
        self.populate_results_tree(self.last_search_results)

        self._last_sort_column_adv = col_id
        self._last_sort_reverse_adv = reverse_sort
