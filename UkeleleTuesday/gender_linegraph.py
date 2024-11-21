import pandas as pd
import matplotlib.pyplot as plt

def generate_gender_line_plot_with_counts(file_path, x_column):
    try:
        # Load the dataset
        data = pd.read_csv(file_path)

        # Ensure the required columns exist
        if x_column not in data.columns:
            print(f"Error: '{x_column}' column not found in the dataset.")
            return

        if 'gender' not in data.columns:
            print("Error: 'gender' column not found in the dataset.")
            return

        # Count occurrences of each gender
        gender_counts = data['gender'].value_counts()

        # Create a DataFrame to map x and y values
        plot_data = pd.DataFrame({
            'gender': gender_counts.index,
            'count': gender_counts.values,
            x_column: range(1, len(gender_counts) + 1)  # Assign sequential x values
        })

        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.plot(
            plot_data[x_column],
            plot_data['count'],
            marker='o',  # Add markers
            label='Genders'
        )
        # Plot each gender separately with a distinct label
        
        for i, row in plot_data.iterrows():
            label = gender_counts.index[i]
            plt.plot(
                [row[x_column]],  # X-value
                [row['count']],    # Y-value
                marker='o',       # Add markers
                label= label # Label with gender
            )

        # Annotate each point with gender names and counts
        for i, row in plot_data.iterrows():
            plt.text(
                row[x_column], row['count'], f"{row['gender']}: {row['count']}",
                ha='center', va='bottom', fontsize=10
            )

        # Customize the plot
        plt.title(f"Line Plot: Gender Counts with {x_column}", fontsize=16)
        plt.xlabel(x_column, fontsize=14)
        plt.ylabel("Counts", fontsize=14)
        plt.xticks(plot_data[x_column], plot_data['gender'])  # Replace x-ticks with gender names
        plt.grid(True)
        
        # Add a legend to show gender categories
        plt.legend(title="Gender Categories", loc='best')

        plt.tight_layout()

        # Show the plot
        plt.show()

    except FileNotFoundError:
        print("Error: File not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
generate_gender_line_plot_with_counts("C:/Users/Checking/Downloads/tabdb_f.csv", "gender")
