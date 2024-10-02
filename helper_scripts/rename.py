import os

# Base directory where your folders are located
base_dir = './trial-3'  

# Walk through the base directory
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.startswith("Trial2_"):
            # Form the old and new file paths
            old_file = os.path.join(root, file)
            new_file = os.path.join(root, file.replace("Trial2_", "Trial3_", 1))
            
            # Rename the file
            os.rename(old_file, new_file)
            print(f'Renamed: {old_file} -> {new_file}')
