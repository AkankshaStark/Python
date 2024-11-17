import pandas as pd
import os
import calendar as cal
import matplotlib.pyplot as plt
import numpy as np

def file_path_input(file_description):
    #while True:
        file_path = input(f"Enter the full file path for {file_description} (CSV format): ").strip()
        if os.path.isfile(file_path):
            try:
                input_file_df = pd.read_csv(file_path)  # Attempt to load the file
                print(f"'{file_description}' loaded successfully! {input_file_df.shape[0]} rows and {input_file_df.shape[1]} columns detected.")
                return input_file_df
            except Exception as e:
                print(f"Error loading file: {e}")
        else:
            print(f"Invalid file path for {file_description}. Please try again.")

def display_menu(column):
    print("Available columns: ")
    for i, col in enumerate(column, 1):
        print(f"{i}. {col}")
    print(f"{len(column) + 1}. Exit")

def select_filter(tab_df, column):
    start_range, end_range = None, None
    choice = int(input("\nSelect the option you want to filter: "))
    if 1 <= choice <= len(column):
        search_column = column[choice-1]
        tab_df[search_column] = tab_df[search_column].astype(str).str.lower()
        filtered_tab_df = tab_df.dropna(subset=[search_column])
        exclude_values = ["none", "nan"]
        filtered_tab_df = filtered_tab_df[~filtered_tab_df[search_column].isin(exclude_values)]
        filtered_tab_df[search_column] = filtered_tab_df[search_column].str.replace(" ", "").str.split(",")
        filtered_tab_df[search_column] = filtered_tab_df[search_column].apply(lambda x: ",".join(sorted(x)))
        if 'date' in search_column:
            filtered_tab_df[search_column] = pd.to_datetime(filtered_tab_df[search_column], errors='coerce')
            filtered_tab_df[search_column] = filtered_tab_df[search_column].dt.strftime('%d-%m-%Y')
        print(filtered_tab_df[search_column].drop_duplicates().to_string(index=False))
        if search_column in ['date', 'year', 'duration']:
            start_range = input(f"Enter the start {search_column} you want to search: ")
            end_range = input(f"Enter the end {search_column} you want to search: ")
            search_term = None
        else:
            selected_terms = input(f"Enter the {search_column} you want to search, separated by commas: ")
            search_term = [term.strip() for term in selected_terms.split(",")]
        return search_term, search_column, start_range, end_range
    elif choice == len(column) + 1:
        print("Exiting....")
        return None, None, None, None
    else:
        print("\nInvalid choice. Select an option between 1 and", len(column) + 1)
        return None, None, None, None

def result_columns(tab_df):
    menu_columns = list(tab_df.columns)
    display_menu(menu_columns)
    selected_options = input("Select the columns to display in the output, separated by commas: ")
    selected_options = [int(index.strip()) - 1 for index in selected_options.split(",")]
    columns_to_display = [menu_columns[i] for i in selected_options]
    return columns_to_display

def search_filter_results(tab_df, start_range, end_range, search_term, search_column, output_columns):
    if search_column in ['date', 'year', 'duration']:
        searched_data = tab_df[(tab_df[search_column] >= start_range) & (tab_df[search_column] <= end_range)]
    else:
        search_term = [term.strip().lower() for term in search_term]
        all_terms = set(
            term.strip().lower()
            for row in tab_df[search_column].dropna().astype(str)
            for term in row.split(",")
        )
        exclude_terms = list(all_terms - set(search_term))
        search_term = ''.join(f"(?=.*\\b{term}\\b)" for term in search_term)
        exclude_pattern = ''.join(f"(?!.*\\b{term}\\b)" for term in exclude_terms)
        search_pattern = f"^{search_term}{exclude_pattern}.*$"
        searched_data = tab_df[tab_df[search_column].str.contains(search_pattern, case=False, na=False, regex=True)]
    result_df = searched_data[output_columns]
    print("\nFiltered results:")
    print(result_df)
    return result_df

def sort_filter_results(result):
    selected_column_sort = input("Enter the columns to sort by, separated by commas: ").strip().split(",")
    sort_order = input("Enter 'asc' for ascending or 'desc' for descending order: ").strip().lower()
    ascending = True if sort_order == 'asc' else False
    sorted_data = result.sort_values(by=selected_column_sort, ascending=ascending)
    print("\nSorted Results:")
    print(sorted_data.to_string(index=False))

