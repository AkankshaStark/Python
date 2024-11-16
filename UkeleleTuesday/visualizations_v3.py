#libraries needed
import pandas as pd
import calendar as cal
import matplotlib.pyplot as plt
import numpy as np

#Read File
all_songs = pd.read_csv(r"C:\Users\rebec\OneDrive\Documentos\UCD First Trimester\Programming for Analytics\group assignment\tabdb_v2.csv", header=0)

#HISTOGRAM OF THE SONGS BY DIFFICULTY LEVEL
#Colour Palette of this graph
colours = ['#A8D5BA', '#86C38F', '#6BAF75', '#4E965A', '#316E42']

# Create the histogram, creates a figure and an axis
fig, ax = plt.subplots() 

# Generate the histogram and get the bin counts
counts, bins, patches = ax.hist(all_songs['difficulty'], bins=5, edgecolor="#2f2f2f", linewidth=1.5)
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
all_songs['duration_seconds'] = pd.to_timedelta(all_songs['duration']).dt.total_seconds()
all_songs['duration_minutes'] = all_songs['duration_seconds'] / 60

# Define the color palette for each bin
colour_palette = ['#CCE5FF', '#99CCFF', '#66B2FF', '#338AFF', '#0066CC']

# Create the histogram
fig, ax = plt.subplots()
counts, bins, patches = ax.hist(all_songs['duration_minutes'], bins=5, edgecolor="#2f2f2f", linewidth=1.5)

# Assign colors to bins
for patch, color in zip(patches, colour_palette):  # Use 'color' instead of 'colours' to avoid conflict
    patch.set_facecolor(color)

# Add title and labels and display the plot
plt.title('Histogram of Songs by Duration')
plt.xlabel('Duration in minutes')
plt.ylabel('Number of Songs')
plt.show()


#BAR CHART SONGS BY LANGUAGE
# Function to standardize language data points
def standardized_languages(languages_string):
    languages = languages_string.split(",")  # Split by comma since this is a csv file
    languages.sort()  # Sort alphabetically
    return ",".join(languages)  # Join back to the column

# Replace NaN and Blanks with the new category called 'unknown' to make it easier to understand
all_songs['language'] = all_songs['language'].fillna('unknown').replace("(Blanks)", "unknown")

# Apply the standardization function only to all values that aren't in the unknown category
all_songs['language'] = all_songs['language'].apply(
    lambda x: standardized_languages(x) if x != 'unknown' else x
)

# Fixing the language column to count individual occurrences and npt have groupped entries such as english, spanish
# Filter out 'unknown'
filtered_languages = all_songs[all_songs['language'] != 'unknown']['language']

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
source_counter = all_songs['source'].value_counts()
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
all_songs['decade'] = (all_songs['year'] // 10) * 10

grouped_decades = all_songs['decade'].value_counts().sort_index()

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
all_songs['date'] = all_songs['date'].dropna().astype(int).astype(str)  # Remove NaN, convert to int, then string

# Revised loop for reformatting dates
for i, raw_date in enumerate(all_songs['date']):
    try:
        raw_date = str(raw_date)  # Ensure raw_date is a string
        year = raw_date[:4]
        month = raw_date[4:6]
        day = raw_date[6:]
        formatted_date = f"{year}-{int(month):02d}-{int(day):02d}"
        all_songs.at[i, 'date'] = formatted_date
    except (ValueError, IndexError):  # Handle invalid or incomplete date strings
        all_songs.at[i, 'date'] = None

# Remove rows with invalid or missing dates
all_songs = all_songs.dropna(subset=['date'])

# Convert to datetime
all_songs['date'] = pd.to_datetime(all_songs['date'], errors='coerce')
all_songs = all_songs.dropna(subset=['date'])

# Generate a cumulative count
cumulative_counter = all_songs['date'].value_counts().sort_index().cumsum()

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

gender_counts = all_songs['gender'].value_counts()
gender_counts = gender_counts[['male', 'female','duet', 'ensemble', 'instrumental']] 

gender_counts.plot(kind='pie', title='Pie Chart of Songs by Gender', colors=[male_colour, female_colour, duet_colour, ensemble_colour, instrumental_colour], labels=['Male', 'Female', 'Duet', 'Ensemble', 'Instrumental'])
plt.ylabel('')  # Explicitly set the Y-axis label to an empty string
plt.show()

