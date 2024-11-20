import pandas as pd
from tkinter import *
from typing import Dict, Any
from Multifilter import get_user_filters  # Assuming you already have the Multifilter module

# Load the dataset
file_path = "/Users/aruba/Documents/PythonAssignment/UkeleleTuesday/dataSet/tabdb.csv"  # Update with your file path
tab_df = pd.read_csv(file_path)

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


# Function to apply filters and call get_user_filters from Multifilter.py
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

    # Display the filtered DataFrame or use it as needed
    print("Filtered DataFrame:")
    print(filtered_df)

    # Call display_results to show the filtered data in the GUI
    display_results(filtered_df)




def display_results(filtered_df):
    """
    Displays the filtered DataFrame results on the GUI with a 'Back' button to return to filter UI.
    """
    # Clear any previous results
    for widget in display_frame.winfo_children():
        widget.destroy()

    # Create a frame for displaying the filtered data
    results_frame = Frame(root)
    results_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Display a message if the DataFrame is empty
    if filtered_df.empty:
        no_results_label = Label(results_frame, text="No matching results found.", fg="red", font=("Arial", 14))
        no_results_label.pack(pady=10)
    else:
        # Create a Text widget to show the results
        result_text = Text(results_frame, height=15, width=80)
        result_text.pack(pady=10)

        # Insert filtered data into the text widget
        result_text.insert(END, filtered_df.to_string(index=False))
        result_text.config(state=DISABLED)  # Disable editing

    # Add a back button to return to the filter UI
    back_button = Button(results_frame, text="Back to Filters", command=lambda: back_to_filters(results_frame))
    back_button.pack(pady=10)


def back_to_filters(results_frame):
    """
    This function hides the filtered results and shows the filter UI again.
    """
    # Hide the results frame
    results_frame.pack_forget()

    # Re-show the filter UI
    display_frame.pack(fill="both", expand=True, padx=20, pady=20)

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

    # You can also refresh the display if necessary (optional)
    # This step might be useful to update the UI visually, if needed:
    # You can call `display_column_values` for each column if you want to reset the display of selected filters.
    # For example:
    # display_column_values(column_name)  # For each column you want to reset.





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

# In your GUI button creation section, add the clear button
clear_button = Button(root, text="Clear All Filters", command=clear_all_checkboxes, bg="red", fg="brown")
clear_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
