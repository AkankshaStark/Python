import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from functools import reduce

# Function to convert 'HH:MM:SS' to total seconds
def convert_duration_to_seconds(duration_str):
    try:
        h, m, s = duration_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    except Exception:
        return None  # Return None if conversion fails

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
                min_val, max_val = value
                return df[(df[column] >= min_val) & (df[column] <= max_val)]
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

        if parsed_filter is None:
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

def plot_filtered_data(df: pd.DataFrame, x_column: str, y_column: str, chart_type: str) -> None:
    # Check if the X-axis column exists
    if x_column not in df.columns:
        messagebox.showerror("Error", f"Column '{x_column}' not found in filtered data.")
        return

    # Handle Histogram
    if chart_type == 'Histogram':
        if pd.api.types.is_numeric_dtype(df[x_column]):
            plt.figure(figsize=(10, 6))
            sns.histplot(df[x_column], bins=10, kde=True)
            plt.title(f"Histogram of {x_column.capitalize()}")
            plt.xlabel(x_column.capitalize())
            plt.ylabel('Frequency')
            plt.tight_layout()
            plt.show()
            return
        else:
            messagebox.showinfo("Plotting Error", f"Cannot plot histogram for non-numeric column '{x_column}'.")
            return

    # Handle Cumulative Line Chart
    elif chart_type == 'Cumulative Line Chart':
        if x_column not in df.columns:
            messagebox.showerror("Error", f"The data does not contain '{x_column}' column.")
            return
        if not pd.api.types.is_datetime64_any_dtype(df[x_column]):
            try:
                df[x_column] = pd.to_datetime(df[x_column], errors='coerce')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to convert '{x_column}' to datetime: {e}")
                return
        df = df.dropna(subset=[x_column])
        df = df.sort_values(x_column)

        # Group by date and count number of songs played
        df_grouped = df.groupby(x_column).size().reset_index(name='song_count')
        df_grouped['cumulative_count'] = df_grouped['song_count'].cumsum()

        plt.figure(figsize=(10, 6))
        plt.plot(df_grouped[x_column], df_grouped['cumulative_count'], marker='o')
        plt.title('Cumulative Number of Songs Played Over Time')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Number of Songs')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        return

    # Handle Pie Chart
    elif chart_type == 'Pie Chart':
        if x_column in df.columns:
            counts = df[x_column].value_counts()
            plt.figure(figsize=(8, 8))
            counts.plot(kind='pie', autopct='%1.1f%%', startangle=90)
            plt.title(f"Distribution of Songs by {x_column.capitalize()}")
            plt.ylabel('')
            plt.tight_layout()
            plt.show()
            return
        else:
            messagebox.showerror("Error", f"Column '{x_column}' not found in data.")
            return

    # Check if the Y-axis column exists
    if y_column not in df.columns:
        messagebox.showerror("Error", f"Column '{y_column}' not found in filtered data.")
        return

    # Both columns are numeric (Scatter Plot)
    if chart_type == 'Scatter Plot':
        if pd.api.types.is_numeric_dtype(df[x_column]) and pd.api.types.is_numeric_dtype(df[y_column]):
            plt.figure(figsize=(10, 6))
            sns.scatterplot(x=x_column, y=y_column, data=df)
            plt.title(f"{y_column.capitalize()} vs {x_column.capitalize()}")
            plt.xlabel(x_column.capitalize())
            plt.ylabel(y_column.capitalize())
            plt.tight_layout()
            plt.show()
            return
        else:
            messagebox.showinfo("Plotting Error", "Both X and Y columns must be numeric for a scatter plot.")
            return

    # X is categorical, Y is numeric (Bar Plot)
    elif chart_type == 'Bar Plot':
        if pd.api.types.is_numeric_dtype(df[y_column]) and (
            pd.api.types.is_categorical_dtype(df[x_column]) or pd.api.types.is_object_dtype(df[x_column])
        ):
            # Ask user for aggregation method
            aggregation = simpledialog.askstring(
                "Aggregation", f"Choose aggregation for {y_column} (sum or average):", initialvalue="average"
            )
            if aggregation and aggregation.lower() == 'sum':
                df_grouped = df.groupby(x_column)[y_column].sum().reset_index()
                agg_label = f"Total {y_column.capitalize()}"
            else:
                df_grouped = df.groupby(x_column)[y_column].mean().reset_index()
                agg_label = f"Average {y_column.capitalize()}"

            plt.figure(figsize=(10, 6))
            sns.barplot(x=x_column, y=y_column, data=df_grouped, ci=None)
            plt.title(f"{agg_label} by {x_column.capitalize()}")
            plt.xlabel(x_column.capitalize())
            plt.ylabel(agg_label)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
            return
        else:
            messagebox.showinfo("Plotting Error", "X must be categorical and Y must be numeric for a bar plot.")
            return

    # X is numeric, Y is categorical (Box Plot)
    elif chart_type == 'Box Plot':
        if pd.api.types.is_numeric_dtype(df[x_column]) and (
            pd.api.types.is_categorical_dtype(df[y_column]) or pd.api.types.is_object_dtype(df[y_column])
        ):
            plt.figure(figsize=(10, 6))
            sns.boxplot(x=y_column, y=x_column, data=df)
            plt.title(f"Distribution of {x_column.capitalize()} by {y_column.capitalize()}")
            plt.xlabel(y_column.capitalize())
            plt.ylabel(x_column.capitalize())
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
            return
        else:
            messagebox.showinfo("Plotting Error", "X must be numeric and Y must be categorical for a box plot.")
            return

    else:
        messagebox.showinfo("Plotting Error", "Could not determine appropriate plot for selected data.")
        return

