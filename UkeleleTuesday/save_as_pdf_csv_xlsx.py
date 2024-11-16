import pandas as pd

# Example DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Los Angeles', 'Chicago']"
}
df = pd.DataFrame(data)
    # change all of the above to connect to the dynamic filters

# Save the DataFrame to a CSV file
df.to_csv('output.csv', index=False)
df.to_excel('output.xlsx', index=False)

# Save DataFrame as a table in a PDF
fig, ax = plt.subplots(figsize=(8, 4))
ax.axis('off')  # Turn off the axis

# Create a table
table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
plt.savefig('output.pdf', bbox_inches='tight')
plt.close()

# Save the plot as a PDF
plt.savefig('songs_by_gender.pdf', format='pdf', bbox_inches='tight')  