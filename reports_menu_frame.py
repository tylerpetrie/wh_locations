import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from .report_display_window import ReportDisplayWindow
from .expiry_options_window import ExpiryReportOptionsWindow
from .audit_history_options_window import AuditHistoryOptionsWindow
from .batch_summary_options import BatchSummaryOptionsWindow
import datetime
import calendar

class ReportsMenuFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance 

        self.grid_rowconfigure(0, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=self.app.get_scaled_padding(30), pady=self.app.get_scaled_padding(30))
        
        # --- Configure content_frame for title + 2 columns for buttons ---
        content_frame.grid_rowconfigure(0, weight=0) # Title row
        content_frame.grid_rowconfigure(1, weight=1) # Button area row (allow expansion if needed)
        content_frame.grid_rowconfigure(2, weight=0) # Back button row
        content_frame.grid_columnconfigure(0, weight=1) # Left column of buttons
        content_frame.grid_columnconfigure(1, weight=1) # Right column of buttons


        # Define button properties
        button_width = self.app.get_scaled_size(230)
        button_height = self.app.get_scaled_size(45)
        bold_button_font = self.app.get_font(size=14, weight="bold")
        button_font = self.app.get_font(size=14)
        button_pady = (7, 7)
        col_padx = (5, 15)
        standard_fg, standard_hover, standard_text, standard_dtext = self.app.get_button_color_config("standard")
        destructive_fg, destructive_hover, destructive_text, destructive_dtext = self.app.get_button_color_config("destructive")

        # --- Title (Row 0, spanning 2 columns) ---
        ctk.CTkLabel(content_frame, text="Select a Report", font=self.app.get_font(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=self.app.get_scaled_padding((0, 20)))

        # --- Left Column of Reports (Column 0, starting at Row 1) ---
        left_col_row = 1 
        # Empty Locations
        self.empty_locations_button = ctk.CTkButton(
            content_frame, text="Empty Locations",
            command=self.show_empty_locations_report,
            fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext,
            width=button_width, height=button_height, font=button_font
        )
        self.empty_locations_button.grid(row=left_col_row, column=0, padx=self.app.get_scaled_padding(col_padx), pady=self.app.get_scaled_padding(button_pady), sticky="ew")
        left_col_row += 1

        # Dangerous Goods
        self.dg_report_button = ctk.CTkButton(
            content_frame, text="Dangerous Goods",
            command=self.show_dg_summary_report,
            fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext,
            width=button_width, height=button_height, font=button_font
        )
        self.dg_report_button.grid(row=left_col_row, column=0, padx=self.app.get_scaled_padding(col_padx), pady=self.app.get_scaled_padding(button_pady), sticky="ew")
        left_col_row += 1

        # Stock by Brand
        self.brand_report_button = ctk.CTkButton(
            content_frame, text="Stock by Brand",
            command=self.show_stock_by_brand_report,
            fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext,
            width=button_width, height=button_height, font=button_font
        )
        self.brand_report_button.grid(row=left_col_row, column=0, padx=self.app.get_scaled_padding(col_padx), pady=self.app.get_scaled_padding(button_pady), sticky="ew")
        left_col_row += 1

        # --- Right Column of Reports (Column 1, starting at Row 1) ---
        right_col_row = 1
        # Audit History Report
        self.audit_history_button = ctk.CTkButton(
            content_frame, text="Audit History",
            command=self.show_audit_history_options,
            fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext,
            width=button_width, height=button_height, font=button_font
        )
        self.audit_history_button.grid(row=right_col_row, column=1, padx=self.app.get_scaled_padding(col_padx), pady=self.app.get_scaled_padding(button_pady), sticky="ew")
        right_col_row += 1

        # Expiry Dates Report
        self.expiry_dates_button = ctk.CTkButton(
            content_frame, text="Expiry Dates",
            command=self.show_expiring_items_report,
            fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext,
            width=button_width, height=button_height, font=button_font
        )
        self.expiry_dates_button.grid(row=right_col_row, column=1, padx=self.app.get_scaled_padding(col_padx), pady=self.app.get_scaled_padding(button_pady), sticky="ew")
        right_col_row += 1
        
        # --- Batch Summary Report Button ---
        self.batch_summary_button = ctk.CTkButton(
            content_frame, text="Batch Summary",
            command=self.show_batch_summary_options,
            fg_color=standard_fg, hover_color=standard_hover, text_color=standard_text, text_color_disabled=standard_dtext,
            width=button_width, height=button_height, font=button_font
        )
        self.batch_summary_button.grid(row=right_col_row, column=1, padx=self.app.get_scaled_padding(col_padx), pady=self.app.get_scaled_padding(button_pady), sticky="ew")
        right_col_row += 1


        # --- Back Button (Row 2, spanning 2 columns) ---
        max_row_for_buttons = max(left_col_row, right_col_row)
        back_button_row = max_row_for_buttons 

        back_button = ctk.CTkButton(content_frame, text="Back to Main Menu", command=self.go_back_to_main,
                                    height=button_height, width=button_width, font=button_font,
                                    fg_color=destructive_fg, hover_color=destructive_hover, text_color=destructive_text, text_color_disabled=destructive_dtext, 
                                    border_color="black", border_width=self.app.get_scaled_size(1))
        back_button.grid(row=back_button_row, column=0, columnspan=2, padx=self.app.get_scaled_padding(10), pady=self.app.get_scaled_padding((25,0)))

        self.after(100, lambda: self.focus_set())


    def show_empty_locations_report(self):
        print("ReportsMenu: Requesting Empty Locations Report Data")
        report_data = self.app.generate_empty_locations_report_data() 
        
        if report_data is None: 
            return 
        if not report_data:
            messagebox.showinfo("Empty Locations", "No empty locations found.", parent=self)
            return

        columns = [
            {'id': 'LocationName', 'text': 'Location', 'width': 150, 'anchor': 'w'},
            {'id': 'DateFirstStocked', 'text': 'Original First Stocked', 'width': 200, 'anchor': 'w', 'stretch': tk.YES}
        ]
        
        formatted_report_data = []
        for row in report_data:
            formatted_row = row.copy()
            raw_date = formatted_row.get('DateFirstStocked')
            if raw_date:
                try:
                    dt_obj = datetime.datetime.fromisoformat(raw_date)
                    formatted_row['DateFirstStocked'] = dt_obj.strftime('%d/%m/%Y %H:%M')
                except ValueError: 
                    formatted_row['DateFirstStocked'] = raw_date
            else:
                 formatted_row['DateFirstStocked'] = "Never Stocked / Cleared"
            formatted_report_data.append(formatted_row)

        ReportDisplayWindow(
            master=self.app, 
            title="Empty Locations Report",
            columns_config=columns,
            data_rows=formatted_report_data,
            app_instance=self.app 
        )

    # --- Audit History Report ---
    def show_audit_history_options(self):
        print("ReportsMenu: Opening Audit History Filter Options")
        AuditHistoryOptionsWindow(
            master=self.app, 
            app_instance=self.app, 
            callback=self._execute_audit_history_report_with_filters
        )

    def _execute_audit_history_report_with_filters(self, filters):
        print(f"ReportsMenu: Requesting Audit History Report Data with filters: {filters}")
        report_data = self.app.generate_audit_history_report_data(filters=filters) 
        
        if report_data is None: return 
        if not report_data:
            messagebox.showinfo("Audit History", "No audit history found matching the specified filters.", parent=self)
            return

        columns = [
            {'id': 'ChangeTimestamp', 'text': 'Timestamp', 'width': 160, 'anchor': 'w'},
            {'id': 'UserName', 'text': 'User', 'width': 100, 'anchor': 'w'},
            {'id': 'ChangeType', 'text': 'Action', 'width': 100, 'anchor': 'w'},
            {'id': 'LocationName', 'text': 'Location', 'width': 90, 'anchor': 'w'},
            {'id': 'SKU', 'text': 'SKU', 'width': 100, 'anchor': 'w'},
            {'id': 'FieldName', 'text': 'Field', 'width': 100, 'anchor': 'w'},
            {'id': 'OldValue', 'text': 'Old Value', 'width': 150, 'anchor': 'w'}, 
            {'id': 'NewValue', 'text': 'New Value', 'width': 150, 'anchor': 'w'}, 
            {'id': 'HistoryEventNotes', 'text': 'Event Notes', 'width': 250, 'stretch': tk.YES}
        ]
        
        formatted_report_data = []
        for row_dict in report_data:
            new_row = row_dict.copy()
            ts_from_db = new_row.get('ChangeTimestamp')

            if isinstance(ts_from_db, datetime.datetime):
                new_row['ChangeTimestamp'] = ts_from_db.strftime('%d/%m/%Y %H:%M:%S')
            elif isinstance(ts_from_db, str):
                try:
                    dt_obj = datetime.datetime.fromisoformat(ts_from_db) 
                    new_row['ChangeTimestamp'] = dt_obj.strftime('%d/%m/%Y %H:%M:%S')
                except ValueError:
                    pass 
            formatted_report_data.append(new_row)

        ReportDisplayWindow(
            master=self.app, 
            title="Filtered Audit History Log",
            columns_config=columns,
            data_rows=formatted_report_data, 
            app_instance=self.app
        )

    # --- Expiry Report ---
    def show_expiring_items_report(self):
        print("ReportsMenu: Opening Expiry Report Options")
        ExpiryReportOptionsWindow(master=self.app, callback=self._execute_expiring_items_report)

    def _execute_expiring_items_report(self, report_params): 
        months_val = report_params.get('months')
        operator_val = report_params.get('operator')
        print(f"ReportsMenu: Requesting Expiring Items Report Data. Params: {report_params}")
        report_data = self.app.generate_expiring_items_report_data(expiry_params=report_params)
        
        if report_data is None: return 
        if not report_data:
            if operator_val == "<=" or operator_val == "<":
                message_verb = "within the next" if operator_val == "<=" else "in less than"
                messagebox.showinfo("Expiring Items", f"No items found expiring {message_verb} {months_val} months.", parent=self)
            elif operator_val == ">":
                messagebox.showinfo("Expiring Items", f"No items found expiring in more than {months_val} months.", parent=self)
            else: 
                messagebox.showinfo("Expiring Items", "No items found for the selected criteria.", parent=self)
            return

        columns = [
            {'id': 'LocationName', 'text': 'Location', 'width': 80},
            {'id': 'SKU', 'text': 'SKU', 'width': 100},
            {'id': 'Description', 'text': 'Description', 'width': 250, 'stretch': tk.YES},
            {'id': 'Brand', 'text': 'Brand', 'width': 100},
            {'id': 'Batch', 'text': 'Batch', 'width': 100},
            {'id': 'ExpiryDate', 'text': 'Expiry (MM/YYYY)', 'width': 100, 'anchor': 'center'},
            {'id': 'Quantity', 'text': 'Qty', 'width': 70, 'anchor': 'e'}
        ]
        
        formatted_report_data = []
        for row_dict in report_data:
            new_row = row_dict.copy()
            raw_expiry_date = new_row.get('ExpiryDate')
            if isinstance(raw_expiry_date, datetime.date):
                new_row['ExpiryDate'] = raw_expiry_date.strftime('%m/%Y')
            elif isinstance(raw_expiry_date, str):
                try:
                    date_obj = datetime.datetime.strptime(raw_expiry_date, '%Y-%m-%d').date()
                    new_row['ExpiryDate'] = date_obj.strftime('%m/%Y')
                except ValueError: 
                    new_row['ExpiryDate'] = raw_expiry_date
            
            formatted_report_data.append(new_row)
        
        title_str = "Expiring Items Report"
        if operator_val == "<=" or operator_val == "<":
            title_verb = "Within Next" if operator_val == "<=" else "Less Than"
            title_str = f"Items Expiring {title_verb} {months_val} Months"
        elif operator_val == ">":
            title_str = f"Items Expiring More Than {months_val} Months"
            
        ReportDisplayWindow(
            master=self.app, 
            title=title_str, 
            columns_config=columns,
            data_rows=formatted_report_data,
            app_instance=self.app
        )

    # --- DGs Report ---
    def show_dg_summary_report(self):
        print("ReportsMenu: Requesting DG Summary Report Data")
        report_data = self.app.generate_dg_summary_report_data()
        
        if report_data is None: return
        if not report_data:
            messagebox.showinfo("DG Summary", "No Dangerous Goods found with UN numbers.", parent=self)
            return

        columns = [
            {'id': 'DG_UN_NUMBER', 'text': 'UN Number', 'width': 100, 'anchor': 'w'},
            {'id': 'LocationName', 'text': 'Location', 'width': 100, 'anchor': 'w'},
            {'id': 'SKU', 'text': 'SKU Code', 'width': 120, 'anchor': 'w'},
            {'id': 'Description', 'text': 'Description', 'width': 250, 'stretch': tk.YES},
            {'id': 'TotalQuantity', 'text': 'Total Qty', 'width': 100, 'anchor': 'e'}
        ]
        
        ReportDisplayWindow(
            master=self.app, 
            title="Dangerous Goods Summary",
            columns_config=columns,
            data_rows=report_data,
            app_instance=self.app
        )

    # --- Brands Report ---
    def show_stock_by_brand_report(self):
        print("ReportsMenu: Requesting Stock by Brand Report Data")
        report_data = self.app.generate_stock_by_brand_report_data()
        
        if report_data is None: return
        if not report_data:
            messagebox.showinfo("Stock by Brand", "No stock data found for any brand.", parent=self)
            return

        columns = [
            {'id': 'Brand', 'text': 'Brand', 'width': 200, 'anchor': 'w', 'stretch': tk.YES},
            {'id': 'LocationCount', 'text': 'Locations', 'width': 100, 'anchor': 'e'},
            {'id': 'TotalQuantity', 'text': 'Total Qty', 'width': 100, 'anchor': 'e'}
        ]
        
        ReportDisplayWindow(
            master=self.app, 
            title="Stock Summary by Brand",
            columns_config=columns,
            data_rows=report_data,
            app_instance=self.app
        )

    # --- Batch Summary Report ---
    def show_batch_summary_options(self):
        print("ReportsMenu: Opening Batch Summary Filter Options")
        BatchSummaryOptionsWindow(
            master=self.app, 
            app_instance=self.app, 
            callback=self._execute_batch_summary_report
        )

    def _execute_batch_summary_report(self, search_criteria):
        """Called by BatchSummaryOptionsWindow with the selected search criteria."""
        search_type = search_criteria.get('type')
        search_term = search_criteria.get('term')
        print(f"ReportsMenu: Requesting Batch Summary Report. Type: {search_type}, Term: '{search_term}'")
        
        report_data = self.app.generate_batch_summary_report_data(search_type, search_term)
        
        if report_data is None:
            return 
        if not report_data:
            messagebox.showinfo("Batch Summary", f"No batch information found for {search_type.upper()} '{search_term}'.", parent=self)
            return

        columns = [
            {'id': 'SKU', 'text': 'SKU', 'width': 120, 'anchor': 'w'},
            {'id': 'Description', 'text': 'Description', 'width': 250, 'stretch': tk.YES},
            {'id': 'Brand', 'text': 'Brand', 'width': 100, 'anchor': 'w'},
            {'id': 'Batch', 'text': 'Batch', 'width': 100, 'anchor': 'w'},
            {'id': 'TotalQuantity', 'text': 'Total Qty', 'width': 80, 'anchor': 'e'},
            {'id': 'Locations', 'text': 'Locations (CSV)', 'width': 200, 'anchor': 'w', 'stretch': tk.YES}
        ]
        

        ReportDisplayWindow(
            master=self.app, 
            title=f"Batch Summary for {search_type.upper()}: {search_term}",
            columns_config=columns,
            data_rows=report_data,
            app_instance=self.app
        )

    # --- Go Back Button ---
    def go_back_to_main(self, event=None): 
        print("ReportsMenu: Going back to Main Page.")
        self.app.show_main_page()