def song_count(play_df, result):
    matching_rows = play_df[play_df['song'].str.lower().isin(result['song'].str.lower())]
    matching_rows.loc[:,'total_plays'] = matching_rows.iloc[:, 2:].sum(axis=1).astype(int)
    print("Matching Songs and Total Plays:")
    print(matching_rows[['song', 'total_plays']])

#BAR CHART SONGS BY LANGUAGE
# Function to standardize language data points
def standardized_languages(languages_string):
    languages = languages_string.split(",")  # Split by comma since this is a csv file
    languages.sort()  # Sort alphabetically
    return ",".join(languages)  # Join back to the column
    
def main():
    tab_df = file_path_input("tabdb")
    play_df = file_path_input("playdb")
    request_df = file_path_input("requestdb")
    tab_df.pop("tabber")
    menu_columns = list(tab_df.columns)
    display_menu(menu_columns)
    search_term, search_column, start_range, end_range = select_filter(tab_df, menu_columns)
    output_columns = result_columns(tab_df)
    result = search_filter_results(tab_df, start_range, end_range, search_term, search_column, output_columns)
    sort_filter_results(result)
    song_count(play_df, result)

    colours = ['#A8D5BA', '#86C38F', '#6BAF75', '#4E965A', '#316E42']
    fig, ax = plt.subplots()
    counts, bins, patches = ax.hist(tab_df['difficulty'], bins=5, edgecolor="#2f2f2f", linewidth=1.5)
    #counts as the number of data points in each bin
    #bins defines the edges of each of the bins
    #patches defines the list of rectangle objects that will lead to bars in the histogram

# Assign colors to bins, for loop goes through each bar (patch) in the histogram and assigns colour from the previously defined colour palette list
    for patch, color in zip(patches, colours):
        patch.set_facecolor(color)

# Add title and labels to improve readability and show the plot
    plt.title('Histogram of Songs by Difficulty Level')
    plt.xlabel('Difficulty Level')
    plt.ylabel('Number of Songs')
    plt.show()


#HISTOGRAM OF SONGS BY DURATION 
# Convert duration to seconds and then to minutes
    tab_df['duration_seconds'] = pd.to_timedelta(tab_df['duration']).dt.total_seconds()
    tab_df['duration_minutes'] = tab_df['duration_seconds'] / 60

# Define the color palette for each bin
    colour_palette = ['#CCE5FF', '#99CCFF', '#66B2FF', '#338AFF', '#0066CC']

# Create the histogram
    fig, ax = plt.subplots()
    counts, bins, patches = ax.hist(tab_df['duration_minutes'], bins=5, edgecolor="#2f2f2f", linewidth=1.5)

# Assign colors to bins
    for patch, color in zip(patches, colour_palette):  # Use 'color' instead of 'colours' to avoid conflict
        patch.set_facecolor(color)

# Add title and labels and display the plot
    plt.title('Histogram of Songs by Duration')
    plt.xlabel('Duration in minutes')
    plt.ylabel('Number of Songs')
    plt.show()

# Replace NaN and Blanks with the new category called 'unknown' to make it easier to understand
    tab_df['language'] = tab_df['language'].fillna('unknown').replace("(Blanks)", "unknown")

# Apply the standardization function only to all values that aren't in the unknown category
    tab_df['language'] = tab_df['language'].apply(
        lambda x: standardized_languages(x) if x != 'unknown' else x
    )

# Fixing the language column to count individual occurrences and npt have groupped entries such as english, spanish
# Filter out 'unknown'
    filtered_languages = tab_df[tab_df['language'] != 'unknown']['language']

# Split and flatten the entries
    flattened_languages = filtered_languages.str.split(",").explode()

    language_counter = flattened_languages.value_counts()

# Define the color palette for the languages
    color_palette = {
        'english': '#1f77b4',
        'french': '#2ca02c',
        'italian': '#d62728',
        'german': '#bcbd22',
        'none': '#7f7f7f',
        'portuguese': '#17becf',
        'unknown': '#8c564b',
        'spanish': '#006400',
        'hawaiian': '#e377c2'
    }

# Map the colors to the languages in the DataFrame
    colors = [color_palette.get(lang, '#000000') for lang in language_counter.index]  # Default to black if not in palette

# Plot the bar chart
    plt.figure()
    language_counter.plot(
        kind='bar',
        title='Songs by Language',
        color=colors,  # Use the custom colors for the bars
        edgecolor='black',  # Black edges for better distinction
        linewidth=1.5
    )
    plt.xlabel('Languages')
    plt.ylabel('Number of Songs')
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    plt.show()


