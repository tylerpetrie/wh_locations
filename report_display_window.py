import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

class ReportDisplayWindow(ctk.CTkToplevel):
    def __init__(self, master, title, columns_config, data_rows, app_instance=None):
        """
        A generic window to display report data in a Treeview.
        Args:
            master: The parent window.
            title (str): The title of the report window.
            columns_config (list of dicts): Configuration for Treeview columns.
                Each dict: {'id': 'col_id', 'text': 'Heading Text', 'width': 100, 'anchor': 'w'}
            data_rows (list of dicts): Data to populate the tree. Keys should match col_id.
            app_instance: Optional reference to the main App instance.
        """
        super().__init__(master)
        self.app = app_instance

        # --- Define fonts and common properties ---
        self.button_font = self.app.get_font(size=14, weight="bold")
        self.button_height = self.app.get_scaled_size(35)
        self.tree_font_family = "Segoi UI"
        self.tree_font_size = 11

        self.title(title)
        self.transient(master)
        self.grab_set() 

        # --- Configure main grid ---
        self.grid_rowconfigure(0, weight=1) 
        self.grid_columnconfigure(0, weight=1) 

        # --- Treeview Frame ---
        tree_frame = ctk.CTkFrame(self)
        tree_frame.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # --- Treeview styling ---
        style = ttk.Style()
        style.map('Treeview', background=[('selected', '#A9CCE3')], foreground=[('selected', 'black')])
        style.configure("Treeview.Heading", font=(self.tree_font_family, self.tree_font_size + 1))
        style.configure("Treeview", rowheight=int(self.tree_font_size * 2.2), font=(self.tree_font_family, self.tree_font_size))
        self.tree = ttk.Treeview(tree_frame, style="Treeview", show='headings', selectmode='browse')
        
        col_ids = [c['id'] for c in columns_config]
        self.tree['columns'] = tuple(col_ids)

        for col_conf in columns_config:
            self.tree.heading(col_conf['id'], text=col_conf['text'])
            self.tree.column(
                col_conf['id'], 
                anchor=col_conf.get('anchor', tk.W),
                stretch=tk.NO
            )
        self.tree.column('#0', width=self.app.get_scaled_size(0), stretch=tk.NO)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky='ew')
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')

        self.populate_tree(col_ids, data_rows)

        # --- Auto-resize columns and window ---
        self.auto_resize_columns_and_window()

        # --- Close Button ---
        close_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        close_button_frame.grid(row=1, column=0, pady=self.app.get_scaled_padding((5,10)), sticky="e")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")
        close_btn = ctk.CTkButton(close_button_frame, text="Close", command=self.destroy, width=self.app.get_scaled_size(100), 
                                  font=self.button_font, height=self.button_height, 
                                  fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext, 
                                  border_color="black", border_width=self.app.get_scaled_size(1))
        close_btn.pack(padx=self.app.get_scaled_padding(10))

        self.bind("<Escape>", lambda event: self.destroy())
        self.lift()
        self.focus_set()

    def populate_tree(self, column_ids, data_rows):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if data_rows:
            for row_data_dict in data_rows:
                values_tuple = tuple(row_data_dict.get(col_id, '') for col_id in column_ids)
                self.tree.insert('', tk.END, values=values_tuple)
    
    def auto_resize_columns_and_window(self):
        """Measures content and resizes Treeview columns and the window to fit."""
        heading_font_tuple = self.app.get_treeview_font(size=self.tree_font_size + 1)
        content_font_tuple = self.app.get_treeview_font(size=self.tree_font_size)
        heading_font = tkfont.Font(family=heading_font_tuple[0], size=heading_font_tuple[1])
        content_font = tkfont.Font(family=content_font_tuple[0], size=content_font_tuple[1])

        total_width = 0
        for col_id in self.tree['columns']:
            max_width = heading_font.measure(self.tree.heading(col_id)['text'])

            for item_id in self.tree.get_children():
                cell_value = self.tree.item(item_id, 'values')[self.tree['columns'].index(col_id)]
                cell_width = content_font.measure(str(cell_value))
                if cell_width > max_width:
                    max_width = cell_width
            
            padded_width = max_width + self.app.get_scaled_size(20)
            
            self.tree.column(col_id, width=padded_width)
            total_width += padded_width
        
        # --- Resize the window ---
        window_padding = self.app.get_scaled_size(60)
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate final window width, but don't exceed screen width
        final_width = min(total_width + window_padding, screen_width - self.app.get_scaled_size(50))

        MAX_HEIGHT_FRACTION = 0.85 
        max_pixel_height = int(screen_height * MAX_HEIGHT_FRACTION)

        # Calculate the desired height based on content
        num_rows = len(self.tree.get_children())
        row_height = self.app.get_scaled_size(int(self.tree_font_size * 2.2))
        header_height = self.app.get_scaled_size(30)
        bottom_button_height = self.app.get_scaled_size(80) # Includes button and padding
        
        # Calculate the ideal height the content needs
        content_based_height = (num_rows * row_height) + header_height + bottom_button_height

        # Choose the smaller of the two: the ideal height or the maximum allowed height
        final_height = min(content_based_height, max_pixel_height)
        
        # Also, ensure a minimum height so tiny reports still look like a window
        final_height = max(final_height, self.app.get_scaled_size(300))
        
        # Keep a reasonable default height, or calculate it based on number of rows
        num_rows = len(self.tree.get_children())
        row_height = self.app.get_scaled_size(int(self.tree_font_size * 2.2))
        header_height = self.app.get_scaled_size(30)
        bottom_button_height = self.app.get_scaled_size(80)
        
        # Calculate final window height
        final_height = (num_rows * row_height) + header_height + bottom_button_height + self.app.get_scaled_size(50)
        final_height = min(final_height, screen_height - 100)
        final_height = max(final_height, 300)

        # Center the window with the new dimensions
        self.update_idletasks()
        x = (screen_width // 2) - (final_width // 2)
        y = (screen_height // 2) - (final_height // 2)
        
        self.geometry(f"{final_width}x{final_height}+{x}+{y}")