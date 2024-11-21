from tkinter import Tk, Frame, Button,messagebox, simpledialog, filedialog
#import matplotlib
import seaborn as sns
import pandas as pd
from tkinter import *
from typing import Dict, Any
import matplotlib.pyplot as plt
from Multifilter import get_user_filters
import numpy as np
# Global variables to store the dataframes
tab_df = None
play_df = None
request_df = None
# Create the GUI application
root = Tk()
root.geometry("800x600")
root.title("Ukulele Tuesday")
# Create a frame for fixed buttons (CSV loading buttons)
button_frame = Frame(root)
button_frame.pack(side="top", fill="x", pady=10)
# Functions to load CSV files
def load_tab_db():
    global tab_df
    file_path = filedialog.askopenfilename(title="Select TAB_DB File")
    if file_path:
        try:
            tab_df = pd.read_csv(file_path)
            messagebox.showinfo("Success", "TAB_DB loaded successfully!")
            create_column_buttons()  # Dynamically create column buttons after loading TAB_DB
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load TAB_DB: {e}")

def load_play_db():
    global play_df
    file_path = filedialog.askopenfilename(title="Select PLAY_DB File")
    if file_path:
        try:
            play_df = pd.read_csv(file_path)
            messagebox.showinfo("Success", "PLAY_DB loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PLAY_DB: {e}")

def load_request_db():
    global request_df
    file_path = filedialog.askopenfilename(title="Select REQUEST_DB File")
    if file_path:
        try:
            request_df = pd.read_csv(file_path)
            messagebox.showinfo("Success", "REQUEST_DB loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load REQUEST_DB: {e}")

# Function to dynamically create column buttons
def create_column_buttons():
    for widget in dynamic_button_frame.winfo_children():
        widget.destroy()  # Clear existing dynamic buttons

    # Add buttons for each column in tab_df
    if tab_df is not None:
        for column_name in tab_df.columns:
            if column_name != "tabber":  # Skip the "tabber" column
                btn = Button(dynamic_button_frame, text=column_name, command=lambda col=column_name: display_column_values(col), width=15)
                btn.pack(side="left", padx=5, pady=5)

def apply_filters():
    filters = {}
    for column, checkbox_vars in selected_filters.items():
        # Collect selected values for each column
        selected_values = [value for value, var in checkbox_vars.items() if var.get() == 1]
        if selected_values:
            filters[column] = selected_values
        print(f"Column: {column}, Selected Values: {selected_values}")  # Debug print

    print("Filters selected by user:", filters)

    # Call get_user_filters with the DataFrame and the filters dictionary
    filtered_df = get_user_filters(tab_df, filters)

    # Remove the 'tabber' column if it exists
    filtered_df = filtered_df.drop(columns=["tabber"], errors="ignore")  # Drop 'tabber' column if it exists

    # Display column selection UI for filtered DataFrame
    display_columns_selection(filtered_df)

