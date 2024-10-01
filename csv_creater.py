import csv

# Define the structure for the CSV files
header = ["Language", "Far Left", "Middle", "Far Right"]
trials = [f"Trial {i}" for i in range(1, 6)]
languages = ["English", "Spanish", "German", "French"]

# Create the CSV files with the specified structure
filenames = ["gpt_cookie_results.csv", "gemini_cookie_results.csv", "perplexity_cookie_results.csv"]

for filename in filenames:
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header row
        for language in languages:
            writer.writerow([language])  # Add language row
            for trial in trials:
                writer.writerow([trial, "", "", ""])  # Add trial rows with empty values

print("CSV files created successfully.")