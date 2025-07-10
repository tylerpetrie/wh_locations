import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import bcrypt
import pyodbc
from .add_user_window import AddUserWindow

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance

        # --- Configure Grid ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # --- Widgets ---
        self.label_title = ctk.CTkLabel(self, text="Warehouse Login", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((20, 15)))

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Username", width=self.app.get_scaled_size(220))
        self.entry_user.grid(row=1, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10))

        self.entry_pin = ctk.CTkEntry(self, placeholder_text="PIN", show="*", width=self.app.get_scaled_size(220))
        self.entry_pin.grid(row=2, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10))
        self.entry_pin.bind("<Return>", self.login_attempt)

        # Frame for buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((15,10)))
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        self.button_font = self.app.get_font(size=14)
        self.quick_access_button_font = self.app.get_font(size=18, weight="bold")

        # -- BUTTON COLORS
        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        neutral_fg, neutral_hover, neutral_text, neutral_dtext = self.app.get_button_color_config("neutral")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")

        self.button_login = ctk.CTkButton(self.button_frame, font=self.button_font, text="LOG IN", command=self.login_attempt, width=self.app.get_scaled_size(100),
                                          fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext)
        self.button_login.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))

        self.button_add_user = ctk.CTkButton(self.button_frame, text="ADD USER", command=self.show_add_user_window, width=self.app.get_scaled_size(100),
                                             fg_color=neutral_fg, hover_color=neutral_hover, text_color=neutral_text, text_color_disabled=neutral_dtext)
        self.button_add_user.grid(row=0, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))

        #         # --- Quick Access Section ---
        # self.quick_access_users = self.fetch_quick_access_users()
        # if self.quick_access_users:
        #     self.quick_access_title = ctk.CTkLabel(self, text="Quick Access:", 
        #                                            font=ctk.CTkFont(size=13, slant="italic"))
        #     self.quick_access_title.grid(row=4, column=0, pady=self.app.get_scaled_padding((15, 0))

        #     self.quick_access_frame = ctk.CTkFrame(self, fg_color="transparent")
        #     self.quick_access_frame.grid(row=5, column=0, pady=self.app.get_scaled_padding((5,15))
        #     # Buttons will be added dynamically to quick_access_frame
        #     self.populate_quick_access_buttons()

        self.button_exit = ctk.CTkButton(self, text="EXIT", command=self.exit_app, width=self.app.get_scaled_size(100),
                                         fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext)
        self.button_exit.grid(row=6, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((10, 20)))

        self.entry_user.focus_set()

    def fetch_quick_access_users(self):
        if not self.app.conn: return []
        try:
            cursor = self.app.conn.cursor()
            cursor.execute("SELECT UserID, UserName FROM Users WHERE IsQuickAccess = 1 ORDER BY UserName")
            return [dict(row) for row in cursor.fetchall()] 
        except pyodbc.Error as e:
            print(f"Error fetching quick access users: {e}")
            return []

    def populate_quick_access_buttons(self):
        if not hasattr(self, 'quick_access_frame'):
            return

        for widget in self.quick_access_frame.winfo_children():
            widget.destroy()

        qa_button_cfg = self.app.get_button_color_config("neutral")

        for i, user_data in enumerate(self.quick_access_users):
            user_id = user_data['UserID']
            username = user_data['UserName']
            button_char = username[0].upper() if username else "?"
            
            btn = ctk.CTkButton(
                self.quick_access_frame,
                text=button_char,
                font=self.quick_access_button_font,
                width=self.app.get_scaled_size(50),
                height=self.app.get_scaled_size(50),
                command=lambda uid=user_id, uname=username: self.perform_quick_login(uid, uname),
                fg_color=qa_button_cfg[0],
                hover_color=qa_button_cfg[1],
                text_color=qa_button_cfg[2],
                text_color_disabled=qa_button_cfg[3]
            )
            btn.grid(row=0, column=i, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(5))

    def perform_quick_login(self, user_id, username):
        print(f"Quick login for UserID: {user_id}, UserName: {username}")
        self.app.current_user_id = user_id
        self.app.current_username = username
        self.entry_user.delete(0, tk.END)
        self.entry_pin.delete(0, tk.END)
        self.app.show_main_page()

    def login_attempt(self, event=None):
        username = self.entry_user.get().upper()
        pin = self.entry_pin.get()

        if not username or not pin:
            messagebox.showwarning("Login Failed", "Please enter both Username and PIN.")
            return

        cursor = self.app.conn.cursor()
        try:
            sql_query = "SELECT UserID, UserName, PINHash FROM dbo.Users WHERE LOWER(UserName) = LOWER(?)"
            cursor.execute(sql_query, username)
            user_record = cursor.fetchone()

            if user_record:
                stored_hash = user_record.PINHash                
                if isinstance(stored_hash, str):
                    stored_hash_bytes = stored_hash.encode('utf-8')
                else:
                    stored_hash_bytes = stored_hash
                pin_bytes = pin.encode('utf-8')

                if bcrypt.checkpw(pin_bytes, stored_hash_bytes):
                    # --- Login Successful ---
                    self.app.current_user_id = user_record.UserID
                    self.app.current_username = user_record.UserName
                    
                    self.entry_user.delete(0, tk.END)
                    self.entry_pin.delete(0, tk.END)
                    self.app.show_main_page()
                else:
                    messagebox.showerror("Login Failed", "Incorrect PIN.")
                    self.entry_pin.delete(0, tk.END)
            else:
                messagebox.showerror("Login Failed", "Username not found.")
                self.entry_user.delete(0, tk.END)
                self.entry_pin.delete(0, tk.END)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"An error occurred during login: {e}")
        except Exception as e:
            messagebox.showerror("Login Error", f"An unexpected error occurred: {e}")
            print(f"Unexpected login error: {e}")


    def show_add_user_window(self):
        """ Opens the Add User dialog """
        if hasattr(self.app, 'add_user_win') and self.app.add_user_win.winfo_exists():
            self.app.add_user_win.focus_set()
            self.app.add_user_win.lift()
            return

        self.app.add_user_win = AddUserWindow(master=self.app, app_instance=self.app)


    def exit_app(self):
        """ Closes the application """
        self.app.on_closing()
