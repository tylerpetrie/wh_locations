import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import bcrypt
import os
import datetime
from ui.login_frame import LoginFrame
from ui.main_page_frame import MainPageFrame
from ui.location_results_frame import LocationResultsFrame
from ui.update_new_window import UpdateNewWindow
from ui.sku_results_frame import SKUResultsFrame
from ui.transfer_location_window import TransferLocationWindow
from ui.advanced_search_window import AdvancedSearchWindow
from ui.reports_menu_frame import ReportsMenuFrame
from ui.replen_builder_frame import ReplenishmentBuilderFrame
from ui.picking_list_frame import PickingListFrame
import pyodbc
import sys
import calendar
import ctypes

try:
    # This is the modern way to set DPI awareness on Windows.
    # 2 corresponds to "Per-Monitor V2" awareness, which is the best.
    # 1 would be "System" awareness.
    ctypes.windll.shcore.SetProcessDpiAwareness(2) 
except AttributeError:
    # For older versions of Windows, fallback to user32.
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        print("Warning: Could not set DPI awareness.")

# --- Constants ---
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Main Application Database Connection Details (SQL Server)
APP_DB_SERVER = 'KS-SVR05V'
APP_DB_DATABASE = 'WH_Location_Live'
APP_DB_CONNECTION_STRING = (
    f'SERVER={APP_DB_SERVER};'
    f'DATABASE={APP_DB_DATABASE};'
    f'Trusted_Connection=yes;'
    f'TrustedServerCertificate=yes;'
)

# LSI Database Connection Details
LSI_DB_SERVER = 'KSSERVER4'
LSI_DB_DATABASE = 'iSupply_live'
LSI_CONNECTION_STRING = (
    f'SERVER={LSI_DB_SERVER};'
    f'DATABASE={LSI_DB_DATABASE};'
    f'Trusted_Connection=yes;'
    f'TrustServerCertificate=yes;'
    # Add UID/PWD if needed
)

# --- Appearance Settings ---
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

