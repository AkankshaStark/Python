from functools import reduce
import pandas as pd
import numpy as np
from typing import Dict, Any


def apply_filter(df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
    """
    Apply a filter to the DataFrame based on the column and value(s) provided.
    """
    print(f"Applying filter for column '{column}' with value(s): {value}")

    # Check if DataFrame is empty
    if df.empty:
        print("The DataFrame is empty. Skipping filtering.")
        return df

    # Check if the column exists
    if column not in df.columns:
        print(f"Warning: Column '{column}' does not exist in the DataFrame. Skipping this filter.")
        return df

    # Handle numeric columns
    if pd.api.types.is_numeric_dtype(df[column]):
        try:
            if isinstance(value, tuple) and len(value) == 2:  # Range filter (min, max)
                return df[(df[column] >= value[0]) & (df[column] <= value[1])]
            if isinstance(value, list):  # List of numeric values
                value = [float(v) for v in value]
                return df[df[column].isin(value)]
            return df[df[column] == float(value)]
        except (ValueError, TypeError):
            print(f"Warning: Could not apply numeric filter on column '{column}' with value '{value}'.")
            return df

    # Handle string columns (normalize for case-insensitive matching)
    if pd.api.types.is_string_dtype(df[column]):
        if isinstance(value, list):
            value = [str(v).strip().lower() for v in value]  # Normalize filter values
            print(f"Normalized string filter values for column '{column}': {value}")
            return df[df[column].str.strip().str.lower().isin(value)]
        else:
            value = str(value).strip().lower()
            return df[df[column].str.strip().str.lower() == value]

    # Handle unsupported column types
    print(f"Warning: Unsupported column type for '{column}'. Skipping this filter.")
    return df


def parse_filter_input(column: str, filter_value: Any, column_type: Any) -> Any:
    """
    Parses the filter value provided by the user and converts it to the correct type.
    """
    try:
        # If filter_value is a list, process each item
        if isinstance(filter_value, list):
            parsed_values = []
            for value in filter_value:
                if pd.api.types.is_numeric_dtype(column_type):  # Numeric column
                    parsed_values.append(float(value.strip()))
                elif pd.api.types.is_string_dtype(column_type):  # String column
                    parsed_values.append(value.strip())
            return parsed_values

        # Handle single value case
        if pd.api.types.is_numeric_dtype(column_type):  # Numeric column
            return float(filter_value.strip())
        elif pd.api.types.is_string_dtype(column_type):  # String column
            return filter_value.strip()

        return filter_value  # Return as is for unsupported types
    except (ValueError, AttributeError):
        print(f"Warning: Could not parse '{filter_value}' for column '{column}' with type '{column_type}'.")
        return None


def get_user_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Collects user input for filter criteria and applies the filters to the DataFrame.
    """
    # Check for empty DataFrame
    if df.empty:
        print("The DataFrame is empty. No filters can be applied.")
        return df

    parsed_filters = {}  # A dictionary to hold parsed filters for each column

    for column, filter_values in filters.items():
        column_type = df[column].dtype  # Get column type (numeric, string, etc.)
        parsed_filter = parse_filter_input(column, filter_values, column_type)

        # Skip invalid or empty filters
        if not parsed_filter:
            print(f"Skipping filter for column '{column}' due to invalid or empty value.")
            continue

        parsed_filters[column] = parsed_filter

    if not parsed_filters:
        print("No valid filters provided.")
        return df

    # Apply filters using reduce
    filtered_df = reduce(lambda df, kv: apply_filter(df, kv[0], kv[1]), parsed_filters.items(), df)

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        print("No results matched the filters.")
        return filtered_df

    return filtered_df


def plot_filtered_data(df: pd.DataFrame, x_column: str, y_column: str) -> None:
    """
    Plots a graph for the filtered data.
    """
    import matplotlib.pyplot as plt

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
        plt.ylabel("Frequency")

    plt.show()


# Main execution flow
if __name__ == "__main__":
    # Assuming ReadInput.py has a read_and_clean_files function that reads and cleans data
    from ReadInput import read_and_clean_files

    # Get file paths from user
    total_files = int(input("Enter the number of files you want to read.\n"))
    file_paths = [input(f"Enter path for file {i + 1}: ") for i in range(total_files)]

    # Load and clean data
    data_frames = read_and_clean_files(file_paths)

    # Combine all dataframes into one if multiple files
    data = pd.concat(data_frames.values(), ignore_index=True) if len(data_frames) > 1 else list(data_frames.values())[0]

    # Check if the combined DataFrame is empty
    if data.empty:
        print("No data available after loading the files.")
        exit()

    # Get filters from user input
    user_filters = {}
    print("Enter filter values for each column (comma-separated for multiple values):")
    for column in data.columns:
        filter_value = input(f"Filter for '{column}': ").strip()
        if filter_value:
            user_filters[column] = filter_value.split(",")  # Allow multiple filter values

    # Specify output columns
    output_columns = input("Columns to display, separated by commas: ").split(",")
    output_columns = list(filter(lambda col: col.strip() in data.columns, map(str.strip, output_columns)))

    # Apply filters to the data
    filtered_data = get_user_filters(data, user_filters)

    # Save results to a CSV file
    if not filtered_data.empty:
        filtered_data.to_csv("output.csv", index=False)
        print("Filtered data saved to 'output.csv'.")
    else:
        print("No data matched the provided filters.")
