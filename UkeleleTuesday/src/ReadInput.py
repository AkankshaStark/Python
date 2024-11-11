import pandas as pd
from pandas import read_csv
from pandas.errors import EmptyDataError

# Take user input for number of files & the files' path name.
totalfilesnum = input("Enter the number of files you want to read.\n")
filepaths = [input(f"Enter path for file {i + 1}: ") for i in range(int(totalfilesnum))]

# Function to clean the data according to specified points
def clean_data(df):
    #Leave 'language' column as-is to signify no lyrics for missing values
    if 'language' in df.columns:
            missing_language_count = df['language'].isna().sum()
            if missing_language_count > 0:
                print(
                    f"Note: {missing_language_count} entries in 'language' are missing, indicating songs with no lyrics.")

    #Standardize 'language', 'source', 'type', and 'gender' to lowercase if they exist
    for col in ['language', 'source', 'type', 'gender']:
        if col in df.columns:
            df[col] = df[col].str.lower()

    #Set missing difficulty levels to -1
    if 'difficulty' in df.columns:
        df.fillna({'difficulty': "-1"}, inplace=True)

    # Return the cleaned DataFrame
    return df

# Read files and add them to a dictionary after cleaning if no exception is encountered.
data_frames = {}
for filepath in filepaths:
    try:
        df = read_csv(filepath)
        print(f"Successfully read file {filepath}")
        # Clean the data
        df = clean_data(df)
        # Store the cleaned DataFrame in the dictionary
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
