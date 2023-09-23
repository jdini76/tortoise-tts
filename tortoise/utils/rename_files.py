import os
import argparse

def rename_files_with_double_digit_numbers(input_folder, output_folder):
    # List all files in the input folder
    files = os.listdir(input_folder)

    if not files:
        print("No files found in the input folder.")
        return

    # Iterate through the files
    for filename in files:
        # Split the filename into its base and extension
        base_name, extension = os.path.splitext(filename)

        # Check if the base name contains an underscore ('_')
        if '_' in base_name:
            parts = base_name.split('_')
            new_parts = []

            # Process each part of the base name
            for part in parts:
                if part.isdigit() and len(part) == 1:
                    # Pad single-digit numbers with a leading zero
                    new_part = part.zfill(2)
                else:
                    new_part = part

                new_parts.append(new_part)

            new_base_name = '_'.join(new_parts)
        else:
            # If there's no underscore, handle the base name as before
            if base_name.isdigit() and len(base_name) == 1:
                new_base_name = base_name.zfill(2)
            else:
                new_base_name = base_name

        new_filename = 'section_'+new_base_name + extension

        # Rename the file
        old_path = os.path.join(input_folder, filename)
        new_path = os.path.join(output_folder, new_filename)
        os.rename(old_path, new_path)

        print(f"Renamed '{filename}' to '{new_filename}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename files by replacing single-digit numbers with double-digit numbers.")
    parser.add_argument("input_folder", type=str, help="Path to the input folder containing files to rename.")
    parser.add_argument("output_folder", type=str, help="Path to the output folder where renamed files will be saved.")
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder

    rename_files_with_double_digit_numbers(input_folder, output_folder)
