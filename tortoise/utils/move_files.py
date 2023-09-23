import os
import shutil

def move_files_by_prefix(source_folder, destination_folder):
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Get a list of all files in the source folder
    files = os.listdir(source_folder)

    # Create a dictionary to store files based on their prefixes
    file_dict = {}

    # Iterate through the files and organize them by prefix
    for filename in files:
        prefix = filename.split('_')[0]  # Assuming underscore '_' is the separator
        if prefix not in file_dict:
            file_dict[prefix] = []
        file_dict[prefix].append(filename)

    # Move files to their respective folders
    for prefix, filenames in file_dict.items():
        prefix_folder = os.path.join(destination_folder, prefix)
        os.makedirs(prefix_folder, exist_ok=True)
        for filename in filenames:
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(prefix_folder, filename)
            shutil.move(source_path, destination_path)
            print(f"Moved '{filename}' to '{prefix_folder}'")

if __name__ == "__main__":
    source_folder = "C:/tools/output_audio_files/deniro"
    destination_folder = "C:/tools/output_audio_files/deniro"
    move_files_by_prefix(source_folder, destination_folder)
