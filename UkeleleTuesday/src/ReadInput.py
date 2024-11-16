# ReadInput.py

import pandas as pd
from pandas import read_csv
from pandas.errors import EmptyDataError
from typing import List


# Function to clean the data according to specified points
def standardize_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Standardizes specified string columns by converting to lowercase and stripping whitespace.

    Parameters:
        df (pd.DataFrame): The DataFrame to clean.
        columns (List[str]): List of columns to standardize.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].str.lower().str.strip()
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handles missing values in specific columns.
    """
    if 'language' in df.columns:
        missing_language_count = df['language'].isna().sum()
        if missing_language_count > 0:
            print(f"Note: {missing_language_count} entries in 'language' are missing, indicating songs with no lyrics.")
    if 'difficulty' in df.columns:
        df['difficulty'] = df['difficulty'].astype(str).fillna("-1")
    return df


# Read and clean each file
def read_and_clean_files(filepaths: List[str]) -> dict:
    """
    Reads, cleans, and returns a dictionary of DataFrames for each file path.

    Parameters:
        filepaths (List[str]): List of file paths to read.

    Returns:
        dict: A dictionary of cleaned DataFrames keyed by file path.
    """
    data_frames = {}
    for filepath in filepaths:
        try:
            df = read_csv(filepath)
            print(f"Successfully read file {filepath}")
            # Apply standardization and missing value handling
            df = standardize_columns(df, ['language', 'source', 'type', 'gender'])
            df = handle_missing_values(df)
            data_frames[filepath] = df
        except FileNotFoundError:
            print(f"File '{filepath}' is not found. Please check the specified path for the file.")
        except pd.errors.ParserError:
            print(f"Error parsing data in file {filepath}")
        except UnicodeDecodeError:
            print(f"Invalid encoding of the file {filepath}")
        except EmptyDataError:
            print(f"Data not found in file {filepath}")
        except Exception as e:
            print(f"Some exception occurred in file {filepath}: {e}")

    return data_frames
