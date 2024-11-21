import pandas as pd
from tkinter import *
from typing import Dict, Any
from Multifilter import get_user_filters  # Assuming you already have the Multifilter module

# Load the dataset
file_path = "/Users/aruba/Documents/PythonAssignment/UkeleleTuesday/dataSet/tabdb.csv"  # Update with your file path
tab_df = pd.read_csv(file_path)

# Load the play dataset
play_file_path = "/Users/aruba/Documents/PythonAssignment/UkeleleTuesday/dataSet/playdb.csv"  # Update with your play data path
play_df = pd.read_csv(play_file_path)

# Dictionary to hold selected filter values for each column
selected_filters = {}

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

    # Add a back button to return to the filter UI
    back_button = Button(display_frame, text="Back to Filters", command=lambda: back_to_filters(display_frame), bg="green")
    back_button.pack(pady=10)



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


# Create the GUI application
root = Tk()
root.title("Column Value Viewer")
root.geometry("800x600")

# Create a frame for buttons
button_frame = Frame(root)
button_frame.pack(side="top", fill="x", pady=10)

# Create a frame for displaying values
display_frame = Frame(root)
display_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Dynamically create buttons for each column, excluding the "tabber" column
for column_name in tab_df.columns:
    if column_name != "tabber":  # Skip the "tabber" column
        btn = Button(button_frame, text=column_name, command=lambda col=column_name: display_column_values(col), width=15)
        btn.pack(side="left", padx=5, pady=5)

# Add a button to apply filters
filter_button = Button(root, text="Apply Filters", command=apply_filters, bg="green", fg="brown")
filter_button.pack(pady=10)

# Add a button for the No. of times played
song_count_button = Button(root, text="No. of Times Played", command=song_count_ui, bg="blue", fg="brown")
song_count_button.pack(pady=10)

# In your GUI button creation section, add the clear button
clear_button = Button(root, text="Clear All Filters", command=clear_all_checkboxes, bg="red", fg="brown")
clear_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
