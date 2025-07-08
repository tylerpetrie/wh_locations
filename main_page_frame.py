import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class MainPageFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance

        # --- Configure Main Frame Grid ---
        # Row 0: Welcome Label
        # Row 1: Top Search Sections (Location Search | Item Search)
        # Row 2: Horizontal Separator
        # Row 3: Bottom Search Sections (Location Transfer | Advanced Item Search)
        # Row 4: Bottom Action Buttons (Reports, Replen, Logout)
        self.grid_rowconfigure(0, weight=0)    # Welcome label
        self.grid_rowconfigure(1, weight=1)    # Top search inputs (allow vertical expansion)
        self.grid_rowconfigure(2, weight=0)    # Horizontal separator
        self.grid_rowconfigure(3, weight=1)    # Bottom search inputs (allow vertical expansion)
        self.grid_rowconfigure(4, weight=0)    # Bottom action buttons
        self.grid_columnconfigure(0, weight=1) # Ensure content centers or fills

        # --- Welcome Label (Row 0) ---
        self.welcome_label = ctk.CTkLabel(self, text=f"Welcome, {self.app.current_username}!", 
                                          font=self.app.get_font(size=18, weight="bold"))
        self.welcome_label.grid(row=0, column=0, padx=self.app.get_scaled_padding(20), pady=self.app.get_scaled_padding((20, 10)), sticky="n")

        # --- Top Search Area (Row 1) ---
        self.top_search_area_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_search_area_frame.grid(row=1, column=0, padx=self.app.get_scaled_padding(20), pady=self.app.get_scaled_padding((10,5)), sticky="nsew")
        
        self.top_search_area_frame.grid_columnconfigure(0, weight=1) # Left (Location Search)
        self.top_search_area_frame.grid_columnconfigure(1, weight=0) # Vertical Separator
        self.top_search_area_frame.grid_columnconfigure(2, weight=1) # Right (Item Search)
        self.top_search_area_frame.grid_rowconfigure(0, weight=1)    # Allow vertical expansion of contents

        # --- Left Search Section (Location Search) ---
        self.location_search_frame = ctk.CTkFrame(self.top_search_area_frame, fg_color="transparent")
        self.location_search_frame.grid(row=0, column=0, padx=self.app.get_scaled_padding((0, 10)), pady=self.app.get_scaled_padding(5), sticky="nsew")
        self.location_search_frame.grid_rowconfigure(0, weight=0) 
        self.location_search_frame.grid_rowconfigure(1, weight=0) 
        self.location_search_frame.grid_rowconfigure(2, weight=0) 
        self.location_search_frame.grid_columnconfigure(0, weight=1) 

        ctk.CTkLabel(self.location_search_frame, text="LOCATION SEARCH", font=self.app.get_font(size=15, weight="bold")).grid(row=0, column=0, pady=self.app.get_scaled_padding((0, 10)))
        
        self.location_entry = ctk.CTkEntry(
            self.location_search_frame, 
            placeholder_text="Enter Location",
            width=self.app.get_scaled_size(200), height=self.app.get_scaled_size(40), font=self.app.get_font(size=14)
        )
        self.location_entry.grid(row=1, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(10), sticky="ew")
        self.location_entry.bind("<Return>", lambda event: self.go_to_location())

        self.location_button = ctk.CTkButton(
            self.location_search_frame, text="Go to Location", command=self.go_to_location,
            fg_color="#FF661A", hover_color="#E65100", text_color="white", text_color_disabled="grey",
            border_width=self.app.get_scaled_size(2), border_color="black",
            width=self.app.get_scaled_size(200), height=self.app.get_scaled_size(80), font=self.app.get_font(size=20, weight="bold")
        )
        self.location_button.grid(row=2, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding((5, 10)))


        # --- Vertical Separator (Middle Column of top_search_area_frame) ---
        separator_vertical = ctk.CTkFrame(self.top_search_area_frame, width=2, fg_color="gray50")
        separator_vertical.grid(row=0, column=1, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(5), sticky="ns")


        # --- Right Search Section (Item Search) ---
        self.item_search_frame = ctk.CTkFrame(self.top_search_area_frame, fg_color="transparent")
        self.item_search_frame.grid(row=0, column=2, padx=self.app.get_scaled_padding((10, 0)), pady=self.app.get_scaled_padding(5), sticky="nsew")
        self.item_search_frame.grid_rowconfigure(0, weight=0) 
        self.item_search_frame.grid_rowconfigure(1, weight=0) 
        self.item_search_frame.grid_rowconfigure(2, weight=0) 
        self.item_search_frame.grid_columnconfigure(0, weight=1) 

        ctk.CTkLabel(self.item_search_frame, text="ITEM SEARCH", font=self.app.get_font(size=15, weight="bold")).grid(row=0, column=0, pady=self.app.get_scaled_padding((0, 10)))

        self.item_search_entry = ctk.CTkEntry(
            self.item_search_frame, placeholder_text="Enter SKU",
            width=self.app.get_scaled_size(200), height=self.app.get_scaled_size(40), font=self.app.get_font(size=14)
        )
        self.item_search_entry.grid(row=1, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(10), sticky="ew")
        self.item_search_entry.bind("<Return>", lambda event: self.search_item())

        self.item_search_button = ctk.CTkButton(
            self.item_search_frame, text="Search Item SKU", command=self.search_item,
            fg_color="#17BD17", hover_color="#14A214", text_color="white", text_color_disabled="grey",
            border_width=self.app.get_scaled_size(2), border_color="black",
            width=self.app.get_scaled_size(200), height=self.app.get_scaled_size(80), font=self.app.get_font(size=20, weight="bold")
        )
        self.item_search_button.grid(row=2, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding((5, 10)))

        # --- Horizontal Separator (Row 2) ---
        separator_horizontal = ctk.CTkFrame(self, height=2, fg_color="gray50")
        separator_horizontal.grid(row=2, column=0, padx=self.app.get_scaled_padding(20), pady=self.app.get_scaled_padding(10), sticky="ew")

        # --- Bottom Search Area (Row 3) ---
        self.bottom_search_area_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_search_area_frame.grid(row=3, column=0, padx=self.app.get_scaled_padding(20), pady=self.app.get_scaled_padding((5,10)), sticky="nsew")

        self.bottom_search_area_frame.grid_columnconfigure(0, weight=1) # Left (Transfer Location)
        self.bottom_search_area_frame.grid_columnconfigure(1, weight=0) # Vertical Separator (optional, can be omitted for cleaner look)
        self.bottom_search_area_frame.grid_columnconfigure(2, weight=1) # Right (Advanced Search)
        self.bottom_search_area_frame.grid_rowconfigure(0, weight=1)

        # --- Left: Transfer Location Button  ---
        transfer_loc_button_container = ctk.CTkFrame(self.bottom_search_area_frame, fg_color="transparent")
        transfer_loc_button_container.grid(row=0, column=0, padx=self.app.get_scaled_padding((0,10)), pady=self.app.get_scaled_padding(5), sticky="nse")
        transfer_loc_button_container.grid_columnconfigure(0, weight=1)

        self.transfer_button = ctk.CTkButton(
            transfer_loc_button_container,
            text="Transfer Location", 
            command=self.open_transfer_dialog,
            width=self.app.get_scaled_size(200), height=self.app.get_scaled_size(40), 
            fg_color="#FF661A", hover_color="#E65100", text_color="white", text_color_disabled="grey",
            font=self.app.get_font(size=14)
        )
        self.transfer_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))

        # --- Right: Advanced Search Button  ---
        adv_search_button_container = ctk.CTkFrame(self.bottom_search_area_frame, fg_color="transparent")
        adv_search_button_container.grid(row=0, column=1, padx=self.app.get_scaled_padding((10,0)), pady=self.app.get_scaled_padding(5), sticky="nsew")
        adv_search_button_container.grid_columnconfigure(0, weight=1)

        self.advanced_search_button = ctk.CTkButton(
            adv_search_button_container,
            text="Advanced Item Search", 
            command=self.open_advanced_search,
            width=self.app.get_scaled_size(200), height=self.app.get_scaled_size(40),
            fg_color="#17BD17", hover_color="#14A214", text_color="white", text_color_disabled="grey",
            font=self.app.get_font(size=14)
        )
        self.advanced_search_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))


        # --- Bottom Buttons Frame (Row 4) - Reports, Replen, Logout ---
        self.bottom_action_buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_action_buttons_frame.grid(row=4, column=0, padx=self.app.get_scaled_padding(20), pady=self.app.get_scaled_padding((10, 20)), sticky="ew")
        
        # Configure 3 columns for Reports | Replen | Logout
        self.bottom_action_buttons_frame.grid_columnconfigure(0, weight=1) 
        self.bottom_action_buttons_frame.grid_columnconfigure(1, weight=1) 
        self.bottom_action_buttons_frame.grid_columnconfigure(2, weight=1) 

        button_width = self.app.get_scaled_size(150) 
        button_height = self.app.get_scaled_size(40)  
        button_font = self.app.get_font(size=14)

        standard_fg, standard_hover, standard_text, standard_dtext = self.app.get_button_color_config("standard")
        # Reports Button (Column 0)
        self.reports_button = ctk.CTkButton(
            self.bottom_action_buttons_frame, 
            text="Reports", command=self.app.navigate_to_reports_menu,
            fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext,
            width=button_width, height=button_height, font=button_font
        )
        self.reports_button.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="e") 

        # Replen List Button (Column 1 - CENTER)
        self.replen_builder_button = ctk.CTkButton(
            self.bottom_action_buttons_frame,
            text="Replen", command=self.open_replen_builder,
            fg_color="#FF9900", hover_color="#E4A802", text_color="white", text_color_disabled="grey",
            width=button_width, height=button_height, font=button_font
        )
        self.replen_builder_button.grid(row=0, column=1, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="")

        # Logout Button (Column 2)
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")
        self.logout_button = ctk.CTkButton(
            self.bottom_action_buttons_frame, 
            text="Logout", command=self.logout, 
            fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext,
            width=button_width, height=button_height, font=button_font
        )
        self.logout_button.grid(row=0, column=2, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10), sticky="w") 

    def go_to_location(self):
        location = self.location_entry.get().strip().upper()
        if location:
            print(f"MainPageFrame: Requesting navigation to location: {location}")
            self.app.navigate_to_location_results(location)
            self.location_entry.delete(0, tk.END) 
        else:
            messagebox.showwarning("Input Needed", "Please enter a location code.", parent=self)

    def search_item(self):
        search_term = self.item_search_entry.get().strip().upper()
        if not search_term:
            messagebox.showwarning("Input Needed", "Please enter an Item Code to search", parent=self)
            self.item_search_entry.focus_set()
            return
        print(f"MainPageFrame: Requesting item search for: '{search_term}'")
        self.app.navigate_to_item_search(search_term)
        self.item_search_entry.delete(0, tk.END)

    def open_advanced_search(self):
        print("MainPageFrame: Requesting Advanced Item Search window.")
        if hasattr(self.app, 'open_advanced_search_window'):
            self.app.open_advanced_search_window()
        else:
            messagebox.showinfo("TODO", "Advanced Item Search window not implemented yet (App method missing).", parent=self)
        
    def show_reports(self):
        print("MainPageFrame: Requesting Reports window.")
        self.app.navigate_to_reports_menu()


    def open_transfer_dialog(self):
        print("MainPageFrame: Requesting Transfer Location window.")
        if hasattr(self.app, 'open_transfer_location_window'):
            self.app.open_transfer_location_window()

    def open_replen_builder(self):
        print("MainPageFrame: Requesting Replenishment Builder window.")
        if hasattr(self.app, 'navigate_to_replen_builder'):
            self.app.navigate_to_replen_builder()
        else:
            messagebox.showinfo("TODO", "Replenishment Builder not implemented yet (App method missing).", parent=self)

    def logout(self):
        print("MainPageFrame: Logging out.")
        self.app.logout()