import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from functools import reduce
import matplotlib.pyplot as plt

# Function definitions for filtering and plotting
def apply_filter(df: pd.DataFrame, column: str, value: any) -> pd.DataFrame:
    print(f"Applying filter for column '{column}' with value(s): {value}")

    if df.empty:
        print("The DataFrame is empty. Skipping filtering.")
        return df

    if column not in df.columns:
        print(f"Warning: Column '{column}' does not exist in the DataFrame. Skipping this filter.")
        return df

    if pd.api.types.is_numeric_dtype(df[column]):
        try:
            if isinstance(value, tuple) and len(value) == 2:
                return df[(df[column] >= value[0]) & (df[column] <= value[1])]
            if isinstance(value, list):
                value = [float(v) for v in value]
                return df[df[column].isin(value)]
            return df[df[column] == float(value)]
        except (ValueError, TypeError):
            print(f"Warning: Could not apply numeric filter on column '{column}' with value '{value}'.")
            return df

    if pd.api.types.is_string_dtype(df[column]):
        if isinstance(value, list):
            value = [str(v).strip().lower() for v in value]
            print(f"Normalized string filter values for column '{column}': {value}")
            return df[df[column].str.strip().str.lower().isin(value)]
        else:
            value = str(value).strip().lower()
            return df[df[column].str.strip().str.lower() == value]

    print(f"Warning: Unsupported column type for '{column}'. Skipping this filter.")
    return df

def parse_filter_input(column: str, filter_value: any, column_type: any) -> any:
    try:
        if isinstance(filter_value, list):
            parsed_values = []
            for value in filter_value:
                if pd.api.types.is_numeric_dtype(column_type):
                    parsed_values.append(float(value.strip()))
                elif pd.api.types.is_string_dtype(column_type):
                    parsed_values.append(value.strip())
            return parsed_values

        if pd.api.types.is_numeric_dtype(column_type):
            return float(filter_value.strip())
        elif pd.api.types.is_string_dtype(column_type):
            return filter_value.strip()

        return filter_value
    except (ValueError, AttributeError):
        print(f"Warning: Could not parse '{filter_value}' for column '{column}' with type '{column_type}'.")
        return None

def get_user_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    if df.empty:
        print("The DataFrame is empty. No filters can be applied.")
        return df

    parsed_filters = {}

    for column, filter_values in filters.items():
        column_type = df[column].dtype
        parsed_filter = parse_filter_input(column, filter_values, column_type)

        if not parsed_filter:
            print(f"Skipping filter for column '{column}' due to invalid or empty value.")
            continue

        parsed_filters[column] = parsed_filter

    if not parsed_filters:
        print("No valid filters provided.")
        return df

    filtered_df = reduce(lambda df, kv: apply_filter(df, kv[0], kv[1]), parsed_filters.items(), df)

    if filtered_df.empty:
        print("No results matched the filters.")
        return filtered_df

    return filtered_df

