#libraries needed
import pandas as pd
import calendar as cal
import matplotlib.pyplot as plt
import numpy as np

#Read File
all_songs = pd.read_csv(r"C:\Users\rebec\OneDrive\Documentos\UCD First Trimester\Programming for Analytics\group assignment\tabdb_v2.csv", header=0)

#saving the hex code of the logo colours to be used later in the graphs
logo_yellow = "#c49526"  
logo_black = "#2f2f2f"  

#Duration conversion to minutes easy way done by python
#all_songs['duration_seconds'] = pd.to_timedelta(all_songs['duration']).dt.total_seconds()
#all_songs['duration_minutes'] = all_songs['duration_seconds'] / 60

#Trying the professor way of changing duration with calendar library and for loop, but more complicated
# Convert all values in the 'duration' column to strings
all_songs['duration'] = all_songs['duration'].astype(str)

# Iterate and replace in-place using a for loop
for i, duration in enumerate(all_songs['duration']):
    try:
        # Split the time string into hours, minutes, and seconds
        hours, minutes, seconds = map(int, duration.split(':'))

        # Calculate the total duration in minutes
        total_minutes = hours * 60 + minutes + seconds / 60

        # Replace the value in-place
        all_songs.at[i, 'duration'] = total_minutes  # Use .at for precise assignment

    except ValueError:
        # Handle cases where the duration value is not in the expected format
        print(f"Skipping invalid duration format at index {i}: {duration}")

# Rename column to reflect the new data
all_songs.rename(columns={'duration': 'duration_minutes'}, inplace=True)

#histogram of the songs by difficulty level
all_songs['difficulty'].plot(kind='hist', bins=5, title='Histogram of Songs by Difficulty Level', color=logo_yellow, edgecolor=logo_black, linewidth=1.5)
plt.xlabel('Difficulty Level')
plt.ylabel('Number of Songs')
plt.show()

# histogram of the songs by duration
plt.figure()  
all_songs['duration_minutes'].plot(kind='hist', bins=5, title='Histogram of Songs by Duration', color=logo_yellow, edgecolor=logo_black, linewidth=1.5)
plt.xlabel('Duration in minutes')
plt.ylabel('Number of Songs')
plt.show()

# bar chart of the songs by language
language_counter = all_songs['language'].value_counts()
plt.figure()  
language_counter.plot(kind='bar', title='Songs by Language', color=logo_yellow, edgecolor=logo_black, linewidth=1.5)
plt.xlabel('Languages')
plt.ylabel('Number of Songs')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# bar chart of the songs  by source
source_counter = all_songs['source'].value_counts()
plt.figure()  
source_counter.plot(kind='bar', title='Songs by Source', color = logo_yellow, edgecolor = logo_black, linewidth=1.5)
plt.xlabel('Source')
plt.ylabel('Number of Songs')
plt.xticks(rotation=45, ha='right')
plt.show()

# bar chart of the songs  by decade
all_songs['decade'] = (all_songs['year'] // 10) * 10
grouped_decades = all_songs['decade'].value_counts().sort_index()
grouped_decades = grouped_decades[grouped_decades > 0]
plt.figure()  
grouped_decades.plot(kind='bar', title='Songs by Decade', color = logo_yellow, edgecolor = logo_black, linewidth=1.5)
plt.xlabel('Decade')
plt.ylabel('Number of Songs')
plt.xticks(rotation=45, ha='right')
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

# Plot the cumulative line chart
plt.figure()
cumulative_counter.plot(kind='line', title='Number of Songs each Tuesday', color=logo_yellow, linewidth=2)
plt.xlabel('Date')
plt.ylabel('Number of Songs')
#leave just this code to get the month view: plt.xticks(rotation=45, ha='right')
#code to get the days view
plt.xticks(cumulative_counter.index, labels=cumulative_counter.index.strftime('%Y-%m-%d'), rotation=45, ha='right')
plt.show()


# Pie chart of the songs by gender.
plt.figure()
# Grouping duet, ensemble and instrumental values into a new category called 'other' 
all_songs['gender'] = np.where(
    all_songs['gender'].isin(['male', 'female']), 
    all_songs['gender'], 
    'other'
)

# Count occurrences of 'male' and 'female' only
gender_counts = all_songs['gender'].value_counts()
gender_counts = gender_counts[['male', 'female']]  # Focus only on male and female

gender_counts.plot(kind='pie', title='Pie Chart of Songs by Gender', colors=[logo_yellow, logo_black], labels=['Male', 'Female'])
plt.ylabel('')  # Explicitly set the Y-axis label to an empty string
plt.show()
