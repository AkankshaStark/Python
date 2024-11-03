import pandas as pd
from pandas import read_csv
from pandas.errors import EmptyDataError

totalfilesnum = input("Enter the number of files you want to read.\n")
filepaths = [input(f"Enter path for file {i + 1}: ") for i in range(int(totalfilesnum))]

df = {}
for filepath in filepaths:
    try:
        df[filepath] = read_csv(filepath)
        print(f"Successfully read file {filepath}")
    except FileNotFoundError:
        print(f"File '{filepath}' is not found. Please check the specified path for the file.")
    except pd.errors.ParserError:
        print(f"Error parsing data in file {filepath}")
    except UnicodeDecodeError:
        print(f"Invalid encoding of the file {filepath}")
    except EmptyDataError:
        print(f"Data not found in file {filepath}")
    except Exception as e:
        print(f"Some exception occurred in file {filepath}")