# GUI Classes
class InputGUI:
    def __init__(self, master):
        self.master = master
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

        # Browse button 
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

        # Initialize sort order
        self.sort_ascending = True
        self.current_column = None

        # Create GUI elements for filtering
        self.create_widgets()

    def load_data(self):
        try:
            # Load the CSV files
            tab_df = pd.read_csv(self.file_paths['Tabdb']['path'])
            play_df = pd.read_csv(self.file_paths['Playdb']['path'])
            request_df = pd.read_csv(self.file_paths['Requestdb']['path'])

            # Drop personal information columns from tab_df
            personal_info_columns = ['tabber']  
            tab_df = tab_df.drop(columns=personal_info_columns, errors='ignore')

            # Convert 'year' to numeric and create 'decade' column in tab_df
            tab_df['year'] = pd.to_numeric(tab_df['year'], errors='coerce')
            tab_df = tab_df.dropna(subset=['year'])
            tab_df['year'] = tab_df['year'].astype(int)
            tab_df['decade'] = (tab_df['year'] // 10) * 10

            # Reset index after dropping rows
            tab_df.reset_index(drop=True, inplace=True)

            # Identify the date columns in play_df 
            date_columns = [col for col in play_df.columns if col.startswith('20')]  # Since the dates start with '20'

            # Check if 'song' and 'artist' columns exist in play_df
            if not all(col in play_df.columns for col in ['song', 'artist']):
                messagebox.showerror("Error", "The 'playdb' file must contain 'song' and 'artist' columns.")
                self.master.destroy()
                return None

            # Reshape play_df using melt to get 'song', 'artist', 'play_date', 'played' columns
            play_df_long = play_df.melt(
                id_vars=['song', 'artist'],
                value_vars=date_columns,
                var_name='play_date',
                value_name='played'
            )

            # Filter out rows where 'played' is NaN or 0 (assuming 1 indicates played)
            play_df_long = play_df_long[play_df_long['played'] == 1]

            # Convert 'play_date' to datetime format
            play_df_long['play_date'] = pd.to_datetime(play_df_long['play_date'], format='%Y%m%d', errors='coerce')

            # Remove rows with invalid dates
            play_df_long = play_df_long.dropna(subset=['play_date'])

            # Standardize 'song' and 'artist' names in both DataFrames
            for df in [tab_df, play_df_long]:
                df['song'] = df['song'].str.strip().str.lower()
                df['artist'] = df['artist'].str.strip().str.lower()

            # Merge tab_df with play_df_long on 'song' and 'artist'
            merged_df = pd.merge(
                tab_df,
                play_df_long[['song', 'artist', 'play_date']],
                on=['song', 'artist'],
                how='left'
            )

            # Convert 'difficulty' to numeric in merged_df
            if 'difficulty' in merged_df.columns:
                merged_df['difficulty'] = pd.to_numeric(merged_df['difficulty'], errors='coerce')

            # Convert 'duration' from 'HH:MM:SS' to total seconds
            if 'duration' in merged_df.columns:
                merged_df['duration_seconds'] = merged_df['duration'].apply(convert_duration_to_seconds)
                # Optionally, drop the original 'duration' column
                # merged_df = merged_df.drop(columns=['duration'])

            # Ensure 'gender' column exists in merged_df
            if 'gender' not in merged_df.columns:
                merged_df['gender'] = 'Unknown'
            else:
                merged_df['gender'] = merged_df['gender'].fillna('Unknown')

            # Store the merged DataFrame in self.tab_df
            self.tab_df = merged_df

            return self.tab_df
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.master.destroy()
            return None

    def create_widgets(self):
        # Adjusted to use grid for buttons
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side="top", fill="x", pady=10)

        self.display_frame = tk.Frame(self.master)
        self.display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create buttons for each column using grid
        columns = self.tab_df.columns.tolist()
        max_columns_in_row = 5  # Adjust as needed
        for idx, column_name in enumerate(columns):
            row = idx // max_columns_in_row
            col = idx % max_columns_in_row
            btn = tk.Button(
                self.button_frame,
                text=column_name,
                command=lambda col=column_name: self.display_column_values(col),
                width=15
            )
            btn.grid(row=row, column=col, padx=5, pady=5)

        # Place the "Sort Order" button to the right of the column buttons
        total_rows = (len(columns) - 1) // max_columns_in_row + 1
        sort_button = tk.Button(
            self.button_frame,
            text="Sort Order",
            command=self.toggle_sort_order,
            bg="blue",
            fg="white",
            width=15
        )
        sort_button.grid(row=0, column=max_columns_in_row, padx=5, pady=5, rowspan=total_rows, sticky='ns')

        # Add Apply Filters button below the buttons
        filter_button = tk.Button(
            self.master,
            text="Apply Filters",
            command=self.apply_filters,
            bg="green",
            fg="white"
        )
        filter_button.pack(pady=5)

        # Add Clear All Filters button below the Apply Filters button
        clear_button = tk.Button(
            self.master,
            text="Clear All Filters",
            command=self.clear_all_filters,
            bg="red",
            fg="white"
        )
        clear_button.pack(pady=5)

    def display_column_values(self, column_name):
        self.current_column = column_name

        # Clear the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Check if the column exists in the DataFrame
        if column_name not in self.tab_df.columns:
            label = tk.Label(
                self.display_frame,
                text=f"Column '{column_name}' does not exist in the data.",
                font=("Arial", 14),
                fg="red"
            )
            label.pack(pady=10)
            return

        # Handle numerical columns differently
        if pd.api.types.is_numeric_dtype(self.tab_df[column_name]):
            # For numerical columns, provide options to filter by range
            min_value = self.tab_df[column_name].min()
            max_value = self.tab_df[column_name].max()

            label = tk.Label(
                self.display_frame,
                text=f"Filter '{column_name}' by range:",
                font=("Arial", 14),
                fg="brown"
            )
            label.pack(pady=10)

            # Entry widgets for min and max values
            min_var = tk.DoubleVar(value=min_value)
            max_var = tk.DoubleVar(value=max_value)

            min_label = tk.Label(self.display_frame, text="Min:")
            min_label.pack()
            min_entry = tk.Entry(self.display_frame, textvariable=min_var)
            min_entry.pack()

            max_label = tk.Label(self.display_frame, text="Max:")
            max_label.pack()
            max_entry = tk.Entry(self.display_frame, textvariable=max_var)
            max_entry.pack()

            # Store the min and max variables in the selected_filters dictionary
            self.selected_filters[column_name] = {'min': min_var, 'max': max_var}
        else:
            # Existing code for categorical columns
            unique_values = self.tab_df[column_name].dropna().unique()
            if len(unique_values) == 0:
                unique_values = ["(No Data)"]
            else:
                unique_values = sorted(unique_values, key=lambda x: str(x), reverse=not self.sort_ascending)

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
        try:
            # Remove existing Show Graph button if it exists
            if hasattr(self, 'show_graph_button') and self.show_graph_button:
                self.show_graph_button.destroy()

            filters = {}
            for column, filter_vars in self.selected_filters.items():
                if isinstance(filter_vars, dict) and 'min' in filter_vars and 'max' in filter_vars:
                    # Numerical range filter
                    min_value = filter_vars['min'].get()
                    max_value = filter_vars['max'].get()
                    filters[column] = (min_value, max_value)
                    print(f"Column: {column}, Range: {min_value} to {max_value}")
                else:
                    # Categorical filter
                    selected_values = [
                        value for value, var in filter_vars.items() if var.get() == 1
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
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred in apply_filters: {e}")
            print(f"An error occurred in apply_filters: {e}")

    def display_results(self, filtered_df):
        try:
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

            # Add the Show Graph button here
            self.show_graph_button = tk.Button(
                results_frame,
                text="Show Graph",
                command=lambda: self.show_graph(filtered_df),
                bg="purple",
                fg="white"
            )
            self.show_graph_button.pack(pady=10)

            # Add a back button to return to the filter UI
            back_button = tk.Button(
                results_frame,
                text="Back to Filters",
                command=lambda: self.back_to_filters(results_frame)
            )
            back_button.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred in display_results: {e}")
            print(f"An error occurred in display_results: {e}")

    def back_to_filters(self, results_frame):
        # Hide the results frame
        results_frame.pack_forget()

        # Re-show the filter UI
        self.display_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_graph(self, filtered_df):
        if filtered_df.empty or filtered_df.columns.empty:
            messagebox.showinfo("No Data", "No data available to plot.")
            return

        try:
            # Clear previous widgets in the display frame
            for widget in self.display_frame.winfo_children():
                widget.destroy()

            # Create variables for selections
            x_var = tk.StringVar()
            y_var = tk.StringVar(value='')  # Default to empty string
            chart_type_var = tk.StringVar()

            # Chart Type Selection
            tk.Label(
                self.display_frame,
                text="Select Chart Type:",
                font=("Arial", 12)
            ).pack(pady=5)
            chart_type_options = ['Histogram', 'Cumulative Line Chart', 'Pie Chart', 'Scatter Plot', 'Bar Plot', 'Box Plot']
            chart_type_dropdown = tk.OptionMenu(self.display_frame, chart_type_var, *chart_type_options)
            chart_type_dropdown.pack(pady=5)

            # X-axis Selection
            tk.Label(
                self.display_frame,
                text="Select X-axis Column:",
                font=("Arial", 12)
            ).pack(pady=5)
            x_dropdown = tk.OptionMenu(self.display_frame, x_var, *filtered_df.columns)
            x_dropdown.pack(pady=5)

            # Y-axis Selection (optional)
            tk.Label(
                self.display_frame,
                text="Select Y-axis Column (optional):",
                font=("Arial", 12)
            ).pack(pady=5)
            y_options = [''] + list(filtered_df.columns)
            y_dropdown = tk.OptionMenu(self.display_frame, y_var, *y_options)
            y_dropdown.pack(pady=5)

            # Generate Graph Button
            def generate_graph():
                x_column = x_var.get()
                y_column = y_var.get()
                chart_type = chart_type_var.get()
                if not x_column or not chart_type:
                    error_label = tk.Label(
                        self.display_frame,
                        text="Please select a chart type and X-axis column.",
                        fg="red"
                    )
                    error_label.pack(pady=5)
                    return
                try:
                    plot_filtered_data(filtered_df, x_column, y_column, chart_type)
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred while plotting: {e}")

            graph_button = tk.Button(
                self.display_frame,
                text="Generate Graph",
                command=generate_graph,
                bg="blue",
                fg="white"
            )
            graph_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def clear_all_filters(self):
        """
        Clears all selected checkboxes and resets selected_filters.
        """
        # Reset the variables in all filters
        for column_vars in self.selected_filters.values():
            if isinstance(column_vars, dict):
                if 'min' in column_vars and 'max' in column_vars:
                    # Numerical range filter
                    column_vars['min'].set(0)
                    column_vars['max'].set(0)
                else:
                    # Categorical filters
                    for var in column_vars.values():
                        var.set(0)
        # Clear the selected_filters dictionary
        self.selected_filters.clear()
        print("All filters have been cleared.")
        # Clear the display frame
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.current_column = None  # Reset current column

    def toggle_sort_order(self):
        self.sort_ascending = not self.sort_ascending
        order = 'Ascending' if self.sort_ascending else 'Descending'
        print(f"Sort order set to {order}")
        messagebox.showinfo("Sort Order", f"Sort order set to {order}")
        # Refresh the displayed values if a column is selected
        if self.current_column:
            self.display_column_values(self.current_column)

# Main application setup
root = tk.Tk()
root.geometry("800x600")  # Adjusted window size
root.title("Ukulele Tuesday")
InputGUI(root)
root.mainloop()
