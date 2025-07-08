import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import bcrypt
import pyodbc
from utils import center_and_size_toplevel


class AddUserWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance

        self.title("Add New User")
        # self.geometry("350x320")
        # self.resizable(False, False)
        # self.transient(master)
        # self.grab_set()

        # --- Configure Grid ---
        self.grid_columnconfigure(0, weight=1)

        # --- Widgets ---
        self.label_title = ctk.CTkLabel(self, text="Create New User", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((20, 15)))

        self.entry_new_user = ctk.CTkEntry(self, placeholder_text="New Username", width=self.app.get_scaled_size(200))
        self.entry_new_user.grid(row=1, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10))

        self.entry_new_pin = ctk.CTkEntry(self, placeholder_text="New PIN", show="*", width=self.app.get_scaled_size(200))
        self.entry_new_pin.grid(row=2, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10))

        self.entry_confirm_pin = ctk.CTkEntry(self, placeholder_text="Confirm PIN", show="*", width=self.app.get_scaled_size(200))
        self.entry_confirm_pin.grid(row=3, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10))

        self.checkbox_quick_access = ctk.CTkCheckBox(self, text="Add to Quick Access?")
        self.checkbox_quick_access.grid(row=4, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(10))

        # Frame for buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=5, column=0, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding(20))
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        self.button_font = self.app.get_font(size=14, weight="bold")
        self.button_height = self.app.get_scaled_size(30)

        positive_fg, positive_hover, positive_text, positive_dtext = self.app.get_button_color_config("positive")
        self.button_save = ctk.CTkButton(self.button_frame, text="SAVE", font=self.button_font, height=self.button_height, command=self.save_user, width=self.app.get_scaled_size(100), fg_color=positive_fg, hover_color=positive_hover, text_color=positive_text, text_color_disabled=positive_dtext, border_color="black", border_width=1)
        self.button_save.grid(row=0, column=0, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(10))

        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")
        self.button_cancel = ctk.CTkButton(self.button_frame, text="CANCEL", font=self.button_font, height=self.button_height, command=self.destroy, width=self.app.get_scaled_size(100), fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext, border_color="black", border_width=1)
        self.button_cancel.grid(row=0, column=1, padx=self.app.get_scaled_padding(5), pady=self.app.get_scaled_padding(10))

        # Center the window relative to the main app
        # self.center_window(master)
        center_and_size_toplevel(self, base_width=350, base_height=340)

        self.lift()
        self.focus_set()
        self.grab_set()


    # def center_window(self, master_window):
    #     master_x = master_window.winfo_x()
    #     master_y = master_window.winfo_y()
    #     master_width = master_window.winfo_width()
    #     master_height = master_window.winfo_height()

    #     self.update_idletasks()
    #     width = self.winfo_width()
    #     height = self.winfo_height()

    #     x = master_x + (master_width // 2) - (width // 2)
    #     y = master_y + (master_height // 2) - (height // 2)
    #     self.geometry(f'{width}x{height}+{x}+{y}')


    def save_user(self):
        """ Validates input and saves the new user to the database """
        username = self.entry_new_user.get().strip()
        pin = self.entry_new_pin.get().upper()
        confirm_pin = self.entry_confirm_pin.get()
        is_quick = 1 if self.checkbox_quick_access.get() else 0

        # --- Input Validation ---
        if not username or not pin or not confirm_pin:
            messagebox.showerror("Error", "All fields are required.", parent=self)
            return
        if len(pin) < 4:
             messagebox.showerror("Error", "PIN must be at least 4 characters long.", parent=self)
             return
        if pin != confirm_pin:
            messagebox.showerror("Error", "PINs do not match.", parent=self)
            self.entry_new_pin.delete(0, tk.END)
            self.entry_confirm_pin.delete(0, tk.END)
            return

        # --- Check if username already exists ---
        cursor = self.app.conn.cursor()
        try:
            sql_check="SELECT UserID FROM dbo.Users WHERE LOWER(UserName) = LOWER(?)"
            cursor.execute(sql_check, username)
            if cursor.fetchone():
                messagebox.showerror("Error", f"Username '{username}' already exists.", parent=self)
                return

            # --- Hash the PIN ---
            hashed_pin_bytes = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())

            # --- Decode ---
            hashed_pin_string = hashed_pin_bytes.decode('utf-8')

            # --- Insert into Database ---
            sql_insert = "INSERT INTO dbo.Users (UserName, PINHash, IsQuickAccess) VALUES (?, ?, ?)"
            cursor.execute(sql_insert, username, hashed_pin_string, is_quick)

            self.app.conn.commit()

            messagebox.showinfo("Success", f"User '{username}' created successfully.", parent=self.master)
            self.destroy()

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save user: {e}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
