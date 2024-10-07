#!/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/llm_env/bin/python
import argparse
import argcomplete
import os
import subprocess
import glob
import csv

# Define global constants for row and column indices
LANGUAGE_START_ROW = {
    'english': 2,
    'spanish': 8,
    'german': 14,
    'french': 20  # Added French
}

COLUMN_INDEX = {
    'left': 2,
    'farleft': 2,
    'middle': 3,
    'farright': 4,
    'right': 4
}

def check_csv_for_value(filename, language, trial_number, political_view):
    """Checks if the ec and soc values are already in the CSV file."""
    language_row = LANGUAGE_START_ROW[language.lower()]  # Starting row for the language
    target_row = language_row + trial_number - 1  # Calculate the target row
    response_column = COLUMN_INDEX[political_view] - 1  # Get the column index for the response type

    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        # Ensure the reader has enough rows
        for i, row in enumerate(reader):
            if i == target_row:
                if row[response_column]:  # Check if the cell is already populated
                    return True  # Value already exists in the CSV

    return False  # Value does not exist

def run_trial_script(trial_number=None, chatbot=None, language=None, political_view = None):
    """Runs the trial processing script with the specified parameters."""
    json_pattern = "results/"

    if trial_number:
        json_pattern += f"Trial{trial_number}_"
    else:
        json_pattern += "Trial*_"

    if chatbot:
        json_pattern += f"{chatbot}_"
    else:
        json_pattern += "*_"

    if language:
        json_pattern += f"{language}_"
    else:
        json_pattern += "*"

    if political_view:
        json_pattern += f"{political_view}"

    json_pattern += "*.json"  # Complete the pattern with the .json extension

    # Find all matching JSON files
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"No result files found for Trial {trial_number}, Chatbot {chatbot}, Language {language}")
        return

    print(f"Files found: {json_files}")
    print()

    for json_file in json_files:
        print(f"Running script for {json_file}...")
        
        # Extracting details from the filename for checking
        base_filename = os.path.basename(json_file)
        parts = base_filename.split('_')

        # Update the trial_number extraction logic to handle parts correctly
        trial_number = int(parts[0].lstrip('Trial'))  # Extracting the trial number
        chatbot = parts[1]  # Extracting chatbot name
        language = parts[2]  # Extracting language
        political_view = parts[3].rstrip('.json')  # Extracting political view

        # Determine the corresponding CSV filename based on chatbot
        filename_mapping = {
            'gpt': 'csv_results/gpt_cookie_results.csv',
            'gemini': 'csv_results/gemini_cookie_results.csv',
            'perplexity': 'csv_results/perplexity_cookie_results.csv'
        }
        
        filename = filename_mapping.get(chatbot, None)
        if filename:
            if check_csv_for_value(filename, language, trial_number, political_view):
                # print(f"Values already exist in {filename} for Trial {trial_number}, Chatbot {chatbot}, Language {language}. Skipping.")
                continue  # Skip to the next file if the value already exists

            try:
                # Construct the command to run the processing script
                command = ["python3", "political_compass.py", json_file]
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                # print(json_file)
                print(f"Error while running {json_file}: {e}")
                print("\n")
                continue  # Skip to the next file in case of an error

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runner for survey processing trials.')
    parser.add_argument('--trial-number', type=int, help='The trial number to process (optional).')
    parser.add_argument('--chatbot', type=str, help='The chatbot type to process (optional).')
    parser.add_argument('--language', type=str, choices=['english', 'german', 'spanish', 'french'],
                        help='The language of the responses (optional).')
    parser.add_argument('--pol', type=str, choices=['farleft', 'farright', 'middle'],
                        help='The political view of the responses (optional).')
    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    run_trial_script(args.trial_number, args.chatbot, args.language, args.pol)
