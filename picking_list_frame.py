import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

class PickingListFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance, picking_list_items):
        super().__init__(master)
        self.app = app_instance
        self.picking_list_items_data_original = picking_list_items
        self.picking_list_items_display = list(picking_list_items)
        self.item_ids_processed_in_session = set()

        # --- Define standard fonts and heights ---
        self.button_font = self.app.get_font(size=14, weight="bold")
        self.button_height = self.app.get_scaled_size(40)
        self.label_font = self.app.get_font(size=13)
        self.radio_font = self.app.get_font(size=13)

        self.tree_font_family = "Segoe UI"
        self.tree_font_size = 11

        # --- Variable for sorting ---
        self.sort_by_var = tk.StringVar(value="sku")

        # --- Configure Main Grid ---
        self.grid_rowconfigure(0, weight=0) # Sort options row
        self.grid_rowconfigure(1, weight=1) # Treeview row expands
        self.grid_rowconfigure(2, weight=0) # Action buttons row
        self.grid_columnconfigure(0, weight=1) # Content column expands

        
        # --- Sort Options Frame (Row 0) ---
        sort_options_frame = ctk.CTkFrame(self, fg_color="transparent")
        sort_options_frame.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((10,0)), sticky="ew")
        
        ctk.CTkLabel(sort_options_frame, text="Sort list by:", font=self.label_font).pack(side=tk.LEFT, padx=self.app.get_scaled_padding((0,5)))
        
        self.sort_sku_radio = ctk.CTkRadioButton(
            sort_options_frame, text="SKU (Default)", 
            variable=self.sort_by_var, value="sku",
            command=self.on_sort_option_change, font=self.radio_font
        )
        self.sort_sku_radio.pack(side=tk.LEFT, padx=self.app.get_scaled_padding(5))

        self.sort_location_radio = ctk.CTkRadioButton(
            sort_options_frame, text="Location", 
            variable=self.sort_by_var, value="location",
            command=self.on_sort_option_change, font=self.radio_font
        )
        self.sort_location_radio.pack(side=tk.LEFT, padx=self.app.get_scaled_padding(5))

        # --- Treeview Frame (Row 1) ---
        tree_frame = ctk.CTkFrame(self)
        tree_frame.grid(row=1, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1) # Treeview takes space

        style = ttk.Style()
        style.map('Picking.Treeview', background=[('selected', '#A9CCE3')], foreground=[('selected', 'black')])
        style.configure('Replenished.Treeitem', background='lightgrey', foreground='grey')

        # Treeview font
        style.configure("Treeview.Heading", font=self.app.get_treeview_font(size=self.tree_font_size + 1, weight="bold")) 
        style.configure("Treeview", rowheight=self.app.get_scaled_size(int(self.tree_font_size * 2.2)), font=self.app.get_treeview_font(size=self.tree_font_size))

        self.picking_tree = ttk.Treeview(tree_frame, style="Picking.Treeview", show='headings', selectmode='browse', height=15)
        
        # Columns: Location (to pick from), SKU, Description, Brand, Qty@Loc, Replenished Qty (Input?), Action
        self.columns = ('pick_location', 'sku', 'description', 'brand', 'qty_at_loc', 'action_placeholder') 
        self.picking_tree['columns'] = self.columns
        
        self.picking_tree.heading('pick_location', text='Pick From')
        self.picking_tree.heading('sku', text='SKU')
        self.picking_tree.heading('description', text='Description')
        self.picking_tree.heading('brand', text='Brand')
        self.picking_tree.heading('qty_at_loc', text='Qty@Loc')
        self.picking_tree.heading('action_placeholder', text='Picked Qty')

        self.picking_tree.column('#0', width=self.app.get_scaled_size(0), stretch=tk.NO)
        self.picking_tree.column('pick_location', width=self.app.get_scaled_size(100), anchor=tk.W)
        self.picking_tree.column('sku', width=self.app.get_scaled_size(120), anchor=tk.W)
        self.picking_tree.column('description', width=self.app.get_scaled_size(300), anchor=tk.W, stretch=tk.YES)
        self.picking_tree.column('brand', width=self.app.get_scaled_size(120), anchor=tk.W)
        self.picking_tree.column('qty_at_loc', width=self.app.get_scaled_size(80), anchor=tk.E)
        self.picking_tree.column('action_placeholder', width=self.app.get_scaled_size(100), anchor=tk.E)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.picking_tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.picking_tree.configure(yscrollcommand=vsb.set)
        self.picking_tree.grid(row=0, column=0, sticky='nsew')

        self.populate_picking_list()

        # Add double-click binding to process a line
        self.picking_tree.bind("<Double-1>", self.process_selected_pick_item)
        self.picking_tree.bind("<<TreeviewSelect>>", self.on_pick_list_select)

        # --- Action Buttons Below Tree ---
        bottom_actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_actions_frame.grid(row=2, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="ew")
        bottom_actions_frame.grid_columnconfigure(0, weight=1)
        bottom_actions_frame.grid_columnconfigure(1, weight=1)
        bottom_actions_frame.grid_columnconfigure(2, weight=1)

        # --- Replenish Selected Button ---
        standard_fg, standard_hover, standard_text, standard_dtext = self.app.get_button_color_config("standard")
        self.replenish_selected_button = ctk.CTkButton(
            bottom_actions_frame,
            text="Replenish Selected Line",
            command=self.process_selected_pick_item,
            fg_color=standard_fg, 
            hover_color=standard_hover, 
            text_color=standard_text,
            text_color_disabled=standard_dtext, 
            border_color="black", 
            border_width=self.app.get_scaled_size(1),
            height=self.button_height,
            font=self.button_font,
            state="disabled"
        )
        self.replenish_selected_button.grid(row=0, column=0, sticky="w", padx=self.app.get_scaled_padding(5))

        # --- Print Button ---
        neutral_fg, neutral_hover, neutral_text, neutral_dtext = self.app.get_button_color_config("neutral")
        self.print_list_button = ctk.CTkButton(
            bottom_actions_frame, text="Print List",
            command=self.print_picking_list,
            fg_color=neutral_fg, 
            hover_color=neutral_hover, 
            text_color=neutral_text, 
            text_color_disabled=neutral_dtext, 
            border_color="black", 
            border_width=self.app.get_scaled_size(1),
            font=self.button_font, 
            height=self.button_height
        )
        self.print_list_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(5))

        # --- Finish Button ---
        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        self.finish_replen_button = ctk.CTkButton(
            bottom_actions_frame,
            text="Finish Replen",
            command=self.finish_session,
            fg_color=positive_fg, 
            hover_color=positive_hover, 
            text_color=positive_text,
            text_color_disabled=standard_dtext, 
            border_color="black", border_width=self.app.get_scaled_size(1),
            height=self.button_height,
            font=self.button_font
        )
        self.finish_replen_button.grid(row=0, column=2, sticky="e", padx=self.app.get_scaled_padding(5))

        self.on_pick_list_select()
        self.after(100, lambda: self.picking_tree.focus_set())

    def on_sort_option_change(self):
        """Called when a sort radio button is selected."""
        print(f"PickingListFrame: Sort option changed to: {self.sort_by_var.get()}")
        self.populate_picking_list()

    def populate_picking_list(self):
        for i in self.picking_tree.get_children(): self.picking_tree.delete(i)

        current_sort_criteria = self.sort_by_var.get()
                
        # Create a working copy to sort for display
        self.picking_list_items_display = list(self.picking_list_items_data_original)

        if current_sort_criteria == "sku":
            self.picking_list_items_display.sort(key=lambda item: (
                item.get('SKU','').lower(), 
                item.get('PickLocation','').lower()
            ))
            print("PickingListFrame: Populating tree sorted by SKU.")
        elif current_sort_criteria == "location":
            self.picking_list_items_display.sort(key=lambda item: (
                item.get('PickLocation','').lower(), 
                item.get('SKU','').lower()
            ))
            print("PickingListFrame: Populating tree sorted by Location.")

        if self.picking_list_items_display:
            for idx, item_detail in enumerate(self.picking_list_items_display):
                tree_iid = item_detail.get('StockItemID_to_pick_from', f"row_{idx}")
                if not item_detail.get('StockItemID_to_pick_from'):
                    tree_iid = f"nostock_{item_detail.get('SKU', f'row_{idx}')}"


                values = (
                    item_detail.get('PickLocation', ''),
                    item_detail.get('SKU', ''),
                    item_detail.get('Description', 'N/A'),
                    item_detail.get('Brand', 'N/A'),
                    item_detail.get('QtyAtLocation', 0),
                    "Replenish" 
                )
                
                # Apply tags for already processed items
                tags_to_apply = []
                if tree_iid in self.item_ids_processed_in_session:
                    tags_to_apply.append('Replenished.Treeitem')
                    processed_item_values = self.get_processed_item_display_values(tree_iid)
                    if processed_item_values:
                        values = processed_item_values
                    else:
                         values = (
                            item_detail.get('PickLocation', ''), item_detail.get('SKU', ''),
                            item_detail.get('Description', 'N/A'), item_detail.get('Brand', 'N/A'),
                            item_detail.get('QtyAtLocation', 0), "Replenish"
                        )


                self.picking_tree.insert('', tk.END, iid=tree_iid, values=values, tags=tuple(tags_to_apply))
        

    def get_processed_item_display_values(self, tree_iid_to_check):
        if tree_iid_to_check in self.item_ids_processed_in_session:
            original_item_data = next((item for item in self.picking_list_items_data_original 
                                       if str(item.get('StockItemID_to_pick_from')) == str(tree_iid_to_check)), None)
            if original_item_data:
                return (
                    original_item_data.get('PickLocation', ''),
                    original_item_data.get('SKU', ''),
                    original_item_data.get('Description', 'N/A'),
                    original_item_data.get('Brand', 'N/A'),
                    original_item_data.get('QtyAtLocation', 0), 
                    "Processed"
                )
        return None


    def process_selected_pick_item(self, event=None):
        selected_tree_iids = self.picking_tree.selection()
        if not selected_tree_iids: return
        
        selected_tree_iid = selected_tree_iids[0]

        item_data = next((item for item in self.picking_list_items_data_original if str(item.get('StockItemID_to_pick_from')) == str(selected_tree_iid)), None)

        if not item_data:
            messagebox.showerror("Error", "Could not find data for selected pick item.", parent=self)
            return
            
        try:
            processed_stock_item_id_int = int(selected_tree_iid) 
        except (ValueError, TypeError):
            messagebox.showerror("Internal Error", "Invalid item ID found in the picking list.", parent=self)
            return

        if processed_stock_item_id_int in self.item_ids_processed_in_session:
            messagebox.showinfo("Already Processed", "This item has already been processed in this session.", parent=self)
            return

        print(f"PickingList: Processing item - SKU: {item_data.get('SKU')}, Loc: {item_data.get('PickLocation')}")
        
        # --- Open Quantity Input Dialog ---       
        picked_qty_str = ctk.CTkInputDialog(text=f"Enter quantity picked for SKU {item_data.get('SKU')}\nfrom {item_data.get('PickLocation')} (Max: {item_data.get('QtyAtLocation')}):", 
                                         title="Enter Picked Quantity").get_input()
        
        if picked_qty_str is None:
            return

        try:
            picked_qty = int(picked_qty_str)
            if not (0 <= picked_qty <= item_data.get('QtyAtLocation', 0)):
                messagebox.showerror("Invalid Quantity", f"Picked quantity must be between 0 and {item_data.get('QtyAtLocation', 0)}.", parent=self)
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for quantity.", parent=self)
            return

        if picked_qty == 0:
            messagebox.showinfo("No Quantity", "No quantity picked for this item.", parent=self)
            return
        
        success = self.app.record_replenishment_pick(
            stock_item_id_to_update=item_data.get('StockItemID_to_pick_from'),
            original_replen_item_id=item_data.get('OriginalReplenItemID'),
            picked_quantity=picked_qty,
            original_location=item_data.get('PickLocation'),
            replen_list_sku=item_data.get('SKU')
        )

        if success:
            messagebox.showinfo("Success", f"{picked_qty} units of {item_data.get('SKU')} recorded as picked.", parent=self)
            self.picking_tree.item(selected_tree_iid, tags=('Replenished.Treeitem',))
            new_qty_at_loc = (item_data.get('QtyAtLocation', 0)) - picked_qty
            self.picking_tree.set(selected_tree_iid, 'qty_at_loc', new_qty_at_loc)
            self.picking_tree.set(selected_tree_iid, 'action_placeholder', f"Picked: {picked_qty}")

            self.item_ids_processed_in_session.add(processed_stock_item_id_int)
            self.on_pick_list_select()
            
        else:
            messagebox.showerror("Error", "Failed to record replenishment pick in database.", parent=self)

    def on_pick_list_select(self, event=None):
        """Enables/disables action buttons based on treeview selection."""
        if self.picking_tree.selection():
            selected_tree_iids = self.picking_tree.selection()
            if selected_tree_iids:
                selected_tree_iid = selected_tree_iids[0]
                if selected_tree_iid in self.item_ids_processed_in_session:
                    self.replenish_selected_button.configure(state="disabled")
                else:
                    self.replenish_selected_button.configure(state="normal")
        else:
            self.replenish_selected_button.configure(state="disabled")

    def finish_session(self):
        ids_to_cancel = []

        for item_detail in self.picking_list_items_data_original:
            original_replen_id = item_detail.get('OriginalReplenItemID')
            if original_replen_id is None:
                continue

            stock_item_id_to_pick = item_detail.get('StockItemID_to_pick_from')

            if stock_item_id_to_pick is not None:
                if stock_item_id_to_pick not in self.item_ids_processed_in_session:
                    ids_to_cancel.append(original_replen_id)

            elif item_detail.get('PickLocation') == 'N/A - No Stock':
                ids_to_cancel.append(original_replen_id)
        
        unique_ids_to_cancel = list(set(ids_to_cancel))
        unprocessed_count = len(unique_ids_to_cancel)

        if unprocessed_count > 0:
            if not messagebox.askyesno("Unprocessed Items", 
                                    f"There are {unprocessed_count} item(s) on the picking list not marked as picked "
                                    f"(or had no stock available).\n"
                                    "Do you want to finish this session anyway?\n\n"
                                    "Choosing 'Yes' will mark these items as 'Cancelled' on the overall replenishment list.",
                                    parent=self):
                return

            if unique_ids_to_cancel:
                print(f"PickingList: Requesting cancellation for ReplenItemIDs: {unique_ids_to_cancel}")
                success = self.app.cancel_pending_replen_items(unique_ids_to_cancel)
                if not success:
                    messagebox.showerror("Error", "Could not mark all unprocessed items as cancelled. Please check logs.", parent=self)
                    return 
            else:
                print("PickingList: No specific ReplenItemIDs to cancel.")
        
        print("PickingList: Finishing session.")
        messagebox.showinfo("Session Finished", "Replenishment session ended.", parent=self.app)
        self.app.show_main_page()

    def print_picking_list(self):
        """
        Generates a text representation of the current picking list and
        offers to save it or copies to clipboard.
        """
        if not self.picking_list_items_display:
            messagebox.showinfo("Empty List", "There is nothing on the picking list to print.", parent=self)
            return

        # --- Option 1: Copy to Clipboard ---
        try:
            import pyperclip
            
            list_string = "Pick From\tSKU\tDescription\tBrand\tQty@Loc\n"
            list_string += "---------\t---\t-----------\t-----\t-------\n"
            for item in self.picking_list_items_display:
                if item.get('PickLocation') == 'N/A - No Stock':
                    continue
                list_string += (
                    f"{item.get('PickLocation', ''):<10}\t"
                    f"{item.get('SKU', ''):<15}\t"
                    f"{item.get('Description', ''):<30.30}\t"
                    f"{item.get('Brand', ''):<15.15}\t"
                    f"{str(item.get('QtyAtLocation', 0)):>7}\n"
                )
            
            pyperclip.copy(list_string)
            messagebox.showinfo("Copied to Clipboard", 
                                "Picking list has been copied to your clipboard.\n"
                                "You can paste it into Notepad, Excel, or another application to print.", 
                                parent=self)
        except ImportError:
            messagebox.showwarning("Clipboard Error", 
                                   "Could not copy to clipboard. The 'pyperclip' module is not installed.\n"
                                   "Please ask for it to be installed, or manually note down the list.", 
                                   parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Could not prepare list for clipboard: {e}", parent=self)