def plot_filtered_data(df: pd.DataFrame, x_column: str, y_column: str) -> None:
    if x_column not in df.columns or y_column not in df.columns:
        print(f"Error: Columns '{x_column}' or '{y_column}' not found in filtered data.")
        return

    plt.figure(figsize=(10, 6))

    if pd.api.types.is_numeric_dtype(df[x_column]) and pd.api.types.is_numeric_dtype(df[y_column]):
        plt.plot(df[x_column], df[y_column], marker="o", linestyle="-", color="b")
        plt.title(f"{y_column} vs {x_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
    else:
        df_grouped = df.groupby(x_column)[y_column].count()
        df_grouped.plot(kind="bar", color="c")
        plt.title(f"{y_column} count by {x_column}")
        plt.xlabel(x_column)
        plt.ylabel(f"Count of {y_column}")

    plt.show()

# GUI Classes
class InputGUI:
    def __init__(self, master):
        self.master = master

        # Set the background color of the entire window to white
        master.configure(bg='#FFFFFF')

        # Add title directly without logo
        title_label = tk.Label(
            master,
            text="Ukulele Tuesday",
            bg='#FFFFFF',
            fg='#000000',
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=10)

        # Main Content of the page
        self.main_frame = tk.Frame(master, bg='#FFFFFF')
        self.main_frame.pack(fill='both', expand=True)

        # Dictionary to store selected file paths
        self.file_paths = {}

        # Creating upload sections
        self.create_file_upload_section("Tabdb", 0)
        self.create_file_upload_section("Playdb", 1)
        self.create_file_upload_section("Requestdb", 2)

        # Style the proceed button and pack it at the bottom right
        self.proceed_button = tk.Button(
            master,
            text="Proceed",
            command=self.next_window,
            bg='#FFFFFF',
            fg='#000000',
            font=('Arial', 12),
            bd=1,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#8B4513',
            padx=20,
            pady=10
        )
        self.proceed_button.pack(side="bottom", anchor="e", padx=20, pady=20)

    def create_file_upload_section(self, db_name, section_number):
        """Creates a file upload section with labels and a button."""

        # Outer frame acting as a border
        border_frame = tk.Frame(
            self.main_frame,
            bg='#FFFFFF',
            highlightbackground='#E0E0E0',
            highlightthickness=1
        )
        border_frame.grid(
            row=section_number,
            column=0,
            padx=20,
            pady=10,
            sticky='w'
        )

        # Inner frame adds spacing within the border frame
        inner_frame = tk.Frame(border_frame, bg='#FFFFFF')
        inner_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Title label aka Section Header
        title_label = tk.Label(
            inner_frame,
            text=f"Upload File - {db_name}",
            bg='#FFFFFF',
            fg='#c49526',
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, sticky='w')

        # Replace the browse button without image
        browse_button = tk.Button(
            inner_frame,
            text="Browse",
            command=lambda: self.browse_file(db_name),
            bg='#FFFFFF',
            borderwidth=1,
            highlightthickness=1,
            activebackground='#FFFFFF'
        )
        browse_button.grid(row=0, column=1, sticky='e', padx=10)

        # Description label
        status_label = tk.Label(
            inner_frame,
            text="Upload a CSV file from your device",
            bg='#FFFFFF',
            fg='#000000',
            font=('Arial', 14),
            wraplength=500
        )
        status_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(10, 0))

        # Store the status label for updating later
        self.file_paths[db_name] = {'path': None, 'label': status_label}

    def browse_file(self, db_name):
        """Opens a file dialog to select a CSV file on the user machine and stores the path."""

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title=f"Select CSV file for {db_name}",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )

        if file_path:
            # Store the selected file path
            self.file_paths[db_name]['path'] = file_path

            # Update the label to show the selected file
            self.file_paths[db_name]['label'].config(text=f"Selected file: {file_path}")

    def next_window(self):
        """Create the next window."""
        # Check if all required files are selected
        required_files = ['Tabdb', 'Playdb', 'Requestdb']
        for db_name in required_files:
            if not self.file_paths[db_name]['path']:
                messagebox.showerror("Error", f"Please select a file for {db_name} before proceeding.")
                return

        # Create the next window and pass the file paths
        next_window = tk.Toplevel(self.master)
        next_window.title("Data Filters")
        next_window.geometry("800x600")
        DataFilterGUI(next_window, self.file_paths)