#BAR CHART OF THE SONGS BY SOURCE
    source_counter = tab_df['source'].value_counts()
# Define the color palette for the sources
    source_color_palette = {
        'new': '#4CAF50',  
        'old': '#FFC107',  
        'off': '#F44336'   
    }

# Map the colors to the sources in the file
    source_colors = [source_color_palette.get(src, '#000000') for src in source_counter.index]  

# Plot the bar chart
    plt.figure()  
    source_counter.plot(
        kind='bar',
        title='Songs by Source',
        color=source_colors,  # Use the custom colors for the bars
        edgecolor='black',  # Black edges for better distinction
        linewidth=1.5
    )
    plt.xlabel('Source')
    plt.ylabel('Number of Songs')
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    plt.show()

#BAR CHART OF THE SONGS BY DECADE
# bar chart of the songs  by decade
    tab_df['decade'] = (tab_df['year'] // 10) * 10

    grouped_decades = tab_df['decade'].value_counts().sort_index()

    grouped_decades = grouped_decades[grouped_decades > 0]

    # Define the color palette for the decades
    decade_color_palette = {
        1890: '#F5E6CC',  # Light Beige
        1900: '#FFFACD',  # Light Yellow
        1950: '#DFF2BF',  # Light Green
        1960: '#A9DFBF',  # Soft Mint Green
        1970: '#73C6B6',  # Soft Teal
        1980: '#5DADE2',  # Light Blue
        1990: '#3498DB',  # Medium Blue
        2000: '#2874A6',  # Indigo
        2010: '#884EA0',  # Violet
        2020: '#633974'   # Dark Purple
    }

# Map the colors to the decades in the DataFrame
    decade_colors = [decade_color_palette.get(decade, '#000000') for decade in grouped_decades.index]  

# Plot the bar chart
    plt.figure()  
    grouped_decades.plot(
        kind='bar',
        title='Songs by Decade',
        color=decade_colors,  # Apply the custom colors
        edgecolor='black',  
        linewidth=1.5
    )
    plt.xlabel('Decade')
    plt.ylabel('Number of Songs')
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    plt.show()

#cumulative line chart of the number of songs played each Tuesday for the dates provided
    tab_df['date'] = tab_df['date'].dropna().astype(int).astype(str)  # Remove NaN, convert to int, then string

# Revised loop for reformatting dates
    for i, raw_date in enumerate(tab_df['date']):
        try:
            raw_date = str(raw_date)  # Ensure raw_date is a string
            year = raw_date[:4]
            month = raw_date[4:6]
            day = raw_date[6:]
            formatted_date = f"{year}-{int(month):02d}-{int(day):02d}"
            tab_df.at[i, 'date'] = formatted_date
        except (ValueError, IndexError):  # Handle invalid or incomplete date strings
            tab_df.at[i, 'date'] = None

# Remove rows with invalid or missing dates
    tab_df = tab_df.dropna(subset=['date'])

# Convert to datetime
    tab_df['date'] = pd.to_datetime(tab_df['date'], errors='coerce')
    tab_df = tab_df.dropna(subset=['date'])

# Generate a cumulative count
    cumulative_counter = tab_df['date'].value_counts().sort_index().cumsum()

#Colour of this graph 
    line_colour = "#4CAF50"  

# Plot the cumulative line chart
    plt.figure()
    cumulative_counter.plot(kind='line', title='Number of Songs each Tuesday', color=line_colour, linewidth=2)
    plt.xlabel('Date')
    plt.ylabel('Number of Songs')
#code to get the days view
    plt.xticks(cumulative_counter.index, labels=cumulative_counter.index.strftime('%Y-%m-%d'), rotation=45, ha='right')
    plt.show()


# Pie chart of the songs by gender.
    plt.figure()

#Colour of this graph 
    male_colour = "#42A5F5"
    female_colour = "#FF7043"
    duet_colour = "#B39DDB"
    ensemble_colour = "#26A69A"
    instrumental_colour = "#B0BEC5"

    gender_counts = tab_df['gender'].value_counts()
    gender_counts = gender_counts[['male', 'female','duet', 'ensemble', 'instrumental']] 

    gender_counts.plot(kind='pie', title='Pie Chart of Songs by Gender', colors=[male_colour, female_colour, duet_colour, ensemble_colour, instrumental_colour], labels=['Male', 'Female', 'Duet', 'Ensemble', 'Instrumental'])
    plt.ylabel('')  # Explicitly set the Y-axis label to an empty string
    plt.show()

main()