# --- Main Application Class ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. SCALING FACTOR
        self.scaling_factor = ctk.ScalingTracker.get_widget_scaling(self)

        # messagebox.showinfo("Debug Info", f"Detected Scaling Factor: {self.scaling_factor}")

        # --- 2. Configure Window ---
        self.title("Warehouse Location Manager")
        self.resizable(False, False) # Prevent resizing for simpler layout initially

        # --- 3. App State ---
        self.current_user_id = None
        self.current_username = None
        self.main_page_frame = None
        self.login_frame = None
        self.location_results_frame = None
        self.sku_results_frame = None
        self.replen_builder_frame = None
        self.replen_builder_escape_id = None
        self.picking_list_frame = None
        self.picking_list_escape_id = None
        
        # --- 4. Button Colour Palette ---
        self.button_colors = {}
        self.initialize_button_colors()
        self.get_button_color_config = lambda role_name: self.button_colors.get(
            role_name, 
            self.button_colors.get("standard")
        )

        # --- 5. Database Connection ---
        self.sql_server_driver = self.find_sql_server_driver()
        if not self.sql_server_driver:
            self.after(100, self.destroy)
            return
            
        self.conn = self.connect_db()
        
        if self.conn:
            self.create_default_admin_if_needed()
        else:
            self.after(100, self.destroy)
            return

        # --- 6. Create and Show Login Frame ---
        self.login_frame = LoginFrame(master=self, app_instance=self) # Pass App instance
        self.login_frame.pack(pady=self.get_scaled_padding(20), padx=self.get_scaled_padding(60), fill="both", expand=True)

        # --- 7. Center the window ---
        self.set_optimal_window_size(base_width=500, base_height=420)

        # --- 8. Terminate on close (x)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Scaling Helper Methods
    def get_font(self, size=12, weight="normal", slant="roman"):
        """
        Returns a CTkFont object with a DPI-scaled size.
        (Refined: Removed unused 'name' parameter for clarity).
        """
        scaled_size = int(size * self.scaling_factor)
        return ctk.CTkFont(family="Segoe UI", size=scaled_size, weight=weight, slant=slant)

    def get_treeview_font(self, size=11, weight="normal"):
        """
        Returns a tuple for ttk.Style with a DPI-scaled size.
        (Refined: Added a minimum size to prevent fonts from becoming unreadably small).
        """
        scaled_size = int(size * self.scaling_factor)
        # Ensure font is not too small on high-res screens with fractional scaling
        scaled_size = max(8, scaled_size) 
        return ("Segoe UI", scaled_size, weight)

    def get_scaled_size(self, size):
        """Returns a DPI-scaled version of a given integer size."""
        return int(size * self.scaling_factor)
    
    def get_scaled_padding(self, padding):
        """
        Returns a DPI-scaled version of a padding value. Handles both integers and tuples.
        (Your implementation is correct).
        """
        if isinstance(padding, tuple):
            return (int(padding[0] * self.scaling_factor), int(padding[1] * self.scaling_factor))
        elif isinstance(padding, (int, float)):
            return int(padding * self.scaling_factor)
        else:
            return padding
        
    def set_optimal_window_size(self, base_width, base_height):
        """
        Resizes the main window to a scaled size and re-centers it on the screen.
        (Your implementation is correct).
        """
        self.update_idletasks()

        width = self.get_scaled_size(base_width)
        height = self.get_scaled_size(base_height)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

    # def resize_and_center_main_window(self, width_fraction, height_fraction):
    #     """ Resizes and centers the MAIN application window using screen proportions. """
        
    #     # Get screen dimensions using a DPI-aware method
    #     screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    #     screen_height = ctypes.windll.user32.GetSystemMetrics(1)

    #     width = int(screen_width * width_fraction)
    #     height = int(screen_height * height_fraction)
        
    #     min_width, min_height = 400, 350
    #     if width < min_width: width = min_width
    #     if height < min_height: height = min_height
        
    #     x = (screen_width // 2) - (width // 2)
    #     y = (screen_height // 2) - (height // 2)
        
    #     self.geometry(f"{width}x{height}+{x}+{y}")

    def initialize_button_colors(self, mode=None):
        if mode is None:
            try:
                mode = ctk.get_appearance_mode() 
            except Exception:
                mode = "Light" 

        # Text Colour
        ACTIVE_BUTTON_TEXT_COLOR = "#FFFFFF" # Active Text - White
        DISABLED_BUTTON_TEXT_COLOR = "#C0C0C0" # Disabled Text - Light Grey
        # WARNING_BUTTON_TEXT_COLOR_ACTIVE = "#000000" # Black for active warning
        # WARNING_BUTTON_TEXT_COLOR_DISABLED = "#505050" # Dark Grey for disabled warning text

        # Your chosen active button colors
        RED_NORMAL = "#D41717"
        YELLOW_ORANGE_NORMAL = "#FF661A"
        GREEN_NORMAL = "#17BD17"
        BLUE_NORMAL = "#1795D4"

        # You can fine-tune these with a color picker
        RED_HOVER = "#B81414"             # Darker Red
        YELLOW_ORANGE_HOVER = "#E65100"   # Darker Orange
        GREEN_HOVER = "#14A214"           # Darker Green
        BLUE_HOVER = "#147FB0"            # Darker Blue

        if mode == "Dark": # Dark Mode
            self.button_colors = {
                # Role: (normal_fg, hover_fg, text_active_fg, disabled_fg, disabled_text_fg)
                "positive":    (GREEN_NORMAL, GREEN_HOVER, ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Green
                "destructive": (RED_NORMAL, RED_HOVER, ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Red
                "warning":     (YELLOW_ORANGE_NORMAL, YELLOW_ORANGE_HOVER, ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Yellow
                "neutral":     ("#6c757d", "#5a6268", ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Grey
                "standard":    (BLUE_NORMAL, BLUE_HOVER, ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Blue
            }
        else: # Light Mode
            self.button_colors = {
                "positive":    (GREEN_NORMAL, GREEN_HOVER, ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Green
                "destructive": (RED_NORMAL, RED_HOVER, ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Red
                "warning":     (YELLOW_ORANGE_NORMAL, YELLOW_ORANGE_HOVER, ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Yellow
                "neutral":     ("#6c757d", "#545b62", ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Grey
                "standard":    (BLUE_NORMAL, BLUE_HOVER, ACTIVE_BUTTON_TEXT_COLOR, DISABLED_BUTTON_TEXT_COLOR), # Blue
            }

    def apply_appearance_mode(self, mode_name): 
        """Applies the appearance mode and re-initializes button colors."""
        try:
            current_mode = ctk.get_appearance_mode()
            if current_mode.lower() != mode_name.lower():
                ctk.set_appearance_mode(mode_name)
        except Exception as e:
            print(f"Error setting appearance mode: {e}")

        self.initialize_button_colors(mode=mode_name)

    def find_sql_server_driver(self):
        """
        Finds the best available SQL Server ODBC driver installed on the system.
        """
        print("Searching for available SQL Server ODBC drivers...")
        installed_drivers = pyodbc.drivers()
        
        preferred_drivers = [
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 17 for SQL Server',
            'ODBC Driver 13 for SQL Server',
            'SQL Server Native Client 11.0',
            'SQL Server'
        ]

        for driver in preferred_drivers:
            if driver in installed_drivers:
                print(f"Found suitable driver: '{driver}'")
                return driver
        
        print("ERROR: No suitable SQL Server ODBC driver found.")
        messagebox.showerror(
            "Driver Not Found",
            "Could not find a suitable ODBC driver for SQL Server.\n\n"
            "Please install the 'Microsoft ODBC Driver 17 or 18 for SQL Server'."
        )
        return None

    def connect_db(self):
        """ Connects to the SQL Server database using the dynamically found driver """ 
        try:
            conn_str = (
                f'DRIVER={{{self.sql_server_driver}}};'
                f'SERVER={APP_DB_SERVER};'
                f'DATABASE={APP_DB_DATABASE};'
                f'Trusted_Connection=yes;'
                f'TrustServerCertificate=yes;'
            )
            print(f"Attempting to connect to '{APP_DB_SERVER}' using driver '{self.sql_server_driver}'...")
            
            conn = pyodbc.connect(conn_str, autocommit=False, timeout=5) 

            print(f"SQL Server database '{APP_DB_DATABASE}' on server '{APP_DB_SERVER}' connected successfully.")
            return conn
        except pyodbc.Error as e:
            sqlstate = e.args[0] if e.args else ''
            error_message = str(e)
            
            error_msg_display = f"Could not connect to the application SQL Server database.\nDetails: {error_message}"

            if '08001' in str(sqlstate):
                error_msg_display = f"Cannot connect to SQL Server '{APP_DB_SERVER}'.\n" \
                                    f"Please check:\n" \
                                    f"- Server name is correct.\n" \
                                    f"- SQL Server is running.\n" \
                                    f"- Network connectivity and firewall rules."
            elif '28000' in str(sqlstate):
                error_msg_display = f"SQL Server login failed for database '{APP_DB_DATABASE}'.\n" \
                                    f"If using Windows Authentication, check permissions for your Windows user.\n" \
                                    f"If using SQL Authentication, check UID/PWD in connection string."
            elif '42000' in str(sqlstate) and "Cannot open database" in error_message:
                error_msg_display = f"SQL Server database '{APP_DB_DATABASE}' not found or access denied for your user.\n" \
                                    f"Please verify the database name and user permissions."
            elif 'HYT00' in str(sqlstate):
                 error_msg_display = f"Connection to SQL Server '{APP_DB_SERVER}' timed out.\n" \
                                     f"Server might be too busy, or network issues are preventing a timely connection."

            print(f"FATAL: SQL Server Database connection error: {e}")
            messagebox.showerror("Database Connection Error", error_msg_display, parent=self if self.winfo_exists() else None)
            
            if hasattr(self, 'master') and self.master is None and not self.winfo_exists():
                sys.exit(f"Failed to connect to database: {error_msg_display}")
            else:
                self.quit()
            return None

    def fetch_lsi_data(self, sku):
        """ Fetches product details from iSupply_live based on SKU"""
        if not self.sql_server_driver:
            print(f"ERROR: No SQL Server driver found.")
            return None
        
        print(f"App: Fetching LSI data for SKU: {sku}")
        lsi_conn = None
        try:
            # Build LSI connection string with the dynamically found driver
            lsi_conn_str = (
                f'DRIVER={{{self.sql_server_driver}}};'
                f'SERVER={LSI_DB_SERVER};'
                f'DATABASE={LSI_DB_DATABASE};'
                f'Trusted_Connection=yes;'
                f'TrustServerCertificate=yes;'
            )
            lsi_conn = pyodbc.connect(lsi_conn_str, autocommit=True, timeout=5)
            cursor = lsi_conn.cursor()

            # --- Query 1: Main LSI Data (Brand, Description, Barcode for single unit, etc.) ---
            sql_main = """
                SELECT TOP 1
                    R370_BRAND, R370_PRODUCT_DESCRIPTION, R890_BIN_LOCATION_CODE,
                    R370_DANGEROUS_GOODS_UN_NO, R411_SUBSTITUTE_EAN_CODE
                FROM
                    F370_PRODUCT_SCANPACK
                INNER JOIN F411_PRODUCT_EAN_SUBS ON F370_PRODUCT_SCANPACK.R370_RECORD_ID = F411_PRODUCT_EAN_SUBS.R411_R370_RECORD_ID
                INNER JOIN F371_PRODUCT_LOCATIONS ON F370_PRODUCT_SCANPACK.R370_RECORD_ID = F371_PRODUCT_LOCATIONS.R371_R370_RECORD_ID
                INNER JOIN F890_WAREHOUSE_BIN_LOCATION ON F371_PRODUCT_LOCATIONS.R371_R890_RECORD_ID = F890_WAREHOUSE_BIN_LOCATION.R890_RECORD_ID
                WHERE
                    F411_PRODUCT_EAN_SUBS.R411_SUBSTITUTE_QUANTITY = '1' -- For single item EAN
                    AND F370_PRODUCT_SCANPACK.R370_INHOUSE_STOCK_CODE = ? -- Parameter for SKU
            """
            cursor.execute(sql_main, sku)
            row_main = cursor.fetchone()

            if not row_main:
                print("App: LSI data not found (main query for SKU failed).")
                return None 
            
            print("App: Main LSI data found.")
            brand = str(row_main[0]).strip() if row_main[0] else None
            description = str(row_main[1]).strip() if row_main[1] else None
            shelf_location = str(row_main[2]).strip() if row_main[2] else None
            dg_un_no_raw = row_main[3]
            barcode = str(row_main[4]).strip() if row_main[4] else None

            is_dg_flag = 1 if dg_un_no_raw and str(dg_un_no_raw).strip() else 0
            dg_un_no_str = str(dg_un_no_raw).strip() if is_dg_flag else None
            
            units_per_carton_lsi = None

            # --- Query 2: Units Per Carton (Outer Quantity for the same SKU) ---
            sql_outer = """
                SELECT TOP 1 R411_SUBSTITUTE_QUANTITY
                FROM F370_PRODUCT_SCANPACK
                INNER JOIN F411_PRODUCT_EAN_SUBS ON F370_PRODUCT_SCANPACK.R370_RECORD_ID = F411_PRODUCT_EAN_SUBS.R411_R370_RECORD_ID
                -- INNER JOIN F371_PRODUCT_LOCATIONS ON F370_PRODUCT_SCANPACK.R370_RECORD_ID = F371_PRODUCT_LOCATIONS.R371_R370_RECORD_ID
                -- INNER JOIN F890_WAREHOUSE_BIN_LOCATION ON F371_PRODUCT_LOCATIONS.R371_R890_RECORD_ID = F890_WAREHOUSE_BIN_LOCATION.R890_RECORD_ID
                INNER JOIN F395_UNIT_MEASURE_CODES ON F395_UNIT_MEASURE_CODES.R395_RECORD_ID = F411_PRODUCT_EAN_SUBS.R411_R395_RECORD_ID
                WHERE F370_PRODUCT_SCANPACK.R370_INHOUSE_STOCK_CODE = ? 
                  AND F395_UNIT_MEASURE_CODES.R395_UNIT_MEASURE_DESC = 'OUTER'
                ORDER BY R411_SUBSTITUTE_QUANTITY DESC
            """            

            cursor.execute(sql_outer, sku)
            row_outer = cursor.fetchone()

            if row_outer and row_outer[0] is not None:
                try:
                    units_per_carton_lsi = int(row_outer[0])
                    print(f"App: LSI UnitsPerCarton (OUTER Qty) found: {units_per_carton_lsi}")
                except ValueError:
                    print(f"App: LSI UnitsPerCarton found but not a valid integer: {row_outer[0]}")
                    units_per_carton_lsi = None
            else:
                print("App: LSI UnitsPerCarton (OUTER Qty) not found or is NULL for SKU.")

            return {
                'Brand': brand,
                'Description': description,
                'ShelfLocation': shelf_location,
                'IsDangerousGood': is_dg_flag,
                'Barcode': barcode,
                'DG_UN_Number': dg_un_no_str,
                'UnitsPerCarton': units_per_carton_lsi
            }

        except pyodbc.Error as e:
            print(f"ERROR: Failed to fetch LSI data for SKU {sku}: {e}", file=sys.stderr)
            sqlstate = e.args[0]
            error_msg = f"Could not retrieve data from iSupply_Live.\nError: {e}"
            if '08001' in str(sqlstate) or 'HYT00' in str(sqlstate):
                 error_msg = f"Could not connect to LSI database server ({LSI_DB_SERVER}). Check network/server status or firewall."
            elif '28000' in str(sqlstate):
                 error_msg = "LSI database login failed. Check credentials/permissions."
            messagebox.showerror("LSI Connection Error", error_msg, parent=self)
            return None
        except Exception as e:
             print(f"ERROR: Unexpected error during LSI fetch for SKU {sku}: {e}", file=sys.stderr)
             messagebox.showerror("LSI Fetch Error", f"An unexpected error occurred.\nError: {e}", parent=self)
             return None
        finally:
            if lsi_conn:
                lsi_conn.close()


    def create_default_admin_if_needed(self):
        """ Creates a default 'Tyler' user if no users exist (SQL Server version) """
        if not self.conn:
            print("Skipping default admin creation: No database connection.")
            return

        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'Users'
            """)
            if cursor.fetchone()[0] == 0:
                msg = f"CRITICAL: 'Users' table not found in database '{APP_DB_DATABASE}' on server '{APP_DB_SERVER}'.\n" \
                       "Please ensure the database schema has been created correctly."
                print(msg)
                messagebox.showerror("Database Schema Error", msg, parent=self if self.winfo_exists() else None)
                return

            # Proceed to check user count
            cursor.execute("SELECT COUNT(*) FROM dbo.Users")
            user_count_result = cursor.fetchone()
            user_count = user_count_result[0] if user_count_result else 0
            
            if user_count == 0:
                print(f"No users found in '{APP_DB_DATABASE}'. Creating default 'Tyler' user with PIN '2004'.")
                default_user = "Tyler"
                default_pin = "2004"
                hashed_pin_bytes = bcrypt.hashpw(default_pin.encode('utf-8'), bcrypt.gensalt())

                hashed_pin_string = hashed_pin_bytes.decode('utf-8')
                hashed_pin = hashed_pin_string
                
                cursor.execute("INSERT INTO dbo.Users (UserName, PINHash, IsQuickAccess) VALUES (?, ?, ?)",
                               (default_user, hashed_pin, 0))
                self.conn.commit()
                messagebox.showinfo("First Time Setup", 
                                    f"Default user '{default_user}' with PIN '{default_pin}' created in SQL Server.\n"
                                    "It's recommended to change this PIN or add a new administrator.",
                                    parent=self if self.winfo_exists() else None)
        except pyodbc.Error as e:
            sqlstate = e.args[0] if e.args and len(e.args) > 0 else ''
            error_message = str(e)
            
            print(f"SQL Server Error during default user creation: {error_message} (SQLSTATE: {sqlstate})")
            msg_detail = f"Failed to setup initial user in SQL Server '{APP_DB_DATABASE}'.\nError: {error_message}"
            if "Invalid object name 'Users'" in error_message:
                 msg_detail = f"'Users' table not found. Please ensure the database schema is correctly deployed."
            
            messagebox.showerror("Database Setup Error", msg_detail, parent=self if self.winfo_exists() else None)
            if self.conn and not self.conn.closed:
                try:
                    self.conn.rollback()
                except pyodbc.Error as rb_e:
                    print(f"Error during rollback attempt: {rb_e}")
        except Exception as e:
            print(f"Unexpected error during default user creation: {e}")
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}", parent=self if self.winfo_exists() else None)
            if self.conn and not self.conn.closed:
                try:
                    self.conn.rollback()
                except pyodbc.Error as rb_e:
                    print(f"Error during rollback attempt: {rb_e}")
        finally:
            if cursor:
                try:
                    cursor.close()
                except pyodbc.Error as cur_e:
                    print(f"Error closing cursor: {cur_e}")

        # Helper to manage unbinding and nullifying frames
    def _clear_primary_frame(self, frame_attr_name, esc_id_attr_name=None):
        if hasattr(self, frame_attr_name):
            frame_instance = getattr(self, frame_attr_name)
            if frame_instance and frame_instance.winfo_exists():
                print(f"App: Destroying frame from attribute '{frame_attr_name}'.")
                frame_instance.destroy()
            setattr(self, frame_attr_name, None)

        if esc_id_attr_name and hasattr(self, esc_id_attr_name):
            binding_id = getattr(self, esc_id_attr_name)
            if binding_id:
                print(f"App: Unbinding ESC for {esc_id_attr_name} (ID: {binding_id})")
                self.unbind("<Escape>", binding_id)
            setattr(self, esc_id_attr_name, None)

    def show_main_page(self):
        """ 
        Switches view to the Main Page Frame.
        This method is the central point for returning to the main menu and cleans up other views.
        """
        print(f"App: Switching to Main Page (User: {self.current_username}).")
        
        # Clear all other primary content frames and their specific ESC bindings
        self._clear_primary_frame('location_results_frame', 'location_results_escape_id')
        self._clear_primary_frame('sku_results_frame', 'sku_results_escape_id')
        self._clear_primary_frame('reports_menu_frame_instance', 'reports_menu_escape_id')
        self._clear_primary_frame('replen_builder_frame', 'replen_builder_escape_id')
        self._clear_primary_frame('picking_list_frame', 'picking_list_escape_id')

        # Ensure LoginFrame is hidden if it was somehow visible (shouldn't be if user is logged in)
        if self.login_frame is not None and self.login_frame.winfo_exists():
            self.login_frame.pack_forget()

        # Create and show the Main Page Frame
        if self.main_page_frame is None or not self.main_page_frame.winfo_exists():
            print("App: Creating new MainPageFrame instance.")
            self.main_page_frame = MainPageFrame(master=self, app_instance=self)
        else:
            print("App: MainPageFrame instance already exists.")
            
        self.main_page_frame.pack(pady=self.get_scaled_padding(20), padx=self.get_scaled_padding(20), fill="both", expand=True)
        self.main_page_frame.focus_set()

        # Update window properties for the main page
        # self.title(f"Warehouse Locations - User: {self.current_username}")
        # self.geometry("700x550")
        # self.center_window()
        self.title(f"Warehouse Locations - User: {self.current_username}")
        self.set_optimal_window_size(base_width=700, base_height=550)
        if hasattr(self.main_page_frame, 'welcome_label') and self.main_page_frame.welcome_label:
            self.main_page_frame.welcome_label.configure(text=f"Welcome, {self.current_username}!")

      
    def show_login_page(self):
        """ Switches back to the Login Page (e.g., on Logout) """
        print("App: Switching to Login Page.")

        self._clear_primary_frame('main_page_frame') # Clear the main page frame itself
        self._clear_primary_frame('location_results_frame', 'location_results_escape_id')
        self._clear_primary_frame('sku_results_frame', 'sku_results_escape_id')
        self._clear_primary_frame('reports_menu_frame_instance', 'reports_menu_escape_id')
        self._clear_primary_frame('replen_builder_frame', 'replen_builder_escape_id')
        self._clear_primary_frame('picking_list_frame', 'picking_list_escape_id')
      
        self.current_user_id = None
        self.current_username = None

        # --- Create login frame if needed ---
        if self.login_frame is None or not self.login_frame.winfo_exists():
            self.login_frame = LoginFrame(master=self, app_instance=self)  
        self.login_frame.pack(pady=self.get_scaled_padding(20), padx=self.get_scaled_padding(60), fill="both", expand=True)

        # --- Adjust window for login ---
        # self.title("Warehouse Location Manager - Login")
        # self.geometry("500x380")
        # self.resizable(False, False)
        # self.center_window()
        self.title("Warehouse Location Manager - Login")
        self.resizable(False, False)
        self.set_optimal_window_size(base_width=500, base_height=380)

    def on_closing(self):
        """ Handle window close event with a more robust shutdown sequence. """
        print("INFO: Closing application...")
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                print("INFO: Database connection closed.")
        except Exception as e:
            print(f"WARNING: Error while closing database connection: {e}")

        self.destroy()
        print("INFO: Tkinter window destroyed.")
        
        print("INFO: Forcing Python process exit.")
        sys.exit(0)

    def navigate_to_location_results(self, location_code):
        """ Fetches data and displays the Location_Results window. """
        print(f"App: Navigating to results for Location: {location_code}")
        location_code = location_code.strip().upper()

        # --- 1. Validate Location (Optional but good) ---
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT LocationName FROM dbo.Locations WHERE LocationName = ?", (location_code,))
            if not cursor.fetchone():
                messagebox.showerror("Invalid Location", f"Location code '{location_code}' does not exist.", parent=self)
                return 
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Error validating location: {e}", parent=self)
            return

        # --- Clear other primary frames and their ESC bindings ---
        if self.main_page_frame and self.main_page_frame.winfo_exists(): self.main_page_frame.pack_forget()
        self._clear_primary_frame('sku_results_frame', 'sku_results_escape_id')
        self._clear_primary_frame('reports_menu_frame_instance', 'reports_menu_escape_id')
        self._clear_primary_frame('location_results_frame', 'location_results_escape_id')

        # --- 2. Fetch Stock Data and Location Header Data ---
        stock_data = []
        location_header_data = None
        try:
            sql_query = """
                SELECT StockItemID, SKU, Brand, Description, ShelfLocation, IsDangerousGood, DG_UN_Number,
                       Barcode, Batch, ExpiryDate, Quantity, UnitsPerCarton, Notes,
                       LastUpdatedBy, LastUpdatedDate, IsAdhoc, IsQuarantined, IsFirst
                FROM dbo.StockItems 
                WHERE LocationName = ?
                ORDER BY SKU, Batch
            """ 
            cursor.execute(sql_query, location_code)

            columns = [column[0] for column in cursor.description]
            stock_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.execute("SELECT DateFirstStocked FROM dbo.Locations WHERE LocationName = ?", (location_code,))
            loc_result = cursor.fetchone()
            if loc_result:
                 location_header_data = {'DateFirstStocked': loc_result.DateFirstStocked}

            print(f"App: Found {len(stock_data)} items and header data for location {location_code}")
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch data for {location_code}: {e}", parent=self)
            return

        # --- Create and Show New Location Results Frame ---
        self.location_results_frame = LocationResultsFrame(
            master=self,
            app_instance=self,
            location_code=location_code,
            stock_data=stock_data,
            location_header_data=location_header_data
        )
        self.location_results_frame.pack(pady=self.get_scaled_padding(10), padx=self.get_scaled_padding(10), fill="both", expand=True)
        self.location_results_frame.focus_set()

        # --- Update Window Properties ---
        # self.title(f"Location: {location_code} - User: {self.current_username}")
        # self.geometry("1200x700")
        # self.center_window()
        self.title(f"Location: {location_code} - User: {self.current_username}")
        self.set_optimal_window_size(base_width=1200, base_height=700)

        # Bind ESC key on the APP WINDOW to go back to main page
        self.location_results_escape_id = self.bind("<Escape>", lambda event: self.show_main_page())
        print(f"App: Bound ESC (App level) for LocationResults to call show_main_page.")

    def navigate_to_item_search(self, search_term):
        """Handles item search requests from the main page."""
        search_term = search_term.strip()
        if not search_term:
            print("App: SKU Search was empty")
            messagebox.showwarning("Input Needed", "Please enter an item code", parent=self) 
        else:
            print(f"App: Navigating to SKU results for Item: {search_term}")
            self.navigate_to_sku_results(search_term)

    def navigate_to_sku_results(self, sku):
        """ Fetches LSI & DB data for an SKU and displays the SKU_Results frame. """
        print(f"App: Navigating to results for SKU: {sku}")
        sku = sku.strip().upper()

        # --- Clear other primary frames and their ESC bindings ---
        if self.main_page_frame and self.main_page_frame.winfo_exists(): self.main_page_frame.pack_forget()
        self._clear_primary_frame('location_results_frame', 'location_results_escape_id')
        self._clear_primary_frame('reports_menu_frame_instance', 'reports_menu_escape_id')
        self._clear_primary_frame('sku_results_frame', 'sku_results_escape_id')

        # --- Fetch LSI Data for Header ---
        lsi_header_data = self.fetch_lsi_data(sku)
        if lsi_header_data: print("App: LSI data found for SKU header.")
        else: print("App: LSI data NOT found for SKU header (might be Adhoc).")

        # --- Fetch Stock Data from Local DB for this SKU (including Location's DateFirstStocked) ---
        stock_data = []
        try:
            cursor = self.conn.cursor()
            sql = """
                SELECT 
                    si.StockItemID, si.LocationName, si.Batch, si.ExpiryDate, si.Quantity, si.UnitsPerCarton,
                    si.Notes, si.LastUpdatedBy, si.LastUpdatedDate, si.IsAdhoc, si.SKU, si.IsQuarantined, si.IsFirst,
                    loc.DateFirstStocked
                FROM dbo.StockItems AS si 
                INNER JOIN Locations AS loc ON si.LocationName = loc.LocationName
                WHERE si.SKU = ?
                ORDER BY si.LocationName, si.Batch
            """
            cursor.execute(sql, (sku,))
            columns = [column[0] for column in cursor.description]
            stock_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print(f"App: Found {len(stock_data)} stock records for SKU {sku} in local DB.")

            if not stock_data and not lsi_header_data:
                 messagebox.showinfo("Not Found", f"SKU '{sku}' not found in LSI or local stock.", parent=self)
                 self.show_main_page()
                 return
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch stock data for SKU {sku}: {e}", parent=self)
            self.show_main_page()
            return
        except Exception as e:
             messagebox.showerror("Data Error", f"Error processing stock data for SKU {sku}: {e}", parent=self)
             self.show_main_page()
             return

        # --- Create and Show New SKU Results Frame ---
        self.sku_results_frame = SKUResultsFrame(
            master=self,
            app_instance=self,
            searched_sku=sku,
            sku_lsi_data=lsi_header_data,
            stock_data=stock_data
        )
        self.sku_results_frame.pack(pady=self.get_scaled_padding(10), padx=self.get_scaled_padding(10), fill="both", expand=True)
        self.sku_results_frame.focus_set()

        # --- Update Window Properties (SKU LOCATIONS) ---
        # self.title(f"SKU Locations: {sku} - User: {self.current_username}")
        # self.geometry("1100x650")
        # self.center_window()
        self.title(f"SKU Locations: {sku} - User: {self.current_username}")
        self.set_optimal_window_size(base_width=1100, base_height=650)

        # Bind ESC key on the APP WINDOW to go back to main page
        self.sku_results_escape_id = self.bind("<Escape>", lambda event: self.show_main_page())
        print(f"App: Bound ESC (App level) for SKUResults to call show_main_page.")

    def execute_location_transfer(self, from_loc_raw, to_loc_raw):
        """
        Executes the logic to transfer stock items from one location to another.
        Handles empty destination, non-empty destination (with merge prompt),
        and updates DateFirstStocked accordingly.
        Returns True on success, or an error message string on failure.
        """
        from_loc = from_loc_raw.strip().upper()
        to_loc = to_loc_raw.strip().upper()

        if not self.conn:
            return "Database connection not available."

        cursor = self.conn.cursor()

        try:
            # --- 1. Validate Locations ---
            cursor.execute("SELECT LocationName, DateFirstStocked FROM dbo.Locations WHERE LocationName = ?", (from_loc,))
            from_loc_data = cursor.fetchone()
            if not from_loc_data:
                return f"Error: 'From Location' {from_loc} does not exist."

            cursor.execute("SELECT LocationName, DateFirstStocked FROM dbo.Locations WHERE LocationName = ?", (to_loc,))
            to_loc_data = cursor.fetchone()
            if not to_loc_data:
                return f"Error: 'To Location' {to_loc} does not exist."

            # --- 2. Check if 'From Location' has stock ---
            cursor.execute("SELECT COUNT(*) FROM dbo.StockItems WHERE LocationName = ?", (from_loc,))
            from_stock_count = cursor.fetchone()[0]
            if from_stock_count == 0:
                return f"Information: 'From Location' {from_loc} has no stock to transfer."

            # --- 3. Check if 'To Location' is empty ---
            cursor.execute("SELECT COUNT(*) FROM dbo.StockItems WHERE LocationName = ?", (to_loc,))
            to_stock_count = cursor.fetchone()[0]

            date_to_set_for_to_loc = to_loc_data.DateFirstStocked
            if to_stock_count == 0:
                if from_loc_data.DateFirstStocked:
                    date_to_set_for_to_loc = from_loc_data.DateFirstStocked

            # --- 4. Perform Transfer based on destination state ---
            if to_stock_count == 0: # Destination is empty
                print(f"App: Transferring from {from_loc} to EMPTY {to_loc}.")
                if from_loc_data.DateFirstStocked:
                    date_to_set_for_to_loc = from_loc_data.DateFirstStocked
                else:
                    date_to_set_for_to_loc = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')

                perform_transfer = True 
            
            else:
                print(f"App: Transferring from {from_loc} to NON-EMPTY {to_loc}.")
                parent_window = self.transfer_win if hasattr(self, 'transfer_win') and self.transfer_win.winfo_exists() else self
                
                merge_message = (
                    f"Desination location '{to_loc}' is not empty.\n\n"
                    f"Do you want to MERGE the contents from '{from_loc}' into '{to_loc}?\n\n"
                )

                merge = messagebox.askyesno(
                    "Confirm Merge",
                    merge_message,
                    parent=parent_window
                )
                if merge:
                    perform_transfer = True
                    if not date_to_set_for_to_loc:
                        date_to_set_for_to_loc = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
                else:
                    perform_transfer = False
                    return "Transfer cancelled by user."

            # --- 5. Execute Database Updates if transfer is confirmed ---
            if perform_transfer:
                now_str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
                user = self.current_username if self.current_username else "Unknown"
                user_id = self.current_user_id

                if user_id is None: # Safety check
                    if self.conn: self.conn.rollback()
                    return "User not identified. Cannot log history for transfer."

                # --- Fetch details of ALL items to be transferred BEFORE updating ---
                items_to_transfer_details = []
                cursor.execute("""
                    SELECT StockItemID, LocationName, SKU, Batch, Quantity 
                    FROM dbo.StockItems 
                    WHERE LocationName = ?
                """, (from_loc,))
                columns = [column[0] for column in cursor.description]
                items_to_transfer_details = [dict(zip(columns, row)) for row in cursor.fetchall()]

                # Update StockItems: Move them and update LastUpdated fields
                cursor.execute("""
                    UPDATE dbo.StockItems 
                    SET LocationName = ?, LastUpdatedBy = ?, LastUpdatedDate = ?
                    WHERE LocationName = ?
                    """, (to_loc, user, now_str, from_loc))
                moved_item_count = cursor.rowcount
                print(f"App: Moved and updated {moved_item_count} stock items from {from_loc} to {to_loc}.")

                # --- Log 'TRANSFER' to StockItemHistory for each item ---
                sql_history_transfer = """
                    INSERT INTO dbo.StockItemHistory 
                        (StockItemID, ChangeTimestamp, UserID, ChangeType, 
                        FieldName, OldValue, NewValue, 
                        LocationName, SKU, Notes)
                    VALUES (?, ?, ?, 'TRANSFER', ?, ?, ?, ?, ?, ?)
                """
                for item_detail in items_to_transfer_details:
                    history_notes = f"Item SKU {item_detail['SKU']} transferred from {from_loc} to {to_loc}."
                    history_params_transfer = (
                        item_detail['StockItemID'],
                        now_str,
                        user_id,
                        # ChangeType is 'TRANSFER'
                        'LocationName', # FieldName
                        from_loc,       # OldValue
                        to_loc,         # NewValue
                        to_loc,         # Current (new) LocationName for denormalization
                        item_detail['SKU'],
                        history_notes
                    )
                    cursor.execute(sql_history_transfer, history_params_transfer)

                # Update 'From Location': Clear its DateFirstStocked as it's now empty
                cursor.execute("UPDATE dbo.Locations SET DateFirstStocked = NULL WHERE LocationName = ?", (from_loc,))
                print(f"App: Cleared DateFirstStocked for {from_loc}.")

                # Update 'To Location': Set its DateFirstStocked
                cursor.execute("UPDATE dbo.Locations SET DateFirstStocked = ? WHERE LocationName = ?", (date_to_set_for_to_loc, to_loc))
                print(f"App: Set DateFirstStocked for {to_loc} to {date_to_set_for_to_loc}.")

                self.conn.commit()
                if self.location_results_frame and self.location_results_frame.winfo_ismapped():
                    if self.location_results_frame.location_code == from_loc:
                        self.refresh_location_results(from_loc)
                    elif self.location_results_frame.location_code == to_loc:
                        self.refresh_location_results(to_loc)
                
                return True
            
            return "Transfer not performed (internal logic error)." 

        except pyodbc.Error as e:
            if self.conn: self.conn.rollback()
            print(f"App: Database error during transfer: {e}")
            return f"Database error during transfer: {e}"
        except Exception as e:
            if self.conn: self.conn.rollback()
            print(f"App: Unexpected error during transfer: {e}")
            return f"An unexpected error occurred: {e}"

    def navigate_to_reports_menu(self):
        """ Switches view to the Reports Menu Frame. """
        print("App: Navigating to Reports Menu.")
        
        # --- Clear other primary frames and their ESC bindings ---
        if self.main_page_frame and self.main_page_frame.winfo_exists(): self.main_page_frame.pack_forget()
        self._clear_primary_frame('location_results_frame', 'location_results_escape_id')
        self._clear_primary_frame('sku_results_frame', 'sku_results_escape_id')
        self._clear_primary_frame('reports_menu_frame_instance', 'reports_menu_escape_id')

        # --- Create and show the Reports Menu Frame ---
        self.reports_menu_frame_instance = ReportsMenuFrame(master=self, app_instance=self)
        self.reports_menu_frame_instance.pack(pady=self.get_scaled_padding(20), padx=self.get_scaled_padding(20), fill="both", expand=True)
        self.reports_menu_frame_instance.focus_set() # Give focus to the new frame

        # --- Update Window Properties (Reports Menu) ---
        # self.title(f"Reports - User: {self.current_username}")
        # self.geometry("600x500")
        # self.center_window()
        self.title(f"Reports - User: {self.current_username}")
        self.set_optimal_window_size(base_width=600, base_height=500)

        # Bind ESC key on the APP WINDOW to go back to main page
        self.reports_menu_escape_id = self.bind("<Escape>", lambda event: self.show_main_page())
        print("App: Bound ESC (App level) for ReportsMenu to call show_main_page.")

    
    def navigate_to_replen_builder(self):
        """ Switches view to the Replenishment List Builder Frame. """
        print("App: Navigating to Replenishment List Builder.")
        
        # Clear other primary frames
        if self.main_page_frame and self.main_page_frame.winfo_exists(): self.main_page_frame.pack_forget()
        self._clear_primary_frame('location_results_frame', 'location_results_escape_id')
        self._clear_primary_frame('sku_results_frame', 'sku_results_escape_id')
        self._clear_primary_frame('reports_menu_frame_instance', 'reports_menu_escape_id')
        self._clear_primary_frame('replen_builder_frame', 'replen_builder_escape_id')

        # Create and show the Replenishment Builder Frame
        self.replen_builder_frame = ReplenishmentBuilderFrame(master=self, app_instance=self)
        self.replen_builder_frame.pack(pady=self.get_scaled_padding(10), padx=self.get_scaled_padding(10), fill="both", expand=True)
        self.replen_builder_frame.focus_set()

        self.title(f"Build Replenishment List - User: {self.current_username}")
        # self.geometry("900x700")
        # self.center_window()
        self.set_optimal_window_size(base_width=900, base_height=700)

        # Bind ESC key on the APP WINDOW to go back to main page
        self.replen_builder_escape_id = self.bind("<Escape>", lambda event: self.show_main_page())
        print("App: Bound ESC (App level) for ReplenBuilder to call show_main_page.")

    def navigate_to_picking_list(self):
        """ 
        Fetches data for the pending replenishment items (the picking list) 
        and displays the PickingListFrame.
        """
        print("App: Navigating to Picking List.")
        
        # Clear other primary frames
        if self.main_page_frame and self.main_page_frame.winfo_exists(): self.main_page_frame.pack_forget()
        self._clear_primary_frame('location_results_frame', 'location_results_escape_id')
        self._clear_primary_frame('sku_results_frame', 'sku_results_escape_id')
        self._clear_primary_frame('reports_menu_frame_instance', 'reports_menu_escape_id')
        self._clear_primary_frame('replen_builder_frame', 'replen_builder_escape_id')
        self._clear_primary_frame('picking_list_frame', 'picking_list_escape_id')
        
        picking_list_data_raw = self.generate_picking_list_data() # To be created

        if picking_list_data_raw is None:
            self.show_main_page()
            return
        
        if not picking_list_data_raw:
            messagebox.showinfo("Picking List", "There are no items currently pending replenishment.", 
                                parent=self)
            if self.replen_builder_frame and self.replen_builder_frame.winfo_exists():
                self.show_main_page()
            else:
                self.show_main_page()
            return

        # --- Sort ALL potential picking list items first ---
        all_sorted_pick_options = self.sort_picking_list_data(picking_list_data_raw)

        # --- Now, select only the TOP priority location for each unique SKU ---
        final_picking_list_for_display = []
        processed_skus_for_picking = set()

        for item in all_sorted_pick_options:
            sku = item.get('SKU')
            # Handle items that couldn't be stocked (PickLocation is 'N/A - No Stock')
            if item.get('PickLocation') == 'N/A - No Stock':
                if sku not in processed_skus_for_picking:
                    final_picking_list_for_display.append(item)
                    processed_skus_for_picking.add(sku)
                continue

            # For items with stock, only add the first (highest priority) location for this SKU
            if sku not in processed_skus_for_picking:
                final_picking_list_for_display.append(item)
                processed_skus_for_picking.add(sku)
        
        print(f"App: Refined picking list to {len(final_picking_list_for_display)} unique SKU pick locations.")

        if not final_picking_list_for_display:
            messagebox.showinfo("Picking List", "No pickable locations found for pending items.", parent=self)
            self.show_main_page()
            return

        # Create and show the Picking List Frame
        self.picking_list_frame = PickingListFrame(
            master=self, 
            app_instance=self, 
            picking_list_items=final_picking_list_for_display
        )
        self.picking_list_frame.pack(pady=self.get_scaled_padding(10), padx=self.get_scaled_padding(10), fill="both", expand=True)
        self.picking_list_frame.focus_set()

        self.title(f"Picking List - User: {self.current_username}")
        # self.geometry("1000x700")
        # self.center_window()
        self.set_optimal_window_size(base_width=1000, base_height=700)

        self.picking_list_escape_id = self.bind("<Escape>", lambda event: self.show_main_page())
        print("App: Bound ESC (App level) for PickingListFrame to call show_main_page.")

    def logout(self):
        """Logs the current user out and returns to login screen"""
        print("App: Logging out")
        self.show_login_page()

    def open_transfer_location_window(self):
        """ Opens the window for transferring stock items between locations. """
        print("App: Opening Transfer Location window.")

        if hasattr(self, 'transfer_win') and self.transfer_win.winfo_exists():
            self.transfer_win.lift()
            self.transfer_win.focus_set()
            return

        # Create a new instance
        self.transfer_win = TransferLocationWindow(master=self, app_instance=self)

    # --- Location Results Actions ---

    def refresh_location_results(self, location_code):
        """ Re-fetches data and updates the location results view """
        print(f"App: Refreshing Location view for {location_code}")
        if self.location_results_frame and self.location_results_frame.winfo_ismapped():
            self.navigate_to_location_results(location_code)
        else:
            print(f"App: Location view {location_code} not visible, refresh skipped.")

    def clear_all_location(self, location_code):
        """ Deletes all stock items for a given location, logs each to history, and resets DateFirstStocked """
        print(f"App: Attempting to clear all items from {location_code}")

        if not self.conn:
            messagebox.showerror("DB Error", "Database connection lost.", parent=self)
            return
        if self.current_user_id is None:
            messagebox.showerror("Auth Error", "User not identified. Cannot log history.", parent=self)
            return

        cursor = self.conn.cursor()
        items_to_log_for_delete = []
        try:
            # --- Fetch ALL items in the location BEFORE deleting for history ---
            cursor.execute("""
                SELECT StockItemID, LocationName, SKU, Batch, Quantity 
                FROM dbo.StockItems 
                WHERE LocationName = ?
            """, (location_code,))
            columns = [column[0] for column in cursor.description]
            items_to_log_for_delete = [dict(zip(columns, row)) for row in cursor.fetchall()]

            if not items_to_log_for_delete:
                messagebox.showinfo("Information", f"Location {location_code} is already empty.", parent=self)
                return

            # --- Delete from StockItems ---
            cursor.execute("DELETE FROM dbo.StockItems WHERE LocationName = ?", (location_code,))
            deleted_count = cursor.rowcount
            print(f"App: Deleted {deleted_count} items from {location_code}")

            # --- Log each deleted item to StockItemHistory ---
            now_str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
            change_type_for_clear_all = 'DELETE_LOCATION_CLEAR'
            
            sql_history_mass_delete = """
                INSERT INTO dbo.StockItemHistory 
                    (StockItemID, ChangeTimestamp, UserID, ChangeType, LocationName, SKU, Notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            for item_detail in items_to_log_for_delete:
                history_notes = f"Item SKU {item_detail['SKU']} (Batch: {item_detail['Batch'] or 'N/A'}, Qty: {item_detail['Quantity']}) deleted during clear all of {location_code}."
                history_params = (
                    item_detail['StockItemID'],
                    now_str,
                    self.current_user_id,
                    change_type_for_clear_all,
                    item_detail['LocationName'],
                    item_detail['SKU'],
                    history_notes
                )
                cursor.execute(sql_history_mass_delete, history_params)

            # Reset DateFirstStocked
            cursor.execute("UPDATE dbo.Locations SET DateFirstStocked = NULL WHERE LocationName = ?", (location_code,))

            self.conn.commit()
            messagebox.showinfo("Success", f"Successfully cleared {deleted_count} item line(s) from {location_code}.", parent=self)
            
            if self.location_results_frame and self.location_results_frame.winfo_ismapped() and self.location_results_frame.location_code == location_code:
                self.refresh_location_results(location_code)
            else:
                self.show_main_page()

        except pyodbc.Error as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to clear location {location_code}: {e}", parent=self)
        except Exception as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)

    def _check_and_clear_location_first_stocked(self, cursor, location_code):
        """ Helper: Checks if location is now empty and clears DateFirstStocked. """
        try:
            cursor.execute("SELECT COUNT(*) FROM dbo.StockItems WHERE LocationName = ?", (location_code,))
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("UPDATE dbo.Locations SET DateFirstStocked = NULL WHERE LocationName = ?", (location_code,))
                print(f"App: Location {location_code} is now empty. Reset DateFirstStocked.")
                return True
        except pyodbc.Error as e:
            print(f"App: Error checking stock count or resetting DateFirstStocked for {location_code}: {e}")
        return False

    def clear_stock_item(self, stock_item_id, location_code_context):
        """ Deletes a single stock item line, logs to history, and checks if location became empty. """
        print(f"App: Attempting to clear StockItemID: {stock_item_id} (context: Location {location_code_context})")
        
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection lost.", parent=self)
            return
        if self.current_user_id is None:
            messagebox.showerror("Auth Error", "User not identified. Cannot log history.", parent=self)
            return

        cursor = self.conn.cursor()
        item_details_for_history = None
        try:
            # --- Fetch item details BEFORE deleting for history logging ---
            cursor.execute("""
                SELECT StockItemID, LocationName, SKU, Batch, Quantity 
                FROM dbo.StockItems 
                WHERE StockItemID = ?
            """, (stock_item_id,))

            raw_row = cursor.fetchone()
            if raw_row:
                columns = [column[0] for column in cursor.description]
                item_details_for_history = dict(zip(columns, raw_row))

            if not item_details_for_history:
                messagebox.showerror("Error", "Could not find the item to delete for history logging.", parent=self)
                return

            # --- Delete the item ---
            cursor.execute("DELETE FROM dbo.StockItems WHERE StockItemID = ?", (stock_item_id,))
            deleted_count = cursor.rowcount
            
            if deleted_count > 0:
                print(f"App: Deleted StockItemID: {stock_item_id}")

                # --- Log 'DELETE' to StockItemHistory ---
                now_str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
                history_notes = f"Item SKU {item_details_for_history['SKU']} (Batch: {item_details_for_history['Batch'] or 'N/A'}, Qty: {item_details_for_history['Quantity']}) deleted from {item_details_for_history['LocationName']}."
                sql_history_delete = """
                    INSERT INTO dbo.StockItemHistory 
                        (StockItemID, ChangeTimestamp, UserID, ChangeType, LocationName, SKU, Notes)
                    VALUES (?, ?, ?, 'DELETE', ?, ?, ?)
                """
                history_params_delete = (
                    item_details_for_history['StockItemID'],
                    now_str,
                    self.current_user_id,
                    item_details_for_history['LocationName'],
                    item_details_for_history['SKU'],
                    history_notes
                )
                cursor.execute(sql_history_delete, history_params_delete)

                self._check_and_clear_location_first_stocked(cursor, location_code_context)
                self.conn.commit() 
                
                if self.location_results_frame and self.location_results_frame.winfo_ismapped() and self.location_results_frame.location_code == location_code_context:
                    self.refresh_location_results(location_code_context)
                else:
                    print(f"App: Location view {location_code_context} not visible/matching, refresh skipped after delete.")
            else:
                messagebox.showerror("Error", "Item not found or already deleted.", parent=self)
                self.conn.rollback()

        except pyodbc.Error as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to clear stock item {stock_item_id}: {e}", parent=self)
        except Exception as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)

    def clear_stock_item_and_refresh_sku_view(self, stock_item_id, sku_to_refresh):
        """ Deletes a single stock item line, logs to history, refreshes SKU view, and checks if location became empty. """
        print(f"App: Attempting to clear StockItemID: {stock_item_id} (context: SKU {sku_to_refresh})")

        if not self.conn:
            messagebox.showerror("DB Error", "Database connection lost.", parent=self)
            return
        if self.current_user_id is None:
            messagebox.showerror("Auth Error", "User not identified. Cannot log history.", parent=self)
            return

        cursor = self.conn.cursor()
        item_details_for_history = None
        try:
            # --- Fetch item details BEFORE deleting for history logging AND to get location ---
            cursor.execute("""
                SELECT StockItemID, LocationName, SKU, Batch, Quantity 
                FROM dbo.StockItems 
                WHERE StockItemID = ?
            """, (stock_item_id,))
            raw_row = cursor.fetchone()
            if raw_row:
                columns = [column[0] for column in cursor.description]
                item_details_for_history = dict(zip(columns, raw_row))

            if not item_details_for_history:
                messagebox.showerror("Error", "Could not find the item to delete.", parent=self)
                return

            location_of_deleted_item = item_details_for_history['LocationName']

            # --- Delete the item ---
            cursor.execute("DELETE FROM dbo.StockItems WHERE StockItemID = ?", (stock_item_id,))
            deleted_count = cursor.rowcount

            if deleted_count > 0:
                print(f"App: Deleted StockItemID: {stock_item_id} from Location: {location_of_deleted_item}")

                # --- Log 'DELETE' to StockItemHistory ---
                now_str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
                history_notes = f"Item SKU {item_details_for_history['SKU']} (Batch: {item_details_for_history['Batch'] or 'N/A'}, Qty: {item_details_for_history['Quantity']}) deleted from {location_of_deleted_item} via SKU view."
                sql_history_delete = """
                    INSERT INTO StockItemHistory 
                        (StockItemID, ChangeTimestamp, UserID, ChangeType, LocationName, SKU, Notes)
                    VALUES (?, ?, ?, 'DELETE', ?, ?, ?)
                """
                history_params_delete = (
                    item_details_for_history['StockItemID'],
                    now_str,
                    self.current_user_id,
                    location_of_deleted_item,
                    item_details_for_history['SKU'],
                    history_notes
                )
                cursor.execute(sql_history_delete, history_params_delete)

                if location_of_deleted_item:
                    self._check_and_clear_location_first_stocked(cursor, location_of_deleted_item)
                self.conn.commit() 

                # Refresh SKU view
                if self.sku_results_frame and self.sku_results_frame.winfo_ismapped() and self.sku_results_frame.searched_sku == sku_to_refresh:
                    self.navigate_to_sku_results(sku_to_refresh)
                else:
                    print(f"App: SKU view {sku_to_refresh} not visible/matching, refresh skipped after delete.")
            else:
                messagebox.showerror("Error", "Item not found or already deleted (race condition?).", parent=self)
                self.conn.rollback()

        except pyodbc.Error as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to clear stock item {stock_item_id}: {e}", parent=self)
        except Exception as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)

    def open_update_new_window(self, location_code, mode, stock_item_id=None, source_view='location'):
        """ Opens the window for adding/updating stock items """
        print(f"App: Opening Update/New window. Mode: {mode}, Location: {location_code}, ItemID: {stock_item_id}, Source: {source_view}")

        existing_data = None
        if mode == 'update' and stock_item_id:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM dbo.StockItems WHERE StockItemID = ?", (stock_item_id,))
                existing_data_row = cursor.fetchone()
                if existing_data_row:
                    columns = [column[0] for column in cursor.description   ]
                    existing_data = dict(zip(columns, existing_data_row))
                else:
                    messagebox.showerror("Error", f"Could not find item with ID {stock_item_id} to update.", parent=self)
                    return
            except pyodbc.Error as e:
                messagebox.showerror("Database Error", f"Failed to fetch item details for update: {e}", parent=self)
                return
            finally:
                if cursor: cursor.close()


        # Create instance
        update_new_win = UpdateNewWindow(master=self,
                                           app_instance=self,
                                           mode=mode,
                                           location_code=location_code,
                                           existing_data=existing_data,
                                           source_view=source_view)
        update_new_win.focus_set()

    def open_advanced_search_window(self):
        """ Opens the window for advanced LSI item searching. """
        print("App: Opening Advanced Item Search window.")
        

        self.adv_search_win = AdvancedSearchWindow(master=self, app_instance=self)

    def perform_advanced_lsi_search(self, search_term):
        print(f"App: Performing advanced LSI search for term: '{search_term}'")
        if not search_term: return []
        lsi_conn = None; results = []

        try:
            lsi_conn_str = (
                f'DRIVER={{{self.sql_server_driver}}};'
                f'SERVER={LSI_DB_SERVER};'
                f'DATABASE={LSI_DB_DATABASE};'
                f'Trusted_Connection=yes;'
                f'TrustServerCertificate=yes;'
            )
            lsi_conn = pyodbc.connect(lsi_conn_str, autocommit=True, timeout=5)
            cursor = lsi_conn.cursor()
            
            sql_search = """
                WITH MatchingProducts AS (
                    -- Step 1: Find all R370_RECORD_IDs that match the criteria
                    SELECT DISTINCT p.R370_RECORD_ID
                    FROM F370_PRODUCT_SCANPACK p
                    LEFT JOIN F411_PRODUCT_EAN_SUBS ean ON p.R370_RECORD_ID = ean.R411_R370_RECORD_ID
                    WHERE
                        (
                            p.R370_INHOUSE_STOCK_CODE LIKE ? OR
                            p.R370_PRODUCT_DESCRIPTION LIKE ? OR
                            p.R370_BRAND LIKE ? OR
                            ean.R411_SUBSTITUTE_EAN_CODE LIKE ?
                        )
                        AND p.R370_INHOUSE_STOCK_CODE LIKE '%-%' AND p.R370_INHOUSE_STOCK_CODE NOT LIKE 'H%'
                        AND (p.R370_PRODUCT_DESCRIPTION NOT LIKE 'DISC%' OR p.R370_PRODUCT_DESCRIPTION IS NULL)
                )

                -- Step 2: Select the primary details for these unique products
                -- We need to pick ONE representative barcode and ONE representative shelf location.
                SELECT TOP 200 -- Still limit overall results
                    p.R370_INHOUSE_STOCK_CODE AS SKU,
                    p.R370_PRODUCT_DESCRIPTION AS Description,
                    p.R370_BRAND AS Brand,
                    -- Subquery to get a primary barcode (e.g., where R411_SUBSTITUTE_QUANTITY = 1)
                    (SELECT TOP 1 ean_primary.R411_SUBSTITUTE_EAN_CODE
                     FROM F411_PRODUCT_EAN_SUBS ean_primary
                     WHERE ean_primary.R411_R370_RECORD_ID = p.R370_RECORD_ID
                       AND ean_primary.R411_SUBSTITUTE_QUANTITY = 1 -- Preference for single unit EAN
                     ORDER BY ean_primary.R411_RECORD_ID) AS PrimaryBarcode, -- Or some other ordering to pick one
                    -- Subquery to get a primary shelf location
                    (SELECT TOP 1 sloc.R890_BIN_LOCATION_CODE
                     FROM F371_PRODUCT_LOCATIONS pl
                     INNER JOIN F890_WAREHOUSE_BIN_LOCATION sloc ON pl.R371_R890_RECORD_ID = sloc.R890_RECORD_ID
                     WHERE pl.R371_R370_RECORD_ID = p.R370_RECORD_ID
                     ORDER BY pl.R371_RECORD_ID) AS ShelfLocation -- Pick one, e.g., by lowest ID
                FROM
                    F370_PRODUCT_SCANPACK p
                INNER JOIN
                    MatchingProducts mp ON p.R370_RECORD_ID = mp.R370_RECORD_ID
                ORDER BY
                    p.R370_INHOUSE_STOCK_CODE;
            """
            
            search_param = f"%{search_term}%"
            params = (search_param, search_param, search_param, search_param)
            
            cursor.execute(sql_search, params)
            
            for row in cursor.fetchall():
                 results.append({
                     'SKU': str(row.SKU).strip() if row.SKU else '',
                     'Description': str(row.Description).strip() if row.Description else '',
                     'Brand': str(row.Brand).strip() if row.Brand else '',
                     'Barcode': str(row.PrimaryBarcode).strip() if row.PrimaryBarcode else '',
                     'ShelfLocation': str(row.ShelfLocation).strip() if row.ShelfLocation else ''
                 })

            print(f"App: Found {len(results)} unique matching SKUs in LSI.")
            return results

        except pyodbc.Error as e:
            print(f"ERROR: Failed to perform advanced LSI search for '{search_term}': {e}", file=sys.stderr)
            sqlstate = e.args[0]
            error_msg = f"Could not retrieve data from iSupply_Live.\nError: {e}"
            if '08001' in str(sqlstate) or 'HYT00' in str(sqlstate):
                error_msg = f"Could not connect to LSI database server ({LSI_DB_SERVER}). Check network/server status or firewall."
            elif '28000' in str(sqlstate):
                error_msg = "LSI database login failed. Check credentials/permissions."
            messagebox.showerror("LSI Search Error", error_msg, parent=self.adv_search_win if hasattr(self, 'adv_search_win') and self.adv_search_win.winfo_exists() else self)
            return []
        except Exception as e:
            print(f"ERROR: Unexpected error during advanced LSI search for '{search_term}': {e}", file=sys.stderr)
            messagebox.showerror("LSI Search Error", f"An unexpected error occurred.\nError: {e}", parent=self.adv_search_win if hasattr(self, 'adv_search_win') and self.adv_search_win.winfo_exists() else self)
            return []
        finally:
            if lsi_conn:
                lsi_conn.close()

    def get_total_quantity_for_sku(self, sku_to_check):
        """Calculates the total on-hand quantity for a given SKU across all locations."""
        if not self.conn or not sku_to_check:
            return 0
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT SUM(Quantity) FROM dbo.StockItems WHERE SKU = ?", (sku_to_check,))
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0
        except pyodbc.Error as e:
            print(f"Error getting total quantity for SKU {sku_to_check}: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
    
    # --- Report Methods ---

    def generate_empty_locations_report_data(self):
        """
        Fetches a list of locations that have no stock items.
        Returns a list of dictionaries, each with {'LocationName': name, 'DateFirstStocked': date}.
        """
        print("App: Generating data for Empty Locations Report.")
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection not available.", parent=self)
            return []

        empty_locations_data = []
        try:
            cursor = self.conn.cursor()
            # Find locations in Locations table that are NOT in StockItems table
            sql = """
                SELECT L.LocationName, L.DateFirstStocked
                FROM dbo.Locations L
                LEFT JOIN StockItems SI ON L.LocationName = SI.LocationName
                WHERE SI.StockItemID IS NULL  -- This condition means no matching stock item
                ORDER BY L.LocationName;
            """
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for row in results:
                empty_locations_data.append(row)

            print(f"App: Found {len(empty_locations_data)} empty locations.")
            return empty_locations_data
            
        except pyodbc.Error as e:
            messagebox.showerror("DB Error", f"Error generating empty locations report: {e}", 
                                 parent=self)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            return []
        finally:
            if cursor: cursor.close()
    
    def generate_dg_summary_report_data(self):
        """
        Fetches a summary of Dangerous Goods, grouped by UN Number and then Location.
        Includes SKU, Description, and total quantity for each group.
        """
        print("App: Generating data for DG Summary Report.")
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection not available.", parent=self)
            return []

        dg_summary_data = []
        try:
            cursor = self.conn.cursor()
            sql = """
                SELECT 
                    SI.DG_UN_NUMBER,
                    SI.LocationName,
                    MIN(SI.SKU) AS SKU,
                    MIN(SI.Description) AS Description,
                    SUM(SI.Quantity) AS TotalQuantity
                FROM dbo.StockItems SI
                WHERE SI.IsDangerousGood = 1 AND SI.DG_UN_NUMBER IS NOT NULL AND SI.DG_UN_NUMBER != ''
                GROUP BY SI.DG_UN_NUMBER, SI.LocationName
                ORDER BY SI.DG_UN_NUMBER, SI.LocationName;
            """
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for row in results:
                dg_summary_data.append(row)

            print(f"App: Found {len(dg_summary_data)} DG UN/Location groupings.")
            return dg_summary_data
            
        except pyodbc.Error as e:
            messagebox.showerror("DB Error", f"Error generating DG summary report: {e}", parent=self)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            return []
        finally:
            if cursor: cursor.close()
    
    def generate_expiring_items_report_data(self, expiry_params):
        """
        Fetches stock items based on expiry parameters.
        expiry_params (dict): {'months': int, 'operator': str ('<=', '<', '>')}
        Returns a list of dicts.
        """
        
        months_lookahead = expiry_params.get('months')
        operator = expiry_params.get('operator')

        print(f"App: Generating data for Expiring Items Report. Params: Months={months_lookahead}, Operator='{operator}'")
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection not available.", parent=self)
            return None
        
        if months_lookahead is None or operator is None:
            messagebox.showerror("Parameter Error", "Invalid parameters for expiry report.", parent=self)
            return None

        expiring_items_data = []
        try:
            cursor = self.conn.cursor()
            
            today = datetime.date.today()
            
            # --- Calculate target_comparison_date based on operator and months_lookahead ---
            
            # Determine the Xth month and year from today
            future_month_offset = today.month + months_lookahead
            future_year_offset = today.year + (future_month_offset - 1) // 12
            future_month_in_year = (future_month_offset - 1) % 12 + 1
            
            # Get the last day of that future month
            _, last_day_of_future_month = calendar.monthrange(future_year_offset, future_month_in_year)
            target_comparison_date_obj = datetime.date(future_year_offset, future_month_in_year, last_day_of_future_month)
            
            target_comparison_date_str = target_comparison_date_obj.strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')

            # --- Build SQL query based on operator ---            
            sql_base = """
                SELECT 
                    LocationName, SKU, Description, Brand, Batch, ExpiryDate, Quantity
                FROM dbo.StockItems
                WHERE ExpiryDate IS NOT NULL AND ExpiryDate != ''
            """
            sql_conditions = ""
            params_sql = []

            if operator == "<=":
                sql_conditions = " AND ExpiryDate >= ? AND ExpiryDate <= ?"
                params_sql = [today_str, target_comparison_date_str]
            
            elif operator == "<": 
                if months_lookahead == 1:
                    _, last_day_current_month = calendar.monthrange(today.year, today.month)
                    effective_target_date_obj = datetime.date(today.year, today.month, last_day_current_month)
                else:
                    prev_month_offset = today.month + (months_lookahead -1)
                    prev_year_offset = today.year + (prev_month_offset -1) // 12
                    prev_month_in_year = (prev_month_offset -1) % 12 + 1
                    _, last_day_of_prev_month = calendar.monthrange(prev_year_offset, prev_month_in_year)
                    effective_target_date_obj = datetime.date(prev_year_offset, prev_month_in_year, last_day_of_prev_month)

                effective_target_date_str = effective_target_date_obj.strftime('%Y-%m-%d')
                sql_conditions = " AND ExpiryDate >= ? AND ExpiryDate <= ?"
                params_sql = [today_str, effective_target_date_str]

            elif operator == ">":
                sql_conditions = " AND ExpiryDate > ?"
                params_sql = [target_comparison_date_str]
            
            else:
                messagebox.showerror("Logic Error", "Unknown operator for expiry report.", parent=self)
                return None

            final_sql = sql_base + sql_conditions + " ORDER BY ExpiryDate, LocationName, SKU;"
            
            cursor.execute(final_sql, tuple(params_sql))
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for row in results:
                expiring_items_data.append(row)

            print(f"App: Found {len(expiring_items_data)} items matching expiry criteria.")
            return expiring_items_data
            
        except pyodbc.Error as e:
            messagebox.showerror("DB Error", f"Error generating expiring items report: {e}", parent=self)
            return None
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred generating expiry report: {e}", parent=self)
            return None
        finally:
            if cursor: cursor.close()
        
    def generate_stock_by_brand_report_data(self):
        """
        Fetches data summarizing stock by brand.
        Returns a list of dicts: 
        {'Brand': brand, 'LocationCount': count, 'TotalQuantity': sum_qty}
        """
        print("App: Generating data for Stock by Brand Report.")
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection not available.", parent=self)
            return []

        stock_by_brand_data = []
        try:
            cursor = self.conn.cursor()
            sql = """
                SELECT 
                    Brand,
                    COUNT(DISTINCT LocationName) AS LocationCount,
                    SUM(Quantity) AS TotalQuantity
                FROM dbo.StockItems
                WHERE Brand IS NOT NULL AND Brand != '' -- Ignore items with no brand
                GROUP BY Brand
                ORDER BY Brand;
            """
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for row in results:
                stock_by_brand_data.append(row)

            print(f"App: Found {len(stock_by_brand_data)} brands with stock.")
            return stock_by_brand_data
            
        except pyodbc.Error as e:
            messagebox.showerror("DB Error", f"Error generating stock by brand report: {e}", parent=self)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            return []
        finally:
            if cursor: cursor.close()

    def generate_audit_history_report_data(self, filters=None, limit=200):
        """
        Fetches records from StockItemHistory, joining with Users to get UserName.
        Applies filters if provided.
        Returns a list of dicts.
        """
        print(f"App: Generating data for Audit History Report. Filters: {filters}, Limit: {limit}")

        if not self.conn:
            messagebox.showerror("DB Error", "Database connection not available.", parent=self)
            return None

        audit_history_data = []
        try:
            cursor = self.conn.cursor()
            
            sql_base = """
                SELECT 
                    H.HistoryID,
                    H.ChangeTimestamp,
                    U.UserName,
                    H.ChangeType,
                    H.LocationName,
                    H.SKU,
                    H.FieldName,
                    H.OldValue,
                    H.NewValue,
                    H.Notes AS HistoryEventNotes 
                FROM dbo.StockItemHistory H
                LEFT JOIN Users U ON H.UserID = U.UserID 
            """
            # --- Dynamically build WHERE clause based on filters ---
            where_clauses = []
            params_sql = []

            if filters:
                if filters.get('date_from'):
                    where_clauses.append("CAST(H.ChangeTimestamp AS DATE) >= ?")
                    params_sql.append(filters['date_from'])
                
                if filters.get('date_to'):
                    where_clauses.append("CAST(H.ChangeTimestamp AS DATE) >= ?")
                    params_sql.append(filters['date_to'])
                
                if filters.get('user_name'):
                    where_clauses.append("U.UserName = ?")
                    params_sql.append(filters['user_name'])
                
                if filters.get('action_type'):
                    where_clauses.append("H.ChangeType = ?")
                    params_sql.append(filters['action_type'])
                
                if filters.get('sku'):
                    where_clauses.append("H.SKU LIKE ?")
                    params_sql.append(f"%{filters['sku']}%")
                
                if filters.get('location_name'):
                    where_clauses.append("H.LocationName LIKE ?")
                    params_sql.append(f"%{filters['location_name']}%")

            final_sql = sql_base
            if where_clauses:
                final_sql += " WHERE " + " AND ".join(where_clauses)
            
            final_sql += " ORDER BY H.ChangeTimestamp DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY"
            params_sql.append(limit) 
            
            cursor.execute(final_sql, tuple(params_sql))
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for row in results:
                audit_history_data.append(row)

            print(f"App: Fetched {len(audit_history_data)} audit history entries.")
            return audit_history_data
            
        except pyodbc.Error as e:
            messagebox.showerror("DB Error", f"Error generating audit history report: {e}", parent=self)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            return []
        finally:
            if cursor: cursor.close()
        
    def generate_batch_summary_report_data(self, search_type, search_term):
        """
        Fetches a summary of batches for a given SKU or a summary of SKUs for a given Batch.
        Includes total quantity and a comma-separated list of locations.
        search_type (str): 'sku' or 'batch'
        search_term (str): The SKU or Batch number to search for.
        Returns a list of dicts, or None on error.
        """
        print(f"App: Generating Batch Summary Report. Type: {search_type}, Term: '{search_term}'")
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection not available.", parent=self)
            return None
        if not search_type or not search_term:
            messagebox.showerror("Input Error", "Search type or term missing for batch summary.", parent=self)
            return None

        report_data = []
        try:
            cursor = self.conn.cursor()
            
            base_select = """
                SELECT 
                    SI.SKU, 
                    SI.Description, 
                    SI.Brand, 
                    SI.Batch, 
                    SUM(SI.Quantity) AS TotalQuantity, 
                    STRING_AGG(CONVERT(NVARCHAR(MAX), SI.LocationName), ', ') AS Locations,
                    SI.IsAdhoc
            """

            from_and_where = ""
            params = []

            if search_type == 'sku':
                from_and_where = """
                    FROM dbo.StockItems SI
                    WHERE SI.SKU = ? AND SI.Batch IS NOT NULL AND SI.Batch != ''
                    GROUP BY SI.SKU, SI.Description, SI.Brand, SI.Batch, SI.IsAdhoc 
                    ORDER BY SI.Batch, SI.SKU 
                """
                params.append(search_term)
            elif search_type == 'batch':
                from_and_where = """
                    FROM dbo.StockItems SI
                    WHERE SI.Batch = ?
                    GROUP BY SI.SKU, SI.Description, SI.Brand, SI.Batch, SI.IsAdhoc
                    ORDER BY SI.SKU, SI.Batch
                """
                params.append(search_term)
            else:
                messagebox.showerror("Logic Error", f"Unknown search type: {search_type}", parent=self)
                return None

            final_sql = base_select + from_and_where
            
            cursor.execute(final_sql, tuple(params))
            columns = [column[0] for column in cursor.description]
            raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            for row_dict_raw in raw_results:
                item_data = dict(row_dict_raw) 
                if item_data.get('IsAdhoc') == 1 and \
                   (not item_data.get('Description') or not item_data.get('Brand')):
                    
                    lsi_details = self.fetch_lsi_data(item_data['SKU'])
                    if lsi_details:
                        if not item_data.get('Description') and lsi_details.get('Description'):
                            item_data['Description'] = lsi_details['Description']
                        if not item_data.get('Brand') and lsi_details.get('Brand'):
                            item_data['Brand'] = lsi_details['Brand']
                
                report_data.append(item_data)

            print(f"App: Found {len(report_data)} summary lines for {search_type} '{search_term}'.")
            return report_data
            
        except pyodbc.Error as e:
            messagebox.showerror("DB Error", f"Error generating batch summary report: {e}", parent=self)
            return None
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            return None
        finally:
            if cursor: cursor.close() 
    
    def add_sku_to_replen_list(self, sku_to_add):
        """Adds a SKU to the replenishment list (ReplenishmentListItems table) 
        if not already pending.
        Returns True if successfully added or already pending, False on error.
        """
        if not sku_to_add:
            messagebox.showwarning("Input Error", "No SKU provided to add to replenishment list.", 
                                parent=self.replen_builder_frame if hasattr(self, 'replen_builder_frame') and self.replen_builder_frame.winfo_exists() else self)
            return False
        if self.current_user_id is None:
            messagebox.showerror("Auth Error", "User not identified. Cannot add to list.", 
                                parent=self.replen_builder_frame if hasattr(self, 'replen_builder_frame') and self.replen_builder_frame.winfo_exists() else self)
            return False
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection not available.", 
                                parent=self.replen_builder_frame if hasattr(self, 'replen_builder_frame') and self.replen_builder_frame.winfo_exists() else self)
            return False

        sku_to_add = sku_to_add.strip().upper()
        now_str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT ReplenItemID FROM ReplenishmentListItems 
                WHERE SKU = ? AND Status = 'Pending'
            """, (sku_to_add,))
            if cursor.fetchone():
                print(f"App: SKU {sku_to_add} is already on the pending replenishment list.")
                return True 
            
            sql_insert = """
                INSERT INTO ReplenishmentListItems (SKU, AddedByUserID, DateAdded, Status)
                VALUES (?, ?, ?, 'Pending')
            """
            cursor.execute(sql_insert, (sku_to_add, self.current_user_id, now_str))
            self.conn.commit()
            print(f"App: SKU {sku_to_add} added to ReplenishmentListItems table.")
            return True
        except pyodbc.Error as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to add SKU {sku_to_add} to DB list: {e}", 
                                parent=self.replen_builder_frame if hasattr(self, 'replen_builder_frame') and self.replen_builder_frame.winfo_exists() else self)
            return False
        except Exception as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", 
                                parent=self.replen_builder_frame if hasattr(self, 'replen_builder_frame') and self.replen_builder_frame.winfo_exists() else self)
            return False
        finally:
            if cursor: cursor.close()

    def generate_picking_list_data(self):
        """
        Generates the raw data for the picking list.
        Fetches all 'Pending' SKUs from ReplenishmentListItems,
        then finds all their current stock locations and details from StockItems.
        Returns a list of dictionaries, where each dict is a pickable line item.
        """
        print("App: Generating data for Picking List.")
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection not available.", parent=self)
            return None

        picking_list_raw_data = []
        try:
            cursor = self.conn.cursor()

            # Step 1: Get all unique SKUs from ReplenishmentListItems with 'Pending' status
            cursor.execute("""
                SELECT DISTINCT SKU, ReplenItemID 
                FROM dbo.ReplenishmentListItems
                WHERE Status = 'Pending'
            """)
            pending_replen_items = cursor.fetchall() # List of Row objects (SKU, ReplenItemID)

            if not pending_replen_items:
                print("App: No items currently pending replenishment.")
                return []

            print(f"App: Found {len(pending_replen_items)} SKUs pending replenishment. Fetching stock details...")

            # Step 2: For each pending SKU, get all its stock item details
            sql_stock_details = """
                SELECT 
                    SI.StockItemID, 
                    SI.SKU, 
                    SI.LocationName, 
                    SI.Quantity, 
                    SI.Batch, 
                    SI.ExpiryDate,
                    SI.UnitsPerCarton, -- Needed for display and potentially sorting
                    SI.Brand,          -- For display
                    SI.Description,    -- For display
                    SI.IsFirst,
                    L.DateFirstStocked -- For sorting by location priority later
                FROM StockItems SI
                JOIN Locations L ON SI.LocationName = L.LocationName
                WHERE SI.SKU = ? AND SI.Quantity > 0 AND SI.IsQuarantined = 0 -- Only pick from locations with stock, and not anything that is Quarantined.
            """
            
            sku_to_replen_item_id_map = {item.SKU: item.ReplenItemID for item in pending_replen_items}

            for pending_item_row in pending_replen_items:
                sku_to_fetch = pending_item_row.SKU
                original_replen_item_id = pending_item_row.ReplenItemID

                cursor.execute(sql_stock_details, (sku_to_fetch,))
                columns = [column[0] for column in cursor.description]
                stock_instances = [dict(zip(columns, row)) for row in cursor.fetchall()]

                if not stock_instances:
                    print(f"Warning: SKU {sku_to_fetch} is pending replenishment but has no current stock (non-quarantined) > 0.")
                    lsi_data_for_sku = self.fetch_lsi_data(sku_to_fetch)
                    picking_list_raw_data.append({
                        'SKU': sku_to_fetch,
                        'Description': lsi_data_for_sku.get('Description', 'N/A') if lsi_data_for_sku else 'LSI Data N/A',
                        'Brand': lsi_data_for_sku.get('Brand', 'N/A') if lsi_data_for_sku else 'LSI Data N/A',
                        'PickLocation': 'N/A - No Stock',
                        'QtyAtLocation': 0,
                        'Batch': 'N/A',
                        'ExpiryDate': None,
                        'UnitsPerCarton': lsi_data_for_sku.get('UnitsPerCarton') if lsi_data_for_sku else None,
                        'DateFirstStockedAtLocation': None,
                        'StockItemID_to_pick_from': None,
                        'OriginalReplenItemID': original_replen_item_id
                    })
                    continue

                for stock_row in stock_instances:
                    item_dict = dict(stock_row)
                    pickable_item = {
                        'SKU': item_dict['SKU'],
                        'Description': item_dict.get('Description', 'N/A'), 
                        'Brand': item_dict.get('Brand', 'N/A'),
                        'PickLocation': item_dict['LocationName'],
                        'QtyAtLocation': item_dict['Quantity'],
                        'Batch': item_dict.get('Batch'),
                        'ExpiryDate': item_dict.get('ExpiryDate'),
                        'UnitsPerCarton': item_dict.get('UnitsPerCarton'),
                        'IsFirst' : item_dict.get('IsFirst',0),
                        'DateFirstStockedAtLocation': item_dict.get('DateFirstStocked'),
                        'StockItemID_to_pick_from': item_dict['StockItemID'],
                        'OriginalReplenItemID': original_replen_item_id
                    }
                    
                    if not pickable_item['Description'] or not pickable_item['Brand']:
                        lsi_data_for_sku = self.fetch_lsi_data(pickable_item['SKU'])
                        if lsi_data_for_sku:
                            if not pickable_item['Description']:
                                pickable_item['Description'] = lsi_data_for_sku.get('Description', 'N/A')
                            if not pickable_item['Brand']:
                                pickable_item['Brand'] = lsi_data_for_sku.get('Brand', 'N/A')
                            if pickable_item.get('UnitsPerCarton') is None:
                                pickable_item['UnitsPerCarton'] = lsi_data_for_sku.get('UnitsPerCarton')


                    picking_list_raw_data.append(pickable_item)

            print(f"App: Generated {len(picking_list_raw_data)} raw pickable lines for the list.")
            return picking_list_raw_data
            
        except pyodbc.Error as e:
            messagebox.showerror("DB Error", f"Error generating picking list data: {e}", parent=self)
            return None
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            return None
        finally:
            if cursor: cursor.close()

    def get_aisle_priority_group(self, location_name):
        """Determines the priority group of a location based on its aisle letter."""
        if not location_name or not isinstance(location_name, str) or len(location_name) == 0:
            return 2 
        
        aisle_letter = location_name[0].upper()
        high_priority_aisles = {'A', 'F', 'G', 'H', 'I', 'J'}
        
        if aisle_letter in high_priority_aisles:
            return 0 # Highest priority group
        else: # B, C, D, E or anything else
            return 1 # Lower priority group

    def sort_picking_list_data(self, raw_picking_data):
        """
        Sorts the raw picking list data according to defined priority rules:
        1. IsFirst (Use First items are highest priority)
        2. Aisle Type (A, F-J first, then B-E)
        3. Earliest Expiry Date (ascending, NULLs/blanks last)
        4. Quantity at Location (ascending - lowest first)
        5. Location Name (alphanumeric A-Z, 0-9)
        6. SKU (alphanumeric A-Z, 0-9) - as a final tie-breaker if needed
        """
        if not raw_picking_data:
            return []

        print(f"App: Sorting {len(raw_picking_data)} picking list items with IsFirst and expiry priority.")

        # --- Define a very large date to sort NULL/empty expiries last ---
        try:
            NULL_EXPIRY_SORT_VALUE = datetime.date.max 
        except AttributeError:
            NULL_EXPIRY_SORT_VALUE = datetime.date(9999, 12, 31)


        def sort_key(item):
            location_name = item.get('PickLocation', '')

            is_first_status = item.get('IsFirst', 0)
            priority_is_first = 0 if is_first_status == 1 else 1
            
            # Handle "N/A - No Stock" items
            if location_name == 'N/A - No Stock':
                aisle_priority_group = 2 
                expiry_date_for_sort = NULL_EXPIRY_SORT_VALUE 
                quantity = float('inf') 
            else:
                aisle_priority_group = self.get_aisle_priority_group(location_name)
                quantity = item.get('QtyAtLocation', float('inf'))
                
                # --- Process Expiry Date for Sorting ---
                raw_expiry = item.get('ExpiryDate') 
                if raw_expiry:
                    try:
                        expiry_date_for_sort = datetime.datetime.strptime(raw_expiry, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        expiry_date_for_sort = NULL_EXPIRY_SORT_VALUE
                else:
                    expiry_date_for_sort = NULL_EXPIRY_SORT_VALUE
            
            sku = item.get('SKU', '').lower()

            return (
                priority_is_first,         # Sort by IsFirst first
                aisle_priority_group,      # 0 for high priority, 1 for low, 2 for N/A
                expiry_date_for_sort,      # Sort by actual date objects, NULLs last
                quantity,                  # Then by quantity ascending
                location_name,             # Then by location name ascending
                sku                        # Finally by SKU ascending
            )

        try:
            sorted_list = sorted(raw_picking_data, key=sort_key)
            print("App: Picking list sorted with expiry priority.")
            return sorted_list
        except Exception as e:
            print(f"Error during picking list sort (expiry focus): {e}")
            messagebox.showerror("Sort Error", f"Could not sort picking list: {e}", parent=self)
            return raw_picking_data

    def record_replenishment_pick(self, stock_item_id_to_update, original_replen_item_id, picked_quantity, original_location, replen_list_sku):
        """
        Records a replenishment pick:
        - Decreases quantity in StockItems (or deletes if qty becomes 0).
        - Updates status of the specific ReplenishmentListItems entry to 'Replenished'.
        - Logs to StockItemHistory.
        Returns True on success, False on failure.
        """
        print(f"App: Recording pick of {picked_quantity} for StockItemID {stock_item_id_to_update} (SKU {replen_list_sku} from {original_location})")

        if not self.conn:
            messagebox.showerror("DB Error", "Database connection lost.", parent=self)
            return False
        if self.current_user_id is None:
            messagebox.showerror("Auth Error", "User not identified.", parent=self)
            return False
        
        now_str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
        user_name = self.current_username or "Unknown"

        cursor = self.conn.cursor()
        try:
            # --- Step 1: Fetch current quantity from StockItems ---
            cursor.execute("SELECT Quantity, Batch FROM dbo.StockItems WHERE StockItemID = ?", (stock_item_id_to_update,))
            stock_item_data = cursor.fetchone()
            if not stock_item_data:
                messagebox.showerror("Error", f"Stock item ID {stock_item_id_to_update} not found for update.", parent=self)
                return False
            
            current_quantity_at_loc = stock_item_data.Quantity
            batch_val = stock_item_data.Batch

            if picked_quantity > current_quantity_at_loc:
                messagebox.showerror("Error", f"Cannot pick {picked_quantity}. Only {current_quantity_at_loc} available at {original_location} for SKU {replen_list_sku}.", parent=self)
                return False

            new_quantity_at_loc = current_quantity_at_loc - picked_quantity

            # --- Step 2: Update or Delete StockItems record ---
            history_stock_change_note = ""
            if new_quantity_at_loc == 0:
                cursor.execute("DELETE FROM dbo.StockItems WHERE StockItemID = ?", (stock_item_id_to_update,))
                print(f"App: Deleted StockItemID {stock_item_id_to_update} as quantity reached 0.")
                history_stock_change_note = f"Picked {picked_quantity} (all remaining). Line cleared from {original_location}."
                self._check_and_clear_location_first_stocked(cursor, original_location)
            else:
                cursor.execute("""
                    UPDATE StockItems 
                    SET Quantity = ?, LastUpdatedBy = ?, LastUpdatedDate = ?
                    WHERE StockItemID = ?
                """, (new_quantity_at_loc, user_name, now_str, stock_item_id_to_update))
                print(f"App: Updated StockItemID {stock_item_id_to_update}, new quantity {new_quantity_at_loc}.")
                history_stock_change_note = f"Picked {picked_quantity} from {original_location}. New qty: {new_quantity_at_loc}."

            # --- Step 3: Log this specific pick to StockItemHistory ---
            sql_history_pick = """
                INSERT INTO StockItemHistory 
                    (StockItemID, ChangeTimestamp, UserID, ChangeType, LocationName, SKU, 
                    FieldName, OldValue, NewValue, Notes)
                VALUES (?, ?, ?, 'REPLEN_PICK', ?, ?, 'Quantity', ?, ?, ?)
            """
            history_params_pick = (
                stock_item_id_to_update, now_str, self.current_user_id, original_location, replen_list_sku,
                str(current_quantity_at_loc), str(new_quantity_at_loc), history_stock_change_note
            )
            cursor.execute(sql_history_pick, history_params_pick)

            # --- Step 4: Update ReplenishmentListItems status ---
            if original_replen_item_id:
                cursor.execute("""
                    UPDATE ReplenishmentListItems 
                    SET Status = 'Replenished', DateReplenished = ?, ReplenishedByUserID = ?
                    WHERE ReplenItemID = ? AND Status = 'Pending' 
                """, (now_str, self.current_user_id, original_replen_item_id))
                
                if cursor.rowcount > 0:
                    print(f"App: Marked ReplenItemID {original_replen_item_id} (SKU {replen_list_sku}) as 'Replenished'.")
                else:
                    print(f"Warning: Did not update ReplenItemID {original_replen_item_id}. It might not have been 'Pending' or ID was incorrect.")
            else:
                print(f"Warning: No OriginalReplenItemID provided to mark as replenished for SKU {replen_list_sku}.")

            self.conn.commit()
            return True

        except pyodbc.Error as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to record replenishment pick: {e}", parent=self)
            return False
        except Exception as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            return False
        finally:
            if cursor: cursor.close()

    def cancel_pending_replen_items(self, replen_item_ids_to_cancel):
        """
        Updates the status of specified ReplenishmentListItems to 'Cancelled'.
        Args:
            replen_item_ids_to_cancel (list): A list of ReplenItemID integers.
        Returns:
            True if successful (or no items to cancel), False on database error.
        """
        if not replen_item_ids_to_cancel:
            return True

        print(f"App: Cancelling {len(replen_item_ids_to_cancel)} pending replenishment items.")
        if not self.conn:
            messagebox.showerror("DB Error", "Database connection lost.", parent=self)
            return False
        if self.current_user_id is None:
            messagebox.showerror("Auth Error", "User not identified for cancellation.", parent=self)
            return False

        now_str = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')

        cursor = self.conn.cursor()
        try:
            placeholders = ', '.join(['?'] * len(replen_item_ids_to_cancel))
            sql_cancel = f"""
                UPDATE ReplenishmentListItems
                SET Status = 'Cancelled', 
                    DateReplenished = ?,  -- Using DateReplenished to store cancellation time
                    ReplenishedByUserID = ? -- Log who effectively cancelled it
                WHERE ReplenItemID IN ({placeholders}) AND Status = 'Pending'
            """
            params = [now_str, self.current_user_id] + replen_item_ids_to_cancel
            
            cursor.execute(sql_cancel, tuple(params))
            updated_count = cursor.rowcount
            self.conn.commit()
            print(f"App: Marked {updated_count} replenishment items as 'Cancelled'.")
            
            return True
        except pyodbc.Error as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to cancel replenishment items: {e}", parent=self)
            return False
        except Exception as e:
            if self.conn: self.conn.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
            return False
        finally:
            if cursor: cursor.close()

# --- Run the App ---
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