def display_column_values(column_name):
    global checkbox_frame
    global checkbox_vars

    # Clear the display frame
    for widget in display_frame.winfo_children():
        widget.destroy()

    # Get unique values of the column and handle null/empty values
    unique_values = tab_df[column_name].dropna().unique()
    if len(unique_values) == 0:
        unique_values = ["(No Data)"]

    # Create a label to display the column name
    label = Label(display_frame, text=f"Values in Column: {column_name}", font=("Arial", 14), fg="brown")
    label.pack(pady=10)

    # Create a canvas with a scrollbar for the checkboxes
    canvas = Canvas(display_frame, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(display_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Configure canvas to work with scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Frame inside the canvas to hold checkboxes
    checkbox_frame = Frame(canvas)
    canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")

    # Dictionary to hold checkbox variables for the current column
    checkbox_vars = {}

    # Dynamically create checkboxes for each unique value
    for value in unique_values:
        display_text = str(value) if len(str(value)) <= 50 else str(value)[:47] + "..."
        var = IntVar()
        checkbox_vars[display_text] = var
        checkbox = Checkbutton(checkbox_frame, text=display_text, variable=var, anchor="w")
        checkbox.pack(fill="x", pady=2, padx=10)

    # Store the checkbox variables in the selected_filters dictionary
    selected_filters[column_name] = checkbox_vars

    # Update the display and focus to force rendering
    checkbox_frame.update_idletasks()
    canvas.focus_set()

    if len(unique_values) == 1 and unique_values[0] == "(No Data)":
        empty_label = Label(checkbox_frame, text="No data available for this column.", fg="red")
        empty_label.pack(pady=10)

def display_columns_selection(filtered_df):
    """
    Display a column selection UI for the user to select which columns to include in the output.
    """
    # Clear the display frame
    for widget in display_frame.winfo_children():
        widget.destroy()

    # Label to guide the user
    label = Label(display_frame, text="Select Columns to Display in Filtered Output", font=("Arial", 14), fg="brown")
    label.pack(pady=10)

    # Create a scrollable frame
    canvas = Canvas(display_frame)
    scrollbar = Scrollbar(display_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)

    # Configure the scrollable frame
    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the scrollable frame and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Create a dictionary to hold checkbox variables for each column
    column_vars = {}
    for column in filtered_df.columns:
        if column != "tabber":  # Exclude "tabber" column
            var = IntVar()
            column_vars[column] = var
            checkbox = Checkbutton(scrollable_frame, text=column, variable=var, anchor="w")
            checkbox.pack(fill="x", pady=2, padx=10)

    # Add a button to confirm column selection
    confirm_button = Button(
        display_frame,
        text="Confirm Selection",
        command=lambda: apply_column_selection(filtered_df, column_vars),
        bg="green",
        fg="brown"
    )
    confirm_button.pack(pady=10)

def display_results(filtered_df):
    """
    Displays the filtered DataFrame results on the GUI with sorting and a 'Back' button to return to filter UI.
    """
    # Clear any previous results
    for widget in display_frame.winfo_children():
        widget.destroy()

    # Create a frame for displaying the filtered data
    results_frame = Frame(display_frame)
    results_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Display a message if the DataFrame is empty
    if filtered_df.empty:
        no_results_label = Label(results_frame, text="No matching results found.", fg="red", font=("Arial", 14))
        no_results_label.pack(pady=10)
    else:
        # Dropdown menu to select a column for sorting
        sort_frame = Frame(display_frame)
        sort_frame.pack(pady=10)

        sort_label = Label(sort_frame, text="Sort by Column:", font=("Arial", 12))
        sort_label.grid(row=0, column=0, padx=5)

        column_var = StringVar()
        column_var.set(filtered_df.columns[0])  # Default to the first column
        column_dropdown = OptionMenu(sort_frame, column_var, *filtered_df.columns)
        column_dropdown.grid(row=0, column=1, padx=5)
    
    # Function to sort the DataFrame and refresh display
    def sort_data(order):
        col = column_var.get()
        sorted_df = filtered_df.sort_values(by=col, ascending=(order == "asc"))
        display_results(sorted_df)  # Refresh display with sorted data
    
     # Buttons to sort in ascending or descending order
        asc_button = Button(sort_frame, text="Sort Ascending", command=lambda: sort_data("asc"), bg="lightblue")
        asc_button.grid(row=0, column=2, padx=5)

        desc_button = Button(sort_frame, text="Sort Descending", command=lambda: sort_data("desc"), bg="lightblue")
        desc_button.grid(row=0, column=3, padx=5)

        # Create a Text widget to show the results
        result_text = Text(results_frame, height=15, width=80)
        result_text.pack(pady=10)

        # Insert filtered data into the text widget
        result_text.insert(END, filtered_df.to_string(index=False))
        result_text.config(state=DISABLED)  # Disable editing

        # Add the Show Graph button here
        show_graph_button = Button(
            results_frame,
            text="Show Graph",
            command=lambda: show_graph(filtered_df),
            bg="purple",
            fg="black"
        )
        show_graph_button.pack(pady=10)

    # Add a back button to return to the filter UI
    back_button = Button(display_frame, text="Back to Filters", command=lambda: back_to_filters(display_frame), bg="green")
    back_button.pack(pady=10)

    def show_graph(filtered_df):
        if filtered_df.empty or filtered_df.columns.empty:
            messagebox.showinfo("No Data", "No data available to plot.")
            return

        try:
            # Clear previous widgets in the display frame
            for widget in display_frame.winfo_children():
                widget.destroy()

            # Create variables for selections
            x_var = StringVar()
            y_var = StringVar(value='')  # Default to empty string
            chart_type_var = StringVar()

            # Chart Type Selection
            Label(
                display_frame,
                text="Select Chart Type:",
                font=("Arial", 12)
            ).pack(pady=5)
            chart_type_options = ['Histogram', 'Cumulative Line Chart', 'Pie Chart', 'Scatter Plot', 'Bar Plot', 'Box Plot']
            chart_type_dropdown = OptionMenu(display_frame, chart_type_var, *chart_type_options)
            chart_type_dropdown.pack(pady=5)

            # X-axis Selection
            Label(
                display_frame,
                text="Select X-axis Column:",
                font=("Arial", 12)
            ).pack(pady=5)
            x_dropdown = OptionMenu(display_frame, x_var, *filtered_df.columns)
            x_dropdown.pack(pady=5)

            # Y-axis Selection (optional)
            Label(
                display_frame,
                text="Select Y-axis Column (optional):",
                font=("Arial", 12)
            ).pack(pady=5)
            y_options = [''] + list(filtered_df.columns)
            y_dropdown = OptionMenu(display_frame, y_var, *y_options)
            y_dropdown.pack(pady=5)

            # Generate Graph Button
            def generate_graph():
                x_column = x_var.get()
                y_column = y_var.get()
                chart_type = chart_type_var.get()
                if not x_column or not chart_type:
                    error_label = Label(
                        display_frame,
                        text="Please select a chart type and X-axis column.",
                        fg="red"
                    )
                    error_label.pack(pady=5)
                    return
                try:
                    plot_filtered_data(filtered_df, x_column, y_column, chart_type)
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred while plotting: {e}")

            graph_button = Button(
                display_frame,
                text="Generate Graph",
                command=generate_graph,
                bg="blue",
                fg="black"
            )
            graph_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        
def apply_column_selection(filtered_df, column_vars):
    """
    Filter the DataFrame to include only selected columns and display the results.
    """
    # Get selected columns
    selected_columns = [col for col, var in column_vars.items() if var.get() == 1]

    if not selected_columns:
        print("No columns selected. Displaying all columns (except 'tabber').")
        selected_columns = [col for col in filtered_df.columns if col != "tabber"]  # Exclude "tabber" by default

    # Display the filtered DataFrame with selected columns
    filtered_data_display = filtered_df[selected_columns]
    display_results(filtered_data_display)

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
            plt.savefig(chart_type + "output_plot.png")
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
        plt.savefig(chart_type + "output_plot.png")
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
            plt.savefig(chart_type + "output_plot.png")
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
            plt.savefig(chart_type + "output_plot.png")
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
            plt.savefig(chart_type + "output_plot.png")
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
            plt.savefig(chart_type + "output_plot.png")
            return
        else:
            messagebox.showinfo("Plotting Error", "X must be numeric and Y must be categorical for a box plot.")
            return

    else:
        messagebox.showinfo("Plotting Error", "Could not determine appropriate plot for selected data.")
        return

def back_to_filters(results_frame):
    """
    This function hides the filtered results and shows the filter UI again.
    """
    # Hide the results frame
    results_frame.pack_forget()

    # Re-show the filter UI
    display_frame.pack(fill="both", expand=True, padx=20, pady=20)


def song_count_ui():
    """
    This function gathers the selected songs and calls the song_count function
    to calculate the number of plays, then displays the result in the UI.
    """
    # Get the selected songs from the filters
    selected_songs = []
    for column, checkbox_vars in selected_filters.items():
        if column == "song":  # Assuming there's a "song" column to filter
            selected_songs = [value for value, var in checkbox_vars.items() if var.get() == 1]

    # Call the song_count function and pass the result to display_song_count_results
    if selected_songs:
        print("Selected Songs for Song Count:", selected_songs)
        matching_rows = song_count(play_df, selected_songs)  # Get matching rows with total plays

        # Display the results in the UI
        display_song_count_results(matching_rows)  # Pass the DataFrame (matching_rows), not selected_songs
        root.update()  # Ensure UI is updated after inserting data
    else:
        print("No songs selected for counting.")


def song_count(play_df, selected_songs):
    matching_rows = play_df[play_df['song'].str.lower().isin([song.lower() for song in selected_songs])]

    # Check if any songs match the filter criteria
    if not matching_rows.empty:
        matching_rows.loc[:, 'total_plays'] = matching_rows.iloc[:, 2:].sum(axis=1).astype(
            int)  # Assuming the play columns start from the 3rd column
        print("Matching Songs and Total Plays:")
        print(matching_rows[['song', 'total_plays']])
        return matching_rows  # Return the DataFrame with matching songs and total plays
    else:
        print("No matching songs found.")
        return None  # Return None if no matches are found


def display_song_count_results(matching_rows):
    """
    This function displays the song count results on the GUI.
    """
    # Clear any previous results
    for widget in display_frame.winfo_children():
        widget.destroy()

    # Create a frame to display song count results
    results_frame = Frame(root)
    results_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Check if matching_rows is empty
    if matching_rows.empty:
        no_results_label = Label(results_frame, text="No matching songs found.", fg="red", font=("Arial", 14))
        no_results_label.pack(pady=10)
        # Add a back button to return to the filter UI
        back_button = Button(results_frame, text="Back to Filters", command=lambda: back_to_filters(results_frame))
        back_button.pack(pady=10)
    else:
        # Create a Text widget to show the song counts
        result_text = Text(results_frame, height=15, width=80)
        result_text.pack(pady=10)

        # Insert the song count results into the text widget
        result_text.insert(END, matching_rows[['song', 'total_plays']].to_string(index=False))
        result_text.config(state=DISABLED)  # Disable editing

        # Force a refresh of the widget
        result_text.update_idletasks()

        # Add a back button to return to the filter UI
        back_button = Button(results_frame, text="Back to Filters", command=lambda: back_to_filters(results_frame))
        back_button.pack(pady=10)

# In your existing GUI.py

def clear_all_checkboxes():
    """
    Clears all selected checkboxes by resetting their variables to 0 (unchecked).
    """
    global checkbox_vars  # Ensure you access the checkbox variables stored globally

    # Iterate over all checkbox variables and reset to 0
    for var in checkbox_vars.values():
        var.set(0)

    print("All checkboxes have been cleared.")
    # Add a back button to return to the filter UI
    back_button = Button(display_frame, text="Back to Filters", command=lambda: back_to_filters(display_frame),
                         bg="green")
    back_button.pack(pady=10)
# Buttons for loading datasets
tab_button = Button(button_frame, text="Load TAB_DB", command=load_tab_db, width=15)
tab_button.pack(side="left", padx=5, pady=5)
play_button = Button(button_frame, text="Load PLAY_DB", command=load_play_db, width=15)
play_button.pack(side="left", padx=5, pady=5)
request_button = Button(button_frame, text="Load REQUEST_DB", command=load_request_db, width=15)
request_button.pack(side="left", padx=5, pady=5)
# Create a separate frame for dynamic buttons (column buttons)
dynamic_button_frame = Frame(root)
dynamic_button_frame.pack(side="top", fill="x", pady=10)
# Create a frame for displaying values
display_frame = Frame(root)
display_frame.pack(fill="both", expand=True, padx=20, pady=10)
# Add a button to apply filters
filter_button = Button(root, text="Apply Filters", command=apply_filters , bg="green", fg="brown")
filter_button.pack(pady=10)
# Add a button for the No. of times played
song_count_button = Button(root, text="No. of Times Played", command=song_count_ui, bg="blue", fg="brown")
song_count_button.pack(pady=10)
# Add a clear button
clear_button = Button(root, text="Clear All Filters", command=clear_all_checkboxes, bg="red", fg="brown")
clear_button.pack(pady=10)
# Dictionary to hold selected filter values for each column
selected_filters = {}
######EXTENSIONS#################
#difficulty histogram with gender counts
# Cleaning  the 'difficulty' and 'gender' columns
tab_df = tab_df.dropna(subset=['year','language','duration','difficulty', 'gender', 'source'])  # Remove rows with NaN in 'difficulty' or 'gender'
genders = tab_df['gender'].unique()  # Get unique gender categories
tab_df['difficulty'] = pd.to_numeric(tab_df['difficulty'], errors='coerce')  # Ensure 'difficulty' is numeric
language_gender_counts = tab_df.groupby(['language', 'gender']).size().unstack(fill_value=0)  
source_gender_counts = tab_df.groupby(['source', 'gender']).size().unstack(fill_value=0)
year_gender_counts = tab_df.groupby(['year', 'gender']).size().unstack(fill_value=0)
#Preparing the data for stacking
difficulty_gender_data = [tab_df[tab_df['gender'] == gender]['difficulty'] for gender in genders]  # Group difficulty by gender
duration_gender_data = [tab_df[tab_df['gender'] == gender]['duration'] for gender in genders]
colors = ['#42A5F5', '#FF7043', '#B39DDB', '#26A69A', '#B0BEC5', '#8D6E63']  # Colors for genders
#Plot the stacked histogram
def plot_stacked_histogram(column):
    plt.figure(figsize=(12, 8))
    # Plot the stacked histogram
    if column == 'difficulty':
        data = difficulty_gender_data
    elif column == 'duration':
        data = duration_gender_data
    else:
        raise ValueError(f"Unsupported column: {column}")
    plt.hist(
        data,
        bins=30,  # Number of bins
        stacked=True,  # Stack the histograms
        color=colors[:len(genders)],  # Use colors based on number of genders
        edgecolor='black',  # Add edge color for clarity
        label=[gender.capitalize() for gender in genders]  # Labels for genders
    )
    # Add titles, labels, and legend
    plt.title(f'Stacked Histogram of Songs by {column.capitalize()} and Gender', fontsize=16)
    plt.xlabel(f'{column.capitalize()}', fontsize=14)
    plt.ylabel('Number of Songs', fontsize=14)
    plt.legend(title="Gender", fontsize=12, title_fontsize=14)
    # Adjust layout for better spacing
    plt.tight_layout()
    # Display the plot
    plt.show()

def plot_stacked_bar_chart(tabdf, column, bar_width, group_by=None):
    required_columns = [column, group_by]
    tabdf_cleaned = tabdf.dropna(subset=required_columns)
    # Special case: if grouping by 'decade', create a 'decade' column
    if column == 'year':
        tabdf_cleaned['decade'] = (tabdf_cleaned['year'] // 10) * 10
        column = 'decade'
    # Group the data and count occurrences
    counts = tabdf_cleaned.groupby([column, group_by]).size().unstack(fill_value=0)
    # Plot the stacked bar chart
    plt.figure(figsize=(12, 8))
    bottom = np.zeros(len(counts))  # Initialize the bottom for stacking
    for group in counts.columns:
        plt.bar(
            counts.index, 
            counts[group], 
            bottom=bottom, 
            label=group, 
            width=bar_width,
            edgecolor='#2f2f2f', 
            linewidth=1.5
        )
        bottom += counts[group]  # Update the bottom for stacking
    # Add titles and labels
    plt.title(f'Stacked Bar Chart of Songs by {column.capitalize()} and {group_by.capitalize()}', fontsize=16)
    plt.xlabel(column.capitalize(), fontsize=14)
    plt.ylabel('Number of Songs', fontsize=14)
    # Adjust x-axis labels for readability
    plt.xticks(rotation=45, ha='right', fontsize=12)
    # Add a legend
    plt.legend(title=group_by.capitalize(), fontsize=12, title_fontsize=14)
    # Adjust layout for better spacing
    plt.tight_layout()
    # Show the plot
    plt.show()
# Plot by language and gender
plot_stacked_bar_chart(tab_df, column='language',bar_width=0.8, group_by='gender')
# Plot by year/decade and gender
plot_stacked_bar_chart(tab_df, column='year', bar_width=3,group_by='gender')
# Plot by source and gender
plot_stacked_bar_chart(tab_df, column='source',bar_width=0.8,group_by='gender')

for gender in year_gender_counts.columns:
    plt.plot(
        year_gender_counts.index,  # X-axis: Years
        year_gender_counts[gender],  # Y-axis: Counts of songs for the gender
        marker='o',  # Add markers for better visibility
        label=gender.capitalize()  # Capitalize gender labels
    )

# Add titles and labels
plt.title('Number of Songs by Gender Over Years', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Number of Songs', fontsize=14)
# Add a legend
plt.legend(title='Gender', fontsize=12, title_fontsize=14)
# Add grid for better readability
plt.grid(visible=True, linestyle='--', alpha=0.7)
# Adjust layout for better spacing and show the plot
plt.tight_layout()
plt.show()
#donut chart 
def generate_gender_donut_chart_with_counts(data):
    try:
        # Ensure the 'gender' column exists
        if 'gender' not in data.columns:
            print("Error: 'gender' column not found in the dataset.")
            return

        # Count occurrences of each gender
        gender_counts = data['gender'].value_counts()

        # Extract values and labels
        levels = gender_counts.values
        labels = gender_counts.index

        # Plot the multi-level donut chart
        fig, ax = plt.subplots(figsize=(8, 8))

        # Define radius and width for each level
        start_radius = 0.7
        width = 0.2

        for i, (count, label) in enumerate(zip(levels, labels)):
            ax.pie(
                [count],  # One slice per gender
                labels=None,  # Disable automatic labels for the pie slice
                radius=start_radius + i * width,
                startangle=90,
                wedgeprops=dict(width=width, edgecolor='w'),
            )

            # Add counts as labels outside the ring
            x = (start_radius + i * width + width / 2) * 0.7  # Adjust position
            ax.text(0, -x, f"{label}: {count}", ha='center', va='center', fontsize=10)

        # Add a central circle to create the donut chart effect
        center_circle = plt.Circle((0, 0), start_radius - 0.1, color='white', fc='white')
        fig.gca().add_artist(center_circle)

        # Add a title
        plt.title("Donut Chart: Gender Distribution with Counts", fontsize=16)
        plt.show()

    except FileNotFoundError:
        print("Error: File not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
generate_gender_donut_chart_with_counts(tab_df)
# Start the GUI event loop
root.mainloop()