class DataFilterGUI:
    def __init__(self, master, file_paths):
        self.master = master
        self.file_paths = file_paths
        self.tab_df = self.load_data()
        self.selected_filters = {}

        # Create GUI elements for filtering
        self.create_widgets()

    def load_data(self):
        # Load the CSV files using the paths from file_paths
        try:
            tab_df = pd.read_csv(self.file_paths['Tabdb']['path'])
            # You can also load Playdb and Requestdb if needed
            return tab_df
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.master.destroy()
            return None

    def create_widgets(self):
        # Create frames and widgets for filtering
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side="top", fill="x", pady=10)

        self.display_frame = tk.Frame(self.master)
        self.display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create buttons for each column
        for column_name in self.tab_df.columns:
            btn = tk.Button(
                self.button_frame,
                text=column_name,
                command=lambda col=column_name: self.display_column_values(col),
                width=15
            )
            btn.pack(side="left", padx=5, pady=5)

        # Add Apply Filters button
        filter_button = tk.Button(
            self.master,
            text="Apply Filters",
            command=self.apply_filters,
            bg="green",
            fg="white"
        )
        filter_button.pack(pady=10)

        # Add Clear All Filters button
        clear_button = tk.Button(
            self.master,
            text="Clear All Filters",
            command=self.clear_all_filters,
            bg="red",
            fg="white"
        )
        clear_button.pack(pady=10)

    def display_column_values(self, column_name):
        # Clear the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        unique_values = self.tab_df[column_name].dropna().unique()
        if len(unique_values) == 0:
            unique_values = ["(No Data)"]

        # Create a label to display the column name
        label = tk.Label(
            self.display_frame,
            text=f"Values in Column: {column_name}",
            font=("Arial", 14),
            fg="brown"
        )
        label.pack(pady=10)

        # Create a canvas with a scrollbar for the checkboxes
        canvas = tk.Canvas(self.display_frame, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            self.display_frame, orient="vertical", command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Frame inside the canvas to hold checkboxes
        checkbox_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")

        # Dictionary to hold checkbox variables for the current column
        checkbox_vars = {}

        # Dynamically create checkboxes for each unique value
        for value in unique_values:
            display_text = str(value) if len(str(value)) <= 50 else str(value)[:47] + "..."
            var = tk.IntVar()
            checkbox_vars[display_text] = var
            checkbox = tk.Checkbutton(
                checkbox_frame, text=display_text, variable=var, anchor="w"
            )
            checkbox.pack(fill="x", pady=2, padx=10)

        # Store the checkbox variables in the selected_filters dictionary
        self.selected_filters[column_name] = checkbox_vars

        # Update the display and focus to force rendering
        checkbox_frame.update_idletasks()
        canvas.focus_set()

        if len(unique_values) == 1 and unique_values[0] == "(No Data)":
            empty_label = tk.Label(
                checkbox_frame,
                text="No data available for this column.",
                fg="red"
            )
            empty_label.pack(pady=10)

    def apply_filters(self):
        # Remove existing Show Graph button if it exists
        if hasattr(self, 'show_graph_button') and self.show_graph_button:
            self.show_graph_button.destroy()

        filters = {}
        for column, checkbox_vars in self.selected_filters.items():
            # Collect selected values for each column
            selected_values = [
                value for value, var in checkbox_vars.items() if var.get() == 1
            ]
            if selected_values:
                filters[column] = selected_values
            print(f"Column: {column}, Selected Values: {selected_values}")  # Debug print

        print("Filters selected by user:", filters)

        # Call get_user_filters with the DataFrame and the filters dictionary
        filtered_df = get_user_filters(self.tab_df, filters)

        # Display the filtered DataFrame or use it as needed
        print("Filtered DataFrame:")
        print(filtered_df)

        # Call display_results to show the filtered data in the GUI
        self.display_results(filtered_df)

        # Add the Show Graph button
        self.show_graph_button = tk.Button(
            self.master,
            text="Show Graph",
            command=lambda: self.show_graph(filtered_df),
            bg="purple",
            fg="white"
        )
        self.show_graph_button.pack(pady=10)

    def display_results(self, filtered_df):
        # Clear any previous results
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Create a frame for displaying the filtered data
        results_frame = tk.Frame(self.display_frame)
        results_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Display a message if the DataFrame is empty
        if filtered_df.empty:
            no_results_label = tk.Label(
                results_frame,
                text="No matching results found.",
                fg="red",
                font=("Arial", 14)
            )
            no_results_label.pack(pady=10)
        else:
            # Create a Text widget to show the results
            result_text = tk.Text(results_frame, height=15, width=80)
            result_text.pack(pady=10)

            # Insert filtered data into the text widget
            result_text.insert(tk.END, filtered_df.to_string(index=False))
            result_text.config(state=tk.DISABLED)  # Disable editing

        # Add a back button to return to the filter UI
        back_button = tk.Button(
            results_frame,
            text="Back to Filters",
            command=lambda: self.back_to_filters(results_frame)
        )
        back_button.pack(pady=10)

    def back_to_filters(self, results_frame):
        # Hide the results frame
        results_frame.pack_forget()

        # Re-show the filter UI
        self.display_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_graph(self, filtered_df):
        # Clear previous widgets in the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Create dropdowns for selecting x and y columns
        x_var = tk.StringVar()
        y_var = tk.StringVar()

        tk.Label(
            self.display_frame,
            text="Select X-axis Column:",
            font=("Arial", 12)
        ).pack(pady=5)
        x_dropdown = tk.OptionMenu(self.display_frame, x_var, *filtered_df.columns)
        x_dropdown.pack(pady=5)

        tk.Label(
            self.display_frame,
            text="Select Y-axis Column:",
            font=("Arial", 12)
        ).pack(pady=5)
        y_dropdown = tk.OptionMenu(self.display_frame, y_var, *filtered_df.columns)
        y_dropdown.pack(pady=5)

        # Button to generate the graph
        def generate_graph():
            x_column = x_var.get()
            y_column = y_var.get()
            if not x_column or not y_column:
                error_label = tk.Label(
                    self.display_frame,
                    text="Please select both X and Y columns.",
                    fg="red"
                )
                error_label.pack(pady=5)
                return
            plot_filtered_data(filtered_df, x_column, y_column)

        graph_button = tk.Button(
            self.display_frame,
            text="Generate Graph",
            command=generate_graph,
            bg="blue",
            fg="white"
        )
        graph_button.pack(pady=10)

    def clear_all_filters(self):
        """
        Clears all selected checkboxes and resets selected_filters.
        """
        # Reset the variables in all checkboxes
        for column_vars in self.selected_filters.values():
            for var in column_vars.values():
                var.set(0)
        # Clear the selected_filters dictionary
        self.selected_filters.clear()
        print("All filters have been cleared.")
        # Clear the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()

# Main application setup
root = tk.Tk()
root.geometry("600x500")
root.title("Ukulele Tuesday")
InputGUI(root)
root.mainloop()
