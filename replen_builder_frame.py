import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

class ReplenishmentBuilderFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.current_replen_list = []

        # --- Define standard fonts and heights ---
        self.entry_font = self.app.get_font(size=14)
        self.button_font = self.app.get_font(size=14, weight="bold")
        self.label_font = self.app.get_font(size=15, weight="bold")

        self.entry_height = self.app.get_scaled_size(35)
        self.button_height = self.app.get_scaled_size(40)

        self.tree_font_family = "Segoe UI"
        self.tree_font_size = 11

        # -- BUTTON COLORS
        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        neutral_fg, neutral_hover, neutral_text, neutral_dtext = self.app.get_button_color_config("destructive")
        warning_fg, warning_hover, warning_text, warning_dtext = self.app.get_button_color_config("warning")
        standard_fg, standard_hover, standard_text, standard_dtext = self.app.get_button_color_config("standard")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")     

        # --- Configure Main Grid (e.g., 2 rows: Search/Results, CurrentList) ---
        self.grid_rowconfigure(0, weight=1) # LSI Search and Results Area
        self.grid_rowconfigure(1, weight=1) # Current Replen List Area
        self.grid_columnconfigure(0, weight=1)

        # --- Top Part: LSI Search and Results ---
        lsi_search_area = ctk.CTkFrame(self)
        lsi_search_area.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="nsew")
        lsi_search_area.grid_rowconfigure(1, weight=1)
        lsi_search_area.grid_columnconfigure(0, weight=1) 

        # Search Input
        search_input_frame = ctk.CTkFrame(lsi_search_area, fg_color="transparent")
        search_input_frame.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="ew")
        search_input_frame.grid_columnconfigure(0, weight=1)
        self.lsi_search_entry = ctk.CTkEntry(search_input_frame, placeholder_text="Search LSI by SKU, Description, Brand...", font=self.entry_font, height=self.entry_height)
        self.lsi_search_entry.grid(row=0, column=0, padx=self.app.get_scaled_padding((0,10)), sticky="ew")
        self.lsi_search_entry.bind("<Return>", self.execute_lsi_search)
        lsi_search_button = ctk.CTkButton(search_input_frame, text="Search LSI", command=self.execute_lsi_search, width=self.app.get_scaled_size(120),     
                                          fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext, 
                                          border_color="black", border_width=self.app.get_scaled_size(1), font=self.entry_font, height=self.entry_height)
        lsi_search_button.grid(row=0, column=1, sticky="e")

        # LSI Results Treeview
        lsi_tree_frame = ctk.CTkFrame(lsi_search_area)
        lsi_tree_frame.grid(row=1, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="nsew")
        lsi_tree_frame.grid_rowconfigure(0, weight=1); lsi_tree_frame.grid_columnconfigure(0, weight=1)
        
        style_lsi = ttk.Style(); 
        style_lsi.map('LSI.Treeview', background=[('selected', '#A9CCE3')], foreground=[('selected', 'black')])
        style_lsi.configure("LSI.Treeview.Heading", font=self.app.get_treeview_font(size=self.tree_font_size + 1, weight="bold")) 
        style_lsi.configure("LSI.Treeview", rowheight=self.app.get_scaled_size(int(self.tree_font_size * 2.2)), font=self.app.get_treeview_font(size=self.tree_font_size))
        self.lsi_results_tree = ttk.Treeview(lsi_tree_frame, style="LSI.Treeview", show='headings', selectmode='browse')
        self.lsi_columns = ('sku', 'description', 'brand', 'on_hand')
        self.lsi_results_tree['columns'] = self.lsi_columns
        self.lsi_results_tree.heading('sku', text='SKU'); self.lsi_results_tree.heading('description', text='Description'); self.lsi_results_tree.heading('brand', text='Brand'); self.lsi_results_tree.heading('on_hand', text='In Bulk')
        self.lsi_results_tree.column('#0', width=self.app.get_scaled_size(0), stretch=tk.NO); self.lsi_results_tree.column('sku', width=self.app.get_scaled_size(100)); self.lsi_results_tree.column('description', width=self.app.get_scaled_size(300), stretch=tk.YES); self.lsi_results_tree.column('brand', width=self.app.get_scaled_size(120)); self.lsi_results_tree.column('on_hand', width=self.app.get_scaled_size(70), anchor='e')

        vsb_lsi = ttk.Scrollbar(lsi_tree_frame, orient="vertical", command=self.lsi_results_tree.yview); vsb_lsi.grid(row=0, column=1, sticky='ns')
        hsb_lsi = ttk.Scrollbar(lsi_tree_frame, orient="horizontal", command=self.lsi_results_tree.xview); hsb_lsi.grid(row=1, column=0, sticky='ew')
        self.lsi_results_tree.configure(yscrollcommand=vsb_lsi.set, xscrollcommand=hsb_lsi.set)
        self.lsi_results_tree.grid(row=0, column=0, sticky="nsew")
        self.lsi_results_tree.bind("<<TreeviewSelect>>", self.on_lsi_result_select)

        # Add to List Button (for LSI results)
        self.add_to_list_button = ctk.CTkButton(lsi_search_area, text="Add to List (+)", command=self.add_selected_lsi_item, state="disabled", 
                                                fg_color=warning_fg, hover_color=warning_hover, text_color=warning_text, text_color_disabled=warning_dtext,
                                                border_color="black", width=self.app.get_scaled_size(1), font=self.button_font, height=self.button_height)
        self.add_to_list_button.grid(row=2, column=0, pady=self.app.get_scaled_padding(10))


        # --- Bottom Part: Current Replenishment List ---
        current_list_area = ctk.CTkFrame(self)
        current_list_area.grid(row=1, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="nsew")
        current_list_area.grid_rowconfigure(1, weight=1)
        current_list_area.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(current_list_area, text="Current Replenishment List (Pending Items)", font=self.label_font).grid(row=0, column=0, columnspan=2, pady=self.app.get_scaled_padding(5))
        
        replen_tree_frame = ctk.CTkFrame(current_list_area)
        replen_tree_frame.grid(row=1, column=0, columnspan=2, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5), sticky="nsew")
        replen_tree_frame.grid_rowconfigure(0, weight=1); replen_tree_frame.grid_columnconfigure(0, weight=1)

        style_replen = ttk.Style() 
        style_replen.map('Replen.Treeview', background=[('selected', '#9dedae')], foreground=[('selected', 'black')])
        style_replen.configure("Replen.Treeview.Heading", font=(self.tree_font_family, self.tree_font_size +1))
        style_replen.configure("Replen.Treeview", rowheight=int(self.tree_font_size * 2.2), font=(self.tree_font_family, self.tree_font_size))

        self.replen_list_tree = ttk.Treeview(replen_tree_frame, style="Replen.Treeview", show='headings', selectmode='browse')
        self.replen_columns = ('sku', 'description', 'brand')
        self.replen_list_tree['columns'] = self.replen_columns
        self.replen_list_tree.heading('sku', text='SKU'); self.replen_list_tree.heading('description', text='Description'); self.replen_list_tree.heading('brand', text='Brand')
        self.replen_list_tree.column('#0', width=self.app.get_scaled_size(0), stretch=tk.NO); self.replen_list_tree.column('sku', width=self.app.get_scaled_size(100)); self.replen_list_tree.column('description', width=self.app.get_scaled_size(300), stretch=tk.YES); self.replen_list_tree.column('brand', width=self.app.get_scaled_size(120))

        vsb_replen = ttk.Scrollbar(replen_tree_frame, orient="vertical", command=self.replen_list_tree.yview); vsb_replen.grid(row=0, column=1, sticky='ns')
        hsb_replen = ttk.Scrollbar(replen_tree_frame, orient="horizontal", command=self.replen_list_tree.xview); hsb_replen.grid(row=1, column=0, sticky='ew')
        self.replen_list_tree.configure(yscrollcommand=vsb_replen.set, xscrollcommand=hsb_replen.set)
        self.replen_list_tree.grid(row=0, column=0, sticky="nsew")
        self.replen_list_tree.bind("<<TreeviewSelect>>", self.on_replen_item_select)

        # Buttons for managing current replen list
        replen_list_actions_frame = ctk.CTkFrame(current_list_area, fg_color="transparent")
        replen_list_actions_frame.grid(row=2, column=0, columnspan=2, pady=self.app.get_scaled_padding(10))
        replen_list_actions_frame.grid_columnconfigure((0,1), weight=1)

        self.remove_from_list_button = ctk.CTkButton(replen_list_actions_frame, text="Remove Selected (-)", command=self.remove_selected_replen_item, state="disabled", 
                                                     font=self.button_font, height=self.button_height, 
                                                     fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext, 
                                                     border_color="black", border_width=self.app.get_scaled_size(1))
        self.remove_from_list_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), sticky="e")
        
        self.finalise_button = ctk.CTkButton(replen_list_actions_frame, text="Finalise & View Picking List", command=self.finalise_list, state="disabled", 
                                             font=self.button_font, height=self.button_height, 
                                             fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext,
                                             border_color="black", border_width=self.app.get_scaled_size(1))
        self.finalise_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(10), sticky="w")

        # Bind ESC for this frame
        self.after(100, lambda: self.lsi_search_entry.focus_set())


    def execute_lsi_search(self, event=None):
        search_term = self.lsi_search_entry.get().strip()
        if not search_term: messagebox.showwarning("Input Needed", "Enter search term for LSI.", parent=self); return
        
        print(f"ReplenBuilder: Searching LSI for '{search_term}'")
        lsi_results = self.app.perform_advanced_lsi_search(search_term)
        
        display_results = []
        if lsi_results:
            for lsi_item in lsi_results:
                sku = lsi_item.get('SKU')
                on_hand_qty = self.app.get_total_quantity_for_sku(sku)
                display_results.append({**lsi_item, 'OnHandQty': on_hand_qty})
        
        self.populate_lsi_results_tree(display_results)

    def populate_lsi_results_tree(self, display_results):
        for i in self.lsi_results_tree.get_children(): self.lsi_results_tree.delete(i)
        if display_results:
            for item in display_results:
                self.lsi_results_tree.insert('', tk.END, iid=item['SKU'],
                                           values=(item['SKU'], item['Description'], item['Brand'], item.get('OnHandQty', 0)))
        self.on_lsi_result_select()

    def on_lsi_result_select(self, event=None):
        self.add_to_list_button.configure(state="normal" if self.lsi_results_tree.selection() else "disabled")

    def add_selected_lsi_item(self):
        selected = self.lsi_results_tree.selection()
        if not selected: return
        
        sku_to_add = selected[0]
        if any(item['SKU'] == sku_to_add for item in self.current_replen_list):
            messagebox.showinfo("Already Added", f"SKU {sku_to_add} is already in the current replenishment list.", parent=self)
            return

        item_values = self.lsi_results_tree.item(sku_to_add, 'values')
        item_details = {'SKU': item_values[0], 'Description': item_values[1], 'Brand': item_values[2]}
        
        self.current_replen_list.append(item_details)
        self.refresh_replen_list_tree()
        self.finalise_button.configure(state="normal" if self.current_replen_list else "disabled")


    def refresh_replen_list_tree(self):
        for i in self.replen_list_tree.get_children(): self.replen_list_tree.delete(i)
        for item in self.current_replen_list:
            self.replen_list_tree.insert('', tk.END, iid=item['SKU'], 
                                       values=(item['SKU'], item['Description'], item['Brand']))
        self.on_replen_item_select()

    def on_replen_item_select(self, event=None):
        self.remove_from_list_button.configure(state="normal" if self.replen_list_tree.selection() else "disabled")

    def remove_selected_replen_item(self):
        selected = self.replen_list_tree.selection()
        if not selected: return
        sku_to_remove = selected[0]
        self.current_replen_list = [item for item in self.current_replen_list if item['SKU'] != sku_to_remove]
        self.refresh_replen_list_tree()
        self.finalise_button.configure(state="normal" if self.current_replen_list else "disabled")


    def finalise_list(self):
        if not self.current_replen_list:
            messagebox.showwarning("Empty List", "Replenishment list is empty.", parent=self)
            return

        print(f"ReplenBuilder: Finalising list with {len(self.current_replen_list)} SKUs.")

        success_count = 0
        for item in self.current_replen_list:
            if self.app.add_sku_to_replen_list(item['SKU']):
                success_count +=1
        
        messagebox.showinfo("List Finalised", 
                            f"{success_count} unique SKUs added/confirmed in DB as 'Pending'.", 
                            parent=self)
        
        self.current_replen_list = []
        self.refresh_replen_list_tree()
        self.finalise_button.configure(state="disabled")

        if hasattr(self.app, 'navigate_to_picking_list'):
            self.app.navigate_to_picking_list()
        else:
            messagebox.showerror("Error", "Picking List navigation not implemented in app.", parent=self)
