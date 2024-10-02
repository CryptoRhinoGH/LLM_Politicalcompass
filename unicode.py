import os
import unicodedata

# Set the directory where your JSON files are located
directory = "results/"

# Function to normalize text using NFKC form
def normalize_text(text):
    return unicodedata.normalize('NFKC', text)

# Loop through all JSON files in the specified directory
for filename in os.listdir(directory):
    if filename.endswith(".json"):
        file_path = os.path.join(directory, filename)

        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Normalize the content
        normalized_content = normalize_text(content)

        # Write the normalized content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(normalized_content)

print("Unicode normalization completed for all JSON files.")
