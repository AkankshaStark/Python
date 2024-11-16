from functools import reduce
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List
from ReadInput import read_and_clean_files  # Import from ReadInput


def filter_data(df: pd.DataFrame, filters: Dict[str, Any], output_columns: List[str]) -> pd.DataFrame:
    """
    Filters the DataFrame based on a dictionary of column-value pairs and returns specified columns.

    Parameters:
        df (pd.DataFrame): The DataFrame to filter.
        filters (dict): A dictionary where keys are column names and values are the filter criteria.
        output_columns (List[str]): List of columns to include in the output.

    Returns:
        pd.DataFrame: A DataFrame filtered according to the specified criteria with selected columns.
    """

    def apply_filter(df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
        if column not in df.columns:
            print(f"Warning: Column '{column}' does not exist in the DataFrame. Skipping this filter.")
            return df  # Return unfiltered DataFrame

        if column == "difficulty":
            df[column] = pd.to_numeric(df[column], errors="coerce")  # Converts non-numeric values to NaN

        # Special handling for 'type' column with single values
        if column == "type" and isinstance(value, list):  # If filtering for multiple types
            value = [v.strip().lower() for v in value]  # Normalize the input values
            return df[df[column].str.strip().str.lower().isin(value)]  # Match any of the input values

        # Handle numeric columns
        if pd.api.types.is_numeric_dtype(df[column]):
            # Handle ranges for "difficulty" or numeric fields
            if isinstance(value, tuple) and len(value) == 2:  # Range specified as (min, max)
                return df[(df[column] >= value[0]) & (df[column] <= value[1])]
            return df[df[column] == value]

        # Handle non-numeric columns (case-insensitive exact match or partial match for composite fields)
        if isinstance(value, list):  # Multiple values provided
            value = [str(v).strip().lower() for v in value]

            # Strict match for composite fields (e.g., language with "English, French")
            return df[df[column].str.strip().str.lower().apply(
                lambda cell: sorted(cell.split(",")) == sorted(value) if isinstance(cell, str) else False
            )]
        else:  # Single value provided
            value = str(value).lower().strip()

            # Strictly match the full value
            return df[df[column].str.strip().str.lower() == value]

    # Apply filters using reduce and the apply_filter helper function
    filtered_df = reduce(lambda df, kv: apply_filter(df, kv[0], kv[1]), filters.items(), df)

    # Ensure "tabber" is not included in the output
    output_columns = [col for col in output_columns if col != "tabber"]

    return filtered_df[output_columns]


def parse_filter_input(column: str, filter_value: str, column_type) -> Any:
    """
    Parses the filter input and converts it to the appropriate data type based on the column type.

    Parameters:
        column (str): Column name.
        filter_value (str): The input filter value(s).
        column_type: Data type of the column.

    Returns:
        Any: Parsed filter value(s) in the appropriate type.
    """
    try:
        # Handle ranges for difficulty or numeric fields
        if "-" in filter_value and column == "difficulty":
            min_val, max_val = map(float, filter_value.split("-"))
            return (min_val, max_val)  # Return as a tuple for range filtering

        if "," in filter_value:  # Handle multiple values
            values = [v.strip() for v in filter_value.split(",")]
            if np.issubdtype(column_type, np.floating):  # Float column
                return [float(v) for v in values]
            elif np.issubdtype(column_type, np.integer):  # Integer column
                return [int(v) for v in values]
            elif np.issubdtype(column_type, np.str_) or np.issubdtype(column_type, np.object_):  # String column
                return values
        else:  # Handle single value
            if np.issubdtype(column_type, np.floating):  # Float column
                return float(filter_value.strip())
            elif np.issubdtype(column_type, np.integer):  # Integer column
                return int(filter_value.strip())
            elif np.issubdtype(column_type, np.str_) or np.issubdtype(column_type, np.object_):  # String column
                return filter_value.strip()
        return filter_value
    except ValueError:
        print(f"Warning: Could not parse '{filter_value}' for column '{column}' with type '{column_type}'.")
        return filter_value


def get_user_filters(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prompts the user to input filter conditions for multiple columns and maps them to correct data types.

    Parameters:
        df (pd.DataFrame): The DataFrame for reference on columns and their types.

    Returns:
        Dict[str, Any]: A dictionary of filter conditions.
    """
    print("Available columns for filtering:", df.columns.tolist())

    selected_columns = input("Enter columns to filter, separated by commas (or type 'done' to finish): ").split(",")
    selected_columns = [col.strip() for col in selected_columns]

    filters = {}
    for column in selected_columns:
        if column not in df.columns:
            print(f"Warning: Column '{column}' does not exist in the DataFrame. Skipping this filter.")
            continue

        column_type = df[column].dtype  # Extract the column's data type
        filter_value = input(
            f"Enter filter value(s) for '{column}' (for multiple values, use comma-separated or range 'min-max' for difficulty): ").strip()

        # Correctly pass column_type to parse_filter_input
        filters[column] = parse_filter_input(column, filter_value, column_type)

    return filters


def plot_filtered_data(df: pd.DataFrame, x_column: str, y_column: str) -> None:
    """
    Plots a graph for the filtered data.

    Parameters:
        df (pd.DataFrame): The DataFrame containing filtered data.
        x_column (str): The column to plot on the x-axis.
        y_column (str): The column to plot on the y-axis.
    """
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
        df_grouped = df.groupby(x_column).size()
        df_grouped.plot(kind="bar", color="c")
        plt.title(f"{x_column} Distribution")
        plt.xlabel(x_column)
        plt.ylabel(y_column)

    plt.show()


# Main execution flow
if __name__ == "__main__":
    # Get file paths from user
    total_files = int(input("Enter the number of files you want to read.\n"))
    file_paths = [input(f"Enter path for file {i + 1}: ") for i in range(total_files)]

    # Load and clean data
    data_frames = read_and_clean_files(file_paths)

    # Combine all dataframes into one if multiple files
    data = pd.concat(data_frames.values(), ignore_index=True) if len(data_frames) > 1 else list(data_frames.values())[0]

    # Get filters from user input
    user_filters = get_user_filters(data)

    # Specify output columns
    output_columns = input("Columns to display, separated by commas: ").split(",")
    output_columns = list(filter(lambda col: col.strip() in data.columns, map(str.strip, output_columns)))

    # Apply filters to the data
    filtered_data = filter_data(data, user_filters, output_columns)

    # Save results to a CSV file
    filtered_data.to_csv("output.csv", index=False)

    # Ensure "tabber" is not displayed
    if "tabber" in filtered_data.columns:
        filtered_data = filtered_data.drop(columns=["tabber"])

    # Display results
    print("Results:" if not filtered_data.empty else "Sorry, no results matched.")
    if not filtered_data.empty:
        print(filtered_data)

        # Plot the filtered data
        plot_x = input("Enter the column for the x-axis: ").strip()
        plot_y = input("Enter the column for the y-axis: ").strip()
        plot_filtered_data(filtered_data, plot_x, plot_y)

